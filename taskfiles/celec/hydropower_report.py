# File handling, date management, and environment variables
import os
import shutil
from dotenv import load_dotenv
import datetime as dt
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# Data processing and statistical analysis
import numpy as np
import pandas as pd
import math
import sqlalchemy as sql
from sqlalchemy import create_engine

# Geospatial data manipulation
import geopandas as gpd
from shapely.geometry import Point
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
import geoglows

# Visualization and plotting
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.image as mpimg
import plotly.graph_objs as go
import plotly.graph_objects as go
import plotly.io as pio
from adjustText import adjust_text

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

# Email management
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders





###############################################################################
#                             COLOR BAR FUNCTIONS                             #
###############################################################################
def color_pacum(pixelValue: float) -> str:
    """
    Returns the corresponding color for a given precipitation value (pixelValue)
    based on predefined ranges following the XML style.

    Parameters:
    pixelValue (float): The precipitation value to determine the color.

    Returns:
    str: The color in hexadecimal format corresponding to the precipitation.
    """
    if pixelValue < 1:
        return "none"  # Label 1
    elif 1 <= pixelValue <= 3.75:
        return "#75baff"  # Label 1.01
    elif 3.76 <= pixelValue <= 7.5:
        return "#359aff"  # Label 3.75
    elif 7.51 <= pixelValue <= 11.25:
        return "#0087ff"  # Label 7.5
    elif 11.26 <= pixelValue <= 15:
        return "#0674C6"  # Label 11.25
    elif 15.01 <= pixelValue <= 18.75:
        return "#0C608D"  # Label 15
    elif 18.76 <= pixelValue <= 22.5:
        return "#148f1b"  # Label 18.75
    elif 22.51 <= pixelValue <= 26.25:
        return "#1acf05"  # Label 22.5
    elif 26.26 <= pixelValue <= 30:
        return "#63ed07"  # Label 26.25
    elif 30.01 <= pixelValue <= 33.75:
        return "#B1F119"  # Label 30
    elif 33.76 <= pixelValue <= 37.5:
        return "#d5f775"  # Label 33.75
    elif 37.51 <= pixelValue <= 41.25:
        return "#fff42b"  # Label 37.5
    elif 41.26 <= pixelValue <= 45:
        return "#ffcb4d"  # Label 41.25
    elif 45.01 <= pixelValue <= 48.75:
        return "#fb9a6f"  # Label 45
    elif 48.76 <= pixelValue <= 52.5:
        return "#f96d73"  # Label 48.75
    elif 52.51 <= pixelValue <= 56.25:
        return "#f84e78"  # Label 52.5
    elif 56.26 <= pixelValue <= 60:
        return "#f71e54"  # Label 56.25
    elif 60.01 <= pixelValue <= 63.75:
        return "#bf0000"  # Label 60
    elif 63.76 <= pixelValue <= 67.5:
        return "#880000"  # Label 63.75
    elif 67.51 <= pixelValue <= 71.25:
        return "#640000"  # Label 67.5
    elif 71.26 <= pixelValue <= 75:
        return "#2d0000"  # Label 71.25
    elif pixelValue > 75:
        return "#2d0000"  # Label 75 and above
    else:
        return "none"  # Default case for values not covered


###############################################################################
#                               PLOTS FUNCTIONS                               #
###############################################################################
def join_images(img1, img2, name):
    # Cargar las imágenes
    imagen1 = mpimg.imread(img1)
    imagen2 = mpimg.imread(img2)
    # Crear una nueva figura con una cuadrícula personalizada
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [1, 1]})
    # Mostrar la primera imagen en la primera subtrama
    ax1.imshow(imagen1)
    ax1.axis('off')
    ax1.set_aspect(aspect='auto')
    # Mostrar la segunda imagen en la segunda subtrama
    ax2.imshow(imagen2)
    ax2.axis('off')
    ax2.set_aspect(aspect='auto')
    # Ajustar el espacio entre las subtramas
    plt.tight_layout()
    # Guardar la figura en un archivo de imagen
    plt.savefig(name)


