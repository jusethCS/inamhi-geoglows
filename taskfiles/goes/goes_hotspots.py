import os
import rasterio
import numpy as np
import pandas as pd
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine

def read_bands_and_convert_to_grayscale(tif_file: str) -> tuple:
    """
    Read the GeoTIFF file and convert to grayscale and red band simultaneously.
    
    Args:
        tif_file (str): Path to the GeoTIFF file.
    
    Returns:
        Tuple containing grayscale band, red band, transform, and CRS.
    """
    try:
        with rasterio.open(tif_file) as dataset:
            raster_data = dataset.read()
            grayscale_band = 0.21 * raster_data[0] + 0.72 * raster_data[1] + 0.07 * raster_data[2]
            red_band = raster_data[0]
            return grayscale_band, red_band, dataset.transform, dataset.crs
    except rasterio.errors.RasterioIOError:
        print(f"Failed to open or read the file: {tif_file}")
        raise


def apply_thresholds(grayscale_band: np.ndarray, red_band: np.ndarray, 
                     grayscale_threshold: float, red_threshold: float) -> np.ndarray:
    """
    Apply thresholding on both grayscale and red band.
    
    Args:
        grayscale_band (np.ndarray): Grayscale band data.
        red_band (np.ndarray): Red band data.
        grayscale_threshold (float): Threshold for grayscale band.
        red_threshold (float): Threshold for red band.
    
    Returns:
        np.ndarray: Combined mask where both conditions are met.
    """
    return (grayscale_band > grayscale_threshold) & (red_band > red_threshold)


def extract_centroids_from_mask(mask: np.ndarray, 
                                transform: rasterio.Affine) -> list[tuple[float, float]]:
    """
    Extract the centroids of pixels that meet both grayscale and red band conditions.
    
    Args:
        mask (np.ndarray): Boolean mask of pixels meeting the conditions.
        transform (rasterio.Affine): Affine transform of the raster.
    
    Returns:
        List of tuples containing longitude and latitude of centroids.
    """
    coords = np.column_stack(np.where(mask))
    return [rasterio.transform.xy(transform, x, y) for x, y in coords]



def process_hotspots(tif_file: str, grayscale_threshold: float, 
                     red_threshold: float, date_file:pd.Timestamp):
    """
    Main function to process the TIFF file and plot filtered centroids.
    
    Args:
        tif_file (str): Path to the input GeoTIFF file.
        output_csv (str): Path to save the output CSV file.
        grayscale_threshold (float): Threshold for grayscale band.
        red_threshold (float): Threshold for red band.
    """
    try:
        grayscale_band, red_band, transform, crs = read_bands_and_convert_to_grayscale(tif_file)
        combined_mask = apply_thresholds(grayscale_band, red_band, grayscale_threshold, red_threshold)
        centroids = extract_centroids_from_mask(combined_mask, transform)
        df = pd.DataFrame(centroids, columns=['longitude', 'latitude'])
        df["datetime"] = date_file
        return(df)
    except Exception as e:
        print(f"An error occurred: {str(e)}")



###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
os.chdir("/home/ubuntu/inamhi-geoglows")

# Import enviromental variables
load_dotenv("db.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

# Change the work directory
os.chdir("/home/ubuntu/data/goes/")

# List last file
workdir = "/usr/share/geoserver/data_dir/data/GOES-RGB-FIRE-TEMPERATURE"
files = os.listdir(workdir)
files.sort()
tif_file = f"{workdir}/{files[-1]}/{files[-1]}.geotiff"
date_file = pd.to_datetime(files[-1], format="%Y%m%d%H%M")
hotspots = process_hotspots(tif_file, date_file=date_file, 
                            grayscale_threshold=30, red_threshold=180)
hotspots.to_sql('goes_hotspots', con=con, if_exists='append', index=False)
con.commit()
con.close()
