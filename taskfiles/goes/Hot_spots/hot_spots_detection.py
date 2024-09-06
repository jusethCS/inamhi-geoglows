import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from typing import Tuple, List
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def read_bands_and_convert_to_grayscale(tif_file: str) -> Tuple[np.ndarray, np.ndarray, rasterio.Affine, rasterio.crs.CRS]:
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
        logging.error(f"Failed to open or read the file: {tif_file}")
        raise

def apply_thresholds(grayscale_band: np.ndarray, red_band: np.ndarray, grayscale_threshold: float, red_threshold: float) -> np.ndarray:
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

def extract_centroids_from_mask(mask: np.ndarray, transform: rasterio.Affine) -> List[Tuple[float, float]]:
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

def plot_filtered_centroids_on_map(df: pd.DataFrame):
    """
    Plot centroids on a map.
    
    Args:
        df (pd.DataFrame): DataFrame containing Longitude and Latitude columns.
    """
    lons, lats = df['Longitude'].values, df['Latitude'].values

    plt.figure(figsize=(12, 8))
    m = Basemap(projection='merc', llcrnrlat=-6, urcrnrlat=2, llcrnrlon=-82, urcrnrlon=-74, resolution='i')
    
    m.drawcoastlines()
    m.drawcountries()

    x, y = m(lons, lats)
    m.scatter(x, y, color='red', marker='o', s=10, label='Filtered Centroids')

    plt.title('Filtered Grayscale and Red Band Centroids on Ecuador Map')
    plt.legend(loc='upper left')
    plt.show()

def process_and_plot_filtered_centroids(tif_file: str, output_csv: str, grayscale_threshold: float, red_threshold: float):
    """
    Main function to process the TIFF file and plot filtered centroids.
    
    Args:
        tif_file (str): Path to the input GeoTIFF file.
        output_csv (str): Path to save the output CSV file.
        grayscale_threshold (float): Threshold for grayscale band.
        red_threshold (float): Threshold for red band.
    """
    try:
        logging.info(f"Processing file: {tif_file}")
        grayscale_band, red_band, transform, crs = read_bands_and_convert_to_grayscale(tif_file)
        
        combined_mask = apply_thresholds(grayscale_band, red_band, grayscale_threshold, red_threshold)
        
        centroids = extract_centroids_from_mask(combined_mask, transform)
        
        df = pd.DataFrame(centroids, columns=['Longitude', 'Latitude'])
        df.to_csv(output_csv, index=False)
        logging.info(f"Saved centroids to: {output_csv}")
        
        plot_filtered_centroids_on_map(df)
        logging.info("Plotted filtered centroids on map")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    tif_file = '/content/RGB-FIRE-TEMPERATURE_202409041830.tif'
    output_csv = 'filtered_grayscale_redband_centroids.csv'
    
    process_and_plot_filtered_centroids(tif_file, output_csv, grayscale_threshold=30, red_threshold=180)