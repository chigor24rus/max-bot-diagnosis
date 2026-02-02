import json
import os
import requests
import psycopg2

# Хранилище сессий пользователей (в продакшене использовать Redis)
user_sessions = {}

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
        update_type = update.get('update_type')
        
        if update_type == 'message_created':
            handle_message(update)
        elif update_type == 'message_callback':
            handle_callback(update)
        
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


def handle_message(update: dict):
    '''Обработка текстовых сообщений'''
    message = update.get('message', {})
    chat_id = message.get('chat_id')
    sender_id = message.get('sender', {}).get('user_id', chat_id)
    user_text = message.get('body', {}).get('text', '').strip()
    
    if not chat_id:
        return
    
    session = user_sessions.get(sender_id, {'step': 0})
    lower_text = user_text.lower()
    
    # Команды
    if lower_text in ['/start', 'начать', 'старт']:
        user_sessions[sender_id] = {'step': 1}
        response_text = '👋 Привет! Я HEVSR Diagnostics bot.\n\nВыберите механика для диагностики:'
        buttons = [
            [{'type': 'callback', 'text': 'Подкорытов С.А.', 'payload': 'mechanic:Подкорытов С.А.'}],
            [{'type': 'callback', 'text': 'Костенко В.Ю.', 'payload': 'mechanic:Костенко В.Ю.'}],
            [{'type': 'callback', 'text': 'Иванюта Д.И.', 'payload': 'mechanic:Иванюта Д.И.'}],
            [{'type': 'callback', 'text': 'Загороднюк Н.Д.', 'payload': 'mechanic:Загороднюк Н.Д.'}]
        ]
        send_message(chat_id, response_text, buttons)
        return
    
    elif lower_text in ['/help', 'помощь']:
        response_text = '''📋 Доступные команды:

/start - Начать новую диагностику
/cancel - Отменить текущую операцию
/help - Показать помощь

Бот проведёт вас через все этапы диагностики!'''
        send_message(chat_id, response_text)
        return
    
    elif lower_text in ['/cancel', 'отмена']:
        user_sessions[sender_id] = {'step': 0}
        response_text = '✅ Операция отменена.\n\nВведите /start для новой диагностики.'
        buttons = [[{'type': 'callback', 'text': 'Начать диагностику', 'payload': 'start'}]]
        send_message(chat_id, response_text, buttons)
        return
    
    # Обработка по шагам
    step = session.get('step', 0)
    
    if step == 0:
        response_text = 'Введите /start для начала диагностики или /help для помощи.'
        buttons = [[{'type': 'callback', 'text': 'Начать диагностику', 'payload': 'start'}]]
        send_message(chat_id, response_text, buttons)
    
    elif step == 2:
        # Ввод госномера
        clean_number = user_text.upper().replace(' ', '').replace('-', '')
        if len(clean_number) >= 5:
            session['car_number'] = clean_number
            session['step'] = 3
            user_sessions[sender_id] = session
            response_text = f'✅ Госномер {clean_number} принят!\n\nТеперь введите пробег автомобиля (в км).\n\nНапример: 150000'
            send_message(chat_id, response_text)
        else:
            response_text = '⚠️ Госномер слишком короткий.\n\nВведите корректный госномер (минимум 5 символов).\n\nНапример: A159BK124'
            send_message(chat_id, response_text)
    
    elif step == 3:
        # Ввод пробега
        mileage_str = ''.join(filter(str.isdigit, user_text))
        if mileage_str and int(mileage_str) > 0:
            session['mileage'] = int(mileage_str)
            session['step'] = 4
            user_sessions[sender_id] = session
            response_text = f'✅ Пробег {int(mileage_str):,} км принят!\n\nТеперь выберите тип диагностики:'.replace(',', ' ')
            buttons = [
                [{'type': 'callback', 'text': '5-ти минутка', 'payload': 'type:5min'}],
                [{'type': 'callback', 'text': 'ДХЧ', 'payload': 'type:dhch'}],
                [{'type': 'callback', 'text': 'ДЭС', 'payload': 'type:des'}]
            ]
            send_message(chat_id, response_text, buttons)
        else:
            response_text = '⚠️ Пожалуйста, введите пробег цифрами.\n\nНапример: 150000'
            send_message(chat_id, response_text)
    
    else:
        response_text = 'Не понял команду. Используйте /help для справки.'
        send_message(chat_id, response_text)