def plot_ec(raster, cor_factor, ec_gdf, points_gdf, color_fun, out_path, title, basins=False):
    # Abre el raster utilizando rasterio
    with rasterio.open(raster) as src:
        # Realiza el enmascaramiento del raster
        out_image, out_transform  = mask(src, ec_gdf.geometry, crop=True)
        out_image = out_image * cor_factor
    #
    # Crear una lista de valores entre 0 y 1
    mmin = out_image.min()
    mmax = out_image.max()
    rang = int(100 * (mmax - mmin))
    values = np.linspace(int(mmin), int(mmax), rang)
    #
    # Crear un objeto ListedColormap basado en la lista de colores
    colors = [color_fun(value) for value in values]
    cmap_custom = ListedColormap(colors)
    #
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    plt.figure(figsize=(8, 8))
    plt.margins(0)
    ax = plt.gca()
    show(out_image, transform=out_transform, ax=plt.gca(), cmap=cmap_custom)
    ec_gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1)
    #
    # Graficar las cuencas
    if basins:
        assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/celec/assets"
        #
        agoyan = gpd.read_file(f"{assets_path}/agoyan.shp")
        agoyan.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
        #
        coca = gpd.read_file(f"{assets_path}/coca.shp")
        coca.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
        #
        delsintanisagua = gpd.read_file(f"{assets_path}/delsintanisagua.shp")
        delsintanisagua.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
        #
        due = gpd.read_file(f"{assets_path}/due.shp")
        due.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
        #
        jubones = gpd.read_file(f"{assets_path}/jubones.shp")
        jubones.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
        #
        paute = gpd.read_file(f"{assets_path}/paute.shp")
        paute.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
        #
        pucara = gpd.read_file(f"{assets_path}/pucara.shp")
        pucara.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1.5)
    #
    # Graficar los puntos del GeoDataFrame de puntos
    points_gdf.plot(ax=ax, color='red', marker='o', markersize=50, alpha=0.7)
    #
    # Añadir las etiquetas de los puntos, pero no graficarlas aún
    texts = []
    for idx, row in points_gdf.iterrows():
        point = row.geometry
        name = row["layer"]
        text = ax.text(point.x, point.y, name, fontsize=10, ha='right', color='black', fontweight='bold')
        texts.append(text)
    #
    # Ajustar las posiciones de las etiquetas para que no se superpongan
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='gray', lw=0.5))
    #
    # Formatear y guardar  
    plt.xlim(-81.3, -74.9)
    plt.ylim(-5.2, 1.6)
    plt.title(title, fontsize=18)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0.2)


def extract_raster_values_to_points(raster_path, gdf, title):
    """
    Extrae los valores de un ráster en las ubicaciones de los puntos del GeoDataFrame, 
    e incluye un campo específico del GeoDataFrame en la tabla final.

    Parameters:
    raster_path (str): Ruta al archivo ráster.
    gdf (GeoDataFrame): GeoDataFrame que contiene los puntos.
    point_field (str): Campo del GeoDataFrame que se incluirá en el DataFrame final.

    Returns:
    pd.DataFrame: DataFrame de pandas con las coordenadas de los puntos, los valores extraídos del ráster
                  y el campo especificado del GeoDataFrame.
    """
    # Abrir el archivo raster
    with rasterio.open(raster_path) as src:
        # Obtener la transformación afín (de píxel a coordenadas)
        transform = src.transform
        #
        # Crear una lista para almacenar los valores extraídos
        data = []
        #
        # Iterar sobre cada punto en el GeoDataFrame
        for idx, row in gdf.iterrows():
            # Obtener la geometría (punto) y el valor del campo especificado
            point = row.geometry
            name = row["NombreCent"]
            #
            # Obtener las coordenadas del punto
            coord = (point.x, point.y)
            #
            # Convertir las coordenadas del punto a índices de píxeles
            row_idx, col_idx = src.index(coord[0], coord[1])
            #
            # Leer el valor del ráster en esa ubicación
            value = src.read(1)[row_idx, col_idx]
            #
            # Almacenar el valor junto con las coordenadas del punto y el campo 'NombreCent'
            data.append({'Hidroeléctrica': name, title: round(value,1)})
    #
    # Convertir la lista a un DataFrame de pandas
    df = pd.DataFrame(data)
    return df



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


