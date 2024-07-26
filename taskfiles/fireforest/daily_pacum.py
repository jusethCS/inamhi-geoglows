import os
import glob
import rasterio
import meteosatpy
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from datetime import datetime, timedelta


###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
def mask(input_raster:str, output_raster:str, bounds:tuple) -> None:
    """
    Crops a raster to the specified bounds and applies a mask to negative 
    values, converting them to NaN.

    Args:
        input_raster (str): Path to the input raster file.
        output_raster (str): Path to the output raster file.
        bounds (tuple): Coordinates of the bounds (xmin, ymin, xmax, ymax).
    """
    # Open the input raster file
    with rasterio.open(input_raster) as src:
        # Calculate the window corresponding to the given bounds
        window = src.window(*bounds)
        #
        # Read the data from the window
        data = src.read(window=window)
        #
        # Apply a mask to set negative values to NaN
        data = np.where(data < 0, np.nan, data)
        #
        # Get the transform for the window
        transform = src.window_transform(window)
        #
        # Update the profile for the output raster
        profile = src.profile
        profile.update({
            'height': window.height,
            'width': window.width,
            'transform': transform
        })
        #
        # Write the masked data to the output raster file
        with rasterio.open(output_raster, 'w', **profile) as dst:
            dst.write(data)


def list_files(pattern, directory='.'):
    """
    Lists all files in the specified directory that match the given pattern.

    Args:
        pattern (str): Pattern to match files.
        directory (str): Directory to search in.

    Returns:
        list: List of matching file paths.
    """
    search_pattern = os.path.join(directory, pattern)
    return glob.glob(search_pattern)


def delete_files(pattern):
    """
    Deletes all files that match the given pattern.

    Args:
        pattern (str): The pattern to match files.
    
    """
    # List all files matching the pattern
    files_to_delete = glob.glob(pattern)
    #
    # Delete each file
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


def sum_and_save_geotiffs(file_list, output_file):
    """
    Sums the values of multiple GeoTIFF files and saves the result to a new 
    GeoTIFF file.

    Args:
        file_list (list): List of paths to the GeoTIFF files.
        output_file (str): Path to the output GeoTIFF file.
    """
    # Sum the values of the GeoTIFF files
    suma_geotiff = None
    for archivo in file_list:
        try:
            with rasterio.open(archivo) as src:
                # Read the first band of the current GeoTIFF
                data = src.read(1)
                #
                # Initialize the sum array if it's None
                if suma_geotiff is None:
                    suma_geotiff = np.zeros_like(data)
                #
                # Sum the data from the current GeoTIFF
                suma_geotiff += data
        except rasterio.errors.RasterioIOError as e:
            print(f"Could not read file {archivo}: {e}")
        except Exception as e:
            print(f"An error occurred while processing file {archivo}: {e}")
    #
    if suma_geotiff is not None:
        try:
            # Open the first file to get the profile
            with rasterio.open(file_list[0]) as src:
                profile = src.profile
                profile.update(count=1)
            #
            # Write the sum to the output GeoTIFF file
            with rasterio.open(output_file, 'w', **profile) as dst:
                dst.write(suma_geotiff, 1)
            print(f"Sum of GeoTIFFs saved to {output_file}")
        except rasterio.errors.RasterioIOError as e:
            print(f"Could not write to file {output_file}: {e}")
        except Exception as e:
            print(f"An error occurred while saving file {output_file}: {e}")
    else:
        print("No GeoTIFF files were processed")



def get_daily_persiann():
    """
    Downloads hourly PERSIANN data for the past 24 hours, sums the data,
    and saves the result to a daily GeoTIFF file.

    """
    # Establish start and end date and geographical bounds
    now = datetime.now()
    end = now.replace(hour=12, minute=0)
    start = end - timedelta(days=1)
    dates = pd.date_range(start, end, freq = "h")
    bounds = (-94, -7.5, -70, 4)
    #
    # Download data
    ch = meteosatpy.PERSIANN()
    for date in dates:
        filename = date.strftime("persiann_%Y%m%d%H00.tif")
        for attempt in range(10):
            try:
                ch.download(
                    date=date, 
                    timestep="hourly",
                    dataset="PDIR", 
                    outpath=filename)
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {date}: {e}")
        else:
            print(f"Failed to download data for {date} after 10 attempts")
    #
    # Read persiann data
    sum_and_save_geotiffs(
        file_list=list_files(pattern="persiann_*.tif"),
        output_file="persiann.tif")
    mask('persiann.tif', "persiann.tif", bounds)
    



