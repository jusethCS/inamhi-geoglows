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
import matplotlib
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
def color_pacum_daily(pixelValue: float) -> str:
    """
    Returns the corresponding color for a given precipitation value based on 
    predefined ranges following the XML style.

    Parameters:
    -----------
      - pixelValue (float): The precipitation value to determine the color.

    Returns:
      - str: The color in hexadecimal format corresponding to the precipitation.
    """
    if pixelValue < 1:
        return "none"
    elif 1 <= pixelValue <= 3.75:
        return "#75baff" 
    elif 3.76 <= pixelValue <= 7.5:
        return "#359aff"
    elif 7.51 <= pixelValue <= 11.25:
        return "#0087ff"
    elif 11.26 <= pixelValue <= 15:
        return "#0674C6" 
    elif 15.01 <= pixelValue <= 18.75:
        return "#0C608D"
    elif 18.76 <= pixelValue <= 22.5:
        return "#148f1b"
    elif 22.51 <= pixelValue <= 26.25:
        return "#1acf05"
    elif 26.26 <= pixelValue <= 30:
        return "#63ed07"
    elif 30.01 <= pixelValue <= 33.75:
        return "#B1F119"
    elif 33.76 <= pixelValue <= 37.5:
        return "#d5f775"
    elif 37.51 <= pixelValue <= 41.25:
        return "#fff42b"
    elif 41.26 <= pixelValue <= 45:
        return "#ffcb4d"
    elif 45.01 <= pixelValue <= 48.75:
        return "#fb9a6f"
    elif 48.76 <= pixelValue <= 52.5:
        return "#f96d73"
    elif 52.51 <= pixelValue <= 56.25:
        return "#f84e78"
    elif 56.26 <= pixelValue <= 60:
        return "#f71e54"
    elif 60.01 <= pixelValue <= 63.75:
        return "#bf0000"
    elif 63.76 <= pixelValue <= 67.5:
        return "#880000"
    elif 67.51 <= pixelValue <= 71.25:
        return "#640000"
    elif 71.26 <= pixelValue <= 75:
        return "#2d0000"
    elif pixelValue > 75:
        return "#2d0000"
    else:
        return "none"


def color_pacum_weekly(pixelValue: float) -> str:
    """
    Returns the corresponding color for a given precipitation value based on 
    predefined ranges following the XML style.

    Parameters:
    -----------
      - pixelValue (float): The precipitation value to determine the color.

    Returns:
      - str: The color in hexadecimal format corresponding to the precipitation.
    """
    if pixelValue < 1:
        return "none"
    elif 1 <= pixelValue <= 10:
        return "#75baff" 
    elif 3.76 <= pixelValue <= 20:
        return "#359aff"
    elif 7.51 <= pixelValue <= 30:
        return "#0087ff"
    elif 11.26 <= pixelValue <= 40:
        return "#0674C6" 
    elif 15.01 <= pixelValue <= 50:
        return "#0C608D"
    elif 18.76 <= pixelValue <= 60:
        return "#148f1b"
    elif 22.51 <= pixelValue <= 70:
        return "#1acf05"
    elif 26.26 <= pixelValue <= 80:
        return "#63ed07"
    elif 30.01 <= pixelValue <= 90:
        return "#B1F119"
    elif 33.76 <= pixelValue <= 100:
        return "#d5f775"
    elif 37.51 <= pixelValue <= 110:
        return "#fff42b"
    elif 41.26 <= pixelValue <= 120:
        return "#ffcb4d"
    elif 45.01 <= pixelValue <= 130:
        return "#fb9a6f"
    elif 48.76 <= pixelValue <= 140:
        return "#f96d73"
    elif 52.51 <= pixelValue <= 150:
        return "#f84e78"
    elif 56.26 <= pixelValue <= 160:
        return "#f71e54"
    elif 60.01 <= pixelValue <= 170:
        return "#bf0000"
    elif 63.76 <= pixelValue <= 180:
        return "#880000"
    elif 67.51 <= pixelValue <= 190:
        return "#640000"
    elif 71.26 <= pixelValue <= 200:
        return "#2d0000"
    elif pixelValue > 200:
        return "#2d0000"
    else:
        return "none"





