import json
import os
import boto3
import psycopg2


def handler(event: dict, context) -> dict:
    '''Получение информации о состоянии S3 хранилища через БД + проверку S3'''

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }

    db_url = os.environ.get('DATABASE_URL')
    schema = os.environ.get('MAIN_DB_SCHEMA')
    aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
    cdn_prefix = f"https://cdn.poehali.dev/projects/{aws_key}/bucket/"

    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    s3 = boto3.client('s3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

    cur.execute(f"SELECT photo_url FROM {schema}.diagnostic_photos")
    photo_rows = cur.fetchall()

    photos_count = 0
    photos_size = 0
    for row in photo_rows:
        url = row[0]
        if url and url.startswith(cdn_prefix):
            s3_key = url[len(cdn_prefix):]
            try:
                resp = s3.head_object(Bucket='files', Key=s3_key)
                photos_size += resp.get('ContentLength', 0)
                photos_count += 1
            except Exception:
                pass

    cur.execute(
        f"SELECT DISTINCT d.id FROM {schema}.diagnostics d "
        f"JOIN {schema}.checklist_answers ca ON ca.diagnostic_id = d.id"
    )
    diag_ids = [row[0] for row in cur.fetchall()]

    reports_count = 0
    reports_size = 0
    for diag_id in diag_ids:
        for suffix in ['', '_photos']:
            key = f"reports/diagnostic_{diag_id}{suffix}.pdf"
            try:
                resp = s3.head_object(Bucket='files', Key=key)
                reports_size += resp.get('ContentLength', 0)
                reports_count += 1
            except Exception:
                pass

    cur.execute(f"SELECT COUNT(*) FROM {schema}.diagnostic_photos WHERE diagnostic_id NOT IN (SELECT id FROM {schema}.diagnostics)")
    orphan_photo_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    total_size = photos_size + reports_size
    total_files = photos_count + reports_count

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
            'totalSize': total_size,
            'totalSizeFormatted': format_size(total_size),
            'totalFiles': total_files,
            'orphanDbRecords': orphan_photo_count,
            'photos': {
                'size': photos_size,
                'sizeFormatted': format_size(photos_size),
                'count': photos_count
            },
            'reports': {
                'size': reports_size,
                'sizeFormatted': format_size(reports_size),
                'count': reports_count
            },
            'other': {
                'size': 0,
                'sizeFormatted': '0 Б',
                'count': 0
            }
        }),
        'isBase64Encoded': False
    }
