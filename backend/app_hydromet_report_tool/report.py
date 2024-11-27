# Django imports
from django.http import HttpResponse

# Standard library imports
import requests
from datetime import datetime, timedelta
from functools import partial
from io import BytesIO
import pandas as pd

# ReportLab imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.paragraph import Paragraph


###############################################################################
#                                   REPORT                                    #
###############################################################################
def header(canvas, doc, content) -> None:
    """
    Draws a header on each page of the document using a ReportLab canvas. The
    content is drawn on the canvas at the top margin, aligned properly with the
    document's width and height.

    Parameters:
    -----------
    - canvas (Canvas): The canvas object from ReportLab, used to draw elements
        on the PDF page.
    - doc (SimpleDocTemplate): The document template that defines the layout
        and page size.
    - content (Paragraph): A ReportLab Paragraph or other flowable content to 
        be rendered as the header.

    Returns:
    --------
    - None: The function draws the header directly onto the canvas without 
        returning any value.
    """
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin,
                   doc.height + doc.bottomMargin + doc.topMargin - h)
    canvas.restoreState()


def footer(canvas, doc, content):
    """
    Draws a footer on each page of the document using a ReportLab canvas. The
    content is drawn at the bottom margin, aligned properly with the document's
    width and height.

    Parameters:
    -----------
    - canvas (Canvas): The canvas object from ReportLab, used to draw elements
        on the PDF page.
    - doc (SimpleDocTemplate): The document template that defines the layout
        and page size.
    - content (Paragraph): A ReportLab Paragraph or other flowable content to 
        be rendered as the footer.

    Returns:
    --------
    - None: The function draws the footer directly onto the canvas without 
        returning any value.
    """
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()


def header_and_footer(canvas, doc, header_content, footer_content):
    """
    Draws both a header and a footer on each page of the document using a 
    ReportLab canvas. It calls the `header` function to draw the header at the 
    top of the page and the `footer` function to draw the footer at the bottom 
    of the page.

    Parameters:
    -----------
    - canvas (Canvas): The canvas object from ReportLab, used to draw elements 
        on the PDF page.
    - doc (SimpleDocTemplate): The document template that defines the layout 
        and page size.
    - header_content (Paragraph): A ReportLab Paragraph or other flowable 
        content to be rendered as the header.
    - footer_content (Paragraph): A ReportLab Paragraph or other flowable 
        content to be rendered as the footer.

    Returns:
    --------
    - None: The function draws both the header and footer directly onto the 
        canvas without returning any value.
    """
    header(canvas, doc, header_content)
    footer(canvas, doc, footer_content)



