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
def get_ffgs_file(date:dt.datetime, product:str, filename:str, colname:str, user:str, 
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
    actual_date = date - dt.timedelta(hours=5)
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
os.chdir("data/fireforest")

actual = dt.datetime.now()

# Humedad Promedio del Suelo (ASM)
asm1 = get_ffgs_file(
        date=actual,
        product="ASM",
        filename = "est_asm_sacsma_06hr",
        colname="asm1",
        user=FFGS_USER,
        password=FFGS_PASS)

asm2 = get_ffgs_file(
        date=actual - dt.timedelta(hours=6),
        product="ASM",
        filename = "est_asm_sacsma_06hr",
        colname="asm2",
        user=FFGS_USER,
        password=FFGS_PASS)

asm3 = get_ffgs_file(
        date=actual - dt.timedelta(hours=12),
        product="ASM",
        filename = "est_asm_sacsma_06hr",
        colname="asm3",
        user=FFGS_USER,
        password=FFGS_PASS)

asm4 = get_ffgs_file(
        date=actual - dt.timedelta(hours=18),
        product="ASM",
        filename = "est_asm_sacsma_06hr",
        colname="asm4",
        user=FFGS_USER,
        password=FFGS_PASS)

# Merge all DataFrames on "BASIN" using outer join
dfs = [asm1, asm2, asm3, asm4]
ffgs = dfs[0]
for df in dfs[1:]:
    ffgs = pd.merge(ffgs, df, on="BASIN", how="outer")
ffgs['asm'] = ffgs[['asm1', 'asm2', 'asm3', 'asm4']].mean(axis=1, skipna=True)

# Combine data with shapefile
ffgs = gdf_shapefile.merge(ffgs, left_on='BASIN', right_on='BASIN', how='left')
ffgs.to_file("asm.shp")

# Rasterize
os.system("gdal_rasterize -a asm -tr 0.01 0.01 -l asm /home/ubuntu/data/fireforest/asm.shp soilmoisture.tif")
upload_to_geoserver("soil_moisture", "soilmoisture.tif", "asm2_style")
