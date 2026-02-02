import json
import os
import requests

def handler(event: dict, context) -> dict:
    '''Webhook для приёма сообщений от MAX бота и отправки ответов'''
    
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
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        update = json.loads(event.get('body', '{}'))
        
        # Проверяем тип события
        update_type = update.get('update_type')
        
        if update_type == 'message_created':
            message = update.get('message', {})
            chat_id = message.get('chat_id')
            user_text = message.get('body', {}).get('text', '')
            
            if not chat_id:
                return {'statusCode': 200, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
            
            # Обрабатываем команды
            response_text = ''
            buttons = []
            
            lower_text = user_text.lower().strip()
            
            if lower_text in ['/start', 'начать', 'старт']:
                response_text = '👋 Привет! Я HEVSR Diagnostics bot — ваш помощник для диагностики автомобилей.\n\nВыберите механика:'
                buttons = [
                    [{'type': 'callback', 'text': 'Подкорытов С.А.', 'payload': 'mechanic:Подкорытов С.А.'}],
                    [{'type': 'callback', 'text': 'Костенко В.Ю.', 'payload': 'mechanic:Костенко В.Ю.'}],
                    [{'type': 'callback', 'text': 'Иванюта Д.И.', 'payload': 'mechanic:Иванюта Д.И.'}],
                    [{'type': 'callback', 'text': 'Загороднюк Н.Д.', 'payload': 'mechanic:Загороднюк Н.Д.'}]
                ]
            
            elif lower_text in ['/help', 'помощь']:
                response_text = '''📋 Доступные команды:

/start - Начать диагностику
/help - Показать помощь
/history - История диагностик

Просто напишите команду или нажмите кнопку!'''
            
            elif lower_text in ['/history', 'история']:
                response_text = '📊 Для просмотра полной истории диагностик откройте веб-приложение.'
                buttons = [[{'type': 'link', 'text': '🌐 Открыть историю', 'url': 'https://your-app-url.poehali.app'}]]
            
            else:
                response_text = f'Вы написали: "{user_text}"\n\nВведите /start для начала диагностики или /help для помощи.'
                buttons = [[{'type': 'callback', 'text': 'Начать диагностику', 'payload': 'start'}]]
            
            # Отправляем сообщение через MAX API
            send_message(chat_id, response_text, buttons)
        
        elif update_type == 'message_callback':
            callback = update.get('callback', {})
            chat_id = callback.get('message', {}).get('chat_id')
            payload = callback.get('payload', '')
            
            if payload.startswith('mechanic:'):
                mechanic = payload.replace('mechanic:', '')
                response_text = f'✅ Механик {mechanic} выбран!\n\nТеперь введите госномер автомобиля (например: A159BK124)'
                send_message(chat_id, response_text)
            
            elif payload == 'start':
                response_text = '👋 Отлично! Выберите механика:'
                buttons = [
                    [{'type': 'callback', 'text': 'Подкорытов С.А.', 'payload': 'mechanic:Подкорытов С.А.'}],
                    [{'type': 'callback', 'text': 'Костенко В.Ю.', 'payload': 'mechanic:Костенко В.Ю.'}],
                    [{'type': 'callback', 'text': 'Иванюта Д.И.', 'payload': 'mechanic:Иванюта Д.И.'}],
                    [{'type': 'callback', 'text': 'Загороднюк Н.Д.', 'payload': 'mechanic:Загороднюк Н.Д.'}]
                ]
                send_message(chat_id, response_text, buttons)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def send_message(chat_id: str, text: str, buttons: list = None):
    '''Отправка сообщения через MAX API'''
    
    token = os.environ.get('MAX_BOT_TOKEN')
    url = 'https://platform-api.max.ru/messages'
    
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    
    if buttons:
        payload['attachments'] = [{
            'type': 'inline_keyboard',
            'payload': {'buttons': buttons}
        }]
    
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
