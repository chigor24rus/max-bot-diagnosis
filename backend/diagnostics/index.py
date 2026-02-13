import json
import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo

def handler(event: dict, context) -> dict:
    '''API для сохранения и получения диагностик автомобилей'''
    
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Cache-Control, If-None-Match'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    db_url = os.environ.get('DATABASE_URL')
    schema = os.environ.get('MAIN_DB_SCHEMA')
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        if method == 'POST':
            body = json.loads(event.get('body', '{}'))
            mechanic = body.get('mechanic')
            car_number = body.get('carNumber')
            mileage = body.get('mileage')
            diagnostic_type = body.get('diagnosticType')
            checklist_answers = body.get('checklistAnswers', [])
            
            if not all([mechanic, car_number, mileage, diagnostic_type]):
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Все поля обязательны для заполнения'}),
                    'isBase64Encoded': False
                }
            
            krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
            now_krsk = datetime.now(krasnoyarsk_tz).strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(
                f"INSERT INTO {schema}.diagnostics (mechanic, car_number, mileage, diagnostic_type, created_at, updated_at) "
                f"VALUES ('{mechanic}', '{car_number}', {mileage}, '{diagnostic_type}', '{now_krsk}', '{now_krsk}') RETURNING id, created_at"
            )
            result = cur.fetchone()
            diagnostic_id = result[0]
            created_at = result[1]
            
            if checklist_answers:
                for answer in checklist_answers:
                    question_id = answer.get('questionId')
                    question_text = answer.get('questionText', '').replace("'", "''")
                    answer_value = answer.get('answerValue', '').replace("'", "''")
                    answer_label = answer.get('answerLabel', '').replace("'", "''")
                    sub_answers = json.dumps(answer.get('subAnswers', {})) if answer.get('subAnswers') else None
                    text_input = answer.get('textInput', '').replace("'", "''") if answer.get('textInput') else None
                    photo_urls = answer.get('photoUrls', [])
                    
                    photo_urls_str = 'NULL'
                    if photo_urls:
                        photo_urls_escaped = [url.replace("'", "''") for url in photo_urls]
                        photo_urls_str = "ARRAY['" + "','".join(photo_urls_escaped) + "']"
                    
                    sub_answers_str = f"'{sub_answers}'" if sub_answers else 'NULL'
                    text_input_str = f"'{text_input}'" if text_input else 'NULL'
                    answer_type = 'single' if not answer.get('subAnswers') else 'multiple'
                    
                    cur.execute(
                        f"INSERT INTO {schema}.checklist_answers "
                        f"(diagnostic_id, question_number, question_text, answer_type, answer_value, sub_answers, photo_urls) "
                        f"VALUES ({diagnostic_id}, {question_id}, '{question_text}', '{answer_type}', '{answer_label}', {sub_answers_str}, {photo_urls_str})"
                    )
            
            conn.commit()
            
            return {
                'statusCode': 201,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'id': diagnostic_id,
                    'createdAt': created_at.isoformat(),
                    'message': 'Диагностика успешно сохранена'
                }),
                'isBase64Encoded': False
            }
        
        elif method == 'DELETE':
            query_params = event.get('queryStringParameters', {}) or {}
            diagnostic_id = query_params.get('id')
            
            if not diagnostic_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'ID диагностики обязателен'}),
                    'isBase64Encoded': False
                }
            
            cur.execute(f"DELETE FROM {schema}.diagnostics WHERE id = {diagnostic_id}")
            conn.commit()
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Диагностика удалена'}),
                'isBase64Encoded': False
            }
        
        elif method == 'GET':
            query_params = event.get('queryStringParameters', {}) or {}
            diagnostic_id = query_params.get('id')
            
            if diagnostic_id:
                cur.execute(
                    f"SELECT id, mechanic, car_number, mileage, diagnostic_type, created_at "
                    f"FROM {schema}.diagnostics WHERE id = {diagnostic_id}"
                )
                row = cur.fetchone()
                
                if not row:
                    return {
                        'statusCode': 404,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Диагностика не найдена'}),
                        'isBase64Encoded': False
                    }
                
                diagnostic = {
                    'id': row[0],
                    'mechanic': row[1],
                    'carNumber': row[2],
                    'mileage': row[3],
                    'diagnosticType': row[4],
                    'createdAt': row[5].isoformat()
                }
            else:
                limit = query_params.get('limit', '50')
                cur.execute(
                    f"SELECT id, mechanic, car_number, mileage, diagnostic_type, created_at "
                    f"FROM {schema}.diagnostics ORDER BY created_at DESC LIMIT {limit}"
                )
                rows = cur.fetchall()
                
                diagnostic = [
                    {
                        'id': row[0],
                        'mechanic': row[1],
                        'carNumber': row[2],
                        'mileage': row[3],
                        'diagnosticType': row[4],
                        'createdAt': row[5].isoformat()
                    }
                    for row in rows
                ]
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(diagnostic),
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