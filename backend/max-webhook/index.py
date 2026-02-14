import json
import os
import requests
import psycopg2
from psycopg2 import pool
import boto3
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from checklist_data import get_checklist_questions_full
from priemka_data import get_priemka_questions

# Connection pool для оптимизации работы с БД
_db_pool = None

def get_db_pool():
    '''Получение connection pool (singleton)'''
    global _db_pool
    if _db_pool is None:
        db_url = os.environ.get('DATABASE_URL')
        _db_pool = pool.SimpleConnectionPool(1, 5, db_url)
    return _db_pool


def reset_db_pool():
    '''Сброс connection pool при ошибках соединения'''
    global _db_pool
    if _db_pool:
        try:
            _db_pool.closeall()
        except Exception:
            pass
    _db_pool = None


def get_session(user_id: str) -> dict:
    '''Получение сессии пользователя из БД'''
    for attempt in range(2):
        conn = None
        try:
            schema = os.environ.get('MAIN_DB_SCHEMA')
            db_pool = get_db_pool()
            conn = db_pool.getconn()
            cur = conn.cursor()
            
            cur.execute(
                f"SELECT session_data FROM {schema}.max_sessions WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()
            cur.close()
            
            if row:
                return row[0]
            return {'step': 0}
        except Exception as e:
            print(f"[ERROR] Failed to get session (attempt {attempt + 1}): {str(e)}")
            if conn:
                try:
                    get_db_pool().putconn(conn, close=True)
                except Exception:
                    pass
                conn = None
            reset_db_pool()
            if attempt == 1:
                return {'step': 0}
        finally:
            if conn:
                try:
                    get_db_pool().putconn(conn)
                except Exception:
                    pass


def save_session(user_id: str, session: dict):
    '''Сохранение сессии пользователя в БД'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        
        session_json = json.dumps(session, ensure_ascii=False)
        
        cur.execute(
            f"INSERT INTO {schema}.max_sessions (user_id, session_data, updated_at) "
            f"VALUES (%s, %s::jsonb, CURRENT_TIMESTAMP) "
            f"ON CONFLICT (user_id) DO UPDATE SET session_data = %s::jsonb, updated_at = CURRENT_TIMESTAMP",
            (user_id, session_json, session_json)
        )
        
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"[ERROR] Failed to save session: {str(e)}")
    finally:
        if conn:
            get_db_pool().putconn(conn)

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
    
    lower_text = user_text.lower()
    if lower_text in ['/cancel', 'отмена', '/отмена'] and session.get('step', 0) > 1:
        mechanic_id = session.get('mechanic_id')
        mechanic_name = session.get('mechanic', '')
        session = {'step': 2, 'mechanic_id': mechanic_id, 'mechanic': mechanic_name, 'user_id': session.get('user_id'), 'user_name': session.get('user_name'), 'phone': session.get('phone')}
        save_session(str(sender_id), session)
        response_text = f'❌ Диагностика отменена.\n\n{mechanic_name}, выберите тип диагностики:'
        buttons = [
            [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
            [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
            [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
            [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
        ]
        send_message(sender_id, response_text, buttons)
        return
    
    # Обработка контакта для авторизации
    if session.get('step') == 1 and attachments:
        for attachment in attachments:
            if attachment.get('type') == 'contact':
                handle_phone_auth(sender_id, session, attachment)
                return
    
    # Обработка текстового ответа на "Иное (указать текстом)"
    if session.get('step') == 5 and session.get('waiting_for_text'):
        if user_text:
            handle_text_answer(sender_id, session, user_text)
        else:
            response_text = '⚠️ Пожалуйста, введите текст или вернитесь назад.'
            send_message(sender_id, response_text)
        return
    
    # Обработка фото в режиме чек-листа
    if session.get('step') == 5 and session.get('waiting_for_photo'):
        if attachments:
            handle_photo_upload(sender_id, session, attachments, user_text)
        else:
            response_text = '⚠️ Пожалуйста, прикрепите фото дефекта или нажмите "Пропустить фото".'
            buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
            send_message(sender_id, response_text, buttons)
        return
    
    # Обработка фото в режиме Приемки
    if session.get('step') == 6 and session.get('waiting_for_photo'):
        if attachments:
            handle_priemka_photo(sender_id, session, attachments, user_text)
        else:
            response_text = '⚠️ Пожалуйста, прикрепите фото.'
            buttons = [[{'type': 'callback', 'text': '⬅️ Назад', 'payload': 'priemka_back'}]]
            send_message(sender_id, response_text, buttons)
        return
    
    # Обработка текста в режиме Приемки (замечания)
    if session.get('step') == 6 and session.get('waiting_for_text'):
        if user_text:
            handle_priemka_text(sender_id, session, user_text)
        else:
            response_text = '⚠️ Пожалуйста, введите текст замечания.'
            send_message(sender_id, response_text)
        return
    
    # Команды
    if lower_text in ['/start', 'начать', 'старт']:
        if session.get('mechanic_id'):
            session['step'] = 2
            save_session(str(sender_id), session)
            response_text = f'👋 С возвращением, {session.get("mechanic", "")}!\n\nВыберите тип диагностики:'
            buttons = [
                [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
                [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
                [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
                [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
            ]
            send_message(sender_id, response_text, buttons)
        else:
            # Не авторизован - запрашиваем телефон
            session = {'step': 1}
            save_session(str(sender_id), session)
            response_text = '👋 Привет! Я HEVSR Diagnostics bot.\n\nДля начала работы поделитесь своим номером телефона:'
            buttons = [
                [{'type': 'request_contact', 'text': '📱 Отправить номер телефона'}]
            ]
            send_message(sender_id, response_text, buttons)
        return
    
    elif lower_text in ['/help', 'помощь']:
        response_text = '''📋 Доступные команды:

/start - Начать новую диагностику
/cancel (или "отмена") - Отменить текущую диагностику
/help - Показать помощь

Команду отмены можно ввести на любом этапе диагностики.'''
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
        response_text = 'Выберите тип диагностики из кнопок выше или введите /start.'
        buttons = [
            [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
            [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
            [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
            [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
        ]
        send_message(sender_id, response_text, buttons)
    
    elif step == 3:
        clean_number = user_text.upper().replace(' ', '').replace('-', '')
        has_cyrillic = any('\u0410' <= char <= '\u042f' or '\u0430' <= char <= '\u044f' for char in clean_number)
        
        if has_cyrillic:
            response_text = '\u26a0\ufe0f \u0413\u043e\u0441\u043d\u043e\u043c\u0435\u0440 \u0434\u043e\u043b\u0436\u0435\u043d \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u0442\u044c \u0442\u043e\u043b\u044c\u043a\u043e \u043b\u0430\u0442\u0438\u043d\u0441\u043a\u0438\u0435 \u0431\u0443\u043a\u0432\u044b.\n\n\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: A159BK124 (\u043d\u0435 \u0410159\u0412\u041a124)'
            send_message(sender_id, response_text)
        elif len(clean_number) >= 5:
            session['car_number'] = clean_number
            diagnostic_type = session.get('diagnostic_type', '')
            if diagnostic_type == 'priemka':
                diagnostic_id = save_diagnostic(session)
                if diagnostic_id:
                    session.pop('waiting_for_photo', None)
                    session.pop('waiting_for_text', None)
                    session.pop('priemka_extra_photos', None)
                    session['diagnostic_id'] = diagnostic_id
                    session['question_index'] = 0
                    session['step'] = 6
                    save_session(str(sender_id), session)
                    response_text = f'\u2705 \u0413\u043e\u0441\u043d\u043e\u043c\u0435\u0440 {clean_number} \u043f\u0440\u0438\u043d\u044f\u0442! \u041d\u0430\u0447\u0438\u043d\u0430\u0435\u043c \u041f\u0440\u0438\u0435\u043c\u043a\u0443.'
                    send_message(sender_id, response_text)
                    send_priemka_question(sender_id, session)
                else:
                    response_text = '\u274c \u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0438 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0441\u043d\u043e\u0432\u0430 /start'
                    send_message(sender_id, response_text)
            else:
                session['step'] = 4
                save_session(str(sender_id), session)
                response_text = f'\u2705 \u0413\u043e\u0441\u043d\u043e\u043c\u0435\u0440 {clean_number} \u043f\u0440\u0438\u043d\u044f\u0442!\n\n\u0422\u0435\u043f\u0435\u0440\u044c \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0440\u043e\u0431\u0435\u0433 \u0430\u0432\u0442\u043e\u043c\u043e\u0431\u0438\u043b\u044f (\u0432 \u043a\u043c).\n\n\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: 150000'
                buttons = [[{'type': 'callback', 'text': '\u274c \u041e\u0442\u043c\u0435\u043d\u0438\u0442\u044c', 'payload': 'cancel_diagnostic'}]]
                send_message(sender_id, response_text, buttons)
        else:
            response_text = '\u26a0\ufe0f \u0413\u043e\u0441\u043d\u043e\u043c\u0435\u0440 \u0441\u043b\u0438\u0448\u043a\u043e\u043c \u043a\u043e\u0440\u043e\u0442\u043a\u0438\u0439.\n\n\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u0440\u0440\u0435\u043a\u0442\u043d\u044b\u0439 \u0433\u043e\u0441\u043d\u043e\u043c\u0435\u0440 (\u043c\u0438\u043d\u0438\u043c\u0443\u043c 5 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432).\n\n\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: A159BK124'
            send_message(sender_id, response_text)
    
    elif step == 4:
        mileage_str = ''.join(filter(str.isdigit, user_text))
        if mileage_str and int(mileage_str) > 0:
            session['mileage'] = int(mileage_str)
            save_session(str(sender_id), session)
            diagnostic_type = session.get('diagnostic_type', '')
            if diagnostic_type == '5min':
                diagnostic_id = save_diagnostic(session)
                if diagnostic_id:
                    session.pop('sub_question_mode', None)
                    session.pop('sub_question_path', None)
                    session.pop('sub_selections', None)
                    session.pop('waiting_for_photo', None)
                    session['diagnostic_id'] = diagnostic_id
                    session['question_index'] = 0
                    session['step'] = 5
                    save_session(str(sender_id), session)
                    response_text = f'\u2705 \u041f\u0440\u043e\u0431\u0435\u0433 {int(mileage_str):,} \u043a\u043c \u043f\u0440\u0438\u043d\u044f\u0442! \u041d\u0430\u0447\u0438\u043d\u0430\u0435\u043c 5-\u0442\u0438 \u043c\u0438\u043d\u0443\u0442\u043a\u0443.'.replace(',', ' ')
                    send_message(sender_id, response_text)
                    send_checklist_question(sender_id, session)
                else:
                    response_text = '\u274c \u041e\u0448\u0438\u0431\u043a\u0430 \u043f\u0440\u0438 \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u0438 \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438. \u041f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0441\u043d\u043e\u0432\u0430 /start'
                    send_message(sender_id, response_text)
            else:
                type_labels = {'dhch': '\u0414\u0425\u0427', 'des': '\u0414\u042d\u0421'}
                type_label = type_labels.get(diagnostic_type, diagnostic_type)
                response_text = f'\ud83d\udea7 \u0420\u0430\u0437\u0434\u0435\u043b \u00ab{type_label}\u00bb \u0432 \u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0435.\n\n\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0434\u0440\u0443\u0433\u043e\u0439 \u0442\u0438\u043f \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438 \u0438\u043b\u0438 \u043d\u0430\u0447\u043d\u0438\u0442\u0435 \u0437\u0430\u043d\u043e\u0432\u043e.'
                buttons = [
                    [{'type': 'callback', 'text': '\u2b05\ufe0f \u0412\u044b\u0431\u0440\u0430\u0442\u044c \u0434\u0440\u0443\u0433\u043e\u0439 \u0442\u0438\u043f', 'payload': 'back_to_type'}],
                    [{'type': 'callback', 'text': '\u041d\u0430\u0447\u0430\u0442\u044c \u043d\u043e\u0432\u0443\u044e \u0434\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0443', 'payload': 'start'}]
                ]
                send_message(sender_id, response_text, buttons)
        else:
            response_text = '\u26a0\ufe0f \u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0440\u043e\u0431\u0435\u0433 \u0446\u0438\u0444\u0440\u0430\u043c\u0438.\n\n\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: 150000'
            send_message(sender_id, response_text)
    
    elif step == 7:
        mileage_str = ''.join(filter(str.isdigit, user_text))
        if mileage_str and int(mileage_str) > 0:
            session['mileage'] = int(mileage_str)
            diagnostic_id = session.get('diagnostic_id')
            if diagnostic_id:
                update_diagnostic_mileage(diagnostic_id, int(mileage_str))
            session['step'] = 6
            session['waiting_for_photo'] = False
            session['waiting_for_text'] = False
            save_session(str(sender_id), session)
            response_text = f'\u2705 \u041f\u0440\u043e\u0431\u0435\u0433 {int(mileage_str):,} \u043a\u043c \u043f\u0440\u0438\u043d\u044f\u0442! \u041f\u0440\u043e\u0434\u043e\u043b\u0436\u0430\u0435\u043c \u041f\u0440\u0438\u0435\u043c\u043a\u0443.'.replace(',', ' ')
            send_message(sender_id, response_text)
            send_priemka_question(sender_id, session)
        else:
            response_text = '\u26a0\ufe0f \u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u043f\u0440\u043e\u0431\u0435\u0433 \u0446\u0438\u0444\u0440\u0430\u043c\u0438.\n\n\u041d\u0430\u043f\u0440\u0438\u043c\u0435\u0440: 150000'
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
        if session.get('mechanic_id'):
            session['step'] = 2
            save_session(str(sender_id), session)
            response_text = f'👋 Отлично! Выберите тип диагностики:'
            buttons = [
                [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
                [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
                [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
                [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
            ]
            send_message(sender_id, response_text, buttons)
        else:
            # Не авторизован - запрашиваем телефон
            session = {'step': 1}
            save_session(str(sender_id), session)
            response_text = '👋 Отлично! Для начала работы поделитесь своим номером телефона:'
            buttons = [
                [{'type': 'request_contact', 'text': '📱 Отправить номер телефона'}]
            ]
            send_message(sender_id, response_text, buttons)
    
    elif payload.startswith('type:'):
        diagnostic_type = payload.replace('type:', '')
        session['diagnostic_type'] = diagnostic_type
        session['step'] = 3
        save_session(str(sender_id), session)
        
        type_labels = {'priemka': 'Приемка', '5min': '5-ти минутка', 'dhch': 'ДХЧ', 'des': 'ДЭС'}
        type_label = type_labels.get(diagnostic_type, diagnostic_type)
        
        response_text = f'✅ Тип: {type_label}\n\nВведите госномер автомобиля.\n\nНапример: A159BK124'
        buttons = [[{'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'}]]
        send_message(sender_id, response_text, buttons)
    
    elif payload == 'cancel_diagnostic':
        mechanic_id = session.get('mechanic_id')
        mechanic_name = session.get('mechanic', '')
        session = {'step': 2, 'mechanic_id': mechanic_id, 'mechanic': mechanic_name, 'user_id': session.get('user_id'), 'user_name': session.get('user_name'), 'phone': session.get('phone')}
        save_session(str(sender_id), session)
        response_text = f'❌ Диагностика отменена.\n\n{mechanic_name}, выберите тип диагностики:'
        buttons = [
            [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
            [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
            [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
            [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
        ]
        send_message(sender_id, response_text, buttons)

    elif payload == 'back_to_type':
        session['step'] = 2
        session.pop('diagnostic_type', None)
        save_session(str(sender_id), session)
        response_text = 'Выберите тип диагностики:'
        buttons = [
            [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
            [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
            [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
            [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
        ]
        send_message(sender_id, response_text, buttons)
    
    elif payload.startswith('priemka_answer:'):
        handle_priemka_callback(sender_id, session, payload)
    
    elif payload == 'priemka_back':
        handle_priemka_back(sender_id, session)
    
    elif payload.startswith('answer:'):
        handle_checklist_answer(sender_id, session, payload)
    
    elif payload.startswith('sub_answer:'):
        # Обработка ответа на подвопрос
        print(f"[DEBUG] Routing to handle_sub_answer for payload: {payload}")
        handle_sub_answer(sender_id, session, payload)
    
    elif payload.startswith('sub_answer_done:'):
        # Завершение выбора подпунктов
        handle_sub_answer_done(sender_id, session, payload)
    
    elif payload.startswith('nested_sub_answer:'):
        # Обработка вложенного подвопроса 3-го уровня
        handle_nested_sub_answer(sender_id, session, payload)
    
    elif payload == 'cancel_sub_question':
        # Отмена режима подвопросов
        session.pop('sub_question_mode', None)
        session.pop('sub_question_path', None)
        session.pop('sub_selections', None)
        save_session(str(sender_id), session)
        send_checklist_question(sender_id, session)
    
    elif payload.startswith('back_to_sub_list'):
        # Возврат к списку подпунктов (из вложенного 3-го уровня)
        # Если передан parent_value — удаляем этот элемент из выбранных
        parts = payload.split(':')
        if len(parts) > 1:
            parent_value = parts[1]
            sub_selections = session.get('sub_selections', {})
            selected = sub_selections.get('main', [])
            
            # Удаляем элемент из списка
            if parent_value in selected:
                selected.remove(parent_value)
                sub_selections['main'] = selected
            
            # Удаляем вложенный ответ
            sub_key = f'main-{parent_value}'
            sub_selections.pop(sub_key, None)
            
            session['sub_selections'] = sub_selections
            save_session(str(sender_id), session)
        
        send_sub_question(sender_id, session)
    
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
        
        # Переход к следующему вопросу
        session['question_index'] += 1
        save_session(str(sender_id), session)
        
        send_checklist_question(sender_id, session)
    
    elif payload == 'previous_question':
        # Возврат к предыдущему ОТВЕЧЕННОМУ вопросу
        diagnostic_id = session.get('diagnostic_id')
        
        if diagnostic_id:
            prev_conn = None
            try:
                schema = os.environ.get('MAIN_DB_SCHEMA')
                db_pool = get_db_pool()
                prev_conn = db_pool.getconn()
                cur = prev_conn.cursor()
                
                # Находим последний отвеченный вопрос
                cur.execute(
                    f"SELECT question_number FROM {schema}.checklist_answers "
                    f"WHERE diagnostic_id = %s "
                    f"ORDER BY question_number DESC LIMIT 1",
                    (diagnostic_id,)
                )
                last_answer = cur.fetchone()
                
                if last_answer:
                    prev_question_number = last_answer[0]
                    
                    # Удаляем этот ответ
                    cur.execute(
                        f"DELETE FROM {schema}.checklist_answers "
                        f"WHERE diagnostic_id = %s AND question_number = %s",
                        (diagnostic_id, prev_question_number)
                    )
                    prev_conn.commit()
                    
                    # Находим индекс этого вопроса
                    questions = get_checklist_questions()
                    prev_index = next((i for i, q in enumerate(questions) if q['id'] == prev_question_number), 0)
                    
                    session['question_index'] = prev_index
                    save_session(str(sender_id), session)
                    send_checklist_question(sender_id, session)
                else:
                    # Если ответов нет - вернуться к первому вопросу
                    session['question_index'] = 0
                    save_session(str(sender_id), session)
                    send_checklist_question(sender_id, session)
                
                cur.close()
            except Exception as e:
                print(f"[ERROR] Failed to go back: {str(e)}")
            finally:
                if prev_conn:
                    db_pool.putconn(prev_conn)
        else:
            # Если нет diagnostic_id - просто вернуться назад
            question_index = session.get('question_index', 0)
            if question_index > 0:
                session['question_index'] = question_index - 1
                save_session(str(sender_id), session)
                send_checklist_question(sender_id, session)


def handle_phone_auth(sender_id: str, session: dict, contact_attachment: dict):
    '''Обработка авторизации по номеру телефона'''
    conn = None
    try:
        # Извлекаем номер телефона из attachment
        contact_payload = contact_attachment.get('payload', {})
        
        # MAX отправляет телефон в VCard формате
        vcf_info = contact_payload.get('vcf_info', '')
        phone = ''
        
        # Парсим VCard для извлечения телефона
        if vcf_info:
            for line in vcf_info.split('\n'):
                if line.startswith('TEL'):
                    # Формат: TEL;TYPE=cell:79293372613
                    phone = line.split(':')[-1].strip()
                    break
        
        print(f"[DEBUG] Phone auth attempt: {phone}")
        print(f"[DEBUG] VCF info: {vcf_info}")
        
        if not phone:
            response_text = '⚠️ Не удалось получить номер телефона. Попробуйте ещё раз.'
            buttons = [[{'type': 'request_contact', 'text': '📱 Отправить номер телефона'}]]
            send_message(sender_id, response_text, buttons)
            return
        
        # Нормализуем номер телефона (добавляем + если нет, удаляем пробелы, дефисы)
        clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if not clean_phone.startswith('+'):
            clean_phone = '+' + clean_phone
        
        # Ищем механика по номеру телефона
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT id, name, is_active FROM {schema}.mechanics WHERE phone = %s",
            (clean_phone,)
        )
        mechanic = cur.fetchone()
        cur.close()
        
        if not mechanic:
            response_text = f'❌ Номер {phone} не зарегистрирован в системе.\n\nОбратитесь к администратору для получения доступа.'
            buttons = [[{'type': 'callback', 'text': '🔙 Вернуться к началу', 'payload': 'start'}]]
            send_message(sender_id, response_text, buttons)
            return
        
        mechanic_id, mechanic_name, is_active = mechanic
        
        if not is_active:
            response_text = f'❌ Ваш аккаунт деактивирован.\n\nОбратитесь к администратору.'
            buttons = [[{'type': 'callback', 'text': '🔙 Вернуться к началу', 'payload': 'start'}]]
            send_message(sender_id, response_text, buttons)
            return
        
        # Сохраняем механика в сессии
        session['mechanic'] = mechanic_name
        session['mechanic_id'] = mechanic_id
        session['user_id'] = mechanic_id  # Для проверки авторизации
        session['user_name'] = mechanic_name
        session['phone'] = clean_phone
        session['step'] = 2
        save_session(str(sender_id), session)
        
        response_text = f'✅ Добро пожаловать, {mechanic_name}!\n\nВыберите тип диагностики:'
        buttons = [
            [{'type': 'callback', 'text': '📋 Приемка', 'payload': 'type:priemka'}],
            [{'type': 'callback', 'text': '⏱ 5-ти минутка', 'payload': 'type:5min'}],
            [{'type': 'callback', 'text': '🔩 ДХЧ', 'payload': 'type:dhch'}],
            [{'type': 'callback', 'text': '⚡ ДЭС', 'payload': 'type:des'}],
        ]
        send_message(sender_id, response_text, buttons)
        
    except Exception as e:
        print(f"[ERROR] Phone auth failed: {str(e)}")
        response_text = '⚠️ Ошибка авторизации. Попробуйте ещё раз или обратитесь к администратору.'
        buttons = [[{'type': 'request_contact', 'text': '📱 Отправить номер телефона'}]]
        send_message(sender_id, response_text, buttons)
    finally:
        if conn:
            get_db_pool().putconn(conn)


def mark_diagnostic_completed(diagnostic_id: int):
    '''Помечает диагностику как завершённую'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        cur.execute(
            f"UPDATE {schema}.diagnostics SET completed = true, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (diagnostic_id,)
        )
        conn.commit()
        cur.close()
        print(f"[SUCCESS] Diagnostic {diagnostic_id} marked as completed")
    except Exception as e:
        print(f"[ERROR] Failed to mark diagnostic completed: {str(e)}")
    finally:
        if conn:
            get_db_pool().putconn(conn)


