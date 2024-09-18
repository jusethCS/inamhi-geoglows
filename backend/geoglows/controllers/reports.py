# Report generation
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Table
from reportlab.platypus import TableStyle, PageBreak
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from functools import partial

from django.http import HttpResponse
from io import BytesIO
import datetime as dt
from datetime import timedelta


###############################################################################
#                                   REPORT                                    #
###############################################################################
def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h)
    canvas.restoreState()

def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

def header_and_footer(canvas, doc, header_content, footer_content):
    header(canvas, doc, header_content)
    footer(canvas, doc, footer_content)

def get_datetime():
    # Obtener la fecha y hora actual
    now = dt.datetime.now() + dt.timedelta(hours=-5) #- dt.timedelta(days=1) 
    # Mapeo de nombres de meses en inglés a español
    meses_ingles_a_espanol = {
        "January": "enero",
        "February": "febrero",
        "March": "marzo",
        "April": "abril",
        "May": "mayo",
        "June": "junio",
        "July": "julio",
        "August": "agosto",
        "September": "septiembre",
        "October": "octubre",
        "November": "noviembre",
        "December": "diciembre"
    }
    # Formatear la fecha y hora de emisión
    emision = "<b>Hora y fecha de emision:</b> " + now.strftime("%d de %B del %Y, %H:%M")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        emision = emision.replace(mes_ingles, mes_espanol)
    #
    # Formatear dia anterior
    anterior = (now + timedelta(days=-1)).strftime("%d de %B del %Y (07H00)")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        anterior = anterior.replace(mes_ingles, mes_espanol)
    # Formatear dia actual
    actual = (now).strftime("%d de %B del %Y (07H00)")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        actual = actual.replace(mes_ingles, mes_espanol)
    # Formatear dia futuro
    futuro = (now + timedelta(days=1)).strftime("%d de %B del %Y (07H00)")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        futuro = futuro.replace(mes_ingles, mes_espanol)
    #
    # Calcular la vigencia para 24 horas
    inicio_vigencia = now.strftime("desde 07:00 del %d de %B")
    fin_vigencia = (now + timedelta(days=1)).strftime("hasta las 07:00 del %d de %B del %Y")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        inicio_vigencia = inicio_vigencia.replace(mes_ingles, mes_espanol)
        fin_vigencia = fin_vigencia.replace(mes_ingles, mes_espanol)
    #
    # Formatear la vigencia
    vigencia = f"<b>Vigencia:</b> {inicio_vigencia} {fin_vigencia}"
    return(emision, vigencia, anterior, actual, futuro)


def agregar_tabla(datos):
    datos_tabla = [datos.columns.tolist()] + datos.values.tolist()
    tabla = Table(datos_tabla)
    tabla.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                               ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                               ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                               ('FONTSIZE', (0, 0), (-1, -1), 7),
                               ('TOPPADDING', (0, 0), (-1, -1), 0.5),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
                               ('BACKGROUND', (0,1), (-1,-1), colors.white),
                               ('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
    return(tabla)



def report():
    # Vars
    header_path = "/home/ubuntu/data/celec/report_header.png"
    footer_path = "/home/ubuntu/data/celec/report_footer.png"
    titulo = "<b>Boletín Hidrometeorológico: Centrales hidroeléctricas</b>"
    emision, vigencia, anterior, actual, futuro = get_datetime()
    parrafo_1 = "La <b>DIRECCIÓN DE PRONÓSTICOS Y ALERTAS HIDROMETEOROLÓGICAS DEL INAMHI</b>, basándose en la información obtenida de la plataforma <b>INAMHI GEOGLOWS</b> emite el siguiente boletín de vigilancia satelital y predicción de precipitación en centrales hidroeléctricas con generación mayor a 50 MW:"
    parrafo_2 = f"Las <b>condiciones antedecentes de precipitación</b>, desde {anterior} hasta {actual}, son estimadas a través del producto satelital PERSIANN PDIR. El <b>pronóstico de precipitación</b>, desde {actual} hasta {futuro}, son obtenidos del modelo WRF de INAMHI."

    # Configurar estilos
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle(
        name='Title',
        fontSize=12,
        textColor=colors.Color(31 / 255, 73 / 255, 125 / 255),
        alignment=TA_CENTER
    )
    estilo_fecha = ParagraphStyle(
        name='Dates',
        fontSize=9,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=3
    )
    estilo_parrafo = ParagraphStyle(
        name='P01',
        fontSize=8,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4,
        leading=14
    )
    estilo_parrafo2 = ParagraphStyle(
        name='P02',
        fontSize=8,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
        leading=14
    )

    # Crear el buffer en memoria
    buffer = BytesIO()

    # Crear el documento PDF en memoria
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Definir el encabezado y pie de pagina
    header_content = Image(header_path, width=doc.width, height=2.5 * cm)
    footer_content = Image(footer_path, width=doc.width, height=1.5 * cm)

    # Agregar elementos al contenido del PDF
    elementos = [
        Paragraph(titulo, estilo_titulo),
        Spacer(1, 12),
        Paragraph(emision, estilo_fecha),
        Paragraph(vigencia, estilo_fecha),
        Spacer(1, 10),
        Paragraph(parrafo_1, estilo_parrafo),
        Spacer(1, 3),
        Image("/var/www/html/assets/reports/hydropowers-forecast-daily.png", width=doc.width, height=8 * cm),
        Image("/var/www/html/assets/reports/colorbar-pacum.png", width=14 * cm, height=0.7 * cm),
        Spacer(1, 10),
        Paragraph(parrafo_2, estilo_parrafo2),
        Spacer(1, 10),
        #agregar_tabla(table),
    ]

    # Construir el PDF
    doc.build(
        elementos,
        onFirstPage=partial(header_and_footer, header_content=header_content, footer_content=footer_content),
        onLaterPages=partial(header_and_footer, header_content=header_content, footer_content=footer_content)
    )

    # Obtener el valor del buffer en memoria
    pdf = buffer.getvalue()
    buffer.close()

    # Retornar el PDF como respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="boletin_hidrometeorologico.pdf"'
    return response

