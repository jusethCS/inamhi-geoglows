import os
import logging
import rasterio
import meteosatpy
import numpy as np
import pandas as pd
from geo.Geoserver import Geoserver


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

# Configure log file
logging.basicConfig(filename='chirps-monthly.log', level=logging.ERROR)

# Instance the geoserver
geo = Geoserver(
    'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
    username='admin', 
    password='geoserver')

# Date range and bounds
dates = pd.date_range("1981-01-01", "2024-03-31", freq = "ME")
bounds = (-94, -7.5, -70, 4)

# Instance the meteosatpy for CHIRPS data
ch = meteosatpy.CHIRPS()

# Donwnload and publish CHIRPS data
for i in range(len(dates)):
    # File paths
    outpath = dates[i].strftime("%Y-%m-01.tif")
    layer_name = dates[i].strftime("%Y-%m-01")
    # Try to download data, retrying if there's an error
    try:
        ch.download(date=dates[i], timestep="monthly", outpath=outpath)
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
            workspace='chirps-monthly')
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace='chirps-monthly')
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=outpath, 
            workspace='chirps-monthly')
    # Add styles
    geo.publish_style(
        layer_name=layer_name, 
        style_name='pacum-monthly', 
        workspace='chirps-monthly')
    # Delete download file
    os.remove(outpath)