def handle_callback(update: dict):
    '''Обработка нажатий на кнопки'''
    callback = update.get('callback', {})
    chat_id = callback.get('message', {}).get('chat_id')
    sender_id = callback.get('user', {}).get('user_id', chat_id)
    payload = callback.get('payload', '')
    
    if not chat_id:
        return
    
    session = user_sessions.get(sender_id, {'step': 0})
    
    if payload == 'start':
        user_sessions[sender_id] = {'step': 1}
        response_text = '👋 Отлично! Выберите механика:'
        buttons = [
            [{'type': 'callback', 'text': 'Подкорытов С.А.', 'payload': 'mechanic:Подкорытов С.А.'}],
            [{'type': 'callback', 'text': 'Костенко В.Ю.', 'payload': 'mechanic:Костенко В.Ю.'}],
            [{'type': 'callback', 'text': 'Иванюта Д.И.', 'payload': 'mechanic:Иванюта Д.И.'}],
            [{'type': 'callback', 'text': 'Загороднюк Н.Д.', 'payload': 'mechanic:Загороднюк Н.Д.'}]
        ]
        send_message(chat_id, response_text, buttons)
    
    elif payload.startswith('mechanic:'):
        mechanic = payload.replace('mechanic:', '')
        session['mechanic'] = mechanic
        session['step'] = 2
        user_sessions[sender_id] = session
        response_text = f'✅ Механик {mechanic} выбран!\n\nВведите госномер автомобиля.\n\nНапример: A159BK124'
        send_message(chat_id, response_text)
    
    elif payload.startswith('type:'):
        diagnostic_type = payload.replace('type:', '')
        session['diagnostic_type'] = diagnostic_type
        user_sessions[sender_id] = session
        
        # Сохраняем в БД
        diagnostic_id = save_diagnostic(session)
        
        if diagnostic_id:
            type_labels = {'5min': '5-ти минутка', 'dhch': 'ДХЧ', 'des': 'ДЭС'}
            type_label = type_labels.get(diagnostic_type, diagnostic_type)
            
            response_text = f'''✅ Диагностика №{diagnostic_id} сохранена!

📋 Сводка:
━━━━━━━━━━━━━━━━
👤 Механик: {session['mechanic']}
🚗 Госномер: {session['car_number']}
🛣 Пробег: {session['mileage']:,} км
🔧 Тип: {type_label}
━━━━━━━━━━━━━━━━

Диагностика завершена!'''.replace(',', ' ')
            
            buttons = [[{'type': 'callback', 'text': 'Начать новую диагностику', 'payload': 'start'}]]
            send_message(chat_id, response_text, buttons)
            
            # Очищаем сессию
            user_sessions[sender_id] = {'step': 0}
        else:
            response_text = '❌ Ошибка сохранения в базу данных. Попробуйте ещё раз.'
            buttons = [[{'type': 'callback', 'text': 'Попробовать снова', 'payload': 'start'}]]
            send_message(chat_id, response_text, buttons)


def save_diagnostic(session: dict) -> int:
    '''Сохранение диагностики в PostgreSQL'''
    try:
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        mechanic = session.get('mechanic', '')
        car_number = session.get('car_number', '')
        mileage = session.get('mileage', 0)
        diagnostic_type = session.get('diagnostic_type', '')
        
        cur.execute(
            f"INSERT INTO {schema}.diagnostics (mechanic, car_number, mileage, diagnostic_type) "
            f"VALUES ('{mechanic}', '{car_number}', {mileage}, '{diagnostic_type}') RETURNING id"
        )
        
        result = cur.fetchone()
        conn.commit()
        
        cur.close()
        conn.close()
        
        return result[0] if result else None
    
    except Exception as e:
        return None


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
