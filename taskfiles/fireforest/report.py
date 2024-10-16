# Standard libraries
import os
import warnings

# Data processing libraries
import numpy as np
import pandas as pd
import geopandas as gpd

# Visualization libraries
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

# Raster handling and geospatial operations
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.io import MemoryFile
from rasterio.warp import calculate_default_transform, reproject, Resampling

# Email manager and sender
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

# Environment configuration
from dotenv import load_dotenv



###############################################################################
#                                   COLORBARS                                 #
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


def color_percent(pixelValue:float) -> str:
    """
    Returns the corresponding color for a given percent value (pixelValue)
    based on predefined ranges.

    Parameters:
    pixelValue (float): The precipitation value to determine the color.

    Returns:
    str: The color in hexadecimal format corresponding to the percent value.
    """
    if pixelValue <= 0:
        return "none"
    if 0 < pixelValue <= 10:
        return "#F9F788"
    elif 10 < pixelValue <= 20:
        return "#D6D309"
    elif 20 < pixelValue <= 30:
        return "#B08C00"
    elif 30 < pixelValue <= 40:
        return "#B6F8A9"
    elif 40 < pixelValue <= 50:
        return "#1DD41C"
    elif 50 < pixelValue <= 60:
        return "#005200"
    elif 60 < pixelValue <= 70:
        return "#359AFF"
    elif 70 < pixelValue <= 80:
        return "#0069D2"
    elif 80 < pixelValue <= 90:
        return "#00367F"
    elif 90 < pixelValue <= 100:
        return "#100053"
    else:
        return "none"



def color_noprec(pixelValue:float) -> str:
    """
    Returns the corresponding color for a given noprec value (pixelValue)
    based on predefined ranges.

    Parameters:
    pixelValue (float): The percentage value to determine the color.

    Returns:
    str: The color in hexadecimal format corresponding to the percentage range.
    """
    if pixelValue < 1:
        return "none"
    elif 1 <= pixelValue < 2:
        return "#b3cae7"
    elif 2 <= pixelValue < 3:
        return "#6795cf"
    elif 3 <= pixelValue < 4:
        return "#3383c7"
    elif 4 <= pixelValue < 5:
        return "#0070C0"
    elif 5 <= pixelValue < 6:
        return "#2488a4"
    elif 6 <= pixelValue < 7:
        return "#49a088"
    elif 7 <= pixelValue < 8:
        return "#6db86c"
    elif 8 <= pixelValue < 9:
        return "#92D050"
    elif 9 <= pixelValue < 10:
        return "#add255"
    elif 10 <= pixelValue < 11:
        return "#c8d45b"
    elif 11 <= pixelValue < 12:
        return "#e3d660"
    elif 12 <= pixelValue < 13:
        return "#FFD966"
    elif 13 <= pixelValue < 14:
        return "#f0b950"
    elif 14 <= pixelValue < 15:
        return "#e2993b"
    elif 15 <= pixelValue < 16:
        return "#d47926"
    elif 16 <= pixelValue < 17:
        return "#C65911"
    elif 17 <= pixelValue < 18:
        return "#c4420c"
    elif 18 <= pixelValue < 19:
        return "#c32c08"
    elif 19 <= pixelValue < 20:
        return "#c11604"
    elif 20 <= pixelValue:
        return "#C00000"
    else:
        return "none"









###############################################################################
#                                PLOT FUNCTIONS                               #
###############################################################################
def plot_raster_res(raster_url:str, gdf: gpd.GeoDataFrame, fig_name:str, 
                    color:any, scale:float=1, res:tuple=(0.01, 0.01)) -> None:
    """
    Plots a raster with optional resampling and masking based on a 
    GeoDataFrame.

    Parameters:
    raster_url (str): Path to the input raster file.
    gdf (GeoDataFrame): GeoDataFrame containing the geometries for masking.
    fig_name (str): Output figure file name.
    color (function): Function that returns a color based on a pixel value.
    scale (float): Scaling factor for the raster values.
    res (tuple): New resolution for resampling in the format (x_res, y_res).
    """
    # Abre el raster utilizando rasterio
    with rasterio.open(raster_url) as src:
        # Realiza el remuestreo del raster a la nueva resolución
        transform, width, height = calculate_default_transform(
            src.crs, 
            src.crs, 
            src.width, 
            src.height, 
            *src.bounds, 
            resolution=res
        )
        profile = src.profile
        profile.update({
            'transform': transform,
            'width': width,
            'height': height,
            'dtype': 'float64'
        })
        # Crear una matriz para almacenar la imagen remuestreada
        out_image_resampled = np.empty(
            (src.count, height, width), 
            dtype=np.float64
        )
        # Aplicar el remuestreo usando interpolación bilineal
        reproject(
            source=rasterio.band(src, 1),
            destination=out_image_resampled[0],
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=src.crs,
            resampling=Resampling.bilinear
        )
        # Guardar el raster remuestreado en memoria
        with MemoryFile() as memfile:
            with memfile.open(**profile) as dataset:
                dataset.write(out_image_resampled)
                # Enmascarar el raster remuestreado con las geometrías del shp
                out_image_masked, out_transform = rasterio.mask.mask(
                    dataset, gdf.geometry, crop=True
                )
                out_image_masked = out_image_masked.astype(np.float64) * scale
                out_image_masked = np.clip(
                    out_image_masked, a_min=-100, a_max=100
                )
    # Crear una lista de valores entre 0 y 1
    mmin = out_image_masked.min()
    mmax = out_image_masked.max()
    rang = 100 * (mmax - mmin)
    values = np.linspace(mmin, mmax, int(rang))
    # Crear una lista de colores utilizando la función color
    colors = [color(value) for value in values]
    cmap_custom = ListedColormap(colors)
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    plt.figure(figsize=(8, 8))
    plt.margins(0)
    show(
        out_image_masked, 
        transform=out_transform, 
        ax=plt.gca(), 
        cmap=cmap_custom
    )
    gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1)
    # Establecer límites en los ejes x e y
    plt.xlim(-81.3, -74.9)
    plt.ylim(-5.2, 1.6)
    plt.axis("off")
    # Save the figure
    fig_path = f'{user_dir}/data/report/{fig_name}'
    plt.savefig(fig_path, bbox_inches='tight', pad_inches=0)