def update_diagnostic_mileage(diagnostic_id: int, mileage: int):
    '''Обновление пробега в существующей диагностике'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        cur.execute(
            f"UPDATE {schema}.diagnostics SET mileage = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
            (mileage, diagnostic_id)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"[ERROR] Failed to update mileage: {str(e)}")
    finally:
        if conn:
            get_db_pool().putconn(conn)


def save_diagnostic(session: dict) -> int:
    '''Сохранение диагностики в PostgreSQL'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        
        mechanic = session.get('mechanic', '')
        mechanic_id = session.get('mechanic_id')
        car_number = session.get('car_number', '')
        mileage = session.get('mileage', 0)
        diagnostic_type = session.get('diagnostic_type', '')
        
        krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
        now = datetime.now(krasnoyarsk_tz)
        
        if mechanic_id:
            cur.execute(
                f"INSERT INTO {schema}.diagnostics (mechanic, mechanic_id, car_number, mileage, diagnostic_type, created_at, updated_at) "
                f"VALUES ('{mechanic}', {mechanic_id}, '{car_number}', {mileage}, '{diagnostic_type}', '{now.isoformat()}', '{now.isoformat()}') RETURNING id"
            )
        else:
            cur.execute(
                f"INSERT INTO {schema}.diagnostics (mechanic, car_number, mileage, diagnostic_type, created_at, updated_at) "
                f"VALUES ('{mechanic}', '{car_number}', {mileage}, '{diagnostic_type}', '{now.isoformat()}', '{now.isoformat()}') RETURNING id"
            )
        
        result = cur.fetchone()
        conn.commit()
        cur.close()
        
        return result[0] if result else None
    except Exception as e:
        print(f"[ERROR] Failed to save diagnostic: {str(e)}")
        return None
    finally:
        if conn:
            get_db_pool().putconn(conn)


