import json
import os
import requests
import psycopg2
import boto3
import base64
from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO
from checklist_data import get_checklist_questions_full


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
            handle_photo_upload(sender_id, session, attachments)
        else:
            response_text = '⚠️ Пожалуйста, прикрепите фото дефекта или нажмите "Пропустить фото".'
            buttons = [[{'type': 'callback', 'text': '⏭ Пропустить фото', 'payload': 'skip_photo'}]]
            send_message(sender_id, response_text, buttons)
        return
    
    lower_text = user_text.lower()
    
    # Команды
    if lower_text in ['/start', 'начать', 'старт']:
        # Проверяем, авторизован ли пользователь (проверка mechanic_id вместо user_id)
        if session.get('mechanic_id'):
            # Уже авторизован - сразу начинаем диагностику с госномера
            session['step'] = 2
            save_session(str(sender_id), session)
            response_text = f'👋 С возвращением, {session.get("mechanic", "")}!\n\nВведите госномер автомобиля.\n\nНапример: A159BK124'
            send_message(sender_id, response_text)
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
        # Проверяем, авторизован ли пользователь (проверка mechanic_id)
        if session.get('mechanic_id'):
            # Уже авторизован - сразу начинаем диагностику с госномера
            session['step'] = 2
            save_session(str(sender_id), session)
            response_text = f'👋 Отлично! Введите госномер автомобиля.\n\nНапример: A159BK124'
            send_message(sender_id, response_text)
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
        save_session(str(sender_id), session)
        
        # Если выбрана "5-ти минутка" - начинаем чек-лист
        if diagnostic_type == '5min':
            # Сохраняем диагностику в БД
            diagnostic_id = save_diagnostic(session)
            if diagnostic_id:
                # Очищаем данные предыдущей диагностики
                session.pop('sub_question_mode', None)
                session.pop('sub_question_path', None)
                session.pop('sub_selections', None)
                session.pop('waiting_for_photo', None)
                
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
            try:
                db_url = os.environ.get('DATABASE_URL')
                schema = os.environ.get('MAIN_DB_SCHEMA')
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                
                # Находим последний отвеченный вопрос
                cur.execute(
                    f"SELECT question_number FROM {schema}.checklist_answers "
                    f"WHERE diagnostic_id = {diagnostic_id} "
                    f"ORDER BY question_number DESC LIMIT 1"
                )
                last_answer = cur.fetchone()
                
                if last_answer:
                    prev_question_number = last_answer[0]
                    
                    # Удаляем этот ответ
                    cur.execute(
                        f"DELETE FROM {schema}.checklist_answers "
                        f"WHERE diagnostic_id = {diagnostic_id} AND question_number = {prev_question_number}"
                    )
                    conn.commit()
                    
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
                conn.close()
            except Exception as e:
                print(f"[ERROR] Failed to go back: {str(e)}")
        else:
            # Если нет diagnostic_id - просто вернуться назад
            question_index = session.get('question_index', 0)
            if question_index > 0:
                session['question_index'] = question_index - 1
                save_session(str(sender_id), session)
                send_checklist_question(sender_id, session)


def handle_phone_auth(sender_id: str, session: dict, contact_attachment: dict):
    '''Обработка авторизации по номеру телефона'''
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
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT id, name, is_active FROM {schema}.mechanics WHERE phone = '{clean_phone}'"
        )
        mechanic = cur.fetchone()
        
        cur.close()
        conn.close()
        
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
        
        response_text = f'✅ Добро пожаловать, {mechanic_name}!\n\nВведите госномер автомобиля.\n\nНапример: A159BK124'
        send_message(sender_id, response_text)
        
    except Exception as e:
        print(f"[ERROR] Phone auth failed: {str(e)}")
        response_text = '⚠️ Ошибка авторизации. Попробуйте ещё раз или обратитесь к администратору.'
        buttons = [[{'type': 'request_contact', 'text': '📱 Отправить номер телефона'}]]
        send_message(sender_id, response_text, buttons)


def save_diagnostic(session: dict) -> int:
    '''Сохранение диагностики в PostgreSQL'''
    try:
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        
        conn = psycopg2.connect(db_url)
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
        conn.close()
        
        return result[0] if result else None
    
    except Exception as e:
        return None


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
    
    # Кнопка "Назад" (если это не первый вопрос)
    if question_index > 0:
        buttons.append([{'type': 'callback', 'text': '⬅️ Назад', 'payload': 'previous_question'}])
    
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
    
    # Кнопка «Назад»
    buttons.append([{
        'type': 'callback',
        'text': '⬅️ Назад',
        'payload': 'cancel_sub_question'
    }])
    
    # Отправляем сообщение (MAX API не поддерживает редактирование inline-клавиатур)
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
    
    # Кнопка «Назад» к выбору подпунктов — передаём parent_value для удаления
    buttons.append([{
        'type': 'callback',
        'text': '⬅️ Назад',
        'payload': f'back_to_sub_list:{parent_value}'
    }])
    
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
    
    # Предлагаем прикрепить фото дефекта
    response_text = '✅ Дефект зафиксирован!\n\nХотите прикрепить фото?'
    buttons = [
        [{'type': 'callback', 'text': '📸 Прикрепить фото', 'payload': 'add_photo'}],
        [{'type': 'callback', 'text': '⏭ Пропустить', 'payload': 'skip_photo'}]
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
    
    # Если выбран "Неисправно" без подпунктов - предлагаем фото
    if answer_value == 'bad':
        save_session(str(sender_id), session)
        response_text = '✅ Дефект зафиксирован!\n\nХотите прикрепить фото?'
        buttons = [
            [{'type': 'callback', 'text': '📸 Прикрепить фото', 'payload': 'add_photo'}],
            [{'type': 'callback', 'text': '⏭ Пропустить', 'payload': 'skip_photo'}]
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
        
        # Формируем SQL с sub_answers
        if sub_answers:
            sub_answers_json = json.dumps(sub_answers, ensure_ascii=False).replace("'", "''")
            cur.execute(
                f"INSERT INTO {schema}.checklist_answers (diagnostic_id, question_number, question_text, answer_type, answer_value, sub_answers) "
                f"VALUES ({diagnostic_id}, {question_number}, '{question_text}', 'single', '{answer_val}', '{sub_answers_json}'::jsonb)"
            )
        else:
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
    
    report_url_base = "https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6"
    
    try:
        # Проверяем наличие фото в БД
        db_url = os.environ.get('DATABASE_URL')
        schema = os.environ.get('MAIN_DB_SCHEMA')
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            f"SELECT COUNT(*) FROM {schema}.diagnostic_photos WHERE diagnostic_id = {diagnostic_id}"
        )
        photo_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        has_photos = photo_count > 0
        
        # Генерируем отчёт без фото (всегда)
        response_no_photos = requests.get(f"{report_url_base}?id={diagnostic_id}", timeout=30)
        pdf_url_no_photos = None
        if response_no_photos.status_code == 200:
            result = response_no_photos.json()
            pdf_url_no_photos = result.get('pdfUrl')
        
        # Генерируем отчёт с фото только если есть фото
        pdf_url_with_photos = None
        if has_photos:
            response_with_photos = requests.get(f"{report_url_base}?id={diagnostic_id}&with_photos=true", timeout=30)
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
    
    try:
        return response.json()
    except:
        return {}