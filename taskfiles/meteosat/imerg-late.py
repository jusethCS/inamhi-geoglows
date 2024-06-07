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
NASA_USER = os.getenv("NASA_USER")
NASA_PASS = os.getenv("NASA_PASS")


###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
def mask(input_raster, bounds, correct_factor):
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
        data = data * correct_factor
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
# Instance the meteosatpy for CHIRPS data
ch = meteosatpy.IMERG(user=NASA_USER, pw=NASA_PASS)

def download_imerg(date_start, date_end, frequency):
    # Configure log file
    log_file = f'imerg-late-{frequency}.log'
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
        freq2 = "D"
        date_format = "%Y-%m-%d"
        correct_factor = 1
        vv = "v06"
    elif frequency == "monthly":
        freq = "MS"
        freq2 = "ME"
        date_format = "%Y-%m-01"
        correct_factor = 1
        vv = "v06"
    elif frequency == "annual":
        freq = "YS"
        freq2 = "YE"
        date_format = "%Y-01-01"
        correct_factor = 1
        vv = "v06"
    else:
        return("Frecuency could be 'daily', 'monthly', 'annual'.")
    #
    # Date range and bounds
    dates = pd.date_range(date_start, date_end, freq = freq)
    dates2 = pd.date_range(date_start, date_end, freq = freq2)
    bounds = (-94, -7.5, -70, 4)
    #
    # Donwnload and publish CHIRPS data
    for i in range(len(dates)):
        # File paths
        outpath = dates[i].strftime(f"{date_format}.tif")
        layer_name = dates[i].strftime(date_format)
        # Try to download data, retrying if there's an error
        try:
            if(frequency == "annual"):
                pacum = None
                dd_range = pd.date_range(dates[i], dates2[i], freq = "MS")
                #
                for i in range(len(dd_range)):
                    dd = dd_range[i].strftime('%Y-%m-%d')
                    endpoint = "/usr/share/geoserver/data_dir/data"
                    url = f"{endpoint}/imerg-late-monthly/{dd}/{dd}.geotiff"
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
                with rasterio.open(url) as src:
                    perfil = src.profile
                    perfil.update(count=1)
                #
                # Guardar el resultado en un nuevo archivo GeoTIFF
                with rasterio.open(outpath, 'w', **perfil) as dst:
                    dst.write(pacum, 1)
            #
            elif(frequency == "monthly"):
                pacum = None
                dd_range = pd.date_range(dates[i], dates2[i], freq = "D")
                #
                for i in range(len(dd_range)):
                    dd = dd_range[i].strftime('%Y-%m-%d')
                    endpoint = "/usr/share/geoserver/data_dir/data"
                    url = f"{endpoint}/imerg-late-daily/{dd}/{dd}.geotiff"
                    #
                    try:
                        with rasterio.open(url) as src:
                            if pacum is None:
                                pacum = src.read(1)
                            else:
                                try:
                                    pacum += src.read(1)
                                except:
                                    print(f"No se pudo sumar un valor: {url}")
                    except:
                        print(f"No se puedo sumar el mes: {url}")
                #
                with rasterio.open(url) as src:
                    perfil = src.profile
                    perfil.update(count=1)
                #
                # Guardar el resultado en un nuevo archivo GeoTIFF
                with rasterio.open(outpath, 'w', **perfil) as dst:
                    dst.write(pacum, 1)
            else:
                ch.download(
                    date=dates[i],
                    version=vv, 
                    run="late", 
                    timestep=frequency, 
                    outpath=outpath)       
        except Exception as e:
            print(e)
            logging.error(f"Error downloading data: {dates[i]}: {e}")
            continue
        # Mask data to Ecuador extent
        mask(outpath, bounds, correct_factor)
        # Publish raster data
        try:
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'imerg-late-{frequency}')
        except:
            geo.delete_coveragestore(
                coveragestore_name=layer_name, 
                workspace=f'imerg-late-{frequency}')
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'imerg-late-{frequency}')
        # Add styles
        geo.publish_style(
            layer_name=layer_name, 
            style_name=f'precipitation_style_imerg_late_{frequency}', 
            workspace=f'imerg-late-{frequency}')
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
    start_date = (actual_date - relativedelta(months=1)).strftime("%Y-%m-%d")
    end_date = actual_date
    download_imerg(start_date, end_date, "daily")
except:
    print("Downloaded daily data")


## Download monthly data
try:
    lmd = calendar.monthrange(actual_date.year, actual_date.month)[1]
    last_month_day = datetime.date(actual_date.year, actual_date.month, lmd)
    start_date = (actual_date - relativedelta(months=2)).strftime("%Y-%m-01")
    end_date = last_month_day.strftime("%Y-%m-%d")
    download_imerg(start_date, end_date, "monthly")
except:
    print("Downloaded monthly data")


## Download yearly data
try:
    start_date = (actual_date - relativedelta(years=6)).strftime("%Y-01-01")
    end_date = datetime.date(actual_date.year, 12, 31).strftime("%Y-%m-%d")
    download_imerg(start_date, end_date, "annual")
except:
    print("Donwloaded annual data")