def get_checklist_questions():
    '''Возвращает полный список вопросов с подпунктами'''
    return get_checklist_questions_full()


def send_checklist_question(sender_id: str, session: dict):
    '''Отправляет текущий вопрос чек-листа или подпункты'''
    
    # Проверяем, находимся ли мы в режиме подвопросов
    if session.get('sub_question_mode'):
        send_sub_question(sender_id, session)
        return
    
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
    
    nav_buttons = []
    if question_index > 0:
        nav_buttons.append({'type': 'callback', 'text': '⬅️ Назад', 'payload': 'previous_question'})
    nav_buttons.append({'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'})
    buttons.append(nav_buttons)
    
    send_message(sender_id, response_text, buttons)


def send_sub_question(sender_id: str, session: dict):
    '''Отправляет подвопросы (subOptions)'''
    questions = get_checklist_questions()
    question_index = session.get('question_index', 0)
    question = questions[question_index]
    
    sub_path = session.get('sub_question_path', [])
    sub_selections = session.get('sub_selections', {})
    
    # Находим текущий уровень subOptions
    current_option = None
    for opt in question['options']:
        if opt['value'] == sub_path[0]:
            current_option = opt
            break
    
    if not current_option or 'subOptions' not in current_option:
        # Нет подпунктов - завершаем режим подвопросов
        finish_sub_questions(sender_id, session)
        return
    
    # Показываем подпункты первого уровня
    allow_multiple = current_option.get('allowMultiple', False)
    
    if allow_multiple:
        selected = sub_selections.get('main', [])
        selected_count = len(selected) if isinstance(selected, list) else 0
        response_text = f'''📋 Уточните неисправности:

{question['title']}

(Выбрано: {selected_count})'''
    else:
        response_text = f'''📋 Уточните неисправность:

{question['title']}'''
    
    buttons = []
    selected_values = sub_selections.get('main', []) if allow_multiple else []
    
    for sub_opt in current_option['subOptions']:
        # Для множественного выбора добавляем галочку к выбранным
        label = sub_opt['label']
        if allow_multiple and sub_opt['value'] in selected_values:
            label = f"✅ {label}"
        
        buttons.append([{
            'type': 'callback',
            'text': label,
            'payload': f"sub_answer:{question['id']}:{sub_opt['value']}"
        }])
    
    # Кнопка "Далее" для множественного выбора
    if allow_multiple:
        buttons.append([{
            'type': 'callback',
            'text': '➡️ Далее',
            'payload': f"sub_answer_done:{question['id']}"
        }])
    
    buttons.append([
        {'type': 'callback', 'text': '⬅️ Назад', 'payload': 'cancel_sub_question'},
        {'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'}
    ])
    
    send_message(sender_id, response_text, buttons)


