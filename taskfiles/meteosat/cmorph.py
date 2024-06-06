import os
import logging
import rasterio
import meteosatpy
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from geo.Geoserver import Geoserver


###############################################################################
#                           ENVIROMENTAL VARIABLES                            #
###############################################################################

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("inamhi-geoglows/taskfiles/meteosat")

# Load enviromental
load_dotenv()
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")


###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
def mask(input_raster, bounds):
    """
    Applies a mask to the input raster within the specified bounds.
    
    Parameters:
        input_raster (str): Path to the input raster file.
        bounds (tuple): Geographic extent (west, south, east, north).
    """
    with rasterio.open(input_raster) as src:
        window = src.window(*bounds)
        data = src.read(window=window)
        data = np.where(data < 0, np.nan, data)
        transform = src.window_transform(window)
        profile = src.profile
        profile.update({
            'height': window.height,
            'width': window.width,
            'transform': transform
        })
        with rasterio.open(input_raster, 'w', **profile) as dst:
            dst.write(data)


def accum(archivos_geotiff):
    suma_geotiff = None
    for archivo in archivos_geotiff:
        with rasterio.open(archivo) as src:
            if suma_geotiff is None:
                suma_geotiff = src.read(1)
            else:
                try:
                    suma_geotiff += src.read(1)
                except:
                    print(f"No se pudo sumar un valor en archivo {archivo}")
    return(suma_geotiff)



###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
def download_cmorph_daily(date):
    # Configure log file
    log_file = f'cmorph-daily.log'
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    #
    # Instance the geoserver
    geo = Geoserver(
        'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
            username=GEOSERVER_USER, 
            password=GEOSERVER_PASS)
    #
    # File paths
    date_format = "%Y-%m-%d"
    outpath = date.strftime(f"{date_format}.tif")
    layer_name = date.strftime(date_format)
    #
    # Instance the meteosatpy for CHIRPS data
    cm = meteosatpy.CMORPH()
    bounds = (-94, -7.5, -70, 4)
    try:
        cm.download(date=date, timestep="daily", outpath=outpath)
    except Exception as e:
        logging.error(f"Error downloading data: {date}: {e}")
    #
    # Mask data to Ecuador extent
    mask(outpath, bounds)
    #
    # Publish raster data
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace=f'cmorph-daily')
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace=f'cmorph-daily')
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace=f'cmorph-daily')
    # Add styles
    geo.publish_style(
        layer_name=layer_name, 
        style_name=f'precipitation_style_cmorph_daily', 
        workspace=f'cmorph-daily')
    # Delete download file
    os.remove(outpath)



def download_cmorph_monthly(date_start, date_end):
    # Configure log file
    log_file = 'cmorph-monthly.log'
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    #
    # Instance the geoserver
    geo = Geoserver(
        'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
            username=GEOSERVER_USER, 
            password=GEOSERVER_PASS)
    #
    # Generate dates
    dates = pd.date_range(date_start, date_end, freq = "D")
    #
    # Sum precipitation
    pacum = None
    #
    for i in range(len(dates)):
        dd = dates[i].strftime('%Y-%m-%d')
        endpoint = "/usr/share/geoserver/data_dir/data"
        url = f"{endpoint}/cmorph-daily/{dd}/{dd}.geotiff"
        #
        if not os.path.exists(url):
            download_cmorph_daily(dates[i])
        #
        with rasterio.open(url) as src:
            if pacum is None:
                pacum = src.read(1)
            else:
                try:
                    pacum += src.read(1)
                except:
                    print(f"No se pudo sumar un valor: {url}")
    #
    # Crear una copia de uno de los archivos GeoTIFF para obtener los metadatos
    with rasterio.open(url) as src:
        perfil = src.profile
        perfil.update(count=1)
    #
    # Publish raster data
    date_format = "%Y-%m-01"
    layer_name = dates[0].strftime(date_format)
    outpath = dates[0].strftime(f"{date_format}.tif")
    #
    # Guardar el resultado en un nuevo archivo GeoTIFF
    with rasterio.open(outpath, 'w', **perfil) as dst:
        dst.write(pacum, 1)
    #
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace=f'cmorph-monthly')
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace=f'cmorph-monthly')
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace=f'cmorph-monthly')
    # Add styles
    geo.publish_style(
        layer_name=layer_name, 
        style_name=f'precipitation_style_cmorph_monthly', 
        workspace=f'cmorph-monthly')
    # Delete download file
    os.remove(outpath)


def download_cmorph_annual(date_start, date_end):
    # Configure log file
    log_file = 'cmorph-annual.log'
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    #
    # Instance the geoserver
    geo = Geoserver(
        'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
            username=GEOSERVER_USER, 
            password=GEOSERVER_PASS)
    #
    # Generate dates
    dates = pd.date_range(date_start, date_end, freq = "D")
    #
    # Sum precipitation
    pacum = None
    #
    for i in range(len(dates)):
        dd = dates[i].strftime('%Y-%m-%d')
        endpoint = "/usr/share/geoserver/data_dir/data"
        url = f"{endpoint}/cmorph-daily/{dd}/{dd}.geotiff"
        #
        if not os.path.exists(url):
            download_cmorph_daily(dates[i])
        #
        with rasterio.open(url) as src:
            if pacum is None:
                pacum = src.read(1)
            else:
                try:
                    pacum += src.read(1)
                except:
                    print(f"No se pudo sumar un valor: {url}")
    #
    # Crear una copia de uno de los archivos GeoTIFF para obtener los metadatos
    with rasterio.open(url) as src:
        perfil = src.profile
        perfil.update(count=1)
    #
    # Publish raster data
    date_format = "%Y-01-01"
    layer_name = dates[0].strftime(date_format)
    outpath = dates[0].strftime(f"{date_format}.tif")
    #
    # Guardar el resultado en un nuevo archivo GeoTIFF
    with rasterio.open(outpath, 'w', **perfil) as dst:
        dst.write(pacum, 1)
    #
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace=f'cmorph-annual')
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace=f'cmorph-annual')
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace=f'cmorph-annual')
    # Add styles
    geo.publish_style(
        layer_name=layer_name, 
        style_name=f'precipitation_style_cmorph_annual', 
        workspace=f'cmorph-annual')
    # Delete download file
    os.remove(outpath)






def download_cmorph(date_start, date_end, frequency):
    # Frequency 
    if frequency == "daily":
        dates = pd.date_range(date_start, date_end, freq = "D")
        for date in dates:
            try:
                download_cmorph_daily(date)
            except:
                download_cmorph_daily(date)
    #
    elif frequency == "monthly":
        dates_start = pd.date_range(date_start, date_end, freq = "MS")
        dates_end = pd.date_range(date_start, date_end, freq = "ME")
        for i in range(len(dates_start)):
            print(dates_start[i], dates_end[i])
            download_cmorph_monthly(dates_start[i], dates_end[i])
    #
    elif frequency == "annual":
        dates_start = pd.date_range(date_start, date_end, freq = "YS")
        dates_end = pd.date_range(date_start, date_end, freq = "YE")
        for i in range(len(dates_start)):
            print(dates_start[i], dates_end[i])
            download_cmorph_annual(dates_start[i], dates_end[i])



date_start = "1998-01-01"
date_end = "2023-12-31"

download_cmorph(date_start, date_end, "daily")
download_cmorph(date_start, date_end, "monthly")
download_cmorph(date_start, date_end, "annual")




