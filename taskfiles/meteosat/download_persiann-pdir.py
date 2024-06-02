import os
import gzip
import logging
import rasterio
import requests
import numpy as np
import pandas as pd
import meteosatpy

from osgeo import osr
from osgeo import gdal

from struct import unpack
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



def ungzip(path:str, remove:bool = True) -> None:
    ungzip_path = path.replace(".gz", "")
    with gzip.open(path, 'rb') as f_in:
        with open(ungzip_path, 'wb') as f_out:
            f_out.write(f_in.read())
    if(remove):
        os.remove(path)


def readBinary(path):
    # open binary file
    f = open(path, "rb")
    #
    # set file dimensions
    xs = 9000
    ys = 3000
    #
    # set number of bytes in file
    NumbytesFile = xs * ys
    #
    # number of columns in row
    NumElementxRecord = -xs
    #
    # create empty array to put data in
    myarr = []
    #
    # loop trough the binary file row by row
    for PositionByte in range(NumbytesFile,0, NumElementxRecord):
            Record = ''
            # the dataset starts at 0 degrees, use 720 to convert to -180 degrees
            for c in range (PositionByte-4500, PositionByte, 1):
                    f.seek(c * 4)
                    DataElement = unpack('>f', f.read(4))
                    Record = Record  + str("%.2f" % DataElement + ' ')
            #
            # 0 - 180 degrees
            for c in range (PositionByte-9000 , PositionByte-4500, 1):
                    f.seek(c * 4)
                    DataElement = unpack('>f', f.read(4))
                    Record = Record  + str("%.2f" % DataElement + ' ')
            #
            # add data to array
            myarr.append(Record[:-1].split(" "))
    #
    # close binary file
    f.close()
    #
    # Array to numpy float
    myarr = np.array(myarr).astype('float')
    #
    # set values < 0 to nodata
    myarr[myarr < 0] = 0
    #
    # mirror array
    myarr = myarr[::-1]
    #
    # define output name
    outname = "temporal.tif"
    #
    # set coordinates
    originy = 60
    originx  = -180
    pixelsize = 0.04
    transform= (originx, pixelsize, 0.0, originy, 0.0, -pixelsize)
    driver = gdal.GetDriverByName( 'GTiff' )
    #
    # set projection
    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)
    #
    ## write dataset to disk
    outputDataset = driver.Create(outname, xs,ys, 1,gdal.GDT_Float32)
    outputDataset.SetGeoTransform(transform)
    outputDataset.SetProjection(target.ExportToWkt())
    outputDataset.GetRasterBand(1).WriteArray(myarr)
    outputDataset.GetRasterBand(1).SetNoDataValue(-9999)
    outputDataset = None







###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
def download_persiann(date_start, date_end, frequency):
    # Configure log file
    log_file = f'persiann-pdir-{frequency}.log'
    logging.basicConfig(filename=log_file, level=logging.ERROR)
    #
    # Instance the geoserver
    geo = Geoserver(
        'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
            username=GEOSERVER_USER, 
            password=GEOSERVER_PASS)
    #
    # Server
    server = "https://persiann.eng.uci.edu/CHRSdata/PDIRNow"
    # https://persiann.eng.uci.edu/CHRSdata/PDIRNow/PDIRNowyearly/pdirnow1year01.bin.gz
    # https://persiann.eng.uci.edu/CHRSdata/PDIRNow/PDIRNowmonthly/pdirnow1mon0003.bin.gz
    # https://persiann.eng.uci.edu/CHRSdata/PDIRNow/PDIRNowdaily/pdirnow1d000301.bin.gz
    #
    # Frequency 
    if frequency == "daily":
        tt = "PDIRNowdaily"
        freq = "D"
        date_format = "%Y-%m-%d"
        file_format = "pdirnow1d%y%j.bin.gz"
    elif frequency == "monthly":
        tt = "PDIRNowmonthly"
        freq = "MS"
        date_format = "%Y-%m-01"
        file_format = "pdirnow1mon%y%m.bin.gz"
    elif frequency == "annual":
        tt = "PDIRNowyearly"
        freq = "YS"
        date_format = "%Y-01-01"
        file_format = "pdirnow1year%y.bin.gz"
    else:
        return("Frecuency could be 'daily', 'monthly', 'annual'.")
    #
    # Date range and bounds
    dates = pd.date_range(date_start, date_end, freq = freq)
    bounds = (-94, -7.5, -70, 4)
    #
    # Instance the meteosatpy for CHIRPS data
    ch = meteosatpy.PERSIANN()
    #
    # Donwnload and publish CHIRPS data
    for i in range(len(dates)):
        # File paths
        print(dates[i])
        outpath = dates[i].strftime(f"{date_format}.tif")
        layer_name = dates[i].strftime(date_format)
        file_data = dates[i].strftime(file_format)
        url = f"{server}/{tt}/{file_data}"
        print(url)
        binDownload = False
        try:
            try:
                ch.download(
                    date=dates[i], 
                    timestep=frequency, 
                    outpath=outpath,
                    dataset="PDIR")
                mask(outpath, outpath, bounds)
            except:
                print("Download using URL")
                response = requests.get(url)
                with open("temporal.bin.gz", 'wb') as archivo:
                    archivo.write(response.content)
                ungzip("temporal.bin.gz")
                readBinary("temporal.bin")
                mask("temporal.tif", outpath, bounds)
                binDownload = True
        except Exception as e:
            print(e)
            logging.error(f"Error downloading data: {dates[i]}: {e}")
            continue
        # Publish raster data
        try:
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'persiann-pdir-{frequency}')
        except:
            geo.delete_coveragestore(
                coveragestore_name=layer_name, 
                workspace=f'persiann-pdir-{frequency}')
            geo.create_coveragestore(
                layer_name=layer_name, 
                path=outpath, 
                workspace=f'persiann-pdir-{frequency}')
        # Add styles
        geo.publish_style(
            layer_name=layer_name, 
            style_name=f'precipitation_style_persiann_pdir_{frequency}', 
            workspace=f'persiann-pdir-{frequency}')
        # Delete download file
        os.remove(outpath)
        if(binDownload):
            os.remove("temporal.tif")
            os.remove("temporal.bin")



###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
import datetime
import calendar
from dateutil.relativedelta import relativedelta

actual_date = datetime.date.today()


## Downloaded daily data
try:
    start_date = "2000-01-01" #(actual_date - relativedelta(months=2)).strftime("%Y-%m-01")
    end_date = actual_date.strftime("%Y-%m-%d")
    download_persiann(start_date, end_date, "daily")
except:
    print("Downloaded daily data")


## Download monthly data
try:
    lmd = calendar.monthrange(actual_date.year, actual_date.month)[1]
    last_month_day = datetime.date(actual_date.year, actual_date.month, lmd)
    start_date = "2000-01-01"#(actual_date - relativedelta(months=12)).strftime("%Y-%m-01")
    end_date = last_month_day.strftime("%Y-%m-%d")
    download_persiann(start_date, end_date, "monthly")
except:
    print("Downloaded monthly data")


## Download yearly data
try:
    start_date = "2000-01-01"#(actual_date - relativedelta(years=6)).strftime("%Y-01-01")
    end_date = datetime.date(actual_date.year, 12, 31).strftime("%Y-%m-%d")
    download_persiann(start_date, end_date, "annual")
except:
    print("Donwloaded annual data")

