import os
import datetime
import rasterio
import numpy as np
import pandas as pd
import subprocess
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from dateutil.relativedelta import relativedelta

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
def write_RGB(R, G, B, profile, output):
    # Normalize each channel by the appropriate range of values
    R = (R-273)/(333-273)
    G = (G-0)/(1-0)
    B = (B-0)/(0.75-0)
    #
    # Apply range limits for each channel. 
    R = np.clip(R, 0, 1)
    G = np.clip(G, 0, 1)
    B = np.clip(B, 0, 1)
    #
    # Apply the gamma correction to Red channel.
    gamma = 0.4
    R = np.power(R, 1/gamma)
    #
    # Write the RGB file
    with rasterio.open(output, 'w', **profile) as dst:
        dst.write(R, 1)
        dst.write(G, 2)
        dst.write(B, 3) 


def upload_geoserver(layer_name, file_path, workspace):
    # Instance the geoserver
    geo = Geoserver(
            'https://inamhi.geoglows.org/geoserver', 
                username=GEOSERVER_USER, 
                password=GEOSERVER_PASS)
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=file_path, 
            workspace=workspace)
        geo.publish_style(
            layer_name=layer_name, 
            style_name="rgb_style", 
            workspace=workspace)
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace=workspace)
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=file_path, 
            workspace=workspace)
        geo.publish_style(
            layer_name=layer_name, 
            style_name="rgb_style", 
            workspace=workspace)


def delete_coverage(workspace):
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
        filedir = f"{endpoint}/{workspace}/{layer_name}"
        if os.path.exists(f"{filedir}/{layer_name}.geotiff"):
            try:
                comando = ['sudo', 'rm', '-rf', filedir]
                subprocess.run(comando, check=True, text=True, capture_output=True)
                geo.delete_coveragestore(
                    coveragestore_name=layer_name, 
                    workspace=f'{workspace}')
                print(f"File :{layer_name} was deleted!")
            except Exception as e:
                print(e)
                print(f"File {workspace}:{layer_name} cannot be deleted!")

   

###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
os.chdir("/home/ubuntu/data/goes/ABI-L2-FIRE")


workdir = "/usr/share/geoserver/data_dir/data"
path_b05 = f"{workdir}/GOES-ABI-L2-CMIPF-05"
path_b06 = f"{workdir}/GOES-ABI-L2-CMIPF-06"
path_b07 = f"{workdir}/GOES-ABI-L2-CMIPF-07"


files = os.listdir(path_b05)
files.sort()
files = files[-5:]

for filename in files:
    # Generate file path
    print(filename)
    file_b05 = f"{path_b05}/{filename}/{filename}.geotiff"
    file_b06 = f"{path_b06}/{filename}/{filename}.geotiff"
    file_b07 = f"{path_b07}/{filename}/{filename}.geotiff"
    #
    # Determinate if exist
    cond_b05 = os.path.isfile(file_b05)
    cond_b06 = os.path.isfile(file_b06)
    cond_b07 = os.path.isfile(file_b07)
    #
    # If exist, compute the fire product
    if (cond_b05 and cond_b06 and cond_b07):
        with rasterio.open(file_b07) as src:
            R = src.read(1)
            profile = src.profile
        #
        with rasterio.open(file_b06) as src:
            G = src.read(1)
        #
        with rasterio.open(file_b05) as src:
            B = src.read(1)
        #
        # Update the geotiff profile
        profile.update(count=3) #, dtype=rasterio.uint8)
        #
        # Generate and upload the fire product
        write_RGB(R, G, B, profile, f"{filename}.tif")
        upload_geoserver(filename, f"{filename}.tif", "GOES-fire-product")
        os.remove(f"{filename}.tif")


delete_coverage("GOES-fire-product")












