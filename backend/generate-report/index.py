import json
import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, Frame, PageTemplate, BaseDocTemplate
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
            f"SELECT question_text, answer_value, sub_answers FROM {schema}.checklist_answers "
            f"WHERE diagnostic_id = {diagnostic_id} ORDER BY question_number"
        )
        checklist_rows = cur.fetchall()
        
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
            'engine': 'Двигатель',
            'battery': 'Батарея',
            'oil': 'Масло',
            'brake': 'Тормоза',
            'right_mirror': 'Правое зеркало',
            'left_mirror': 'Левое зеркало',
            'pressure': 'Давление',
            'bulges_cuts': 'Грыжи/порезы',
            'tread': 'Протектор',
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
        
        for question, answer, sub_answers in checklist_rows:
            if answer == 'Исправно':
                working_items.append(question)
            elif answer == 'Неисправно':
                defect_details = parse_defects(sub_answers)
                if defect_details:
                    broken_items.append(f'{question}: {", ".join(defect_details)}')
                else:
                    broken_items.append(question)
        
        font_path = '/tmp/DejaVuSans.ttf'
        
        if not os.path.exists(font_path):
            font_url = 'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf'
            urllib.request.urlretrieve(font_url, font_path)
        
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        font_name = 'DejaVu'
        
        background_image_path = '/tmp/hevsr_background.png'
        if not os.path.exists(background_image_path):
            background_url = 'https://cdn.poehali.dev/projects/4bb6cea8-8d41-426a-b677-f4304502c188/bucket/e0986711-d405-44d1-a66b-83e4a1ba096d.png'
            urllib.request.urlretrieve(background_url, background_image_path)
        
        pdf_buffer = BytesIO()
        
        page_width, page_height = A4
        
        def add_background(canvas, doc):
            canvas.saveState()
            canvas.drawImage(background_image_path, 0, 0, 
                           width=page_width, height=page_height, preserveAspectRatio=False, mask='auto')
            canvas.restoreState()
        
        doc = BaseDocTemplate(pdf_buffer, pagesize=A4)
        
        frame = Frame(20*mm, 15*mm, page_width - 40*mm, page_height - 30*mm, 
                     id='normal', topPadding=50*mm)
        
        template = PageTemplate(id='background_template', frames=[frame], onPage=add_background)
        doc.addPageTemplates([template])
        
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
        
        story.append(Paragraph('Отчет по осмотру автомобиля', title_style))
        story.append(Spacer(1, 8*mm))
        
        krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
        created_at_local = diagnostic_data['createdAt'].astimezone(krasnoyarsk_tz)
        
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
        
        if working_items:
            story.append(Paragraph('Проверенные исправные узлы и детали автомобиля', section_style))
            for item in working_items:
                story.append(Paragraph(f'• {item}', item_style))
            story.append(Spacer(1, 6*mm))
        
        if broken_items:
            story.append(Paragraph('Обнаруженные неисправности:', section_style))
            for item in broken_items:
                story.append(Paragraph(f'• {item}', item_style))
            story.append(Spacer(1, 8*mm))
        
        story.append(Spacer(1, 10*mm))
        
        signature_style = ParagraphStyle(
            'Signature',
            fontName=font_name,
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=3
        )
        
        story.append(Paragraph('Механик: __________________________________', signature_style))
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph('<font size=9 color="#666666">(подпись)</font>', signature_style))
        
        doc.build(story)
        
        pdf_content = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        s3 = boto3.client('s3',
            endpoint_url='https://bucket.poehali.dev',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )
        
        now_krasnoyarsk = datetime.now(krasnoyarsk_tz)
        file_key = f"reports/diagnostic_{diagnostic_id}_{now_krasnoyarsk.strftime('%Y%m%d_%H%M%S')}.pdf"
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