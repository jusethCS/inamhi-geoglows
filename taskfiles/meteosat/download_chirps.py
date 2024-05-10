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
# inamhi-geoglows/taskfiles/meteosat/
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





###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
def download_chirps(date_start, date_end, frequency):
    # Configure log file
    log_file = f'chirps-{frequency}.log'
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    #
    # Instance the geoserver
    geo = Geoserver(
        'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
            username=GEOSERVER_USER, 
            password=GEOSERVER_PASS)
    #
    # Frequency 
    if frequency == "daily":
        freq = "D"
        date_format = "%Y-%m-%d"
    elif frequency == "monthly":
        freq = "ME"
        date_format = "%Y-%m-01"
    elif frequency == "annual":
        freq = "YE"
        date_format = "%Y-01-01"
    else:
        return("Frecuency could be 'daily', 'monthly', 'annual'.")
    #
    # Date range and bounds
    dates = pd.date_range(date_start, date_end, freq = freq)
    bounds = (-94, -7.5, -70, 4)
    #
    # Instance the meteosatpy for CHIRPS data
    ch = meteosatpy.CHIRPS()
    #
    # Donwnload and publish CHIRPS data
    for i in range(len(dates)):
        # File paths
        outpath = dates[i].strftime(f"{date_format}.tif")
        layer_name = dates[i].strftime(date_format)
        # Try to download data, retrying if there's an error
        try:
            ch.download(date=dates[i], timestep=frequency, outpath=outpath)
        except Exception as e:
            logging.error(f"Error downloading data: {dates[i]}: {e}")
            continue
        # Mask data to Ecuador extent
        mask(outpath, bounds)
        # Publish raster data
        try:
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'chirps-{frequency}')
        except:
            geo.delete_coveragestore(
                coveragestore_name=layer_name, 
                workspace=f'chirps-{frequency}')
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'chirps-{frequency}')
        # Add styles
        geo.publish_style(
            layer_name=layer_name, 
            style_name=f'precipitation_style_chirps_{frequency}', 
            workspace=f'chirps-{frequency}')
        # Delete download file
        os.remove(outpath)



date_start = "1981-01-01"
date_end = "2024-05-01"
frequency = "annual"

download_chirps(date_start, date_end, frequency)
