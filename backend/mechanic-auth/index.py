import json
import os
import psycopg2


def handler(event: dict, context) -> dict:
    '''API для авторизации механиков по номеру телефона и пин-коду'''
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
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
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        phone = body.get('phone', '').strip()
        pin_code = body.get('pin_code', '').strip()
        
        if not phone or not pin_code:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Номер телефона и пин-код обязательны'}),
                'isBase64Encoded': False
            }
        
        # Нормализуем номер телефона
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Проверяем учётные данные
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT id, name, is_active FROM {schema}.mechanics "
            f"WHERE phone = '{clean_phone}' AND pin_code = '{pin_code}'"
        )
        mechanic = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if not mechanic:
            return {
                'statusCode': 401,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Неверный номер телефона или пин-код'}),
                'isBase64Encoded': False
            }
        
        mechanic_id, mechanic_name, is_active = mechanic
        
        if not is_active:
            return {
                'statusCode': 403,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Аккаунт деактивирован'}),
                'isBase64Encoded': False
            }
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': True,
                'mechanic': {
                    'id': mechanic_id,
                    'name': mechanic_name
                }
            }),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        print(f"[ERROR] Auth failed: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Ошибка сервера'}),
            'isBase64Encoded': False
        }
