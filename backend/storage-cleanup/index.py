import json
import os
import boto3
import psycopg2


def handler(event: dict, context) -> dict:
    '''Очистка хранилища от осиротевших файлов и записей БД'''

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

    s3 = boto3.client('s3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

    cur.execute(
        f"SELECT id, photo_url, diagnostic_id FROM {schema}.diagnostic_photos "
        f"WHERE diagnostic_id NOT IN (SELECT id FROM {schema}.diagnostics)"
    )
    orphan_photos = cur.fetchall()

    orphan_s3_keys = []
    orphan_size = 0
    for row in orphan_photos:
        url = row[1]
        if url and url.startswith(cdn_prefix):
            s3_key = url[len(cdn_prefix):]
            orphan_s3_keys.append(s3_key)
            try:
                resp = s3.head_object(Bucket='files', Key=s3_key)
                orphan_size += resp.get('ContentLength', 0)
            except Exception:
                pass

    cur.execute(f"SELECT DISTINCT diagnostic_id FROM {schema}.diagnostic_photos WHERE diagnostic_id NOT IN (SELECT id FROM {schema}.diagnostics)")
    orphan_photo_diag_ids = set(row[0] for row in cur.fetchall())

    cur.execute(f"SELECT DISTINCT diagnostic_id FROM {schema}.checklist_answers WHERE diagnostic_id NOT IN (SELECT id FROM {schema}.diagnostics)")
    orphan_answer_diag_ids = set(row[0] for row in cur.fetchall())

    orphan_db_records = len(orphan_photo_diag_ids) + len(orphan_answer_diag_ids)

    deleted_files = 0
    deleted_db = 0

    if not dry_run:
        for s3_key in orphan_s3_keys:
            try:
                s3.delete_object(Bucket='files', Key=s3_key)
                deleted_files += 1
            except Exception:
                pass

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

    def format_size(bytes_val):
        if bytes_val < 1024:
            return f"{bytes_val} Б"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.1f} КБ"
        elif bytes_val < 1024 * 1024 * 1024:
            return f"{bytes_val / (1024 * 1024):.1f} МБ"
        else:
            return f"{bytes_val / (1024 * 1024 * 1024):.2f} ГБ"

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'dryRun': dry_run,
            'orphanFiles': len(orphan_s3_keys),
            'orphanSize': orphan_size,
            'orphanSizeFormatted': format_size(orphan_size),
            'orphanDbRecords': orphan_db_records,
            'deletedFiles': deleted_files,
            'deletedDbRecords': deleted_db
        }),
        'isBase64Encoded': False
    }