def send_nested_sub_question(sender_id: str, session: dict, parent_option: dict, parent_value: str):
    '''Отправляет вложенные подпункты 3-го уровня'''
    questions = get_checklist_questions()
    question_index = session.get('question_index', 0)
    question = questions[question_index]
    
    response_text = f'''📋 Уточните проблему:

{parent_option['label']}'''
    
    buttons = []
    for nested_opt in parent_option['subOptions']:
        buttons.append([{
            'type': 'callback',
            'text': nested_opt['label'],
            'payload': f"nested_sub_answer:{question['id']}:{parent_value}:{nested_opt['value']}"
        }])
    
    buttons.append([
        {'type': 'callback', 'text': '⬅️ Назад', 'payload': f'back_to_sub_list:{parent_value}'},
        {'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'}
    ])
    
    send_message(sender_id, response_text, buttons)


def finish_sub_questions(sender_id: str, session: dict):
    '''Завершает сбор подпунктов и сохраняет ответ'''
    sub_selections = session.get('sub_selections', {})
    question_index = session.get('question_index', 0)
    questions = get_checklist_questions()
    question = questions[question_index]
    
    # Сохраняем ответ с подпунктами
    success = save_checklist_answer_with_subs(
        session['diagnostic_id'], 
        question['id'], 
        'bad',  # Основной ответ всегда "Неисправно"
        sub_selections
    )
    
    if not success:
        response_text = '⚠️ Ошибка при сохранении ответа. Попробуйте ещё раз.'
        send_message(sender_id, response_text)
        return
    
    # Очищаем режим подвопросов
    session.pop('sub_question_mode', None)
    session.pop('sub_question_path', None)
    session.pop('sub_selections', None)
    save_session(str(sender_id), session)
    
    response_text = '✅ Дефект зафиксирован!\n\nХотите прикрепить фото?'
    buttons = [
        [{'type': 'callback', 'text': '📸 Прикрепить фото', 'payload': 'add_photo'}],
        [{'type': 'callback', 'text': '⏭ Пропустить', 'payload': 'skip_photo'}],
        [{'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'}]
    ]
    send_message(sender_id, response_text, buttons)


