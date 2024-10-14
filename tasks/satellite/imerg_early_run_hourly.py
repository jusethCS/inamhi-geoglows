import os
import shutil
import xarray
import platform
import datetime
import rasterio
import requests
import subprocess
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from geo.Geoserver import Geoserver
from rasterio.transform import from_origin


###############################################################################
#                                    UTILS                                    #
###############################################################################
def earth_data_explorer_credential(username:str, password:str) -> None:
    """
    This function sets up the necessary credentials to access NASA EarthData.
    It creates configuration files that enable automatic authentication 
    when using EarthData services.
    
    Parameters
    ----------
      - username: EarthData username for authentication.
      - password: Password associated with the username.
    """
    # Generate Loggin
    auth_url = 'https://urs.earthdata.nasa.gov/login'
    auth_data = {'username': NASA_USER, 'password': NASA_PASS}
    response = requests.post(auth_url, data=auth_data)
    #
    if response.status_code == 200:
        # Earthdata URL for authentication 
        urs = 'urs.earthdata.nasa.gov'
        #
        # Determine the user's home directory
        homeDir = os.path.expanduser("~") + os.sep
        #
        # Create and write the .netrc file to store EarthData login credentials
        with open(homeDir + '.netrc', 'w') as file:
            file.write(f'machine {urs} login {username} password {password}')
            file.close()
        #
        # Create an empty .urs_cookies file for storing session cookies
        with open(homeDir + '.urs_cookies', 'w') as file:
            file.write('')
            file.close()
        #
        # Create the .dodsrc file to link the .netrc and cookies file for HTTP
        with open(homeDir + '.dodsrc', 'w') as file:
            file.write('HTTP.COOKIEJAR={}.urs_cookies\n'.format(homeDir))
            file.write('HTTP.NETRC={}.netrc'.format(homeDir))
            file.close()
        #
        # Print a message to indicate where the files have been saved
        print('Saved .netrc, .urs_cookies, and .dodsrc to:', homeDir)
        #
        # Adjust file permissions on Linux/macOS to protect the .netrc file
        if platform.system() != "Windows":
            subprocess.Popen('chmod og-rw ~/.netrc', shell=True)
        else:
            # On Windows, copy the .dodsrc file to the current working directory
            shutil.copy2(homeDir + '.dodsrc', os.getcwd())
            print('Copied .dodsrc to:', os.getcwd())
    else:
        err = "Invalid username or password. Please provide correct username and"
        err = f"{err} password for Earth Data Explorer Account. {response.read()}"
        raise(err)



def nc_to_tif(path:str, var:str, time:str, out_path:str = None) -> None:
    """
    Parse a netcdf file to GeoTIFF and write it.
    
    Parameters
    ----------
      - path: File path of the netcdf file
      - var: Selected variable to write in the GeoTIFF file
      - time: Selected timestamp (yyyy-mm-dd HH:MM) to write in the GeoTIFF
      - out_path: Path where GeoTIFF will be write.
    """
    # Remove the extension
    if out_path==None:
        out_path = path.replace(".nc", ".tif")
    #
    # Read the netcdf file
    ds = xarray.open_dataset(path)
    ds = ds.sel(time=ds['time'][0])
    #
    # Extract data
    data = ds[var].values
    #if multidimention:
    #    data = data[0]
    #
    # Extract coordinates
    lat = ds['lat'].values
    lon = ds['lon'].values
    #
    # Compute the spatial resolution
    res_lat = abs(lat[1] - lat[0])
    res_lon = abs(lon[1] - lon[0])
    #
    # Compute the spatial tranformation
    lon_min = lon.min() - res_lon/2
    lat_max = lat.max() + res_lat/2
    #
    # Traspose
    data = np.transpose(data)
    #
    # Flipping the image upright in the axis = 0 i.e., vertically
    data = np.flip(data,0)
    #
    # Transform the projection considering correction
    transform = from_origin(lon_min, lat_max, res_lon, res_lat)
    #
    # Raster metadata
    meta = {"driver": "GTiff", 
            "height": data.shape[0],
            "width": data.shape[1],
            "transform": transform,
            "crs": '+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0',
            "count" : 1, 
            "dtype" :str(data.dtype)}
    #
    # Save data as GeoTIFF file
    with rasterio.open(out_path, 'w', **meta) as dst:
        dst.write(data, 1)



def mask(input_raster:str, bounds:tuple, correct_factor:float = 1) -> None:
    """
    Applies a mask to the input raster within the specified bounds.
    
    Parameters
    -----------
      - input_raster (str): Path to the input raster file.
      - bounds (tuple): Geographic extent (west, south, east, north).
      - correct_factor (float): Numeric factor to correct and transform data.
    """
    with rasterio.open(input_raster) as src:
        window = src.window(*bounds)
        data = src.read(window=window)
        data = np.where(data < 0, np.nan, data)
        data = data * correct_factor
        transform = src.window_transform(window)
        profile = src.profile
        profile.update({
            'height': window.height,
            'width': window.width,
            'transform': transform
        })
        with rasterio.open(input_raster, 'w', **profile) as dst:
            dst.write(data)


