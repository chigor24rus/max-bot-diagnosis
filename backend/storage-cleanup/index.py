import json
import os
import boto3
import psycopg2


def handler(event: dict, context) -> dict:
    '''Очистка хранилища S3 от осиротевших файлов (не привязанных к существующим диагностикам)'''

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

    s3 = boto3.client('s3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

    orphan_keys = []
    orphan_size = 0
    kept_keys = 0
    kept_size = 0

    continuation_token = None
    while True:
        params = {'Bucket': 'files', 'MaxKeys': 1000}
        if continuation_token:
            params['ContinuationToken'] = continuation_token

        response = s3.list_objects_v2(**params)

        for obj in response.get('Contents', []):
            key = obj['Key']
            size = obj['Size']
            diag_id = extract_diagnostic_id(key)

            if diag_id is not None and diag_id not in existing_ids:
                orphan_keys.append(key)
                orphan_size += size
            else:
                kept_keys += 1
                kept_size += size

        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

    cur.execute(f"SELECT DISTINCT diagnostic_id FROM {schema}.diagnostic_photos")
    photo_diag_ids = set(row[0] for row in cur.fetchall())
    orphan_photo_ids = photo_diag_ids - existing_ids
    orphan_db_records = len(orphan_photo_ids)

    cur.execute(f"SELECT DISTINCT diagnostic_id FROM {schema}.checklist_answers")
    answer_diag_ids = set(row[0] for row in cur.fetchall())
    orphan_answer_ids = answer_diag_ids - existing_ids

    if not dry_run:
        deleted_count = 0
        if orphan_keys:
            batch_size = 1000
            for i in range(0, len(orphan_keys), batch_size):
                batch = orphan_keys[i:i + batch_size]
                delete_objects = [{'Key': k} for k in batch]
                s3.delete_objects(Bucket='files', Delete={'Objects': delete_objects})
                deleted_count += len(batch)

        if orphan_photo_ids:
            ids_str = ','.join(str(i) for i in orphan_photo_ids)
            cur.execute(f"DELETE FROM {schema}.diagnostic_photos WHERE diagnostic_id IN ({ids_str})")

        if orphan_answer_ids:
            ids_str = ','.join(str(i) for i in orphan_answer_ids)
            cur.execute(f"DELETE FROM {schema}.checklist_answers WHERE diagnostic_id IN ({ids_str})")

        conn.commit()
    else:
        deleted_count = 0

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
            'orphanFiles': len(orphan_keys),
            'orphanSize': orphan_size,
            'orphanSizeFormatted': format_size(orphan_size),
            'orphanDbRecords': orphan_db_records,
            'deletedFiles': deleted_count,
            'keptFiles': kept_keys,
            'keptSize': kept_size,
            'keptSizeFormatted': format_size(kept_size)
        }),
        'isBase64Encoded': False
    }


def extract_diagnostic_id(key):
    if key.startswith('diagnostics/'):
        parts = key.split('/')
        if len(parts) >= 2:
            try:
                return int(parts[1])
            except (ValueError, IndexError):
                pass

    if key.startswith('reports/diagnostic_'):
        name = key.split('/')[-1]
        name = name.replace('diagnostic_', '')
        idx = name.find('_')
        if idx == -1:
            idx = name.find('.')
        if idx > 0:
            try:
                return int(name[:idx])
            except ValueError:
                pass

    return None