def handle_checklist_answer(sender_id: str, session: dict, payload: str):
    '''Обработка ответа на вопрос чек-листа'''
    # Парсим payload: "answer:question_id:value"
    parts = payload.split(':')
    if len(parts) < 3:
        return
    
    question_id = int(parts[1])
    answer_value = parts[2]
    
    # Проверяем, есть ли у выбранного ответа подпункты
    questions = get_checklist_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    
    if question:
        selected_option = next((opt for opt in question['options'] if opt['value'] == answer_value), None)
        
        # Если у ответа есть подпункты - переходим в режим подвопросов
        if selected_option and 'subOptions' in selected_option:
            session['sub_question_mode'] = True
            session['sub_question_path'] = [answer_value]
            session['sub_selections'] = {}
            save_session(str(sender_id), session)
            send_checklist_question(sender_id, session)
            return
    
    # Если выбран "Иное (указать текстом)" - запрашиваем текст
    if answer_value == 'other':
        session['waiting_for_text'] = True
        session['waiting_for_text_question_id'] = question_id
        save_session(str(sender_id), session)
        response_text = '✏️ Укажите текстом:'
        send_message(sender_id, response_text)
        return
    
    # Сохраняем обычный ответ без подпунктов
    if answer_value != 'skip':
        success = save_checklist_answer(session['diagnostic_id'], question_id, answer_value)
        if not success:
            response_text = '⚠️ Ошибка при сохранении ответа. Попробуйте ещё раз.'
            send_message(sender_id, response_text)
            return
    
    if answer_value == 'bad':
        save_session(str(sender_id), session)
        response_text = '✅ Дефект зафиксирован!\n\nХотите прикрепить фото?'
        buttons = [
            [{'type': 'callback', 'text': '📸 Прикрепить фото', 'payload': 'add_photo'}],
            [{'type': 'callback', 'text': '⏭ Пропустить', 'payload': 'skip_photo'}],
            [{'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'}]
        ]
        send_message(sender_id, response_text, buttons)
        return
    
    # Проверяем логику пропуска вопросов при выборе "Не предусмотрено"
    skip_logic = {
        26: 28,  # Уровень масла ДВС (na) → пропускаем 27 (Состояние масла ДВС)
        28: 30,  # Уровень жидкости ГУР (na) → пропускаем 29 (Состояние жидкости ГУР)
        30: 34,  # Уровень охлаждающей жидкости ДВС (na) → пропускаем 31-33
        34: 38,  # Уровень охлаждающей жидкости HV (na) → пропускаем 35-37
        38: 42,  # Уровень охлаждающей жидкости турбины (na) → пропускаем 39-41
        45: 47,  # Уровень масла КПП (na или need_disassembly) → пропускаем 46 (Состояние масла КПП)
    }
    
    # Специальная обработка вопроса 55 (Иные замечания)
    if question_id == 55 and answer_value == 'add_notes':
        session['waiting_for_text'] = True
        session['waiting_for_text_question_id'] = question_id
        save_session(str(sender_id), session)
        response_text = '✏️ Укажите замечания текстом:'
        send_message(sender_id, response_text)
        return
    
    # Проверяем условия пропуска
    should_skip = False
    target_question_id = None
    
    if question_id in skip_logic and answer_value == 'na':
        should_skip = True
        target_question_id = skip_logic[question_id]
    
    # Вопрос 45: при выборе "Требуется разбор" тоже пропускаем вопрос 46
    if question_id == 45 and answer_value == 'need_disassembly':
        should_skip = True
        target_question_id = 47
    
    if should_skip and target_question_id:
        # Находим целевой вопрос
        questions = get_checklist_questions()
        target_index = next((i for i, q in enumerate(questions) if q['id'] == target_question_id), None)
        if target_index is not None:
            session['question_index'] = target_index
        else:
            session['question_index'] += 1
    else:
        # Переход к следующему вопросу
        session['question_index'] += 1
    
    save_session(str(sender_id), session)
    
    send_checklist_question(sender_id, session)


def handle_text_answer(sender_id: str, session: dict, user_text: str):
    '''Обработка текстового ответа на "Иное (указать текстом)"'''
    question_id = session.get('waiting_for_text_question_id')
    
    if not question_id:
        return
    
    # Сохраняем текстовый ответ
    success = save_checklist_answer(session['diagnostic_id'], question_id, f'Иное: {user_text}')
    
    if not success:
        response_text = '⚠️ Ошибка при сохранении ответа. Попробуйте ещё раз.'
        send_message(sender_id, response_text)
        return
    
    # Очищаем флаг ожидания текста
    session['waiting_for_text'] = False
    session.pop('waiting_for_text_question_id', None)
    
    # Переход к следующему вопросу
    session['question_index'] += 1
    save_session(str(sender_id), session)
    
    response_text = '✅ Ответ сохранён!'
    send_message(sender_id, response_text)
    
    send_checklist_question(sender_id, session)


def handle_photo_upload(sender_id: str, session: dict, attachments: list, caption: str = ''):
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
        photo_response = requests.get(photo_url, timeout=15)
        
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
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        photo_conn = db_pool.getconn()
        try:
            cur = photo_conn.cursor()
            cur.execute(
                f"INSERT INTO {schema}.diagnostic_photos (diagnostic_id, question_index, photo_url, caption) "
                f"VALUES (%s, %s, %s, %s)",
                (diagnostic_id, question_index, cdn_url, caption if caption else None)
            )
            photo_conn.commit()
            cur.close()
        finally:
            db_pool.putconn(photo_conn)
        
        session['waiting_for_photo'] = False
        
        # Переход к следующему вопросу
        session['question_index'] += 1
        save_session(str(sender_id), session)
        
        response_text = '✅ Фото дефекта сохранено!\n\nПродолжаем диагностику.'
        send_message(sender_id, response_text)
        
        send_checklist_question(sender_id, session)
        
    except Exception as e:
        print(f"[ERROR] Failed to upload photo: {str(e)}")
        response_text = '⚠️ Ошибка при загрузке фото. Попробуйте ещё раз или пропустите.'
        buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
        send_message(sender_id, response_text, buttons)