def report(filename, table):
    # Vars
    header_path = "report_header.png"
    footer_path = "report_footer.png"
    titulo = "<b>Boletín Hidrometeorológico: Centrales hidroeléctricas</b>"
    emision, vigencia, anterior, actual, futuro = get_datetime()
    parrafo_1 = "La <b>DIRECCIÓN DE PRONÓSTICOS Y ALERTAS HIDROMETEOROLÓGICAS DEL INAMHI</b>, basándose en la información obtenida de la plataforma <b>INAMHI GEOGLOWS</b> emite el siguiente boletín de vigilancia satelital y predicción de precipitación en centrales hidroeléctricas con generación mayor a 50 MW:"
    parrafo_2 = f"Las <b>condiciones antedecentes de precipitación</b>, desde {anterior} hasta {actual}, son estimadas a través del producto satelital PERSIANN PDIR. El <b>pronóstico de precipitación</b>,desde {actual} hasta {futuro}, son obtenidos del modelo WRF de INAMHI."
    #
    # Configurar estilos
    estilos = getSampleStyleSheet()
    #
    estilo_titulo = ParagraphStyle(
        name = 'Title',
        fontSize = 12,
        textColor = colors.Color(31/255, 73/255, 125/255),
        alignment = TA_CENTER)
    #
    estilo_subtitulo = ParagraphStyle(
        name = 'Subtitle',
        fontSize = 10,
        textColor = colors.Color(31/255, 73/255, 125/255),
        alignment = TA_LEFT,
        spaceAfter = 3)
    #
    estilo_fecha = ParagraphStyle(
        name = 'Dates',
        fontSize = 9,
        alignment = TA_CENTER,
        spaceBefore = 3,
        spaceAfter = 3)
    #
    estilo_parrafo = ParagraphStyle(
        name = 'P01',
        fontSize = 8,
        alignment = TA_CENTER,
        spaceBefore = 4,
        spaceAfter = 4,
        leading = 14)
    #
    estilo_parrafo2 = ParagraphStyle(
        name = 'P02',
        fontSize = 8,
        alignment = TA_JUSTIFY,
        spaceBefore = 4,
        spaceAfter = 4,
        leading = 14)
    #
    # Crear el documento PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    #
    # Definir el encabezado y pie de pagina
    header_content = Image(header_path, width=doc.width, height=2.5*cm)
    footer_content = Image(footer_path, width=doc.width, height=1.5*cm)
    #
    # Agregar elementos al contenido del PDF
    elementos = [
        Paragraph(titulo, estilo_titulo),
        Spacer(1, 12),
        Paragraph(emision, estilo_fecha),
        Paragraph(vigencia, estilo_fecha),
        Spacer(1, 10),
        Paragraph(parrafo_1, estilo_parrafo),
        Spacer(1, 3),
        Image("report-hydro-plot.png", width=doc.width, height=8*cm),
        Image("pacum24.png", width=14*cm, height=0.7*cm),
        Spacer(1, 10),
        Paragraph(parrafo_2, estilo_parrafo2),
        Spacer(1, 10),
        agregar_tabla(table),
        
        ]
    #
    # Contruir el pdf
    doc.build(
        elementos, 
        onFirstPage=partial(header_and_footer, header_content=header_content, footer_content=footer_content), 
        onLaterPages=partial(header_and_footer, header_content=header_content, footer_content=footer_content))



###############################################################################
#                                EMAIL ROUTNES                                #
###############################################################################
def send_report(subject, body, attachment_file, sender, password):
    # Users to send email
    recipients = [
        "jusethchancay@ecociencia.org", "varreaga@inamhi.gob.ec"]
    #
    # SMTP server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    #
    # Configure the message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject
    #
    # Attach the email body
    message.attach(MIMEText(body, 'plain'))
    #
    # Attach the PDF file
    attachment = open(attachment_file, 'rb')
    attachment_part = MIMEBase('application', 'octet-stream')
    attachment_part.set_payload((attachment).read())
    encoders.encode_base64(attachment_part)
    attachment_part.add_header('Content-Disposition', "attachment; filename= %s" % attachment_file)
    message.attach(attachment_part)
    #
    # Connect to the SMTP server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipients, message.as_string())
    server.quit()


