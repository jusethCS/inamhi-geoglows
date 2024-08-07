import os
import time
import glob
import GOES
import datetime
import subprocess
import numpy as np
import pandas as pd
import pyproj as pyproj
from pyresample import utils
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from pyresample.geometry import SwathDefinition
from pyresample.kd_tree import resample_nearest
from dateutil.relativedelta import relativedelta
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS


###############################################################################
#                           ENVIROMENTAL VARIABLES                            #
###############################################################################
# Load enviromental
load_dotenv("/home/ubuntu/inamhi-geoglows/taskfiles/meteosat/.env")
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")



###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
def parse_goes(path, outpath, pixel):
    """
    Parse y procesa un archivo de datos GOES para generar una imagen GeoTIFF.

    Parámetros:
        path : str
            Ruta al archivo de datos GOES.
        outpath : str
            Ruta al archivo geotiff de salida
    """
    # Abre el conjunto de datos GOES
    ds = GOES.open_dataset(path)
    #
    # Define el dominio de interés [LonMin, LonMax, LatMin, LatMax]
    domain = [-94, -70, -7.5, 4]
    #
    # Extrae la imagen CMI y las coordenadas de longitud y latitud de los centros de las celdas
    CMI, LonCen, LatCen = ds.image('CMI', lonlat='center', domain=domain)
    #
    # Extrae atributos específicos del satélite y de la banda
    sat = ds.attribute('platform_ID')
    band = ds.variable('band_id').data[0]
    wl = ds.variable('band_wavelength').data[0]
    standard_name = CMI.standard_name
    units = CMI.units
    time_bounds = CMI.time_bounds
    #
    # Crea una rejilla de mapa en proyección cilíndrica equidistante
    LonCenCyl, LatCenCyl = GOES.create_gridmap(domain, PixResol=pixel)
    #
    # Define la proyección utilizando pyproj
    Prj = pyproj.Proj('+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +a=6378.137 +b=6378.137 +units=km')
    #
    # Identificadores y parámetros de la proyección
    AreaID = 'cyl'
    AreaName = 'cyl'
    ProjID = 'cyl'
    Proj4Args = '+proj=eqc +lat_ts=0 +lat_0=0 +lon_0=0 +x_0=0 +y_0=0 +a=6378.137 +b=6378.137 +units=km'
    #
    # Calcula el número de píxeles en las direcciones y y x
    ny, nx = LonCenCyl.data.shape
    #
    # Determina la extensión del área en la proyección
    SW = Prj(LonCenCyl.data.min(), LatCenCyl.data.min())
    NE = Prj(LonCenCyl.data.max(), LatCenCyl.data.max())
    area_extent = [SW[0], SW[1], NE[0], NE[1]]
    #
    # Define el área en la proyección cilíndrica equidistante
    AreaDef = utils.get_area_def(AreaID, AreaName, ProjID, Proj4Args, nx, ny, area_extent)
    #
    # Define el área de muestreo utilizando las coordenadas de la rejilla original
    SwathDef = SwathDefinition(lons=LonCen.data, lats=LatCen.data)
    #
    # Re-muestrea los datos a la nueva rejilla
    CMICyl = resample_nearest(SwathDef, CMI.data, AreaDef, radius_of_influence=6000,
                              fill_value=np.nan, epsilon=3, reduce_data=True)
    #
    # Definir la transformación afín usando los límites del dominio
    lon_min, lon_max, lat_min, lat_max = domain
    transform = from_bounds(lon_min, lat_min, lon_max, lat_max, nx, ny)
    #
    # Definir el sistema de coordenadas (CRS)
    crs = CRS.from_epsg(4326)
    #
    # Guardar los datos en un archivo GeoTIFF
    with rasterio.open(
        outpath,
        'w',
        driver='GTiff',
        height=CMICyl.shape[0],
        width=CMICyl.shape[1],
        count=1,
        dtype=CMICyl.dtype,
        crs=crs,
        transform=transform,
    ) as dst:
        dst.write(CMICyl, 1)



def extract_datetime_from_path(path):
    # Encuentra la posición del bloque que comienza con 's'
    start_index = path.find('s') + 1
    datetime_str = path[start_index:start_index + 14]
    #
    # Extrae los componentes del bloque
    year = int(datetime_str[0:4])
    day_of_year = int(datetime_str[4:7])
    hour = int(datetime_str[7:9])
    minute = int(datetime_str[9:11])
    #
    # Convierte el día juliano a una fecha
    date = datetime.datetime(year, 1, 1) + relativedelta(days=day_of_year-1)
    #
    # Añade la hora y los minutos
    date_time = date.replace(hour=hour, minute=minute)
    return date_time


