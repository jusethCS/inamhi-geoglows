import os
import rasterio
import meteosatpy
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timedelta
from hs_restclient import HydroShare, HydroShareAuthBasic


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
HS_USER=os.getenv("HS_USER")
HS_PASS=os.getenv("HS_PASS")
HS_IDRS=os.getenv("HS_IDRS")

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
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
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


auth = HydroShareAuthBasic(username=HS_USER, password=HS_PASS)
hs = HydroShare(auth=auth)
local_file = "pacum-cut.tif"
resource_filename = f"pacum_persiann_daily7.tif"
try:
    hs.deleteResourceFile(HS_IDRS,  resource_filename)
except:
    hs.addResourceFile(HS_IDRS, local_file, resource_filename)
    hs.resource(HS_IDRS).public(True)
    hs.resource(HS_IDRS).shareable(True)
    print("Uploaded data!")


for f in os.listdir():
        os.remove(f)

# https://www.hydroshare.org/resource/925ad37f78674d578eab2494e13db240/data/contents/pacum_persiann_daily7.tif
# http://ec2-3-211-227-44.compute-1.amazonaws.com:4200/data/dpa/pacum-persiann-pdir/pacum-persiann-pdir.geotiff