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

# Pronostico de precipitacion WRF proximas 6 horas
fmap06 = get_ffgs_file(
        product = "FMAP2", 
        filename = "fcst_map_forecast2_06hr",  
        colname="fmap06",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de precipitacion WRF proximas 24 horas
fmap24 = get_ffgs_file(
        product = "FMAP2", 
        filename = "fcst_map_forecast2_24hr", 
        colname="fmap24",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de riesgo de crecidas repentinas proximas 12 horas
ffr12 = get_ffgs_file(
        product = "FFR2", 
        filename = "fcst_ffr_outlook2_12hr", 
        colname="ffr12",
        user=FFGS_USER,
        password=FFGS_PASS)

# Pronostico de riesgo de crecidas repentinas proximas 24 horas
ffr24 = get_ffgs_file(
        product = "FFR2", 
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
ffgs = gdf_shapefile.merge(ffgs, left_on='BASIN', right_on='BASIN', how='left')

# Save the new shapefile
ffgs.to_file("ffgs.shp")
os.system("zip -r ffgs.zip .")
geo.create_shp_datastore(path="ffgs.zip", store_name='ffgs', workspace='ffgs')

#geo.publish_style(layer_name='ffgs', style_name='asm_style', workspace='ffgs')
#geo.publish_style(layer_name='ffgs', style_name='fmap24_style', workspace='ffgs')
#geo.publish_style(layer_name='ffgs', style_name='asm', workspace='ffgs')
#os.system("gdal_rasterize -a asm -tr 0.001 0.001 -l nwsaffds /home/ubuntu/data/nwsaffgs/nwsaffds.shp soilmoisture.tif")