def min_code(date):
    hora = date.hour
    minuto = date.minute
    codigo = hora * 60 + minuto
    return f"{codigo:04d}"



def download_data(current_date, mins):
    """
    Downloads GPM data from NASA OPeNDAP, processes it to GeoTIFF and mask it.

    Parameters:
    current_date -- the date for which to download and process the data.
    mins -- Minute to process
    """
    #Configure date
    current_date = current_date.replace(minute=mins, second=0, microsecond=0)
    #
    # Parameters
    year = current_date.strftime("%Y")
    actual = current_date.strftime("%Y%m%d")
    code = min_code(current_date)
    julian_day = current_date.strftime("%j")
    end_date = current_date + datetime.timedelta(seconds=1799)
    ss = current_date.strftime("%H%M00")
    ee = end_date.strftime("%H%M59")
    #
    # Construct the URL for the GPM data
    url = (f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/hyrax/GPM_L3/"
        f"GPM_3IMERGHHE.07/{year}/{julian_day}/3B-HHR-E.MS.MRG.3IMERG."
        f"{actual}-S{ss}-E{ee}.{code}.V07B.HDF5.nc4?")
    #
    # Download the data
    response = requests.get(url)
    #
    # Check if the response is successful
    if response.status_code == 200:
        # Save the downloaded content to a local file
        with open("temporal.nc", 'wb') as f:
            f.write(response.content)
    #
    nc_to_tif(path="temporal.nc", var="precipitation", time=current_date, 
            out_path=f"temporal_{mins}.tif")
    mask(f"temporal_{mins}.tif", bounds= (-94, -7.5, -70, 4), correct_factor=0.5)


def sum_rasters(path1, path2, output_path):
    """
    Function to sum two raster files and save the result to a new file.

    Parameters:
    path1 (str): Path to the first raster file.
    path2 (str): Path to the second raster file.
    output_path (str): Path to save the output raster file.

    Returns:
    None: The function saves the resulting raster to the specified output path.
    """
    # Open the first raster file
    with rasterio.open(path1) as src1:
        # Read the data of the first raster (band 1)
        raster1 = src1.read(1)
        profile = src1.profile 
    #
    # Open the second raster file
    with rasterio.open(path2) as src2:
        # Read the data of the second raster (band 1)
        raster2 = src2.read(1)
        #
        # Check if the shapes of the two rasters match
        if raster1.shape != raster2.shape:
            raise ValueError("The dimensions of the two rasters do not match.")
    #
    # Sum the two raster arrays
    suma = raster1 + raster2
    #
    # Save the resulting raster to a new file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(suma, 1)  # Write the sum as the first band


def to_geoserver(current_date):
    # Establish the path and process if it does not exists
    path = ("/usr/share/geoserver/data_dir/coverages/"
            "imerg_early_run_hourly/%Y%m%d%H00.tif")
    path = current_date.strftime(path)
    print(current_date.strftime("%Y-%m-%d %H:00"))
    if not os.path.isfile(path):
        # Download data
        download_data(current_date, mins=0)
        download_data(current_date, mins=30)
        #
        # Verify if folder exists
        #folder_path = os.path.dirname(path)
        #if not os.path.exists(folder_path):
        #    os.makedirs(folder_path)
        #
        # Create the coverage
        sum_rasters("temporal_0.tif", "temporal_30.tif", path)
        os.remove("temporal.nc")
        os.remove("temporal_0.tif")
        os.remove("temporal_30.tif")
        #os.system(f"chmod 777 {path}")
        print(f"Inserted data for: {path}")




###############################################################################
#                           ENVIROMENTAL VARIABLES                            #
###############################################################################

# Load enviromental
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
NASA_USER = os.getenv("NASA_USER")
NASA_PASS = os.getenv("NASA_PASS")

# Change work directory
os.chdir("/home/ubuntu/data/process/imerg-early-run-daily")

# Login
earth_data_explorer_credential(NASA_USER, NASA_PASS)

# Download
end = datetime.datetime.now() 
start = end - datetime.timedelta(days=10)
dates = pd.date_range(start=start, end=end, freq='1H')

for date in dates:
    try:
        to_geoserver(date)
    except Exception as e:
        print(f"Failed to process: {date.strftime('%Y-%m-%d %H:00')} \n {e}")




#http://ec2-54-234-81-180.compute-1.amazonaws.com/geoserver/web/wicket/bookmarkable/org.geoserver.web.data.layer.NewLayerPage?17





import requests

# Configuración
geoserver_url = "http://ec2-54-234-81-180.compute-1.amazonaws.com/geoserver"
workspace = "test"
datastore = "imerg_early_run_hourly"
auth = ('admin', 'geoserver')  # Usuario y contraseña de GeoServer

# URL de recarga del DataStore
url = f"{geoserver_url}/rest/workspaces/{workspace}/datastores/{datastore}/reload"

# Solicitud POST para recargar el DataStore
response = requests.post(url, auth=auth)

# Verificar la respuesta
if response.status_code == 200:
    print("DataStore recargado exitosamente.")
else:
    print(f"Error al recargar DataStore: {response.status_code}")
