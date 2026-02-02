import json
import os
import requests
import psycopg2
import boto3
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO


def get_session(user_id: str) -> dict:
    '''Получение сессии пользователя из БД'''
    try:
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT session_data FROM {schema}.max_sessions WHERE user_id = '{user_id}'"
        )
        row = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if row:
            return row[0]
        return {'step': 0}
    except Exception as e:
        print(f"[ERROR] Failed to get session: {str(e)}")
        return {'step': 0}


def save_session(user_id: str, session: dict):
    '''Сохранение сессии пользователя в БД'''
    try:
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        session_json = json.dumps(session, ensure_ascii=False).replace("'", "''")
        
        cur.execute(
            f"INSERT INTO {schema}.max_sessions (user_id, session_data, updated_at) "
            f"VALUES ('{user_id}', '{session_json}'::jsonb, CURRENT_TIMESTAMP) "
            f"ON CONFLICT (user_id) DO UPDATE SET session_data = '{session_json}'::jsonb, updated_at = CURRENT_TIMESTAMP"
        )
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[ERROR] Failed to save session: {str(e)}")

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
        
        print(f"[DEBUG] Received update_type: {update_type}")
        print(f"[DEBUG] Full update: {json.dumps(update, ensure_ascii=False)}")
        
        if update_type == 'message_created':
            print("[DEBUG] Handling message_created")
            handle_message(update)
        elif update_type == 'message_callback':
            print("[DEBUG] Handling message_callback")
            handle_callback(update)
        else:
            print(f"[WARNING] Unknown update_type: {update_type}")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        print(f"[ERROR] Exception in handler: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def handle_message(update: dict):
    '''Обработка текстовых сообщений и вложений'''
    message = update.get('message', {})
    sender_id = message.get('sender', {}).get('user_id')
    user_text = message.get('body', {}).get('text', '').strip()
    attachments = message.get('body', {}).get('attachments', [])
    
    print(f"[DEBUG] Extracted sender_id: {sender_id}, text: {user_text}")
    print(f"[DEBUG] Attachments: {attachments}")
    
    if not sender_id:
        print("[WARNING] No sender_id found, skipping message")
        return
    
    session = get_session(str(sender_id))
    
    # Обработка фото в режиме чек-листа
    if session.get('step') == 5 and session.get('waiting_for_photo'):
        if attachments:
            handle_photo_upload(sender_id, session, attachments)
        else:
            response_text = '⚠️ Пожалуйста, прикрепите фото дефекта или нажмите "Пропустить фото".'
            buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
            send_message(sender_id, response_text, buttons)
        return
    
    lower_text = user_text.lower()
    
    # Команды
    if lower_text in ['/start', 'начать', 'старт']:
        session = {'step': 1}
        save_session(str(sender_id), session)
        response_text = '👋 Привет! Я HEVSR Diagnostics bot.\n\nВыберите механика для диагностики:'
        buttons = [
            [{'type': 'callback', 'text': 'Подкорытов С.А.', 'payload': 'mechanic:Подкорытов С.А.'}],
            [{'type': 'callback', 'text': 'Костенко В.Ю.', 'payload': 'mechanic:Костенко В.Ю.'}],
            [{'type': 'callback', 'text': 'Иванюта Д.И.', 'payload': 'mechanic:Иванюта Д.И.'}],
            [{'type': 'callback', 'text': 'Загороднюк Н.Д.', 'payload': 'mechanic:Загороднюк Н.Д.'}]
        ]
        send_message(sender_id, response_text, buttons)
        return
    
    elif lower_text in ['/help', 'помощь']:
        response_text = '''📋 Доступные команды:

/start - Начать новую диагностику
/cancel - Отменить текущую операцию
/help - Показать помощь

Бот проведёт вас через все этапы диагностики!'''
        send_message(sender_id, response_text)
        return
    
    elif lower_text in ['/cancel', 'отмена']:
        session = {'step': 0}
        save_session(str(sender_id), session)
        response_text = '✅ Операция отменена.\n\nВведите /start для новой диагностики.'
        buttons = [[{'type': 'callback', 'text': 'Начать диагностику', 'payload': 'start'}]]
        send_message(sender_id, response_text, buttons)
        return
    
    # Обработка по шагам
    step = session.get('step', 0)
    
    if step == 0:
        response_text = 'Введите /start для начала диагностики или /help для помощи.'
        buttons = [[{'type': 'callback', 'text': 'Начать диагностику', 'payload': 'start'}]]
        send_message(sender_id, response_text, buttons)
    
    elif step == 2:
        # Ввод госномера
        clean_number = user_text.upper().replace(' ', '').replace('-', '')
        
        # Проверка на кириллицу
        has_cyrillic = any('А' <= char <= 'Я' or 'а' <= char <= 'я' for char in clean_number)
        
        if has_cyrillic:
            response_text = '⚠️ Госномер должен содержать только латинские буквы.\n\nНапример: A159BK124 (не А159ВК124)'
            send_message(sender_id, response_text)
        elif len(clean_number) >= 5:
            session['car_number'] = clean_number
            session['step'] = 3
            save_session(str(sender_id), session)
            response_text = f'✅ Госномер {clean_number} принят!\n\nТеперь введите пробег автомобиля (в км).\n\nНапример: 150000'
            send_message(sender_id, response_text)
        else:
            response_text = '⚠️ Госномер слишком короткий.\n\nВведите корректный госномер (минимум 5 символов).\n\nНапример: A159BK124'
            send_message(sender_id, response_text)
    
    elif step == 3:
        # Ввод пробега
        mileage_str = ''.join(filter(str.isdigit, user_text))
        if mileage_str and int(mileage_str) > 0:
            session['mileage'] = int(mileage_str)
            session['step'] = 4
            save_session(str(sender_id), session)
            response_text = f'✅ Пробег {int(mileage_str):,} км принят!\n\nТеперь выберите тип диагностики:'.replace(',', ' ')
            buttons = [
                [{'type': 'callback', 'text': '5-ти минутка', 'payload': 'type:5min'}],
                [{'type': 'callback', 'text': 'ДХЧ', 'payload': 'type:dhch'}],
                [{'type': 'callback', 'text': 'ДЭС', 'payload': 'type:des'}]
            ]
            send_message(sender_id, response_text, buttons)
        else:
            response_text = '⚠️ Пожалуйста, введите пробег цифрами.\n\nНапример: 150000'
            send_message(sender_id, response_text)
    
    else:
        response_text = 'Не понял команду. Используйте /help для справки.'
        send_message(sender_id, response_text)


def handle_callback(update: dict):
    '''Обработка нажатий на кнопки'''
    callback = update.get('callback', {})
    sender_id = callback.get('user', {}).get('user_id')
    payload = callback.get('payload', '')
    
    print(f"[DEBUG] Callback - sender_id: {sender_id}, payload: {payload}")
    
    if not sender_id:
        print("[WARNING] No sender_id found in callback, skipping")
        return
    
    session = get_session(str(sender_id))
    
    if payload == 'start':
        session = {'step': 1}
        save_session(str(sender_id), session)
        response_text = '👋 Отлично! Выберите механика:'
        buttons = [
            [{'type': 'callback', 'text': 'Подкорытов С.А.', 'payload': 'mechanic:Подкорытов С.А.'}],
            [{'type': 'callback', 'text': 'Костенко В.Ю.', 'payload': 'mechanic:Костенко В.Ю.'}],
            [{'type': 'callback', 'text': 'Иванюта Д.И.', 'payload': 'mechanic:Иванюта Д.И.'}],
            [{'type': 'callback', 'text': 'Загороднюк Н.Д.', 'payload': 'mechanic:Загороднюк Н.Д.'}]
        ]
        send_message(sender_id, response_text, buttons)
    
    elif payload.startswith('mechanic:'):
        mechanic = payload.replace('mechanic:', '')
        session['mechanic'] = mechanic
        session['step'] = 2
        save_session(str(sender_id), session)
        response_text = f'✅ Механик {mechanic} выбран!\n\nВведите госномер автомобиля.\n\nНапример: A159BK124'
        send_message(sender_id, response_text)
    
    elif payload.startswith('type:'):
        diagnostic_type = payload.replace('type:', '')
        session['diagnostic_type'] = diagnostic_type
        save_session(str(sender_id), session)
        
        # Если выбрана "5-ти минутка" - начинаем чек-лист
        if diagnostic_type == '5min':
            # Сохраняем диагностику в БД
            diagnostic_id = save_diagnostic(session)
            if diagnostic_id:
                session['diagnostic_id'] = diagnostic_id
                session['question_index'] = 0
                session['step'] = 5
                save_session(str(sender_id), session)
                send_checklist_question(sender_id, session)
            else:
                response_text = '❌ Ошибка при сохранении диагностики. Попробуйте снова /start'
                send_message(sender_id, response_text)
        else:
            # ДХЧ и ДЭС - сохраняем без чек-листа
            diagnostic_id = save_diagnostic(session)
            
            if diagnostic_id:
                type_labels = {'dhch': 'ДХЧ', 'des': 'ДЭС'}
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
                send_message(sender_id, response_text, buttons)
                session = {'step': 0}
                save_session(str(sender_id), session)
            else:
                response_text = '❌ Ошибка при сохранении диагностики. Попробуйте снова /start'
                send_message(sender_id, response_text)
    
    elif payload.startswith('answer:'):
        # Обработка ответа на вопрос чек-листа
        handle_checklist_answer(sender_id, session, payload)
    
    elif payload == 'add_photo':
        # Запрос на добавление фото
        session['waiting_for_photo'] = True
        save_session(str(sender_id), session)
        response_text = '📸 Прикрепите фото дефекта в следующем сообщении.'
        buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
        send_message(sender_id, response_text, buttons)
    
    elif payload == 'skip_photo':
        # Пропуск фото
        session['waiting_for_photo'] = False
        save_session(str(sender_id), session)
        send_checklist_question(sender_id, session)


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


def get_checklist_questions():
    '''Возвращает список вопросов для чек-листа 5-ти минутки'''
    return [
        {'id': 1, 'title': 'Сигнал звукового тона', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 2, 'title': 'Батарейка ключа', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 3, 'title': 'Щетки стеклоочистителя переднего', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 4, 'title': 'Стекло лобовое', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 5, 'title': 'Подсветка приборов', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 6, 'title': 'Лампы неисправностей на панели приборов', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 7, 'title': 'Рамка переднего госномера', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 8, 'title': 'Габариты передние', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 9, 'title': 'Ближний свет', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 10, 'title': 'Дальний свет', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 11, 'title': 'Передние противотуманные фары', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 12, 'title': 'Повороты передние', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 13, 'title': 'Колесо переднее левое', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 14, 'title': 'Колесо заднее левое', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 15, 'title': 'Щетка стеклоочистителя заднего', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 16, 'title': 'Рамка заднего госномера', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 17, 'title': 'Подсветка заднего госномера', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 18, 'title': 'Габариты задние', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 19, 'title': 'Повороты задние', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 20, 'title': 'Стоп сигналы задние', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 21, 'title': 'Сигнал заднего хода', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 22, 'title': 'Задние противотуманные фары', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 23, 'title': 'Колесо заднее правое', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 24, 'title': 'Колесо переднее правое', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}]},
        {'id': 25, 'title': 'Состояние приводных ремней', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 26, 'title': 'Уровень масла ДВС', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': '50-75', 'label': '50-75%'}, {'value': '75-100', 'label': '75-100%'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 27, 'title': 'Состояние масла ДВС', 'options': [{'value': 'fresh', 'label': 'Свежее'}, {'value': 'working', 'label': 'Рабочее'}, {'value': 'particles', 'label': 'С примесями'}]},
        {'id': 28, 'title': 'Уровень жидкости ГУР', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': '50-75', 'label': '50-75%'}, {'value': '75-100', 'label': '75-100%'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 29, 'title': 'Состояние жидкости ГУР', 'options': [{'value': 'fresh', 'label': 'Свежее'}, {'value': 'working', 'label': 'Рабочее'}, {'value': 'burnt', 'label': 'Горелое'}]},
        {'id': 30, 'title': 'Уровень охлаждающей жидкости ДВС', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': 'level', 'label': 'Уровень'}, {'value': 'above', 'label': 'Выше уровня'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 31, 'title': 'Цвет охлаждающей жидкости ДВС', 'options': [{'value': 'red', 'label': 'Красный'}, {'value': 'green', 'label': 'Зеленый'}, {'value': 'blue', 'label': 'Синий'}]},
        {'id': 32, 'title': 'Состояние охлаждающей жидкости ДВС', 'options': [{'value': 'clean', 'label': 'Чистая'}, {'value': 'cloudy', 'label': 'Мутная'}]},
        {'id': 33, 'title': 'Температура кристаллизации ОЖ ДВС', 'options': [{'value': '25_35', 'label': '-25-35°С'}, {'value': '35_45', 'label': '-35-45°С'}, {'value': 'more_45', 'label': 'Более -45°С'}]},
        {'id': 34, 'title': 'Уровень охлаждающей жидкости HV', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': 'level', 'label': 'Уровень'}, {'value': 'above', 'label': 'Выше уровня'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 35, 'title': 'Цвет охлаждающей жидкости HV', 'options': [{'value': 'red', 'label': 'Красный'}, {'value': 'green', 'label': 'Зеленый'}, {'value': 'blue', 'label': 'Синий'}]},
        {'id': 36, 'title': 'Состояние охлаждающей жидкости HV', 'options': [{'value': 'clean', 'label': 'Чистая'}, {'value': 'cloudy', 'label': 'Мутная'}]},
        {'id': 37, 'title': 'Температура кристаллизации ОЖ HV', 'options': [{'value': '25_35', 'label': '-25-35°С'}, {'value': '35_45', 'label': '-35-45°С'}, {'value': 'more_45', 'label': 'Более -45°С'}]},
        {'id': 38, 'title': 'Уровень охлаждающей жидкости турбины', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': 'level', 'label': 'Уровень'}, {'value': 'above', 'label': 'Выше уровня'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 39, 'title': 'Цвет охлаждающей жидкости турбины', 'options': [{'value': 'red', 'label': 'Красный'}, {'value': 'green', 'label': 'Зеленый'}, {'value': 'blue', 'label': 'Синий'}]},
        {'id': 40, 'title': 'Состояние охлаждающей жидкости турбины', 'options': [{'value': 'clean', 'label': 'Чистая'}, {'value': 'cloudy', 'label': 'Мутная'}]},
        {'id': 41, 'title': 'Температура кристаллизации ОЖ турбины', 'options': [{'value': '25_35', 'label': '-25-35°С'}, {'value': '35_45', 'label': '-35-45°С'}, {'value': 'more_45', 'label': 'Более -45°С'}]},
        {'id': 42, 'title': 'Уровень тормозной жидкости', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': 'level', 'label': 'Уровень'}, {'value': 'above', 'label': 'Выше уровня'}]},
        {'id': 43, 'title': 'Температура кипения тормозной жидкости', 'options': [{'value': 'less_180', 'label': 'Менее 180°С'}, {'value': 'more_180', 'label': 'Более 180°С'}]},
        {'id': 44, 'title': 'Состояние тормозной жидкости', 'options': [{'value': 'clean', 'label': 'Чистая'}, {'value': 'cloudy', 'label': 'Мутная'}]},
        {'id': 45, 'title': 'Уровень масла КПП', 'options': [{'value': 'below', 'label': 'Ниже уровня'}, {'value': '50-75', 'label': '50-75%'}, {'value': '75-100', 'label': '75-100%'}, {'value': 'need_disassembly', 'label': 'Требуется разбор'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 46, 'title': 'Состояние масла КПП', 'options': [{'value': 'fresh', 'label': 'Свежее'}, {'value': 'working', 'label': 'Рабочее'}, {'value': 'burnt', 'label': 'Горелое'}]},
        {'id': 47, 'title': 'Омывающая жидкость', 'options': [{'value': 'present', 'label': 'Присутствует'}, {'value': 'missing', 'label': 'Отсутствует'}, {'value': 'frozen', 'label': 'Замерзла'}]},
        {'id': 48, 'title': 'Работа стартера при запуске ДВС', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 49, 'title': 'Работа ДВС', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 50, 'title': 'Работа КПП', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 51, 'title': 'Течи технических жидкостей', 'options': [{'value': 'no_leaks', 'label': 'Нет течей'}, {'value': 'has_leaks', 'label': 'Есть течи'}]},
        {'id': 52, 'title': 'Состояние воздушного фильтра', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'need_disassembly', 'label': 'Требуется разбор'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 53, 'title': 'Состояние салонного фильтра', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'need_disassembly', 'label': 'Требуется разбор'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 54, 'title': 'Состояние фильтра ВВБ', 'options': [{'value': 'ok', 'label': 'Исправно'}, {'value': 'bad', 'label': 'Неисправно'}, {'value': 'need_disassembly', 'label': 'Требуется разбор'}, {'value': 'na', 'label': 'Не предусмотрено'}]},
        {'id': 55, 'title': 'Иные замечания', 'options': [{'value': 'complete', 'label': 'Завершить, замечаний нет'}]},
    ]


def send_checklist_question(sender_id: str, session: dict):
    '''Отправляет текущий вопрос чек-листа'''
    questions = get_checklist_questions()
    question_index = session.get('question_index', 0)
    
    if question_index >= len(questions):
        # Чек-лист завершен - генерируем отчет
        finish_checklist(sender_id, session)
        return
    
    question = questions[question_index]
    total = len(questions)
    
    response_text = f'''📋 Вопрос {question_index + 1} из {total}

{question['title']}'''
    
    # Формируем кнопки из опций
    buttons = []
    for option in question['options']:
        buttons.append([{
            'type': 'callback',
            'text': option['label'],
            'payload': f"answer:{question['id']}:{option['value']}"
        }])
    
    # Кнопка добавления фото для "Неисправно"
    has_bad_option = any(opt['value'] == 'bad' for opt in question['options'])
    if has_bad_option:
        buttons.append([{'type': 'callback', 'text': '📸 Прикрепить фото дефекта', 'payload': 'add_photo'}])
    
    send_message(sender_id, response_text, buttons)


def handle_checklist_answer(sender_id: str, session: dict, payload: str):
    '''Обработка ответа на вопрос чек-листа'''
    # Парсим payload: "answer:question_id:value"
    parts = payload.split(':')
    if len(parts) < 3:
        return
    
    question_id = int(parts[1])
    answer_value = parts[2]
    
    # Сохраняем ответ в БД
    if answer_value != 'skip':
        success = save_checklist_answer(session['diagnostic_id'], question_id, answer_value)
        if not success:
            response_text = '⚠️ Ошибка при сохранении ответа. Попробуйте ещё раз или нажмите "Пропустить".'
            send_message(sender_id, response_text)
            return
    
    # Переход к следующему вопросу
    session['question_index'] += 1
    save_session(str(sender_id), session)
    
    send_checklist_question(sender_id, session)


def handle_photo_upload(sender_id: str, session: dict, attachments: list):
    '''Обработка загрузки фото дефекта'''
    try:
        # Ищем фото в attachments
        photo_url = None
        for attachment in attachments:
            if attachment.get('type') == 'image':
                payload = attachment.get('payload', {})
                photo_url = payload.get('url')
                break
        
        if not photo_url:
            response_text = '⚠️ Не найдено фото. Попробуйте ещё раз или пропустите.'
            buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
            send_message(sender_id, response_text, buttons)
            return
        
        # Скачиваем фото
        print(f"[DEBUG] Downloading photo from: {photo_url}")
        photo_response = requests.get(photo_url, timeout=10)
        
        if photo_response.status_code != 200:
            response_text = '⚠️ Не удалось загрузить фото. Попробуйте ещё раз.'
            buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
            send_message(sender_id, response_text, buttons)
            return
        
        # Сохраняем фото в S3
        diagnostic_id = session.get('diagnostic_id')
        question_index = session.get('question_index', 0)
        krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
        now = datetime.now(krasnoyarsk_tz)
        
        file_key = f"diagnostics/{diagnostic_id}/question_{question_index + 1}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"
        
        s3 = boto3.client('s3',
            endpoint_url='https://bucket.poehali.dev',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        
        s3.put_object(
            Bucket='files',
            Key=file_key,
            Body=photo_response.content,
            ContentType='image/jpeg'
        )
        
        cdn_url = f"https://cdn.poehali.dev/projects/{os.environ['AWS_ACCESS_KEY_ID']}/bucket/{file_key}"
        
        # Сохраняем фото в базу данных
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            f"INSERT INTO {schema}.diagnostic_photos (diagnostic_id, question_index, photo_url) "
            f"VALUES ({diagnostic_id}, {question_index}, '{cdn_url}')"
        )
        conn.commit()
        cur.close()
        conn.close()
        
        session['waiting_for_photo'] = False
        save_session(str(sender_id), session)
        
        response_text = '✅ Фото дефекта сохранено!\n\nПродолжаем диагностику.'
        send_message(sender_id, response_text)
        
        # Переход к следующему вопросу
        send_checklist_question(sender_id, session)
        
    except Exception as e:
        print(f"[ERROR] Failed to upload photo: {str(e)}")
        response_text = '⚠️ Ошибка при загрузке фото. Попробуйте ещё раз или пропустите.'
        buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
        send_message(sender_id, response_text, buttons)


def save_checklist_answer(diagnostic_id: int, question_number: int, answer_value: str) -> bool:
    '''Сохранение ответа на вопрос чек-листа в БД'''
    try:
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        questions = get_checklist_questions()
        question = next((q for q in questions if q['id'] == question_number), None)
        
        if not question:
            print(f"[ERROR] Question {question_number} not found")
            return False
        
        question_text = question['title']
        
        # Определяем значение ответа для answer_value
        if answer_value == 'ok':
            answer_val = 'Исправно'
        elif answer_value == 'bad':
            answer_val = 'Неисправно'
        elif answer_value == 'na':
            answer_val = 'Не предусмотрено'
        elif answer_value == 'no_leaks':
            answer_val = 'Нет течей'
        elif answer_value == 'has_leaks':
            answer_val = 'Есть течи'
        elif answer_value == 'complete':
            answer_val = 'Завершить, замечаний нет'
        else:
            # Найдем label в опциях
            option = next((opt for opt in question['options'] if opt['value'] == answer_value), None)
            answer_val = option['label'] if option else answer_value
        
        cur.execute(
            f"INSERT INTO {schema}.checklist_answers (diagnostic_id, question_number, question_text, answer_type, answer_value) "
            f"VALUES ({diagnostic_id}, {question_number}, '{question_text}', 'single', '{answer_val}')"
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[SUCCESS] Saved answer for question {question_number}")
        return True
    
    except Exception as e:
        print(f"[ERROR] Failed to save checklist answer: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False


def finish_checklist(sender_id: str, session: dict):
    '''Завершение чек-листа и генерация отчета'''
    diagnostic_id = session.get('diagnostic_id')
    
    # Генерируем оба варианта отчёта
    report_url_base = "https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6"
    
    try:
        # Отчёт без фото
        response_no_photos = requests.get(f"{report_url_base}?id={diagnostic_id}", timeout=30)
        pdf_url_no_photos = None
        if response_no_photos.status_code == 200:
            result = response_no_photos.json()
            pdf_url_no_photos = result.get('pdfUrl')
        
        # Отчёт с фото
        response_with_photos = requests.get(f"{report_url_base}?id={diagnostic_id}&with_photos=true", timeout=30)
        pdf_url_with_photos = None
        if response_with_photos.status_code == 200:
            result = response_with_photos.json()
            pdf_url_with_photos = result.get('pdfUrl')
        
        if pdf_url_no_photos and pdf_url_with_photos:
            response_text = f'''✅ Диагностика №{diagnostic_id} завершена!

📋 Сводка:
━━━━━━━━━━━━━━━━
👤 Механик: {session['mechanic']}
🚗 Госномер: {session['car_number']}
🛣 Пробег: {session['mileage']:,} км
🔧 Тип: 5-ти минутка
━━━━━━━━━━━━━━━━

📄 Отчёты готовы!

Без фото: {pdf_url_no_photos}

С фото: {pdf_url_with_photos}'''.replace(',', ' ')
        elif pdf_url_no_photos:
            response_text = f'''✅ Диагностика №{diagnostic_id} завершена!

📋 Сводка:
━━━━━━━━━━━━━━━━
👤 Механик: {session['mechanic']}
🚗 Госномер: {session['car_number']}
🛣 Пробег: {session['mileage']:,} км
🔧 Тип: 5-ти минутка
━━━━━━━━━━━━━━━━

📄 Отчёт готов!
{pdf_url_no_photos}'''.replace(',', ' ')
        else:
            response_text = f'''✅ Диагностика №{diagnostic_id} завершена!

📋 Чек-лист сохранен, но отчет временно недоступен.'''
    except Exception as e:
        print(f"[ERROR] Failed to generate report: {str(e)}")
        response_text = f'''✅ Диагностика №{diagnostic_id} завершена!

📋 Чек-лист сохранен.'''
    
    buttons = [[{'type': 'callback', 'text': 'Начать новую диагностику', 'payload': 'start'}]]
    send_message(sender_id, response_text, buttons)
    
    # Сброс сессии
    session = {'step': 0}
    save_session(str(sender_id), session)


def send_message(user_id: int, text: str, buttons: list = None):
    '''Отправка сообщения через MAX API'''
    
    token = os.environ.get('MAX_BOT_TOKEN')
    url = f'https://platform-api.max.ru/messages?user_id={user_id}'
    
    payload = {
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
    
    print(f"[DEBUG] Sending message to user_id: {user_id}")
    print(f"[DEBUG] URL: {url}")
    print(f"[DEBUG] Payload: {json.dumps(payload, ensure_ascii=False)}")
    
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"[DEBUG] Response status: {response.status_code}")
    print(f"[DEBUG] Response body: {response.text}")
    
    return response.json()