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
#                                RGB PRODUCTS                                 #
###############################################################################

def get_latlon(raster_path):
    with rasterio.open(raster_path) as src:
        # Obtener las dimensiones del raster
        height, width = src.shape
        transform = src.transform
    #
    # Crear matrices de índice de fila y columna
    rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
    #
    # Calcular las matrices de latitud y longitud
    lons, lats = rasterio.transform.xy(transform, rows, cols)
    lons = np.array(lons)
    lats = np.array(lats)
    return(lats, lons)


def fire_temperature_rgb(R_PATH, G_PATH, B_PATH, output):
    # Determinate if exist
    cond_R = os.path.isfile(R_PATH)
    cond_G = os.path.isfile(G_PATH)
    cond_B = os.path.isfile(B_PATH)
    #
    # If exist, compute the fire product
    if (cond_R and cond_G and cond_B):
        with rasterio.open(R_PATH) as src:
            R = src.read(1)
            profile = src.profile
        #
        with rasterio.open(G_PATH) as src:
            G = src.read(1)
        #
        with rasterio.open(B_PATH) as src:
            B = src.read(1)
        #
        # Update the geotiff profile
        profile.update(count=3, dtype=rasterio.uint8)
        #
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
        # Scale to 0-255 and convert to uint8
        R = (R * 255).astype(np.uint8)
        G = (G * 255).astype(np.uint8)
        B = (B * 255).astype(np.uint8)
        #
        # Write the RGB file
        with rasterio.open(output, 'w', **profile) as dst:
            dst.write(R, 1)
            dst.write(G, 2)
            dst.write(B, 3) 



def day_cloud_phase_rgb(R_PATH, G_PATH, B_PATH, output):
    # Determinate if exist
    cond_R = os.path.isfile(R_PATH)
    cond_G = os.path.isfile(G_PATH)
    cond_B = os.path.isfile(B_PATH)
    #
    # If exist, compute the fire product
    if (cond_R and cond_G and cond_B):
        with rasterio.open(R_PATH) as src:
            R = src.read(1)
            profile = src.profile
        #
        with rasterio.open(G_PATH) as src:
            G = src.read(1)
        #
        with rasterio.open(B_PATH) as src:
            B = src.read(1)
        #
        # Update the geotiff profile
        profile.update(count=3, dtype=rasterio.uint8)
        #
        # Normalize each channel by the appropriate range of values
        R = (R-280)/(219-280)
        G = (G-0)/(0.78-0)
        B = (B-0.01)/(0.59-0.01)
        #
        # Apply range limits for each channel. 
        R = np.clip(R, 0, 1)
        G = np.clip(G, 0, 1)
        B = np.clip(B, 0, 1)
        #
        # Scale to 0-255 and convert to uint8
        R = (R * 255).astype(np.uint8)
        G = (G * 255).astype(np.uint8)
        B = (B * 255).astype(np.uint8)
        #
        # Write the RGB file
        with rasterio.open(output, 'w', **profile) as dst:
            dst.write(R, 1)
            dst.write(G, 2)
            dst.write(B, 3) 



def true_color_rgb(R_PATH, G_PATH, B_PATH, output):
    # Determinate if exist
    cond_R = os.path.isfile(R_PATH)
    cond_G = os.path.isfile(G_PATH)
    cond_B = os.path.isfile(B_PATH)
    #
    # If exist, compute the fire product
    if (cond_R and cond_G and cond_B):
        with rasterio.open(R_PATH) as src:
            R = src.read(1)
            profile = src.profile
        #
        with rasterio.open(G_PATH) as src:
            G = src.read(1)
        #
        with rasterio.open(B_PATH) as src:
            B = src.read(1)
        #
        # Update the geotiff profile
        profile.update(count=3, dtype=rasterio.uint8)
        #
        # Apply range limits for each channel. 
        R = np.clip(R, 0, 1)
        G = np.clip(G, 0, 1)
        B = np.clip(B, 0, 1)
        #
        # Apply a gamma correction to the image to correct ABI detector brightness
        gamma = 2.2
        R = np.power(R, 1/gamma)
        G = np.power(G, 1/gamma)
        B = np.power(B, 1/gamma)
        #
        # Generate the true green
        G = 0.45 * R + 0.1 * G + 0.45 * B
        G = np.clip(G, 0, 1)
        #
        # Scale to 0-255 and convert to uint8
        R = (R * 255).astype(np.uint8)
        G = (G * 255).astype(np.uint8)
        B = (B * 255).astype(np.uint8)
        #
        # Write the RGB file
        with rasterio.open(output, 'w', **profile) as dst:
            dst.write(R, 1)
            dst.write(G, 2)
            dst.write(B, 3) 




