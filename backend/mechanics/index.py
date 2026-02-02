import json
import os
import psycopg2

def handler(event: dict, context) -> dict:
    '''API для управления списком механиков'''
    
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    schema = os.environ.get('MAIN_DB_SCHEMA')
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        if method == 'GET':
            cur.execute(
                f"SELECT id, name, phone, pin_code, is_active, created_at FROM {schema}.mechanics ORDER BY name"
            )
            rows = cur.fetchall()
            
            mechanics = [
                {
                    'id': row[0],
                    'name': row[1],
                    'phone': row[2],
                    'pinCode': row[3],
                    'isActive': row[4],
                    'createdAt': row[5].isoformat() if row[5] else None
                }
                for row in rows
            ]
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(mechanics),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            body = json.loads(event.get('body', '{}'))
            name = body.get('name', '').strip()
            phone = body.get('phone', '').strip()
            pin_code = body.get('pinCode', '').strip()
            
            if not name or not phone or not pin_code:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Имя, телефон и пин-код обязательны'}),
                    'isBase64Encoded': False
                }
            
            if len(pin_code) != 4 or not pin_code.isdigit():
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Пин-код должен состоять из 4 цифр'}),
                    'isBase64Encoded': False
                }
            
            # Нормализуем номер телефона
            clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            
            cur.execute(
                f"INSERT INTO {schema}.mechanics (name, phone, pin_code) "
                f"VALUES ('{name}', '{clean_phone}', '{pin_code}') RETURNING id, created_at"
            )
            result = cur.fetchone()
            conn.commit()
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'id': result[0],
                    'name': name,
                    'phone': clean_phone,
                    'pinCode': pin_code,
                    'isActive': True,
                    'createdAt': result[1].isoformat() if result[1] else None
                }),
                'isBase64Encoded': False
            }
        
        elif method == 'PUT':
            body = json.loads(event.get('body', '{}'))
            mechanic_id = body.get('id')
            name = body.get('name', '').strip()
            phone = body.get('phone', '').strip()
            pin_code = body.get('pinCode', '').strip()
            is_active = body.get('isActive', True)
            
            if not mechanic_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'ID механика обязателен'}),
                    'isBase64Encoded': False
                }
            
            # Формируем список обновлений
            updates = []
            if name:
                updates.append(f"name = '{name}'")
            if phone:
                clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                updates.append(f"phone = '{clean_phone}'")
            if pin_code:
                if len(pin_code) != 4 or not pin_code.isdigit():
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Пин-код должен состоять из 4 цифр'}),
                        'isBase64Encoded': False
                    }
                updates.append(f"pin_code = '{pin_code}'")
            
            updates.append(f"is_active = {is_active}")
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            if updates:
                update_sql = f"UPDATE {schema}.mechanics SET {', '.join(updates)} WHERE id = {mechanic_id}"
                cur.execute(update_sql)
                conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Механик обновлён'}),
                'isBase64Encoded': False
            }
        
        elif method == 'DELETE':
            query_params = event.get('queryStringParameters', {}) or {}
            mechanic_id = query_params.get('id')
            
            if not mechanic_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'ID механика обязателен'}),
                    'isBase64Encoded': False
                }
            
            cur.execute(f"DELETE FROM {schema}.mechanics WHERE id = {mechanic_id}")
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Механик удалён'}),
                'isBase64Encoded': False
            }
        
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Метод не поддерживается'}),
            'isBase64Encoded': False
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()