import json
import os
import re
import boto3
import psycopg2


def handler(event: dict, context) -> dict:
    '''Полная очистка хранилища: удаляет файлы и записи БД от несуществующих диагностик'''

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

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute(f"SELECT id FROM {schema}.diagnostics")
    existing_ids = set(row[0] for row in cur.fetchall())
    print(f"[cleanup] existing diagnostic IDs: {existing_ids}")

    s3 = boto3.client('s3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

    all_s3_keys = []
    orphan_keys = []
    orphan_size = 0

    for prefix in ['diagnostics/', 'reports/']:
        print(f"[cleanup] listing S3 prefix: {prefix}")
        try:
            continuation_token = None
            while True:
                kwargs = {'Bucket': 'files', 'Prefix': prefix, 'MaxKeys': 1000}
                if continuation_token:
                    kwargs['ContinuationToken'] = continuation_token

                resp = s3.list_objects_v2(**kwargs)
                contents = resp.get('Contents', [])
                print(f"[cleanup] list_objects_v2({prefix}): {len(contents)} objects, IsTruncated={resp.get('IsTruncated')}")

                for obj in contents:
                    key = obj['Key']
                    size = obj.get('Size', 0)
                    all_s3_keys.append(key)

                    diag_id = _extract_diagnostic_id(key, prefix)
                    if diag_id is not None and diag_id not in existing_ids:
                        orphan_keys.append(key)
                        orphan_size += size
                        print(f"[cleanup] ORPHAN: {key} (diag_id={diag_id}, size={size})")

                if resp.get('IsTruncated'):
                    continuation_token = resp.get('NextContinuationToken')
                else:
                    break
        except Exception as e:
            print(f"[cleanup] list_objects_v2 failed for {prefix}: {e}")
            try:
                resp = s3.list_objects(Bucket='files', Prefix=prefix, MaxKeys=1000)
                contents = resp.get('Contents', [])
                print(f"[cleanup] list_objects({prefix}): {len(contents)} objects")
                for obj in contents:
                    key = obj['Key']
                    size = obj.get('Size', 0)
                    all_s3_keys.append(key)
                    diag_id = _extract_diagnostic_id(key, prefix)
                    if diag_id is not None and diag_id not in existing_ids:
                        orphan_keys.append(key)
                        orphan_size += size
                        print(f"[cleanup] ORPHAN: {key} (diag_id={diag_id}, size={size})")
            except Exception as e2:
                print(f"[cleanup] list_objects also failed for {prefix}: {e2}")

    print(f"[cleanup] Total S3 keys found: {len(all_s3_keys)}, orphans: {len(orphan_keys)}, orphan_size: {orphan_size}")
    if all_s3_keys[:5]:
        print(f"[cleanup] Sample keys: {all_s3_keys[:5]}")

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
    print(f"[cleanup] Orphan DB photo_diags: {orphan_photo_diag_ids}, answer_diags: {orphan_answer_diag_ids}")

    deleted_files = 0
    deleted_db = 0

    if not dry_run:
        for key in orphan_keys:
            try:
                s3.delete_object(Bucket='files', Key=key)
                deleted_files += 1
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
        print(f"[cleanup] Deleted {deleted_files} files, {deleted_db} DB records")

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
            'deletedDbRecords': deleted_db,
            'totalS3Keys': len(all_s3_keys)
        }),
        'isBase64Encoded': False
    }


def _extract_diagnostic_id(key, prefix):
    if prefix == 'diagnostics/':
        parts = key.split('/')
        if len(parts) >= 2:
            try:
                return int(parts[1])
            except (ValueError, IndexError):
                return None
    elif prefix == 'reports/':
        m = re.search(r'diagnostic_(\d+)', key)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                return None
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