def handle_sub_answer(sender_id: str, session: dict, payload: str):
    '''Обработка ответа на подвопрос'''
    # Парсим payload: "sub_answer:question_id:value"
    parts = payload.split(':')
    if len(parts) < 3:
        return
    
    question_id = int(parts[1])
    sub_value = parts[2]
    
    questions = get_checklist_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    if not question:
        return
    
    # Получаем текущую выбранную опцию
    sub_path = session.get('sub_question_path', [])
    if not sub_path:
        return
    
    main_option = next((opt for opt in question['options'] if opt['value'] == sub_path[0]), None)
    if not main_option:
        return
    
    sub_selections = session.get('sub_selections', {})
    
    # Если allowMultiple - добавляем/убираем из списка (toggle)
    if main_option.get('allowMultiple'):
        if 'main' not in sub_selections:
            sub_selections['main'] = []
        
        # Toggle: если уже выбран - убираем, если нет - добавляем
        if sub_value in sub_selections['main']:
            sub_selections['main'].remove(sub_value)
            # Удаляем вложенные ответы для этого элемента
            sub_key = f'main-{sub_value}'
            sub_selections.pop(sub_key, None)
        else:
            sub_selections['main'].append(sub_value)
        
        session['sub_selections'] = sub_selections
        save_session(str(sender_id), session)
        
        # Обновляем список с галочками
        send_sub_question(sender_id, session)
    else:
        # Одиночный выбор
        sub_selections['main'] = sub_value
        session['sub_selections'] = sub_selections
        save_session(str(sender_id), session)
        
        # Проверяем вложенные subOptions
        sub_option = next((so for so in main_option['subOptions'] if so['value'] == sub_value), None)
        if sub_option and 'subOptions' in sub_option:
            send_nested_sub_question(sender_id, session, sub_option, sub_value)
        else:
            # Завершаем сбор подпунктов
            finish_sub_questions(sender_id, session)


def handle_sub_answer_done(sender_id: str, session: dict, payload: str):
    '''Обработка завершения выбора подпунктов'''
    sub_selections = session.get('sub_selections', {})
    selected = sub_selections.get('main', [])
    
    # Проверяем, есть ли хотя бы один выбор
    if not selected or len(selected) == 0:
        response_text = '⚠️ Выберите хотя бы один пункт или нажмите "Назад".'
        send_message(sender_id, response_text)
        return
    
    # Проверяем, нужны ли вложенные подпункты
    questions = get_checklist_questions()
    question_index = session.get('question_index', 0)
    question = questions[question_index]
    sub_path = session.get('sub_question_path', [])
    
    main_option = next((opt for opt in question['options'] if opt['value'] == sub_path[0]), None)
    if main_option:
        # Проверяем, есть ли у выбранных элементов свои subOptions
        for selected_value in selected:
            sub_key = f'main-{selected_value}'
            if sub_key not in sub_selections:
                # Нужно показать подпункты для этого элемента
                sub_option = next((so for so in main_option['subOptions'] if so['value'] == selected_value), None)
                if sub_option and 'subOptions' in sub_option:
                    send_nested_sub_question(sender_id, session, sub_option, selected_value)
                    return
    
    # Все подпункты собраны - завершаем
    finish_sub_questions(sender_id, session)


def handle_nested_sub_answer(sender_id: str, session: dict, payload: str):
    '''Обработка вложенного ответа 3-го уровня'''
    # Парсим payload: "nested_sub_answer:question_id:parent_value:nested_value"
    parts = payload.split(':')
    if len(parts) < 4:
        return
    
    question_id = int(parts[1])
    parent_value = parts[2]
    nested_value = parts[3]
    
    sub_selections = session.get('sub_selections', {})
    
    # Сохраняем вложенный ответ с ключом вида "main-parent_value"
    sub_key = f'main-{parent_value}'
    sub_selections[sub_key] = nested_value
    
    session['sub_selections'] = sub_selections
    save_session(str(sender_id), session)
    
    # Проверяем, нужно ли показать подпункты для других выбранных элементов
    questions = get_checklist_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    if not question:
        finish_sub_questions(sender_id, session)
        return
    
    sub_path = session.get('sub_question_path', [])
    main_option = next((opt for opt in question['options'] if opt['value'] == sub_path[0]), None)
    
    if main_option and main_option.get('allowMultiple'):
        # Проверяем остальные выбранные элементы
        selected_items = sub_selections.get('main', [])
        
        for selected_value in selected_items:
            sub_key = f'main-{selected_value}'
            if sub_key not in sub_selections:
                # Нужно показать подпункты для этого элемента
                sub_option = next((so for so in main_option['subOptions'] if so['value'] == selected_value), None)
                if sub_option and 'subOptions' in sub_option:
                    send_nested_sub_question(sender_id, session, sub_option, selected_value)
                    return
        
        # Все вложенные подпункты собраны - завершаем сбор
        finish_sub_questions(sender_id, session)
        return
    
    # Одиночный выбор - завершаем
    finish_sub_questions(sender_id, session)


def save_checklist_answer(diagnostic_id: int, question_number: int, answer_value: str) -> bool:
    '''Сохранение ответа на вопрос чек-листа в БД (без подпунктов)'''
    return save_checklist_answer_with_subs(diagnostic_id, question_number, answer_value, None)


def save_checklist_answer_with_subs(diagnostic_id: int, question_number: int, answer_value: str, sub_answers: dict) -> bool:
    '''Сохранение ответа на вопрос чек-листа в БД с подпунктами'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
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
        elif answer_value == 'add_notes':
            answer_val = 'Добавить замечания'
        elif answer_value == 'need_disassembly':
            answer_val = 'Требуется дополнительный разбор'
        else:
            # Найдем label в опциях
            option = next((opt for opt in question['options'] if opt['value'] == answer_value), None)
            answer_val = option['label'] if option else answer_value
        
        # Формируем SQL с sub_answers
        if sub_answers:
            sub_answers_json = json.dumps(sub_answers, ensure_ascii=False)
            cur.execute(
                f"INSERT INTO {schema}.checklist_answers (diagnostic_id, question_number, question_text, answer_type, answer_value, sub_answers) "
                f"VALUES (%s, %s, %s, 'single', %s, %s::jsonb)",
                (diagnostic_id, question_number, question_text, answer_val, sub_answers_json)
            )
        else:
            cur.execute(
                f"INSERT INTO {schema}.checklist_answers (diagnostic_id, question_number, question_text, answer_type, answer_value) "
                f"VALUES (%s, %s, %s, 'single', %s)",
                (diagnostic_id, question_number, question_text, answer_val)
            )
        
        conn.commit()
        cur.close()
        
        print(f"[SUCCESS] Saved answer for question {question_number}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save checklist answer: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False
    finally:
        if conn:
            get_db_pool().putconn(conn)


def finish_checklist(sender_id: str, session: dict):
    '''Завершение чек-листа и генерация отчета'''
    diagnostic_id = session.get('diagnostic_id')
    report_url_base = "https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6"
    
    mark_diagnostic_completed(diagnostic_id)
    
    conn = None
    try:
        # Проверяем наличие фото в БД
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT COUNT(*) FROM {schema}.diagnostic_photos WHERE diagnostic_id = %s",
            (diagnostic_id,)
        )
        photo_count = cur.fetchone()[0]
        cur.close()
        
        has_photos = photo_count > 0
        
        # Генерируем отчёт без фото (всегда)
        response_no_photos = requests.get(f"{report_url_base}?id={diagnostic_id}", timeout=45)
        pdf_url_no_photos = None
        if response_no_photos.status_code == 200:
            result = response_no_photos.json()
            pdf_url_no_photos = result.get('pdfUrl')
        
        # Генерируем отчёт с фото только если есть фото
        pdf_url_with_photos = None
        if has_photos:
            response_with_photos = requests.get(f"{report_url_base}?id={diagnostic_id}&with_photos=true", timeout=45)
            if response_with_photos.status_code == 200:
                result = response_with_photos.json()
                pdf_url_with_photos = result.get('pdfUrl')
        
        # Формируем ответ
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
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        response_text = f'''✅ Диагностика №{diagnostic_id} завершена!

