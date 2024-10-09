import os
import glob
import rasterio
import meteosatpy
import numpy as np
import pandas as pd
import geopandas as gpd
from rasterio.mask import mask
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from datetime import datetime, timedelta


###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################
def maskTIFF(path:str, output_raster:str, shp:gpd.GeoDataFrame) -> None:
    """
    Creates a masked GeoTIFF using input shapes. Pixels are masked or set 
    to nodata outside the input shapes.
    
    Args:
        path: Raster path to which the mask will be applied
        shp: A geopandas dataframe with iterable geometries

    Return:
        tuple (two elements):
            out_image: Data contained in the raster after applying the mask.
            out_meta: Information for mapping pixel coordinates in masked
    """
    # Read the file and crop to target area
    with rasterio.open(path) as src:
        out_image, out_transform = mask(src, shp.geometry, crop=True)
        profile = src.meta
    #
    # Update the metadata of GeoTIFF file
    profile.update({
        "driver": "GTiff", 
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })
    #
    # Write the masked data to the output raster file
    with rasterio.open(output_raster, 'w', **profile) as dst:
        dst.write(out_image)


def list_files(pattern:str, directory:str = '.') -> list:
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



def delete_files(pattern:str) -> None:
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



def sum_and_save_geotiffs(file_list:list, output_file:str) -> None:
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



def download_persiann_data(days: int, shp:gpd.GeoDataFrame) -> None:
    """
    Downloads hourly PERSIANN data for the past specified days, sums the data,
    and saves the result to a GeoTIFF file.

    Args:
        days (int): Number of past days to download data (1,2,3 days).
        shp (gpd.GeoDataFrame): A geopandas dataframe with iterable geometries
    """
    # Establish start and end date and geographical bounds
    now = datetime.now()
    end = now.replace(hour=12, minute=0)
    start = end - timedelta(days=days)
    dates = pd.date_range(start, end, freq="h")
    bounds = (-94, -7.5, -70, 4)
    
    # Download data
    ch = meteosatpy.PERSIANN()
    for date in dates:
        filename = date.strftime(f"hourly_persiann_{days}d_%Y%m%d%H00.tif")
        if not os.path.exists(filename):
            for attempt in range(5):
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
    
    # Read and process PERSIANN data
    sum_and_save_geotiffs(
        file_list=list_files(pattern=f"hourly_persiann_{days}d_*.tif"),
        output_file=f"persiann{days}d.tif")
    maskTIFF(f"persiann{days}d.tif", f"persiann{days}d.tif", shp)
    delete_files(pattern=f"hourly_persiann_{days}d_*.tif")



def get_no_rain_days(noprec_file, persiann_file):
    """
    Updates a raster file with the number of consecutive no-rain days based on
    PERSIANN precipitation data.

    Args:
        noprec_file (str): Path to the raster file tracking days without rain.
        persiann_file (str): Path to the PERSIANN raster file containing 
            precipitation data.

    Notes:
        - The function assumes that areas with less than 2 mm of precipitation 
            are considered no-rain areas.
        - The input and output rasters are expected to have the same dimensions 
            and geospatial properties.
    """
    with rasterio.open(noprec_file) as src:
        noprec_data = src.read(1)
        profile = src.profile
    #
    with rasterio.open(persiann_file) as src:
        persiann_data = src.read(1)
        mask = persiann_data < 2
    #
    out = mask * (noprec_data + 1)
    #
    profile.update({'count': 1, 'dtype': 'float32', 'compress': 'lzw'})
    # 
    with rasterio.open(noprec_file, 'w', **profile) as dst:
        dst.write(out, 1) 



def upload_to_geoserver(layer_name:str, path:str, style:str):
    """
    Uploads a layer to GeoServer, handles errors if the store already exists, 
    and applies the specified style.

    Parameters:
        layer_name (str): The name of the layer to be created or updated in 
            GeoServer.
        path (str): The file path to the data (e.g., GeoTIFF, Shapefile) that 
            will be used to create the layer.
        style (str): The name of the style to be applied to the layer in 
            GeoServer.

    Exceptions:
        In case the store creation fails initially, the function will attempt 
        to delete the existing store before trying again.

    Notes:
        - This function assumes the use of a `geo` object with methods for 
            interacting with GeoServer (e.g., `create_coveragestore`, 
            `delete_coveragestore`, `publish_style`).
        - The workspace is fixed to 'fireforest' and should be modified if a 
            different workspace is required.
    """
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
user_dir = os.path.expanduser(f'~{user}')
os.chdir(user_dir)
os.chdir("inamhi-geoglows")

# Load enviromental
load_dotenv()
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")

# Instance the geoserver
geo = Geoserver(
    'https://inamhi.geoglows.org/geoserver', 
    username=GEOSERVER_USER, 
    password=GEOSERVER_PASS)

# Re change the work directory
os.chdir(user_dir)
os.chdir("data/fireforest")

# Path for shp extention
path = "/home/ubuntu/inamhi-geoglows/taskfiles/shp/ffgs.shp"
ec = gpd.read_file(path)

# Download data and publish on geoserver - PERSIANN
download_persiann_data(1, ec)
upload_to_geoserver("daily_precipitation", "persiann1d.tif", "pacum-style")
download_persiann_data(2, ec)
upload_to_geoserver("2days_precipitation", "persiann2d.tif", "pacum-style")
download_persiann_data(3, ec)
upload_to_geoserver("3days_precipitation", "persiann3d.tif", "pacum-style")

# Compute the no rain days
maskTIFF("noprec.tif", "noprec.tif", ec)
get_no_rain_days("noprec.tif", "persiann1d.tif")
upload_to_geoserver("no_precipitation_days", "noprec.tif", "noprec-style")
