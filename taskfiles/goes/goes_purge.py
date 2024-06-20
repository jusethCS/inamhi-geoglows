import os
import datetime
import subprocess
import pandas as pd
import pyproj as pyproj
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from dateutil.relativedelta import relativedelta

# Load enviromental
load_dotenv("/home/ubuntu/inamhi-geoglows/taskfiles/meteosat/.env")
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")

def delete_coverage(product, band):
    # Generate dates (start and end)
    now = datetime.datetime.now()
    start = now - relativedelta(days=10)
    end = now - relativedelta(hours=12)
    date_range = pd.date_range(start, end, freq="1T")
    #
    # Variables
    endpoint = "/usr/share/geoserver/data_dir/data"
    #
    # Instance the geoserver
    geo = Geoserver(
            'http://ec2-3-211-227-44.compute-1.amazonaws.com/geoserver', 
                username=GEOSERVER_USER, 
                password=GEOSERVER_PASS)
    #
    for date in date_range:
        layer_name = date.strftime('%Y%m%d%H%M')
        filedir = f"{endpoint}/GOES-{product}-{band}/{layer_name}"
        if os.path.exists(f"{filedir}/{layer_name}.geotiff"):
            try:
                comando = ['sudo', 'rm', '-rf', filedir]
                subprocess.run(comando, check=True, text=True, capture_output=True)
                geo.delete_coveragestore(
                    coveragestore_name=layer_name, 
                    workspace=f'GOES-{product}-{band}')
                print(f"File {product}-{band}:{layer_name} was deleted!")
            except Exception as e:
                print(e)
                print(f"File {product}-{band}:{layer_name} cannot be deleted!")


bands = ["01", "02", "03", "04", "05", "06", "07", "08", 
         "09", "10", "11", "12", "13", "14", "15", "16"]
product = "ABI-L2-CMIPF"

for band in bands:
    delete_coverage(product, band)

