import json
import os
import psycopg2
from datetime import datetime
from zoneinfo import ZoneInfo
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
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
        
        font_path = '/tmp/DejaVuSans.ttf'
        
        if not os.path.exists(font_path):
            font_url = 'https://cdn.jsdelivr.net/npm/dejavu-fonts-ttf@2.37.3/ttf/DejaVuSans.ttf'
            urllib.request.urlretrieve(font_url, font_path)
        
        pdfmetrics.registerFont(TTFont('DejaVu', font_path))
        font_name = 'DejaVu'
        
        header_image_path = '/tmp/hevsr_header.png'
        if not os.path.exists(header_image_path):
            header_url = 'https://cdn.poehali.dev/projects/4bb6cea8-8d41-426a-b677-f4304502c188/bucket/1b4f4332-6d1a-4f46-b4ad-75c0ee2869a8.png'
            urllib.request.urlretrieve(header_url, header_image_path)
        
        pdf_buffer = BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=10*mm, bottomMargin=15*mm, leftMargin=20*mm, rightMargin=20*mm)
        
        story = []
        styles = getSampleStyleSheet()
        
        header_img = Image(header_image_path, width=170*mm, height=40*mm)
        story.append(header_img)
        story.append(Spacer(1, 15*mm))
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            fontName=font_name,
            alignment=TA_CENTER,
            spaceAfter=12,
            textColor=colors.HexColor('#1E5BA8')
        )
        
        story.append(Paragraph('ОТЧЁТ О ДИАГНОСТИКЕ АВТОМОБИЛЯ', title_style))
        story.append(Spacer(1, 8*mm))
        
        diagnostic_types = {
            '5min': '5-ти минутка',
            'dhch': 'ДХЧ',
            'des': 'ДЭС'
        }
        
        krasnoyarsk_tz = ZoneInfo('Asia/Krasnoyarsk')
        created_at_local = diagnostic_data['createdAt'].astimezone(krasnoyarsk_tz)
        
        hevsr_green = colors.HexColor('#7AB51D')
        hevsr_blue = colors.HexColor('#1E5BA8')
        
        data = [
            ['№ диагностики:', str(diagnostic_data['id'])],
            ['Дата:', created_at_local.strftime('%d.%m.%Y %H:%M')],
            ['Механик:', diagnostic_data['mechanic']],
            ['Госномер:', diagnostic_data['carNumber']],
            ['Пробег:', f"{diagnostic_data['mileage']:,} км".replace(',', ' ')],
            ['Тип диагностики:', diagnostic_types.get(diagnostic_data['diagnosticType'], diagnostic_data['diagnosticType'])]
        ]
        
        table = Table(data, colWidths=[55*mm, 105*mm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), hevsr_blue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, hevsr_blue),
            ('LINEWIDTH', (0, 0), (-1, -1), 1.5)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20*mm))
        
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