def get_3days_persiann():
    """
    Downloads hourly PERSIANN data for the past 72 hours, sums the data,
    and saves the result to a daily GeoTIFF file.

    """
    # Establish start and end date and geographical bounds
    now = datetime.now()
    end = now.replace(hour=12, minute=0)
    start = end - timedelta(days=3)
    dates = pd.date_range(start, end, freq = "h")
    bounds = (-94, -7.5, -70, 4)
    #
    # Download data
    ch = meteosatpy.PERSIANN()
    for date in dates:
        filename = date.strftime("persiann3d_%Y%m%d%H00.tif")
        for attempt in range(10):
            try:
                ch.download(
                    date=date, 
                    timestep="hourly",
                    dataset="PDIR", 
                    outpath=filename)
                break
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {date}: {e}")
        else:
            print(f"Failed to download data for {date} after 10 attempts")
    #
    # Read persiann data
    sum_and_save_geotiffs(
        file_list=list_files(pattern="persiann3d_*.tif"),
        output_file="persiann3d.tif")
    mask('persiann3d.tif', "persiann3d.tif", bounds)


def get_no_rain_days(noprec_file, persiann_file):
    with rasterio.open(noprec_file) as src:
        noprec_data = src.read(1)
        profile = src.profile
    #
    with rasterio.open(persiann_file) as src:
        persiann_data = src.read(1)
        mask = persiann_data < 1
    #
    out = mask * (noprec_data + 1)
    #
    profile.update({'count': 1, 'dtype': 'float32', 'compress': 'lzw'})
    # 
    with rasterio.open(noprec_file, 'w', **profile) as dst:
        dst.write(out, 1) 


def upload_to_geoserver(layer_name, path, style):
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=path, 
            workspace='fireforest')
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace='fireforest')
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=path, 
            workspace='fireforest')
    geo.publish_style(
        layer_name=layer_name,  
        style_name=style, 
        workspace='fireforest')

###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("inamhi-geoglows")

# Load enviromental
load_dotenv()
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")

# Instance the geoserver
geo = Geoserver(
    'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
    username=GEOSERVER_USER, 
    password=GEOSERVER_PASS)

# Re change the work directory
os.chdir(user_dir)
os.chdir("data/fireforest")

# Download data and publish on geoserver - PERSIANN
get_daily_persiann()
delete_files(pattern="persiann_*.tif")
upload_to_geoserver("daily_precipitation", "persiann.tif", "pacum-style")
print("Upload daily precipitation!")

# Download data and publish on geoserver - PERSIANN
get_3days_persiann()
delete_files(pattern="persiann3d_*.tif")
upload_to_geoserver("3days_precipitation", "persiann3d.tif", "pacum-style")
print("Upload 3 days precipitation!")

# Compute the no rain days
get_no_rain_days("noprec.tif", "persiann.tif")
os.system("gdalwarp -cutline /home/ubuntu/inamhi-geoglows/taskfiles/shp/ffgs.shp -crop_to_cutline -dstalpha noprec.tif noprec-cut.tif")
upload_to_geoserver("no_precipitation_days", "noprec-cut.tif", "noprec-style")
print("Upload no precipitation days")



# /usr/share/geoserver/data_dir/data
#
# http://ec2-3-211-227-44.compute-1.amazonaws.com:4200/fireforest/daily_precipitation/daily_precipitation.geotiff
# http://ec2-3-211-227-44.compute-1.amazonaws.com:4200/fireforest/no_precipitation_days/no_precipitation_days.geotiff
#
# http://ec2-3-211-227-44.compute-1.amazonaws.com/api/geoglows/daily-precipitation
# http://ec2-3-211-227-44.compute-1.amazonaws.com/api/geoglows/days-without-precipitation
# http://ec2-3-211-227-44.compute-1.amazonaws.com/api/geoglows/3days-precipitation
# http://ec2-3-211-227-44.compute-1.amazonaws.com/api/geoglows/soil-moisture