📋 Чек-лист сохранен.'''
    finally:
        if conn:
            get_db_pool().putconn(conn)
    
    buttons = [[{'type': 'callback', 'text': 'Начать новую диагностику', 'payload': 'start'}]]
    send_message(sender_id, response_text, buttons)
    
    session_data = {
        'step': 0,
        'mechanic': session.get('mechanic'),
        'mechanic_id': session.get('mechanic_id'),
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'phone': session.get('phone'),
    }
    save_session(str(sender_id), session_data)


def send_priemka_question(sender_id: str, session: dict):
    '''Отправляет текущий вопрос Приемки'''
    questions = get_priemka_questions()
    question_index = session.get('question_index', 0)

    if question_index >= len(questions):
        finish_priemka(sender_id, session)
        return

    question = questions[question_index]

    prev_question = questions[question_index - 1] if question_index > 0 else None
    if prev_question and prev_question['id'] == 19 and not session.get('mileage'):
        session['step'] = 7
        session['waiting_for_photo'] = False
        session['waiting_for_text'] = False
        save_session(str(sender_id), session)
        response_text = '🛣 Введите пробег автомобиля (в км).\n\nНапример: 150000'
        buttons = [[{'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'}]]
        send_message(sender_id, response_text, buttons)
        return

    if question['id'] == 10 and session.get('skip_rear_right_door'):
        save_priemka_answer(session.get('diagnostic_id'), 10, question['title'], 'Не предусмотрено', None)
        session['question_index'] += 1
        save_session(str(sender_id), session)
        send_priemka_question(sender_id, session)
        return
    total = len(questions)
    q_type = question.get('type', 'photo')

    progress_text = f'📋 Приемка — шаг {question_index + 1} из {total}\n\n{question["title"]}'

    if q_type == 'photo':
        session['waiting_for_photo'] = True
        save_session(str(sender_id), session)
        response_text = f'{progress_text}\n\n📸 Прикрепите фото.'
        nav_buttons = []
        if question_index > 0:
            nav_buttons.append({'type': 'callback', 'text': '⬅️ Назад', 'payload': 'priemka_back'})
        nav_buttons.append({'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'})
        send_message(sender_id, response_text, [nav_buttons])

    elif q_type == 'choice':
        session['waiting_for_photo'] = question.get('allow_photo', False)
        save_session(str(sender_id), session)
        buttons = []
        if question.get('allow_photo'):
            response_text = f'{progress_text}\n\n📸 Прикрепите фото или выберите вариант:'
        else:
            response_text = progress_text
        for opt in question.get('options', []):
            buttons.append([{
                'type': 'callback',
                'text': opt['label'],
                'payload': f"priemka_answer:{question['id']}:{opt['value']}"
            }])
        nav_buttons = []
        if question_index > 0:
            nav_buttons.append({'type': 'callback', 'text': '⬅️ Назад', 'payload': 'priemka_back'})
        nav_buttons.append({'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'})
        buttons.append(nav_buttons)
        send_message(sender_id, response_text, buttons)

    elif q_type == 'text_choice':
        session['waiting_for_photo'] = False
        session['waiting_for_text'] = False
        save_session(str(sender_id), session)
        buttons = []
        for opt in question.get('options', []):
            buttons.append([{
                'type': 'callback',
                'text': opt['label'],
                'payload': f"priemka_answer:{question['id']}:{opt['value']}"
            }])
        nav_buttons = []
        if question_index > 0:
            nav_buttons.append({'type': 'callback', 'text': '⬅️ Назад', 'payload': 'priemka_back'})
        nav_buttons.append({'type': 'callback', 'text': '❌ Отменить', 'payload': 'cancel_diagnostic'})
        buttons.append(nav_buttons)
        send_message(sender_id, progress_text, buttons)


def handle_priemka_photo(sender_id: str, session: dict, attachments: list, caption: str = ''):
    '''Обработка фото в режиме Приемки'''
    try:
        photo_url = None
        for attachment in attachments:
            if attachment.get('type') == 'image':
                payload = attachment.get('payload', {})
                photo_url = payload.get('url')
                break

        if not photo_url:
            response_text = '⚠️ Не найдено фото. Попробуйте ещё раз.'
            buttons = [[{'type': 'callback', 'text': '⬅️ Назад', 'payload': 'priemka_back'}]]
            send_message(sender_id, response_text, buttons)
            return

        photo_response = requests.get(photo_url, timeout=15)
        if photo_response.status_code != 200:
            response_text = '⚠️ Не удалось загрузить фото. Попробуйте ещё раз.'
            send_message(sender_id, response_text)
            return

        diagnostic_id = session.get('diagnostic_id')
        question_index = session.get('question_index', 0)
        questions = get_priemka_questions()
        question = questions[question_index] if question_index < len(questions) else None

        krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
        now = datetime.now(krasnoyarsk_tz)
        file_key = f"diagnostics/{diagnostic_id}/priemka_q{question_index + 1}_{now.strftime('%Y%m%d_%H%M%S')}.jpg"

        s3 = boto3.client('s3',
            endpoint_url='https://bucket.poehali.dev',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        s3.put_object(Bucket='files', Key=file_key, Body=photo_response.content, ContentType='image/jpeg')
        cdn_url = f"https://cdn.poehali.dev/projects/{os.environ['AWS_ACCESS_KEY_ID']}/bucket/{file_key}"

        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        photo_conn = db_pool.getconn()
        try:
            cur = photo_conn.cursor()
            cur.execute(
                f"INSERT INTO {schema}.diagnostic_photos (diagnostic_id, question_index, photo_url, caption) "
                f"VALUES (%s, %s, %s, %s)",
                (diagnostic_id, question_index, cdn_url, caption if caption else None)
            )
            photo_conn.commit()
            cur.close()
        finally:
            db_pool.putconn(photo_conn)

        answer_text = f'Фото прикреплено. Комментарий: {caption}' if caption else 'Фото прикреплено'
        if question:
            save_priemka_answer(diagnostic_id, question['id'], question['title'], answer_text, cdn_url)

        session['waiting_for_photo'] = False

        extra_count = session.get('priemka_extra_photos', 0) + 1
        session['priemka_extra_photos'] = extra_count
        session['waiting_for_photo'] = True
        save_session(str(sender_id), session)

        payload_action = 'no_extra' if question and question['id'] == 21 else 'next_step'
        response_text = f'✅ Фото сохранено! (фото: {extra_count})\n\nМожете прикрепить ещё фото или нажмите "Далее".'
        buttons = [
            [{'type': 'callback', 'text': '➡️ Далее', 'payload': f"priemka_answer:{question['id']}:{payload_action}"}]
        ]
        if question_index > 0:
            buttons.append([{'type': 'callback', 'text': '⬅️ Назад', 'payload': 'priemka_back'}])
        send_message(sender_id, response_text, buttons)

    except Exception as e:
        print(f"[ERROR] Priemka photo upload failed: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        response_text = '⚠️ Ошибка при загрузке фото. Попробуйте ещё раз.'
        send_message(sender_id, response_text)


def handle_priemka_callback(sender_id: str, session: dict, payload: str):
    '''Обработка нажатий кнопок в Приемке'''
    parts = payload.split(':')
    if len(parts) < 3:
        return

    question_id = int(parts[1])
    answer_value = parts[2]

    questions = get_priemka_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    if not question:
        return

    diagnostic_id = session.get('diagnostic_id')

    if answer_value == 'add_notes':
        session['waiting_for_text'] = True
        session['waiting_for_text_question_id'] = question_id
        save_session(str(sender_id), session)
        response_text = '✏️ Введите замечания текстом:'
        send_message(sender_id, response_text)
        return

    if answer_value == 'complete':
        save_priemka_answer(diagnostic_id, question_id, question['title'], 'Замечаний нет', None)
        session['question_index'] += 1
        session['waiting_for_photo'] = False
        session['waiting_for_text'] = False
        save_session(str(sender_id), session)
        send_priemka_question(sender_id, session)
        return

    if answer_value == 'next_step':
        session['question_index'] += 1
        session['waiting_for_photo'] = False
        session['priemka_extra_photos'] = 0
        save_session(str(sender_id), session)
        send_priemka_question(sender_id, session)
        return

    if answer_value == 'not_applicable':
        save_priemka_answer(diagnostic_id, question_id, question['title'], 'Не предусмотрено', None)
        if question_id == 6:
            session['skip_rear_right_door'] = True
        session['question_index'] += 1
        session['waiting_for_photo'] = False
        session['priemka_extra_photos'] = 0
        save_session(str(sender_id), session)
        send_priemka_question(sender_id, session)
        return

    if answer_value == 'no_extra':
        session['question_index'] += 1
        session['waiting_for_photo'] = False
        session['priemka_extra_photos'] = 0
        save_session(str(sender_id), session)
        send_priemka_question(sender_id, session)
        return

    opt_label = next((o['label'] for o in question.get('options', []) if o['value'] == answer_value), answer_value)
    save_priemka_answer(diagnostic_id, question_id, question['title'], opt_label, None)
    session['question_index'] += 1
    session['waiting_for_photo'] = False
    save_session(str(sender_id), session)
    send_priemka_question(sender_id, session)


def handle_priemka_text(sender_id: str, session: dict, user_text: str):
    '''Обработка текстового замечания в Приемке'''
    question_id = session.get('waiting_for_text_question_id')
    diagnostic_id = session.get('diagnostic_id')

    if not question_id or not diagnostic_id:
        return

    questions = get_priemka_questions()
    question = next((q for q in questions if q['id'] == question_id), None)
    if not question:
        return

    save_priemka_answer(diagnostic_id, question_id, question['title'], f'Замечания: {user_text}', None)

    session['waiting_for_text'] = False
    session.pop('waiting_for_text_question_id', None)
    session['question_index'] += 1
    save_session(str(sender_id), session)

    response_text = '✅ Замечание сохранено!'
    send_message(sender_id, response_text)
    send_priemka_question(sender_id, session)


def handle_priemka_back(sender_id: str, session: dict):
    '''Возврат к предыдущему шагу Приемки'''
    question_index = session.get('question_index', 0)

    if question_index > 0:
        diagnostic_id = session.get('diagnostic_id')
        prev_index = question_index - 1
        questions = get_priemka_questions()
        prev_question = questions[prev_index] if prev_index < len(questions) else None

        if prev_question and prev_question['id'] == 10 and session.get('skip_rear_right_door'):
            delete_priemka_answer(diagnostic_id, prev_question['id'])
            prev_index -= 1
            prev_question = questions[prev_index] if prev_index >= 0 and prev_index < len(questions) else None

        if prev_question and diagnostic_id:
            delete_priemka_answer(diagnostic_id, prev_question['id'])

        session['question_index'] = prev_index
        session['waiting_for_photo'] = False
        session['waiting_for_text'] = False
        session['priemka_extra_photos'] = 0
        save_session(str(sender_id), session)

    send_priemka_question(sender_id, session)


def save_priemka_answer(diagnostic_id: int, question_number: int, question_text: str, answer_value: str, photo_url: str):
    '''Сохраняет ответ Приемки в checklist_answers'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()

        if photo_url:
            cur.execute(
                f"INSERT INTO {schema}.checklist_answers (diagnostic_id, question_number, question_text, answer_type, answer_value, photo_urls) "
                f"VALUES (%s, %s, %s, 'priemka', %s, ARRAY[%s])",
                (diagnostic_id, question_number, question_text, answer_value, photo_url)
            )
        else:
            cur.execute(
                f"INSERT INTO {schema}.checklist_answers (diagnostic_id, question_number, question_text, answer_type, answer_value) "
                f"VALUES (%s, %s, %s, 'priemka', %s)",
                (diagnostic_id, question_number, question_text, answer_value)
            )

        conn.commit()
        cur.close()
        print(f"[SUCCESS] Saved priemka answer for question {question_number}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save priemka answer: {str(e)}")
        return False
    finally:
        if conn:
            get_db_pool().putconn(conn)