def goes_to_geoserver(product, band, workdir, pixelBand, styled=False):     
    # Generate dates (start and end)
    now = datetime.datetime.now()
    start = now - relativedelta(minutes=30)
    end = now + relativedelta(minutes=30)
    start_str = start.strftime("%Y%m%d-%H%M00")
    end_str = end.strftime("%Y%m%d-%H%M00")
    workdir = f"{workdir}/{product}-{band}/"
    os.chdir(workdir)
    #
    # Instance the geoserver
    geo = Geoserver(
            'https://inamhi.geoglows.org/geoserver', 
                username=GEOSERVER_USER, 
                password=GEOSERVER_PASS)
    #
    # Download data
    try:
        GOES.download('goes16', product,
                DateTimeIni = start_str, DateTimeFin = end_str, 
                channel = [band], path_out=workdir)
        print("Downloaded GOES data")
    except:
        print("Downloaded GOES data")
    #
    # List NC files
    nc_files = glob.glob("*.nc")
    #
    # Upload data into geoserver
    for nc_file in nc_files:
        start = extract_datetime_from_path(nc_file)
        print(start.strftime(f'{product} Band:{band} - %Y-%m-%d %H:%M'))
        layer_name = start.strftime('%Y%m%d%H%M')
        outpath = start.strftime('%Y%m%d%H%M.tif')
        try:
            parse_goes(nc_file, outpath, pixelBand)
        except:
            print("GOES data was not parse to TIFF")
            pass
        try:
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'GOES-{product}-{band}')
            if styled:
                geo.publish_style(
                    layer_name=layer_name, 
                    style_name=f'GOES-{product}-{band}', 
                    workspace=f'GOES-{product}-{band}')
        except:
            geo.delete_coveragestore(
                coveragestore_name=layer_name, 
                workspace=f'GOES-{product}-{band}')
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'GOES-{product}-{band}')
            if styled:
                geo.publish_style(
                    layer_name=layer_name, 
                    style_name=f'GOES-{product}-{band}', 
                    workspace=f'GOES-{product}-{band}')
        time.sleep(2)
    #
    # Remove NC data
    for archivo in os.listdir(workdir):
        ruta_completa = os.path.join(workdir, archivo)
        if os.path.isfile(ruta_completa):
            os.unlink(ruta_completa)

def delete_coverage(product, band):
    # Generate dates (start and end)
    now = datetime.datetime.now()
    start = now - relativedelta(days=10)
    end = now - relativedelta(hours=12)
    date_range = pd.date_range(start, end, freq="1T")
    #
    # Variables
    endpoint = "/usr/share/geoserver/data_dir/data"
    #
    # Instance the geoserver
    geo = Geoserver(
            'https://inamhi.geoglows.org/geoserver', 
                username=GEOSERVER_USER, 
                password=GEOSERVER_PASS)
    #
    for date in date_range:
        layer_name = date.strftime('%Y%m%d%H%M')
        filedir = f"{endpoint}/GOES-{product}-{band}/{layer_name}"
        if os.path.exists(f"{filedir}/{layer_name}.geotiff"):
            try:
                comando = ['sudo', 'rm', '-rf', filedir]
                subprocess.run(comando, check=True, text=True, capture_output=True)
                geo.delete_coveragestore(
                    coveragestore_name=layer_name, 
                    workspace=f'GOES-{product}-{band}')
                print(f"File {product}-{band}:{layer_name} was deleted!")
            except Exception as e:
                print(e)
                print(f"File {product}-{band}:{layer_name} cannot be deleted!")


###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
# Change the work directory
workdir = "/home/ubuntu/data/goes"

# GOES variables
product = "ABI-L2-CMIPF"

# Brigthness temperature Bands
goes_to_geoserver(product=product, band="08", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="08")

goes_to_geoserver(product=product, band="09", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="09")

goes_to_geoserver(product=product, band="10", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="10")

goes_to_geoserver(product=product, band="11", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="11")

goes_to_geoserver(product=product, band="12", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="12")

goes_to_geoserver(product=product, band="13", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="13")

goes_to_geoserver(product=product, band="14", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="14")

goes_to_geoserver(product=product, band="15", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="15")

goes_to_geoserver(product=product, band="16", workdir=workdir, styled=True, pixelBand=0.5)
delete_coverage(product=product, band="16")
