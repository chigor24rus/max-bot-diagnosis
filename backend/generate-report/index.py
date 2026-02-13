import json
import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate, BaseDocTemplate, NextPageTemplate
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import boto3
from io import BytesIO
import urllib.request

def handler(event: dict, context) -> dict:
    '''API для генерации PDF отчёта по диагностике автомобиля'''
    
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
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
    
    if method != 'GET':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Метод не поддерживается'}),
            'isBase64Encoded': False
        }
    
    query_params = event.get('queryStringParameters', {}) or {}
    diagnostic_id = query_params.get('id')
    with_photos = query_params.get('with_photos', 'false').lower() == 'true'
    
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
    
    db_url = os.environ.get('DATABASE_URL')
    schema = os.environ.get('MAIN_DB_SCHEMA')
    
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
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
        
        diagnostic_data = {
            'id': row[0],
            'mechanic': row[1],
            'carNumber': row[2],
            'mileage': row[3],
            'diagnosticType': row[4],
            'createdAt': row[5]
        }
        
        cur.execute(
            f"SELECT question_number, question_text, answer_value, sub_answers FROM {schema}.checklist_answers "
            f"WHERE diagnostic_id = {diagnostic_id} ORDER BY question_number"
        )
        checklist_rows = cur.fetchall()
        
        photos_by_question = {}
        if with_photos:
            cur.execute(
                f"SELECT question_index, photo_url FROM {schema}.diagnostic_photos "
                f"WHERE diagnostic_id = {diagnostic_id} ORDER BY question_index, created_at"
            )
            photo_rows = cur.fetchall()
            for question_idx, photo_url in photo_rows:
                if question_idx not in photos_by_question:
                    photos_by_question[question_idx] = []
                photos_by_question[question_idx].append(photo_url)
        
        defect_labels = {
            'chips': 'Сколы',
            'cracks': 'Трещины',
            'discharged': 'Разряжена',
            'missing': 'Отсутствует',
            'damaged': 'Повреждена',
            'smearing': 'Мажет',
            'worn': 'Изношена',
            'cracked': 'Треснута',
            'left': 'Слева',
            'right': 'Справа',
            'center': 'По центру',
            'front-left': 'Передняя левая',
            'front-right': 'Передняя правая',
            'rear-left': 'Задняя левая',
            'rear-right': 'Задняя правая',
            'srs': 'SRS',
            'abs': 'ABS',
            'akb': 'АКБ',
            'check_engine': 'Check Engine',
            'hybrid': 'Hybrid System / IMA',
            'engine': 'Двигатель',
            'battery': 'АКБ',
            'oil': 'Масло',
            'brake': 'Тормоза',
            'right_mirror': 'Правое зеркало',
            'left_mirror': 'Левое зеркало',
            'right_main': 'Справа основной',
            'left_main': 'Слева основной',
            'right_wing': 'Справа крыло',
            'left_wing': 'Слева крыло',
            'pressure': 'Давление',
            'bulges_cuts': 'Грыжи/порезы',
            'valve_cracks': 'Вентиль трещины',
            'missing_nut': 'Отсутствует гайка колеса',
            'tread': 'Протектор',
            'timing_belt': 'Ремень ГРМ',
            'alternator_belt': 'Ремень генератора',
            'power_steering_belt': 'Ремень ГУР',
            'ac_belt': 'Ремень кондиционера',
            'pump_belt': 'Ремень помпы',
            'peeling': 'Отслоения',
            'below': 'Ниже уровня',
            '0-25': '0-25%',
            '25-50': '25-50%',
            '50-75': '50-75%',
            '75-100': '75-100%',
            'above': 'Выше уровня',
            'fresh': 'Свежее',
            'working': 'Рабочее',
            'particles': 'С механическими примесями',
            'water': 'Примеси воды / антифриза',
            'burnt': 'Горелое',
            'level': 'Уровень',
            'red': 'Красный',
            'green': 'Зеленый',
            'blue': 'Синий',
            'yellow': 'Желтый',
            'clear': 'Бесцветный',
            'clean': 'Чистая',
            'cloudy': 'Мутная',
            'less_25': 'Менее -25°С',
            '25_35': '-25 - 35°С',
            '35_45': '-35 - 45°С',
            'more_45': 'Более -45°С',
            'less_180': 'Менее 180°С',
            'more_180': 'Более 180°С',
            'need_disassembly': 'Требуется дополнительный разбор',
            'present': 'Присутствует',
            'frozen': 'Замерзла',
            'noise': 'Посторонний шум',
            'long_start': 'Длительный запуск',
            'jamming': 'Заклинивание',
            'uneven': 'Неровная работа',
            'jolts': 'Пинки / Толчки',
            'valve_cover': 'Течь клапанной крышки',
            'turbo': 'Течь турбокомпрессора',
            'oil_cooler': 'Течь охладителя масла',
            'brake_fluid': 'Течь тормозной жидкости',
            'coolant': 'Течь антифриза',
            'dirty': 'Загрязнен',
            'moisture': 'Попадание влаги',
        }
        
        def parse_defects(sub_answers):
            if not sub_answers:
                return []
            
            defects = []
            main = sub_answers.get('main')
            
            if isinstance(main, str):
                defects.append(defect_labels.get(main, main))
            elif isinstance(main, list):
                for item in main:
                    sub_key = f'main-{item}'
                    if sub_key in sub_answers:
                        sub_value = sub_answers[sub_key]
                        location = defect_labels.get(item, item)
                        problem = defect_labels.get(sub_value, sub_value)
                        defects.append(f'{location}: {problem}')
                    else:
                        defects.append(defect_labels.get(item, item))
            
            return defects
        
        working_items = []
        broken_items = []
        
        for question_num, question, answer, sub_answers in checklist_rows:
            if answer == 'Исправно':
                working_items.append(question)
            elif answer == 'Неисправно':
                defect_details = parse_defects(sub_answers)
                if defect_details:
                    broken_items.append((question_num, f'{question}: {", ".join(defect_details)}'))
                else:
                    broken_items.append((question_num, question))
        
        font_path = '/tmp/DejaVuSans.ttf'
        
        if not os.path.exists(font_path):
            font_url = 'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf'
            urllib.request.urlretrieve(font_url, font_path)
        
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        font_name = 'DejaVu'
        
        first_page_bg_path = '/tmp/hevsr_first_page.png'
        if not os.path.exists(first_page_bg_path):
            first_page_url = 'https://cdn.poehali.dev/projects/4bb6cea8-8d41-426a-b677-f4304502c188/bucket/1b9feaf1-b2e2-44e2-9d52-53bb62a5a421.png'
            urllib.request.urlretrieve(first_page_url, first_page_bg_path)
        
        other_pages_bg_path = '/tmp/hevsr_background.png'
        if not os.path.exists(other_pages_bg_path):
            other_pages_url = 'https://cdn.poehali.dev/projects/4bb6cea8-8d41-426a-b677-f4304502c188/bucket/e0986711-d405-44d1-a66b-83e4a1ba096d.png'
            urllib.request.urlretrieve(other_pages_url, other_pages_bg_path)
        
        pdf_buffer = BytesIO()
        
        page_width, page_height = A4
        
        krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
        created_at_local = diagnostic_data['createdAt'].astimezone(krasnoyarsk_tz)
        footer_date = created_at_local.strftime('%d.%m.%Y')
        footer_time = created_at_local.strftime('%H:%M')
        
        def add_first_page_background(canvas, doc):
            canvas.saveState()
            canvas.drawImage(first_page_bg_path, 0, 0, 
                           width=page_width, height=page_height, preserveAspectRatio=False, mask='auto')
            
            canvas.setFont(font_name, 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            
            footer_text = f"Отчет по осмотру автомобиля гос.номер: {diagnostic_data['carNumber']}, пробег: {diagnostic_data['mileage']} км, {footer_date}, {footer_time}"
            canvas.drawString(20*mm, 10*mm, footer_text)
            
            page_number = f"Стр. {doc.page}"
            canvas.drawRightString(page_width - 20*mm, 10*mm, page_number)
            
            canvas.restoreState()
        
        def add_other_pages_background(canvas, doc):
            canvas.saveState()
            canvas.drawImage(other_pages_bg_path, 0, 0, 
                           width=page_width, height=page_height, preserveAspectRatio=False, mask='auto')
            
            canvas.setFont(font_name, 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            
            footer_text = f"Отчет по осмотру автомобиля гос.номер: {diagnostic_data['carNumber']}, пробег: {diagnostic_data['mileage']} км, {footer_date}, {footer_time}"
            canvas.drawString(20*mm, 10*mm, footer_text)
            
            page_number = f"Стр. {doc.page}"
            canvas.drawRightString(page_width - 20*mm, 10*mm, page_number)
            
            canvas.restoreState()
        
        doc = BaseDocTemplate(pdf_buffer, pagesize=A4)
        
        first_page_frame = Frame(20*mm, 15*mm, page_width - 40*mm, page_height - 30*mm, 
                                id='first', topPadding=70*mm)
        other_pages_frame = Frame(20*mm, 15*mm, page_width - 40*mm, page_height - 30*mm, 
                                 id='normal', topPadding=50*mm)
        
        first_template = PageTemplate(id='first_page', frames=[first_page_frame], onPage=add_first_page_background)
        other_template = PageTemplate(id='other_pages', frames=[other_pages_frame], onPage=add_other_pages_background)
        doc.addPageTemplates([first_template, other_template])
        
        story = []
        styles = getSampleStyleSheet()
        
        story.append(Spacer(1, 5*mm))
        
        title_style = ParagraphStyle(
            'Title',
            fontName=font_name,
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.HexColor('#1E5BA8'),
            fontWeight='bold'
        )
        
        report_title = 'Акт приемки автомобиля' if diagnostic_data.get('diagnosticType') == 'priemka' else 'Отчет по осмотру автомобиля'
        story.append(Paragraph(report_title, title_style))
        story.append(Spacer(1, 8*mm))
        
        info_style = ParagraphStyle(
            'Info',
            fontName=font_name,
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=4,
            textColor=colors.black
        )
        
        story.append(Paragraph(f'<b>Дата:</b> {created_at_local.strftime("%d.%m.%Y %H:%M")}', info_style))
        story.append(Paragraph(f'<b>Механик:</b> {diagnostic_data["mechanic"]}', info_style))
        story.append(Paragraph(f'<b>Гос.номер:</b> {diagnostic_data["carNumber"]}', info_style))
        story.append(Paragraph(f'<b>Пробег:</b> {diagnostic_data["mileage"]:,} км'.replace(',', ' '), info_style))
        story.append(Spacer(1, 8*mm))
        
        section_style = ParagraphStyle(
            'Section',
            fontName=font_name,
            fontSize=14,
            alignment=TA_LEFT,
            spaceAfter=6,
            textColor=colors.HexColor('#1E5BA8'),
            fontWeight='bold'
        )
        
        item_style = ParagraphStyle(
            'Item',
            fontName=font_name,
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=3,
            textColor=colors.black,
            leftIndent=10
        )
        
        is_priemka = diagnostic_data.get('diagnosticType') == 'priemka'
        
        if is_priemka:
            story.append(Paragraph('Фотофиксация автомобиля', section_style))
            story.append(Spacer(1, 4*mm))
            
            story.append(NextPageTemplate('other_pages'))
            
            priemka_photos_by_q = {}
            cur.execute(
                f"SELECT question_index, photo_url FROM {schema}.diagnostic_photos "
                f"WHERE diagnostic_id = {diagnostic_id} ORDER BY question_index, created_at"
            )
            priemka_photo_rows = cur.fetchall()
            for q_idx, p_url in priemka_photo_rows:
                if q_idx not in priemka_photos_by_q:
                    priemka_photos_by_q[q_idx] = []
                priemka_photos_by_q[q_idx].append(p_url)
            
            for question_num, question_text, answer_value, sub_answers in checklist_rows:
                story.append(Paragraph(f'<b>{question_text}</b>', item_style))
                
                if answer_value and answer_value not in ('Фото прикреплено',):
                    story.append(Paragraph(f'  {answer_value}', item_style))
                
                q_index = question_num - 1
                if q_index in priemka_photos_by_q:
                    for photo_url in priemka_photos_by_q[q_index]:
                        try:
                            photo_resp = urllib.request.urlopen(photo_url)
                            photo_data = photo_resp.read()
                            img_reader = ImageReader(BytesIO(photo_data))
                            iw, ih = img_reader.getSize()
                            max_w = 130*mm
                            max_h = 180*mm
                            scale = min(max_w / iw, max_h / ih)
                            img = Image(img_reader, width=iw*scale, height=ih*scale)
                            story.append(Spacer(1, 2*mm))
                            story.append(img)
                        except Exception as e:
                            print(f"[WARNING] Could not load priemka photo {photo_url}: {str(e)}")
                
                story.append(Spacer(1, 4*mm))
        else:
            if working_items:
                story.append(Paragraph('Проверенные исправные узлы и детали автомобиля', section_style))
                for item in working_items:
                    story.append(Paragraph(f'• {item}', item_style))
                story.append(Spacer(1, 6*mm))
            
            story.append(NextPageTemplate('other_pages'))
            
            if broken_items:
                story.append(Paragraph('Обнаруженные неисправности:', section_style))
                for question_num, item in broken_items:
                    story.append(Paragraph(f'• {item}', item_style))
                    
                    if with_photos and question_num in photos_by_question:
                        story.append(Spacer(1, 2*mm))
                        for photo_url in photos_by_question[question_num]:
                            try:
                                photo_response = urllib.request.urlopen(photo_url)
                                photo_data = photo_response.read()
                                img_reader = ImageReader(BytesIO(photo_data))
                                iw, ih = img_reader.getSize()
                                max_w = 120*mm
                                max_h = 180*mm
                                scale = min(max_w / iw, max_h / ih)
                                img = Image(img_reader, width=iw*scale, height=ih*scale)
                                story.append(img)
                                story.append(Spacer(1, 2*mm))
                            except Exception as e:
                                print(f"[WARNING] Could not load photo {photo_url}: {str(e)}")
                
                story.append(Spacer(1, 8*mm))
        
        doc.build(story)
        
        pdf_content = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        s3 = boto3.client('s3',
            endpoint_url='https://bucket.poehali.dev',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        
        now_krasnoyarsk = datetime.now(krasnoyarsk_tz)
        photo_suffix = '_with_photos' if with_photos else ''
        file_key = f"reports/diagnostic_{diagnostic_id}{photo_suffix}_{now_krasnoyarsk.strftime('%Y%m%d_%H%M%S')}.pdf"
        s3.put_object(
            Bucket='files',
            Key=file_key,
            Body=pdf_content,
            ContentType='application/pdf'
        )
        
        cdn_url = f"https://cdn.poehali.dev/projects/{os.environ['AWS_ACCESS_KEY_ID']}/bucket/{file_key}"
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'pdfUrl': cdn_url,
                'message': 'PDF отчёт успешно сгенерирован'
            }),
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