def send_error(error, sender, password):
    # Users to send email
    recipients = [ "prediccion@inamhi.gob.ec", "jusethchancay@ecociencia.org"]
    #
    # SMTP server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    #
    # Configure the message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = ", ".join(recipients)
    message['Subject'] = "Error en el envío de reporte automático a SGR"
    #
    # Attach the email body
    body = f"Existió un error en el envío del reporte automático a SGR\n {error} \n\nPonerse en contacto con Juseth, lo antes posible...\nSaludos coordiales,\nINAMHI GEOGLOWS"
    message.attach(MIMEText(body, 'plain'))
    #
    # Connect to the SMTP server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipients, message.as_string())
    server.quit()




###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("inamhi-geoglows")

# Load enviromental variables - credentials
load_dotenv()
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASS = os.getenv('MAIL_PASS')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Read SHP files
assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/celec/assets"
hydropowers = gpd.read_file(f"{assets_path}/hidroelectricas_mayores_50W.shp")
prov = gpd.read_file(f"{assets_path}/ecuador_diss.shp")


# Change the work directory
os.chdir(user_dir)
os.chdir("data/celec")


# Datos satelitales
url = "/home/ubuntu/data/fireforest/persiann1d.tif"
os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} pacum-hydro.tif")
pacum = extract_raster_values_to_points("pacum-hydro.tif", hydropowers, "Precipitación satelital (mm)")
plot_ec("pacum-hydro.tif", 1, prov, hydropowers, color_pacum, "pacum-hydro.png", "Precipitación satelital (PERSIANN PDIR)")
os.remove("pacum-hydro.tif")

# Pronóstico
now = dt.datetime.now() #- dt.timedelta(days=1)
datestr = now.strftime("%Y-%m-%d00Z-24H-%Y%m%d07h00")
url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} forecast-hydro.tif")
forecast = extract_raster_values_to_points("forecast-hydro.tif", hydropowers, "Pronóstico de precipitación (mm)")
plot_ec("forecast-hydro.tif", 1, prov, hydropowers, color_pacum, "forecast-hydro.png", "Pronóstico de precipitación (WRF)")
os.remove("forecast-hydro.tif")

# Pronostico para el siguiente dia
tomorrow = now + dt.timedelta(days=1)
a = now.strftime("%Y-%m-%d00Z-24H-")
b = tomorrow.strftime("%Y%m%d07h00")
datestr = f"{a}{b}"
url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} forecast-tomorrow.tif")
forecast2 = extract_raster_values_to_points("forecast-tomorrow.tif", hydropowers, "Pronóstico de precipitación (mm)")
forecast2.to_csv("/var/www/html/assets/reports/forecast-daily.csv", sep=",",index=False)
plot_ec("forecast-tomorrow.tif", 1, prov, hydropowers, color_pacum, "/var/www/html/assets/reports/hydropowers-forecast-daily.png", "Pronóstico de precipitación (WRF)", True)
os.remove("forecast-tomorrow.tif")


# Table and plot
join_images("pacum-hydro.png", "forecast-hydro.png", "report-hydro-plot.png")
table_precp = pd.merge(pacum, forecast, on='Hidroeléctrica', how='inner')

# Generate report
now = dt.datetime.now()
nowstr = now.strftime("%Y-%m-%d")
report(f"reporte-hidroelectricas-{nowstr}.pdf", table_precp)

# Send report
subject = f"Boletín Hidrometeorológico Centrales Hidroeléctricas {nowstr}"
body = "Estimados y estimadas, \n\nLa DIRECCIÓN DE PRONÓSTICOS Y ALERTAS HIDROMETEOROLÓGICAS DEL INAMHI, basándose en la información obtenida de la plataforma INAMHI GEOGLOWS emite el siguiente boletín de vigilancia y predicción de condiciones hidrometeorológicas. \n\nSaludos Cordiales,\nDirección de Pronósticos y Alertas Hidrometeorológicas\n(593-2) 2497100 ext. 88003\n'Nuestro compromiso el país y nuestra misión servirle'"
send_report(subject=subject, body=body, attachment_file=f"reporte-hidroelectricas-{nowstr}.pdf",sender=MAIL_USER, password=MAIL_PASS)