def plot_raster(raster_url: str, gdf: gpd.GeoDataFrame, fig_name: str, color: any, 
                scale: float = 1) -> None:
    """
    Plots a raster, masking it based on a GeoDataFrame.

    Parameters:
    raster_url (str): Path to the input raster file.
    gdf (GeoDataFrame): GeoDataFrame containing the geometries for masking.
    fig_name (str): Output figure file name.
    color (function): Function that returns a color based on a pixel value.
    scale (float): Scaling factor for the raster values.
    """
    # Abre el raster utilizando rasterio
    with rasterio.open(raster_url) as src:
        # Enmascarar el raster original con las geometrías del shp
        out_image_masked, out_transform = rasterio.mask.mask(
            src, gdf.geometry, crop=True
        )
        out_image_masked = out_image_masked.astype(np.float64) * scale
        out_image_masked = np.clip(
            out_image_masked, a_min=-100, a_max=100
        )
    #
    # Crear una lista de valores entre 0 y 1
    mmin = out_image_masked.min()
    mmax = out_image_masked.max()
    rang = 100 * (mmax - mmin)
    values = np.linspace(mmin, mmax, int(rang))
    #
    # Crear una lista de colores utilizando la función color
    colors = [color(value) for value in values]
    cmap_custom = ListedColormap(colors)
    #
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    plt.figure(figsize=(8, 8))
    plt.margins(0)
    show(
        out_image_masked, 
        transform=out_transform, 
        ax=plt.gca(), 
        cmap=cmap_custom
    )
    gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1)
    #
    # Establecer límites en los ejes x e y
    plt.xlim(-81.3, -74.9)
    plt.ylim(-5.2, 1.6)
    plt.axis("off")
    #
    # Guardar la figura
    fig_path = f'{user_dir}/data/report/{fig_name}'
    plt.savefig(fig_path, bbox_inches='tight', pad_inches=0)



def send(subject:str, body:str, attachment_files:list, sender:str, 
         password:str) -> None:
    """
    Sends an email with the specified subject, body, and attachments to a 
    predefined list of recipients.

    Parameters:
    subject (str): The subject line of the email.
    body (str): The main content of the email.
    attachment_files (list of str): A file list for the attachment.
    sender (str): The email address of the sender.
    password (str): The password for the sender's email account.
    """
    # Users to send email
    recipients = ["prediccion@inamhi.gob.ec","jusethchancay@ecociencia.org"]
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
    for attachment_file in attachment_files:
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





###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Load enviromental variables - credentials
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASS = os.getenv('MAIL_PASS')

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser(f'~{user}')
os.chdir(user_dir)
os.chdir("data/report")

# Path for shp extention
path = "/home/ubuntu/inamhi-geoglows/taskfiles/shp/ecuador.shp"
ec = gpd.read_file(path)

# Pacum raster URL
p24 = "/home/ubuntu/data/fireforest/persiann1d.tif"
p72 = "/home/ubuntu/data/fireforest/persiann3d.tif"
asm = "/home/ubuntu/data/fireforest/soilmoisture.tif"
npr = "/home/ubuntu/data/fireforest/noprec.tif"

# Generate figures
plot_raster(raster_url=p24, gdf=ec, fig_name="pacum24h.png", color=color_pacum)
plot_raster(raster_url=p72, gdf=ec, fig_name="pacum72h.png", color=color_pacum)
plot_raster(raster_url=asm, gdf=ec, fig_name="asm.png", color=color_percent, scale=100)
plot_raster(raster_url=npr, gdf=ec, fig_name="noprec.png", color=color_noprec)

# Send email
subject = "Cartas para boletín de focos de calor"
body = "Estimad@s,\n\nDesde la plataforma INAMHI GEOGLOWS se adjuntan las graficas actualizadas de FFGS y precipitacion satelital, para su uso en productos generados por la DPA.\n\nArchivos adjuntos:\n\n1. Humedad del suelo (24 hrs)\n2. Precipitación acumulada (24 hrs)\n3. Precipitación acumulada (72 hrs)\n4. Días consecutivos sin lluvia. \n\nSaludos Cordiales,\nINAMHI GEOGLOWS"
attachment_files = [
    "/home/ubuntu/data/report/asm.png",
    "/home/ubuntu/data/report/pacum24h.png",
    "/home/ubuntu/data/report/pacum72h.png",
    "/home/ubuntu/data/report/noprec.png"
]
send(subject, body, attachment_files, MAIL_USER, MAIL_PASS)