###############################################################################
#                               PLOTS FUNCTIONS                               #
###############################################################################
def plot_daily_forecast(raster:str) -> plt.Figure:
    """
    Generates a plot with a raster layer, overlaid with geometries from a 
    GeoDataFrame, and optionally adds basin layers and point markers. The 
    resulting plot is saved to a specified output path.

    Parameters:
    -----------
      - raster (str): Path to the raster file to be opened and processed.

    Returns:
    --------
      - matplotlib.Figure: The generated plot as a Matplotlib figure.
    """
    # Load shapefiles
    assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/celec/assets"
    ec = gpd.read_file(f"{assets_path}/ecuador_diss.shp")
    hydropowers = gpd.read_file(f"{assets_path}/hidroelectricas_mayores_50W.shp")
    agoyan = gpd.read_file(f"{assets_path}/agoyan.shp")
    coca = gpd.read_file(f"{assets_path}/coca.shp")
    delsintanisagua = gpd.read_file(f"{assets_path}/delsintanisagua.shp")
    due = gpd.read_file(f"{assets_path}/due.shp")
    jubones = gpd.read_file(f"{assets_path}/jubones.shp")
    paute = gpd.read_file(f"{assets_path}/paute.shp")
    pucara = gpd.read_file(f"{assets_path}/pucara.shp")

    # Abre el raster utilizando rasterio
    with rasterio.open(raster) as src:
        # Realiza el enmascaramiento del raster
        out_image, out_transform  = mask(src, ec.geometry, crop=True)
    
    # Crear una lista de valores entre 0 y 1
    mmin = out_image.min()
    mmax = out_image.max()
    rang = int(100 * (mmax - mmin))
    values = np.linspace(int(mmin), int(mmax), rang)
    
    # Crear un objeto ListedColormap basado en la lista de colores
    colors = [color_pacum_daily(value) for value in values]
    cmap_custom = ListedColormap(colors)
    
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.margins(0)
    plt.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.05)
    show(out_image, transform=out_transform, ax=ax, cmap=cmap_custom)
    ec.plot(ax=ax, color='none', edgecolor='black', linewidth=1)
    
    # Graficar las cuencas
    agoyan.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    coca.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    delsintanisagua.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    due.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    jubones.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    paute.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    pucara.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)  
    
    # Graficar los puntos del GeoDataFrame de puntos
    hydropowers.plot(ax=ax, color='red', marker='o', markersize=50, alpha=0.7)
    
    # Añadir las etiquetas de los puntos
    texts = []
    for idx, row in hydropowers.iterrows():
        point = row.geometry
        name = row["layer"]
        text = ax.text(
            point.x, point.y, 
            name, 
            fontsize=10,
            ha='right',
            color='black', 
            fontweight='bold')
        texts.append(text)
    
    # Ajustar las posiciones de las etiquetas para que no se superpongan
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='gray', lw=0.5))
    
    # Formatear y retornar
    ax.set_xlim(-81.3, -74.9)
    ax.set_ylim(-5.2, 1.6)
    ax.set_title("Pronóstico diario de precipitación (WRF)", fontsize=18)
    
    # Retorna la figura
    return fig




