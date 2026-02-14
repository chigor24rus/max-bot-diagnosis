import json
import os
import boto3


def handler(event: dict, context) -> dict:
    '''Получение информации о состоянии S3 хранилища (размер, количество файлов)'''

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

    s3 = boto3.client('s3',
        endpoint_url='https://bucket.poehali.dev',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
    )

    total_size = 0
    total_files = 0
    photos_size = 0
    photos_count = 0
    reports_size = 0
    reports_count = 0
    other_size = 0
    other_count = 0

    continuation_token = None
    while True:
        params = {'Bucket': 'files', 'MaxKeys': 1000}
        if continuation_token:
            params['ContinuationToken'] = continuation_token

        response = s3.list_objects_v2(**params)

        for obj in response.get('Contents', []):
            key = obj['Key']
            size = obj['Size']
            total_size += size
            total_files += 1

            if key.startswith('diagnostics/'):
                photos_size += size
                photos_count += 1
            elif key.startswith('reports/'):
                reports_size += size
                reports_count += 1
            else:
                other_size += size
                other_count += 1

        if response.get('IsTruncated'):
            continuation_token = response.get('NextContinuationToken')
        else:
            break

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
                'size': other_size,
                'sizeFormatted': format_size(other_size),
                'count': other_count
            }
        }),
        'isBase64Encoded': False
    }
