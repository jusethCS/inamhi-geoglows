import os
import time
import glob
import GOES
import datetime
import numpy as np
import pandas as pd
import pyproj as pyproj
from pyresample import utils
from dotenv import load_dotenv
from pyresample.geometry import SwathDefinition
from pyresample.kd_tree import resample_nearest
from dateutil.relativedelta import relativedelta
import rasterio
from rasterio.transform import from_bounds
from rasterio.crs import CRS

import sqlalchemy as sql
from sqlalchemy import create_engine



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
    CMI, LonCen, LatCen = ds.image('Power', lonlat='center', domain=domain)
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


def tif_to_dataframe(tif_path):
    # Abrir el archivo TIFF
    with rasterio.open(tif_path) as src:
        # Leer la primera banda (asumimos que solo hay una banda)
        band = src.read(1) 
        # Obtener los valores transformados (para las coordenadas)
        transform = src.transform
        # Crear listas para almacenar los datos
        latitudes = []
        longitudes = []
        # Iterar sobre cada píxel
        for row in range(band.shape[0]):
            for col in range(band.shape[1]):
                # Obtener el valor del píxel
                value = band[row, col]   
                # Ignorar los valores nulos (generalmente se considera que los nulos son NaN o nodata)
                if not np.isnan(value) and value != src.nodata:
                    # Convertir el índice de la fila y columna en coordenadas
                    lon, lat = rasterio.transform.xy(transform, row, col)
                    # Almacenar las coordenadas y el valor
                    latitudes.append(lat)
                    longitudes.append(lon)
        # Crear un DataFrame con las coordenadas y valores
        df = pd.DataFrame({
            'latitude': latitudes,
            'longitude': longitudes
        })
    return df




def goes_hotspot(product, workdir):     
    # Generate dates (start and end)
    now = datetime.datetime.now()
    start = now - relativedelta(minutes=30)
    end = now + relativedelta(minutes=30)
    start_str = start.strftime("%Y%m%d-%H%M00")
    end_str = end.strftime("%Y%m%d-%H%M00")
    workdir = f"{workdir}/{product}/"
    os.chdir(workdir)
    #
    try:
        GOES.download('goes16', product, DateTimeIni = start_str, DateTimeFin = end_str,  path_out=workdir)
    except:
        pass
    #
    # List NC files
    nc_files = glob.glob("*.nc")
    #
    # Upload data into geoserver
    for nc_file in nc_files:
        start = extract_datetime_from_path(nc_file)
        print(start.strftime(f'{product} - %Y-%m-%d %H:%M'))
        layer_name = start.strftime('%Y%m%d%H%M')
        outpath = start.strftime('%Y%m%d%H%M.tif')
        try:
            parse_goes(nc_file, outpath, 2)
        except:
            print("GOES data was not parse to TIFF")
            pass
    #
    # List TIFF files
    tif_files = glob.glob("*.tif")
    tif_files.sort()
    #
    print(tif_files[-1])
    data = tif_to_dataframe(tif_files[-1])
    data["datetime"] = pd.to_datetime(tif_files[-1].replace(".tif", ""), format="%Y%m%d%H%M")
    #
    # Remove data
    for archivo in os.listdir(workdir):
        ruta_completa = os.path.join(workdir, archivo)
        if os.path.isfile(ruta_completa):
            os.unlink(ruta_completa)
    return(data)
    



###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
os.chdir("/home/ubuntu/inamhi-geoglows")

# Import enviromental variables
load_dotenv("db.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

# Change the work directory
workdir = "/home/ubuntu/data/goes"
product = "ABI-L2-FDCF"
hotspots = goes_hotspot(product, workdir)
hotspots.to_sql('goes_hotspots', con=con, if_exists='append', index=False)
print(hotspots)
con.commit()
con.close()