def delete_priemka_answer(diagnostic_id: int, question_number: int):
    '''Удаляет ответ Приемки при возврате назад'''
    conn = None
    try:
        schema = os.environ.get('MAIN_DB_SCHEMA')
        db_pool = get_db_pool()
        conn = db_pool.getconn()
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM {schema}.checklist_answers WHERE diagnostic_id = %s AND question_number = %s",
            (diagnostic_id, question_number)
        )
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"[ERROR] Failed to delete priemka answer: {str(e)}")
    finally:
        if conn:
            get_db_pool().putconn(conn)


def finish_priemka(sender_id: str, session: dict):
    '''Завершение Приемки и генерация отчёта'''
    diagnostic_id = session.get('diagnostic_id')
    report_url_base = "https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6"

    mark_diagnostic_completed(diagnostic_id)

    mechanic = session.get('mechanic', '—')
    car_number = session.get('car_number', '—')
    mileage = session.get('mileage', 0)
    mileage_str = f'{mileage:,}'.replace(',', ' ')

    summary = f'''📋 Сводка:
━━━━━━━━━━━━━━━━
👤 Механик: {mechanic}
🚗 Госномер: {car_number}
🛣 Пробег: {mileage_str} км
🔧 Тип: Приемка
━━━━━━━━━━━━━━━━'''

    response_text = f'✅ Приемка №{diagnostic_id} завершена!\n\n{summary}'

    try:
        response_with_photos = requests.get(f"{report_url_base}?id={diagnostic_id}&with_photos=true", timeout=60)
        pdf_url = None
        if response_with_photos.status_code == 200:
            result = response_with_photos.json()
            pdf_url = result.get('pdfUrl')

        if pdf_url:
            response_text = f'✅ Приемка №{diagnostic_id} завершена!\n\n{summary}\n\n📄 Отчёт готов!\n{pdf_url}'
        else:
            response_text = f'✅ Приемка №{diagnostic_id} завершена!\n\n{summary}\n\n📋 Данные сохранены, отчет временно недоступен.'
    except Exception as e:
        print(f"[ERROR] Failed to generate priemka report: {str(e)}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        response_text = f'✅ Приемка №{diagnostic_id} завершена!\n\n{summary}\n\n📋 Данные сохранены, отчет временно недоступен.'

    buttons = [[{'type': 'callback', 'text': 'Начать новую диагностику', 'payload': 'start'}]]
    send_message(sender_id, response_text, buttons)

    session_data = {
        'step': 0,
        'mechanic': session.get('mechanic'),
        'mechanic_id': session.get('mechanic_id'),
        'user_id': session.get('user_id'),
        'user_name': session.get('user_name'),
        'phone': session.get('phone'),
    }
    save_session(str(sender_id), session_data)


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
    
    response = requests.post(url, json=payload, headers=headers, timeout=10)
    
    print(f"[DEBUG] Response status: {response.status_code}")
    print(f"[DEBUG] Response body: {response.text}")
    
    try:
        return response.json()
    except:
        return {}