def plot_weekly_forecast(raster:str) -> plt.Figure:
    """
    Generates a plot with a raster layer, overlaid with geometries from a 
    GeoDataFrame, and optionally adds basin layers and point markers. The 
    resulting plot is saved to a specified output path.

    Parameters:
    -----------
      - raster (str): Path to the raster file to be opened and processed.

    Returns:
    --------
      - matplotlib.Figure: The generated plot as a Matplotlib figure.
    """
    # Load shapefiles
    assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/celec/assets"
    ec = gpd.read_file(f"{assets_path}/ecuador_diss.shp")
    hydropowers = gpd.read_file(f"{assets_path}/hidroelectricas_mayores_50W.shp")
    agoyan = gpd.read_file(f"{assets_path}/agoyan.shp")
    coca = gpd.read_file(f"{assets_path}/coca.shp")
    delsintanisagua = gpd.read_file(f"{assets_path}/delsintanisagua.shp")
    due = gpd.read_file(f"{assets_path}/due.shp")
    jubones = gpd.read_file(f"{assets_path}/jubones.shp")
    paute = gpd.read_file(f"{assets_path}/paute.shp")
    pucara = gpd.read_file(f"{assets_path}/pucara.shp")

    # Abre el raster utilizando rasterio
    with rasterio.open(raster) as src:
        # Realiza el enmascaramiento del raster
        out_image, out_transform  = mask(src, ec.geometry, crop=True)
    
    # Crear una lista de valores entre 0 y 1
    mmin = out_image.min()
    mmax = out_image.max()
    rang = int(100 * (mmax - mmin))
    values = np.linspace(int(mmin), int(mmax), rang)
    
    # Crear un objeto ListedColormap basado en la lista de colores
    colors = [color_pacum_weekly(value) for value in values]
    cmap_custom = ListedColormap(colors)
    
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.margins(0)
    plt.subplots_adjust(left=0.05, right=0.98, top=0.95, bottom=0.05)
    show(out_image, transform=out_transform, ax=ax, cmap=cmap_custom)
    ec.plot(ax=ax, color='none', edgecolor='black', linewidth=1)
    
    # Graficar las cuencas
    agoyan.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    coca.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    delsintanisagua.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    due.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    jubones.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    paute.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)
    pucara.plot(ax=ax, color='none', edgecolor='black', linewidth=1.5)  
    
    # Graficar los puntos del GeoDataFrame de puntos
    hydropowers.plot(ax=ax, color='red', marker='o', markersize=50, alpha=0.7)
    
    # Añadir las etiquetas de los puntos
    texts = []
    for idx, row in hydropowers.iterrows():
        point = row.geometry
        name = row["layer"]
        text = ax.text(
            point.x, point.y, 
            name, 
            fontsize=10,
            ha='right',
            color='black', 
            fontweight='bold')
        texts.append(text)
    
    # Ajustar las posiciones de las etiquetas para que no se superpongan
    adjust_text(texts, arrowprops=dict(arrowstyle="->", color='gray', lw=0.5))
    
    # Formatear y retornar
    ax.set_xlim(-81.3, -74.9)
    ax.set_ylim(-5.2, 1.6)
    ax.set_title("Pronóstico semanal de precipitación (WRF)", fontsize=18)
    
    # Retorna la figura
    return fig



def extract_raster_values_to_points(raster_path:str) -> pd.DataFrame:
    """
    Extracts raster values at the locations of points in the GeoDataFrame,
    and includes a specific field from the GeoDataFrame in the final table.

    Parameters:
    -----------
      - raster_path (str): Path to the raster file.

    Returns:
      - pd.DataFrame: Pandas DataFrame with the coordinates of the points, the 
            extracted raster values, and the specified field from the 
            GeoDataFrame.
    """
    # Load shapefiles
    assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/celec/assets"
    gdf = gpd.read_file(f"{assets_path}/hidroelectricas_mayores_50W.shp")

    # Open the raster file
    with rasterio.open(raster_path) as src:
        # Get the affine transformation (from pixel to coordinates)
        transform = src.transform
        
        # Create a list to store the extracted values
        data = []
        
        # Iterate over each point in the GeoDataFrame
        for idx, row in gdf.iterrows():
            # Get the geometry (point) and the value of the specified field
            point = row.geometry
            name = row["NombreCent"]
            
            # Get the coordinates of the point
            coord = (point.x, point.y)
            
            # Convert the point coordinates to pixel indices
            row_idx, col_idx = src.index(coord[0], coord[1])
            
            # Read the raster value at that location
            value = src.read(1)[row_idx, col_idx]
            
            # Store the value along with the point coordinates and 
            # the 'NombreCent' field
            data.append({
                'hydropower': name, 
                "forecast": round(value, 1)
            })
    
    return data
