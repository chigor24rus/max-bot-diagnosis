import json
import os
import boto3
import psycopg2
from datetime import datetime, timedelta


def handler(event: dict, context) -> dict:
    '''Очистка хранилища: удаляет файлы осиротевших диагностик через проверку по известным URL и перебор дат'''

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }

    if event.get('httpMethod') != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }

    body = json.loads(event.get('body', '{}'))
    dry_run = body.get('dryRun', True)

    db_url = os.environ.get('DATABASE_URL')
    schema = os.environ.get('MAIN_DB_SCHEMA')
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    cdn_prefix = f"https://cdn.poehali.dev/projects/{aws_key}/bucket/"

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(f"SELECT id FROM {schema}.diagnostics")
    existing_ids = set(row[0] for row in cur.fetchall())

    cur.execute(f"SELECT last_value FROM {schema}.diagnostics_id_seq")
    max_id = cur.fetchone()[0]

    deleted_ids = set(range(1, max_id + 1)) - existing_ids
    print(f"[cleanup] existing: {len(existing_ids)} IDs, max_id: {max_id}, deleted_ids: {len(deleted_ids)} IDs to check")

    s3 = boto3.client('s3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

    orphan_keys = []
    orphan_size = 0

    cur.execute(f"SELECT diagnostic_id, photo_url FROM {schema}.diagnostic_photos")
    for row in cur.fetchall():
        diag_id = row[0]
        url = row[1]
        if diag_id not in existing_ids and url and url.startswith(cdn_prefix):
            key = url[len(cdn_prefix):]
            size = _check_s3_key(s3, key)
            if size is not None:
                orphan_keys.append(key)
                orphan_size += size
                print(f"[cleanup] ORPHAN photo from DB: {key} ({size} bytes)")

    if deleted_ids:
        ids_list = list(deleted_ids)
        cur.execute(f"SELECT id, report_url, report_with_photos_url FROM {schema}.diagnostics WHERE id IN ({','.join(str(i) for i in ids_list)})")
    else:
        cur.execute(f"SELECT id, report_url, report_with_photos_url FROM {schema}.diagnostics WHERE FALSE")
    for row in cur.fetchall():
        for url in [row[1], row[2]]:
            if url and url.startswith(cdn_prefix):
                key = url[len(cdn_prefix):]
                size = _check_s3_key(s3, key)
                if size is not None:
                    orphan_keys.append(key)
                    orphan_size += size
                    print(f"[cleanup] ORPHAN report from DB: {key} ({size} bytes)")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=60)
    
    scan_limit = min(len(deleted_ids), 5)
    scanned_count = 0
    for diag_id in sorted(deleted_ids, reverse=True):
        if scanned_count >= scan_limit:
            break
        print(f"[cleanup] Checking reports for deleted diagnostic {diag_id} (date range scan)")
        current_date = start_date
        found_count = 0
        while current_date <= end_date and found_count < 3:
            date_str = current_date.strftime('%Y%m%d')
            for hour in range(0, 24, 12):
                for minute in [0, 30]:
                    time_str = f"{hour:02d}{minute:02d}"
                    for suffix in ['', '_with_photos']:
                        for second in [0, 30]:
                            key = f"reports/diagnostic_{diag_id}{suffix}_{date_str}_{time_str}{second:02d}.pdf"
                            size = _check_s3_key(s3, key)
                            if size is not None:
                                if key not in orphan_keys:
                                    orphan_keys.append(key)
                                    orphan_size += size
                                    found_count += 1
                                    print(f"[cleanup] ORPHAN report by scan: {key} ({size} bytes)")
            current_date += timedelta(days=1)
        scanned_count += 1

    print(f"[cleanup] Total orphan files: {len(orphan_keys)}, size: {orphan_size}")

    cur.execute(
        f"SELECT DISTINCT diagnostic_id FROM {schema}.diagnostic_photos "
        f"WHERE diagnostic_id NOT IN (SELECT id FROM {schema}.diagnostics)"
    )
    orphan_photo_diag_ids = set(row[0] for row in cur.fetchall())

    cur.execute(
        f"SELECT DISTINCT diagnostic_id FROM {schema}.checklist_answers "
        f"WHERE diagnostic_id NOT IN (SELECT id FROM {schema}.diagnostics)"
    )
    orphan_answer_diag_ids = set(row[0] for row in cur.fetchall())

    orphan_db_records = len(orphan_photo_diag_ids) + len(orphan_answer_diag_ids)
    print(f"[cleanup] Orphan DB records: {orphan_db_records}")

    deleted_files = 0
    deleted_db = 0

    if not dry_run:
        for key in orphan_keys:
            try:
                s3.delete_object(Bucket='files', Key=key)
                deleted_files += 1
                print(f"[cleanup] DELETED: {key}")
            except Exception as e:
                print(f"[cleanup] Failed to delete {key}: {e}")

        if orphan_photo_diag_ids:
            ids_str = ','.join(str(i) for i in orphan_photo_diag_ids)
            cur.execute(f"DELETE FROM {schema}.diagnostic_photos WHERE diagnostic_id IN ({ids_str})")
            deleted_db += cur.rowcount

        if orphan_answer_diag_ids:
            ids_str = ','.join(str(i) for i in orphan_answer_diag_ids)
            cur.execute(f"DELETE FROM {schema}.checklist_answers WHERE diagnostic_id IN ({ids_str})")
            deleted_db += cur.rowcount

        conn.commit()

    cur.close()
    conn.close()

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'dryRun': dry_run,
            'orphanFiles': len(orphan_keys),
            'orphanSize': orphan_size,
            'orphanSizeFormatted': _format_size(orphan_size),
            'orphanDbRecords': orphan_db_records,
            'deletedFiles': deleted_files,
            'deletedDbRecords': deleted_db
        }),
        'isBase64Encoded': False
    }


def _check_s3_key(s3, key):
    try:
        resp = s3.head_object(Bucket='files', Key=key)
        return resp.get('ContentLength', 0)
    except Exception:
        return None


def _format_size(bytes_val):
    if bytes_val < 1024:
        return f"{bytes_val} Б"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} КБ"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.1f} МБ"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} ГБ"