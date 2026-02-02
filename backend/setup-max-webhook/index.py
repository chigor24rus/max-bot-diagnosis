import json
import os
import requests

def handler(event: dict, context) -> dict:
    '''API для настройки webhook подписки в MAX боте'''
    
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    token = os.environ.get('MAX_BOT_TOKEN')
    base_url = 'https://platform-api.max.ru'
    
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    try:
        if method == 'GET':
            # Получаем текущие подписки
            response = requests.get(f'{base_url}/subscriptions', headers=headers)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'subscriptions': response.json(),
                    'message': 'Текущие подписки получены'
                }),
                'isBase64Encoded': False
            }
        
        elif method == 'POST':
            # Создаём новую подписку
            webhook_url = 'https://functions.poehali.dev/f48b0eea-37b1-4cf5-a470-aa20ae0fd775'
            
            payload = {
                'url': webhook_url,
                'update_types': ['message_created', 'message_callback']
            }
            
            response = requests.post(f'{base_url}/subscriptions', json=payload, headers=headers)
            
            if response.status_code in [200, 201]:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'subscription': response.json(),
                        'message': 'Webhook успешно настроен!',
                        'webhook_url': webhook_url
                    }),
                    'isBase64Encoded': False
                }
            else:
                return {
                    'statusCode': response.status_code,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'error': response.text,
                        'message': 'Ошибка при создании подписки'
                    }),
                    'isBase64Encoded': False
                }
        
        elif method == 'DELETE':
            # Удаляем все подписки
            subscriptions_response = requests.get(f'{base_url}/subscriptions', headers=headers)
            subscriptions = subscriptions_response.json()
            
            deleted = []
            for sub in subscriptions.get('subscriptions', []):
                sub_url = sub.get('url')
                delete_response = requests.delete(
                    f'{base_url}/subscriptions',
                    params={'url': sub_url},
                    headers=headers
                )
                if delete_response.status_code == 200:
                    deleted.append(sub_url)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'deleted': deleted,
                    'message': f'Удалено подписок: {len(deleted)}'
                }),
                'isBase64Encoded': False
            }
        
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'}),
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