def format_dates(date: datetime, type: str) -> list[str]:
    """
    Formats a given date into three different string representations, using
    Spanish month names and specific date/time formats. Supports daily or 
    weekly generation.

    Parameters:
    -----------
    - date (datetime): The date object to format.
    - type (str): The type of date generation, either 'daily' or 'weekly'.

    Returns:
    --------
    list[str]: A list of three formatted strings:
        1. Full timestamp (e.g., '20 de octubre del 2024, 14:30').
        2. Time range for the next day/week (e.g., 'desde las 07:00 del 21 de 
           octubre hasta las 07:00 del 22 de octubre del 2024').
        3. Time range in a detailed format (e.g., 'desde el 21 de octubre del
           2024 (07H00) hasta el 22 de octubre del 2024 (07H00)').
    """
    months = [
        "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    date = date - timedelta(hours=5)

    # Format 1: Full timestamp for the given date
    day = date.day
    month = months[date.month - 1]
    year = date.year
    hours = f"{date.hour:02d}"
    minutes = f"{date.minute:02d}"
    format1 = f"{day} de {month} del {year}, {hours}:{minutes}"

    # Advance date by 1 day for daily or 7 days for weekly
    increment = 1 if type == 'daily' else 7
    date += timedelta(days=1)
    start_day = date.day
    start_month = months[date.month - 1]
    start_year = date.year

    # Format 2: Time range for the next day/week
    end_date = date + timedelta(days=increment)
    end_day = end_date.day
    end_month = months[end_date.month - 1]
    end_year = end_date.year
    format2 = (
        f"desde las 07:00 del {start_day} de {start_month} hasta las 07:00 del "
        f"{end_day} de {end_month} del {end_year}"
    )

    # Format 3: Detailed time range with day/month/year
    format3 = (
        f"desde el {start_day} de {start_month} del {start_year} (07H00) "
        f"hasta el {end_day} de {end_month} del {end_year} (07H00)"
    )

    return [format1, format2, format3]



def custom_table(data) -> Table:
    """
    Creates a table using ReportLab's Table class based on a pandas DataFrame 
    and applies styling such as background color, text color, alignment, 
    font size, and padding.

    Parameters:
    -----------
    - data (DataFrame): A pandas DataFrame where the columns and values are 
      used to populate the table.

    Returns:
    --------
    - Table: A ReportLab Table object with the specified styles applied to 
        headers and content.
    
    Styling:
    --------
    - Header row: Grey background, white text, center-aligned.
    - Content rows: White background, black grid lines, center-aligned.
    """
    data_table = [data.columns.tolist()] + data.values.tolist()
    table = Table(data_table)
    table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                               ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                               ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                               ('FONTSIZE', (0, 0), (-1, -1), 7),
                               ('TOPPADDING', (0, 0), (-1, -1), 0.5),
                               ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
                               ('BACKGROUND', (0,1), (-1,-1), colors.white),
                               ('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
    return table



def report_hydropower_forecast(img, legend, data, typeDate):
    """
    Generates a hydrometeorological bulletin report in PDF format, including 
    images, tables, and formatted text. The report is based on hydropower 
    daily forecasts and is styled using ReportLab.

    Parameters:
    -----------

    Returns:
    --------
    - HttpResponse: A response object containing the generated PDF report, 
        ready for download.

    HTTP Response:
    --------------
    - Content type: 'application/pdf'.
    - File name: 'boletin_hidrometeorologico.pdf'.
    """
    # Path for statics images
    header_path = "/home/ubuntu/data/celec/report_header.png"
    footer_path = "/home/ubuntu/data/celec/report_footer.png"

    # Dates
    formatted_dates = format_dates(datetime.now(), type=typeDate)

    # Title and texts
    title = "<b>Boletín Hidrometeorológico: Centrales hidroeléctricas</b>"
    text_01 = f"<b>Hora y fecha de emision:</b> {formatted_dates[0]}"
    text_02 = f"<b>Vigencia:</b> {formatted_dates[1]}"
    text_03 = (
        "La <b>DIRECCIÓN DE PRONÓSTICOS Y ALERTAS HIDROMETEOROLÓGICAS DEL "
        "INAMHI</b>, basándose en la información obtenida de la <b>plataforma "
        "INAMHI GEOGLOWS</b> emite el siguiente boletín de vigilancia "
        "satelital y predicción de precipitación en centrales hidroeléctricas "
        "con generación mayor a 50 MW:")
    text_04 = (
        f"El <b>pronóstico de precipitación</b>, {formatted_dates[2]}, son obtenidos "
        "del modelo WRF de INAMHI."
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='Title',
        fontSize=12,
        textColor=colors.Color(31 / 255, 73 / 255, 125 / 255),
        alignment=TA_CENTER
    )
    dates_styles = ParagraphStyle(
        name='Dates',
        fontSize=9,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=3
    )
    paragraph_style_1 = ParagraphStyle(
        name='P01',
        fontSize=8,
        alignment=TA_CENTER,
        spaceBefore=4,
        spaceAfter=4,
        leading=14
    )
    paragraph_style_2 = ParagraphStyle(
        name='P02',
        fontSize=8,
        alignment=TA_JUSTIFY,
        spaceBefore=4,
        spaceAfter=4,
        leading=14
    )

    # Create the buffer and document in temporal memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Define the header and footer
    header_content = Image(header_path, width=doc.width, height=2.5 * cm)
    footer_content = Image(footer_path, width=doc.width, height=1.5 * cm)

    # Table for forecast
    table = {
        "Hidroeléctrica": [
            "Mazar", "Paute-Molino", "Sopladora", "Coca-Codo Sinclair", 
            "Pucará", "Agoyán", "Minas San Francisco", "Delsitanisagua"],
        "Pronóstico de precipitación WRF (mm)":data
    }
    table = pd.DataFrame(table)

    # Add elements to the document
    elements = [
        Paragraph(title, title_style),
        Spacer(1, 12),
        Paragraph(text_01, dates_styles),
        Paragraph(text_02, dates_styles),
        Spacer(1, 10),
        Paragraph(text_03, paragraph_style_1),
        #Image(img, width=10*cm, height=10*cm)
        #Image(legend, width=10*cm, height=10*cm)
        Spacer(1, 10),
        Paragraph(text_04, paragraph_style_2),
        Spacer(1, 10),
        custom_table(table),
    ]

    # Build the document
    doc.build(
        elements,
        onFirstPage=partial(
            header_and_footer, 
            header_content=header_content, 
            footer_content=footer_content),
        onLaterPages=partial(
            header_and_footer, 
            header_content=header_content, 
            footer_content=footer_content)
    )

    # Get the buffer document in memory
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
