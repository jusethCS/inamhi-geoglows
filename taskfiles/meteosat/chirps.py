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
        'https://inamhi.geoglows.org/geoserver', 
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
            print("")
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


###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
import datetime
import calendar
from dateutil.relativedelta import relativedelta

# Update datetime (now)
actual_date = datetime.date.today()

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("logs")

## Downloaded daily data
try:
    start_date = (actual_date - relativedelta(months=1)).strftime("%Y-%m-01")
    end_date = actual_date.strftime("%Y-%m-%d")
    download_chirps(start_date, end_date, "daily")
except:
    print("Downloaded daily data")


## Download monthly data
try:
    lmd = calendar.monthrange(actual_date.year, actual_date.month)[1]
    last_month_day = datetime.date(actual_date.year, actual_date.month, lmd)
    start_date = (actual_date - relativedelta(months=3)).strftime("%Y-%m-01")
    end_date = last_month_day.strftime("%Y-%m-%d")
    download_chirps(start_date, end_date, "monthly")
except:
    print("Downloaded monthly data")


## Download yearly data
try:
    start_date = (actual_date - relativedelta(years=3)).strftime("%Y-01-01")
    end_date = datetime.date(actual_date.year, 12, 31).strftime("%Y-%m-%d")
    download_chirps(start_date, end_date, "annual")
except:
    print("Donwloaded annual data")

