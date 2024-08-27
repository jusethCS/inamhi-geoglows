import os
import gzip
import shutil
import pandas as pd
import datetime as dt
import geopandas as gpd
from dotenv import load_dotenv
from geo.Geoserver import Geoserver


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def get_ffgs_file(product:str, filename:str, colname:str, user:str, 
                  password:str) -> pd.DataFrame:
    """
    Downloads and processes a compressed file from a remote server and 
    returns it as a pandas DataFrame.
    
    Args:
        product (str): The name of the product.
        filename (str): The name of the file.
        run (str): The run hour in "HH" format.
        colname (str): The name of the column to rename in the DataFrame.
        user (str): The username for server authentication.
        password (str): The password for server authentication.
        
    Returns:
        pd.DataFrame: A pandas DataFrame with the processed data.
    """
    # Generar la fecha actual ajustada
    actual_date = dt.datetime.now() - dt.timedelta(hours=5)
    actual_year = actual_date.strftime("%Y")
    actual_month = actual_date.strftime("%m")
    actual_day = actual_date.strftime("%d")
    actual_hour = actual_date.hour
    run_hours = ["00", "06", "12", "18"]
    run = run_hours[actual_hour // 6]
    #
    # URL del archivo comprimido (*.gz)
    url = (
        f"https://nwsaffgs-ubuntu.hrcwater.org/NWSAFFGS_CONSOLE/EXPORTS/REGIONAL/"
        f"{actual_year}/{actual_month}/{actual_day}/{product}_TXT/"
        f"{actual_year}{actual_month}{actual_day}-{run}00_ffgs_prod_{filename}_regional.txt.gz"
    )
    #
    # Descargar el archivo comprimido
    gz_filename = "data.gz"
    command = (
        f"wget --user {user}"
        f" --password {password}"
        f" --no-check-certificate {url}"
        f" -O {gz_filename}"
    )
    os.system(command)
    #
    # Descomprimir el archivo .gz
    output = "data.txt"
    with gzip.open(gz_filename, 'rb') as gz_file, open(output, 'wb') as out_file:
        shutil.copyfileobj(gz_file, out_file)
    #
    # Leer y procesar el archivo descomprimido
    data = pd.read_table(output, sep="\t")
    data.columns = ["BASIN", colname]
    return data



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
        - The workspace is fixed to 'ffgs' and should be modified if a 
            different workspace is required.
    """
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=path, 
            workspace='ffgs')
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace='ffgs')
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=path, 
            workspace='ffgs')
    geo.publish_style(
        layer_name=layer_name,  
        style_name=style, 
        workspace='ffgs')






###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("inamhi-geoglows")

# Import enviromental variables
load_dotenv()
FFGS_USER = os.getenv('FFGS_USER')
FFGS_PASS = os.getenv('FFGS_PASS')
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")

# Instance the geoserver
geo = Geoserver(
    'https://inamhi.geoglows.org/geoserver', 
    username=GEOSERVER_USER, 
    password=GEOSERVER_PASS)

# Read FFGS basins for Ecuador
shp = "taskfiles/shp/ffgs.shp"
gdf_shapefile = gpd.read_file(shp)

# Rechange the work directory
os.chdir(user_dir)
os.chdir("data/ffgs")

# Humedad Promedio del Suelo (ASM)
asm = get_ffgs_file(
        product="ASM",
        filename = "est_asm_sacsma_06hr",
        colname="asm",
        user=FFGS_USER,
        password=FFGS_PASS)

# Precipitacion critica para crecida (FFG)
ffg = get_ffgs_file(
        product="FFG",
        filename = "est_ffg_smffg_06hr",
        colname="ffg",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de precipitacion WRF (prox. 6h)
fmap06 = get_ffgs_file(
        product = "FMAP1", 
        filename = "fcst_map_forecast2_06hr",  
        colname="fmap06",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de precipitacion WRF (prox. 24h)
fmap24 = get_ffgs_file(
        product = "FMAP1", 
        filename = "fcst_map_forecast2_24hr", 
        colname="fmap24",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de riesgo de crecidas repentinas (prox. 12h)
ffr12 = get_ffgs_file(
        product = "FFR1", 
        filename = "fcst_ffr_outlook2_12hr", 
        colname="ffr12",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de riesgo de crecidas repentinas (prox. 24h)
ffr24 = get_ffgs_file(
        product = "FFR1", 
        filename = "fcst_ffr_outlook2_24hr", 
        colname="ffr24",
        user=FFGS_USER,
        password=FFGS_PASS)


# Merge all DataFrames on "BASIN" using outer join
dfs = [asm, ffg, fmap06, fmap24, ffr12, ffr24]
ffgs = dfs[0]
for df in dfs[1:]:
    ffgs = pd.merge(ffgs, df, on="BASIN", how="outer")

# Combine data with shapefile
ffgs = gdf_shapefile.merge(
    ffgs, left_on='BASIN', right_on='BASIN', how='left')

# Save the new shapefile
ffgs.to_file("ffgs.shp")


# Rasterize each information
os.system("gdal_rasterize -a asm -tr 0.01 0.01 -l ffgs /home/ubuntu/data/ffgs/ffgs.shp asm.tif")
upload_to_geoserver("asm", "asm.tif", "asm_style")

os.system("gdal_rasterize -a ffg -tr 0.01 0.01 -l ffgs /home/ubuntu/data/ffgs/ffgs.shp ffg.tif")
upload_to_geoserver("ffg", "ffg.tif", "ffg_style")

os.system("gdal_rasterize -a fmap06 -tr 0.01 0.01 -l ffgs /home/ubuntu/data/ffgs/ffgs.shp fmap06.tif")
upload_to_geoserver("fmap06", "fmap06.tif", "fmap_style")

os.system("gdal_rasterize -a fmap24 -tr 0.01 0.01 -l ffgs /home/ubuntu/data/ffgs/ffgs.shp fmap24.tif")
upload_to_geoserver("fmap24", "fmap24.tif", "fmap_style")

os.system("gdal_rasterize -a ffr12 -tr 0.01 0.01 -l ffgs /home/ubuntu/data/ffgs/ffgs.shp ffr12.tif")
upload_to_geoserver("ffr12", "ffr12.tif", "asm_style")

os.system("gdal_rasterize -a ffr24 -tr 0.01 0.01 -l ffgs /home/ubuntu/data/ffgs/ffgs.shp ffr24.tif")
upload_to_geoserver("ffr24", "ffr24.tif", "asm_style")