###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
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
os.chdir("/home/ubuntu/data/goes/")


workdir = "/usr/share/geoserver/data_dir/data"
path_b01 = f"{workdir}/GOES-ABI-L2-CMIPF-01"
path_b02 = f"{workdir}/GOES-ABI-L2-CMIPF-02"
path_b03 = f"{workdir}/GOES-ABI-L2-CMIPF-03"
path_b05 = f"{workdir}/GOES-ABI-L2-CMIPF-05"
path_b06 = f"{workdir}/GOES-ABI-L2-CMIPF-06"
path_b07 = f"{workdir}/GOES-ABI-L2-CMIPF-07"
path_b13 = f"{workdir}/GOES-ABI-L2-CMIPF-13"

files = os.listdir(path_b02)
files.sort()
files = files[-5:]




for filename in files:
    # Generate file path
    print(filename)
    file_b01 = f"{path_b01}/{filename}/{filename}.geotiff"
    file_b02 = f"{path_b02}/{filename}/{filename}.geotiff"
    file_b03 = f"{path_b03}/{filename}/{filename}.geotiff"
    file_b05 = f"{path_b05}/{filename}/{filename}.geotiff"
    file_b06 = f"{path_b06}/{filename}/{filename}.geotiff"
    file_b07 = f"{path_b07}/{filename}/{filename}.geotiff"
    file_b13 = f"{path_b13}/{filename}/{filename}.geotiff"
    #
    # Fire temperature
    try:
        fire_temperature_rgb(
            R_PATH = file_b07, 
            G_PATH = file_b06, 
            B_PATH = file_b05, 
            output = f"RGB-FIRE-TEMPERATURE/{filename}.tif")
        upload_geoserver(
            layer_name = filename, 
            file_path = f"RGB-FIRE-TEMPERATURE/{filename}.tif", 
            workspace = "GOES-RGB-FIRE-TEMPERATURE")
        os.remove(f"RGB-FIRE-TEMPERATURE/{filename}.tif")
    except:
        print(f"Fire temperature {filename} no uploaded to geoserver")
    #
    # Day Cloud phase
    try:
        day_cloud_phase_rgb(
            R_PATH = file_b13, 
            G_PATH = file_b02, 
            B_PATH = file_b05, 
            output = f"RGB-DAY-CLOUD-PHASE/{filename}.tif")
        upload_geoserver(
            layer_name = filename, 
            file_path = f"RGB-DAY-CLOUD-PHASE/{filename}.tif", 
            workspace = "GOES-RGB-DAY-CLOUD-PHASE")
        os.remove(f"RGB-DAY-CLOUD-PHASE/{filename}.tif")
    except:
        print(f"Day cloud phase {filename} no uploaded to geoserver")
    #
    # True color
    try:
        true_color_rgb(
            R_PATH = file_b02, 
            G_PATH = file_b03, 
            B_PATH = file_b01, 
            output = f"RGB-TRUE-COLOR/{filename}.tif")
        upload_geoserver(
            layer_name = filename, 
            file_path = f"RGB-TRUE-COLOR/{filename}.tif", 
            workspace = "GOES-RGB-TRUE-COLOR")
        os.remove(f"RGB-TRUE-COLOR/{filename}.tif")
    except:
        print(f"Day cloud phase {filename} no uploaded to geoserver")
    


delete_coverage("GOES-RGB-FIRE-TEMPERATURE")
delete_coverage("GOES-RGB-DAY-CLOUD-PHASE")
delete_coverage("GOES-RGB-TRUE-COLOR")



