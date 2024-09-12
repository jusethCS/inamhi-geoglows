import os
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import sqlalchemy as sql
from dotenv import load_dotenv
from shapely.geometry import Point
from sqlalchemy import create_engine
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
from affine import Affine
import numpy as np

def read_bands_and_convert_to_grayscale(tif_file: str) -> tuple:
    """
    Read the GeoTIFF file, remap to a new resolution using maximum pixel value, and convert to grayscale.
    
    Args:
        tif_file (str): Path to the GeoTIFF file.
    
    Returns:
        Tuple containing grayscale band, red band, transform, and CRS.
    """
    try:
        with rasterio.open(tif_file) as dataset:
            # Verificar que el raster tenga dimensiones válidas
            if dataset.width == 0 or dataset.height == 0:
                raise ValueError("The raster has invalid dimensions (width or height is zero).")
            #
            # Obtener la resolución actual y calcular la nueva
            scale_factor = 4  # Ajusta este valor según sea necesario
            dst_width = int(dataset.width / scale_factor)
            dst_height = int(dataset.height / scale_factor)
            #
            # Calcular la nueva transformación
            dst_transform = Affine(dataset.transform.a * scale_factor, dataset.transform.b, dataset.transform.c,
                                   dataset.transform.d, dataset.transform.e * scale_factor, dataset.transform.f)
            #
            # Crear arrays vacíos para almacenar los datos remuestreados
            remapped_data = np.empty((dataset.count, dst_height, dst_width), dtype=dataset.dtypes[0])
            #
            # Remuestrear utilizando reproject con Resampling.max
            for i in range(1, dataset.count + 1):
                reproject(
                    source=rasterio.band(dataset, i),
                    destination=remapped_data[i - 1],
                    src_transform=dataset.transform,
                    src_crs=dataset.crs,
                    dst_transform=dst_transform,
                    dst_crs=dataset.crs,
                    resampling=Resampling.max  # Usar remuestreo basado en el máximo
                )
            #
            # Convertir las bandas a escala de grises
            grayscale_band = 0.21 * remapped_data[0] + 0.72 * remapped_data[1] + 0.07 * remapped_data[2]
            red_band = remapped_data[0]
            return grayscale_band, red_band, dst_transform, dataset.crs
    except rasterio.errors.RasterioIOError:
        print(f"Failed to open or read the file: {tif_file}")
        raise
    except ValueError as ve:
        print(f"Error: {ve}")
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
    #try:
    grayscale_band, red_band, transform, crs = read_bands_and_convert_to_grayscale(tif_file)
    combined_mask = apply_thresholds(grayscale_band, red_band, grayscale_threshold, red_threshold)
    centroids = extract_centroids_from_mask(combined_mask, transform)
    data = pd.DataFrame(centroids, columns=['longitude', 'latitude'])
    data["datetime"] = date_file
    #
    # Generate a geopandas dataframe
    geometry = [Point(xy) for xy in zip(data['longitude'], data['latitude'])]
    gdf = gpd.GeoDataFrame(data, geometry=geometry)
    gdf = gdf.set_crs(epsg=4326, inplace=True)
    #
    # Filter the points within ecuador
    ecu = gpd.read_file("/home/ubuntu/inamhi-geoglows/taskfiles/shp/ecuador.shp")
    gdf = gdf[gdf.geometry.within(ecu.geometry.union_all())]
    data = gdf.drop(columns='geometry')
    return(data)
    #except Exception as e:
    #   print(f"An error occurred: {str(e)}")



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
