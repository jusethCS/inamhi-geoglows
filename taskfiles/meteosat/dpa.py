import os
import rasterio
import numpy as np
import pandas as pd
import meteosatpy
from dotenv import load_dotenv
from datetime import datetime, timedelta
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
def mask(input_raster, output_raster, bounds):
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
        with rasterio.open(output_raster, 'w', **profile) as dst:
            dst.write(data)


###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
os.chdir(user_dir)
os.chdir("data/dpa")

now = datetime.now()
end = now.replace(hour=12, minute=0, second=0, microsecond=0)
start = end - timedelta(days=1)

dates = pd.date_range(start, end, freq = "h")
bounds = (-94, -7.5, -70, 4)

ch = meteosatpy.PERSIANN()

for date in dates:
    print(date)
    filename = date.strftime("%Y%m%d%H00.tif")
    try:
        ch.download(date=date, timestep="hourly", outpath=filename, dataset="PDIR")
    except:
        try:
            ch.download(date=date, timestep="hourly", outpath=filename, dataset="PDIR")
        except:
            print(f"Fail: {date}")


archivos_geotiff = []
for archivo in os.listdir():
    if archivo.endswith('.tif'):
        archivos_geotiff.append(archivo)

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

with rasterio.open(archivos_geotiff[0]) as src:
    perfil = src.profile
    perfil.update(count=1)

with rasterio.open('pacum.tif', 'w', **perfil) as dst:
    dst.write(suma_geotiff, 1)

mask('pacum.tif', "pacum-cut.tif", bounds)


geo = Geoserver(
    'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
    username=GEOSERVER_USER, password=GEOSERVER_PASS)

try:
    geo.create_coveragestore(layer_name="pacum-persiann-pdir", path="pacum-cut.tif", workspace="dpa")
    geo.publish_style(layer_name="pacum-persiann-pdir", style_name='pacum', workspace='dpa')
except:
    geo.delete_coveragestore(coveragestore_name="pacum-persiann-pdir", workspace='dpa')
    geo.create_coveragestore(layer_name="pacum-persiann-pdir", path="pacum-cut.tif", workspace="dpa")
    geo.publish_style(layer_name="pacum-persiann-pdir", style_name='pacum', workspace='dpa')

for f in os.listdir():
        os.remove(f)


# http://ec2-3-211-227-44.compute-1.amazonaws.com:4200/data/dpa/pacum-persiann-pdir/pacum-persiann-pdir.geotiff