import os
import shutil
import xarray
import platform
import datetime
import rasterio
import requests
import subprocess
import numpy as np
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
    ds = ds.sel(time=time.replace(hour=0, minute=0, second=0, microsecond=0))
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


def upload_to_geoserver(geo:Geoserver, layer_name:str, path:str, workspace:str,
                          style_name:str) -> None:
    """
    Create and manage a coveragestore in GeoServer, and apply a style.

    Parameters
    ----------
      - geo (Geoserver): object that contains GeoServer methods.
      - layer_name (str): layer name for geoserver.
      - path (str): Path to the tif file.
      - workspace (str): GeoServer workspace .
      - style_name (str): Style to apply.
    """
    
    try:
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=path, 
            workspace=workspace)
        geo.publish_style(
            layer_name=layer_name, 
            style_name=style_name, 
            workspace=workspace)
    except:
        geo.delete_coveragestore(
            coveragestore_name=layer_name, 
            workspace=workspace)
        geo.create_coveragestore(
            layer_name=layer_name, 
            path=path, 
            workspace=workspace)
        geo.publish_style(
            layer_name=layer_name, 
            style_name=style_name, 
            workspace=workspace)


def process_and_upload_data(geo, current_date):
    """
    Downloads GPM data from NASA OPeNDAP, processes it to GeoTIFF, masks the 
    data, and uploads it to GeoServer.

    Parameters:
    geo -- object that contains GeoServer methods.
    current_date -- the date for which to download and process the data.
    bounds -- geographic bounds to mask the GeoTIFF file.
    """
    #
    # Extract year, month, and day from the current date
    year = current_date.strftime('%Y')
    month = current_date.strftime('%m')
    day = current_date.strftime('%d')
    #
    # Configure bounds
    bounds = (-94, -7.5, -70, 4)
    #
    # Construct the URL for the GPM data
    url = (f"https://gpm1.gesdisc.eosdis.nasa.gov/opendap/hyrax/GPM_L3/"
           f"GPM_3IMERGDE.07/{year}/{month}/3B-DAY-E.MS.MRG.3IMERG."
           f"{year}{month}{day}-S000000-E235959.V07B.nc4.nc4?")
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
        # Convert the NetCDF to GeoTIFF and apply the mask
        nc_to_tif(
            path="temporal.nc", 
            var="precipitation", 
            time=current_date)
        mask("temporal.tif", bounds)
        #
        # Upload the processed GeoTIFF to GeoServer
        upload_to_geoserver(
            geo=geo, 
            layer_name=current_date.strftime('%Y-%m-%d'), 
            path="temporal.tif", 
            workspace="imerg-early-daily", 
            style_name="precipitation_style_imerg_early_daily")
    else:
        print(f"Error downloading data for {current_date}:\n {response.status_code}")


###############################################################################
#                           ENVIROMENTAL VARIABLES                            #
###############################################################################

# Load enviromental
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
GEOSERVER_USER = os.getenv("GEOSERVER_USER")
GEOSERVER_PASS = os.getenv("GEOSERVER_PASS")
NASA_USER = os.getenv("NASA_USER")
NASA_PASS = os.getenv("NASA_PASS")

# Login
earth_data_explorer_credential(NASA_USER, NASA_PASS)
geo = Geoserver(
        'https://inamhi.geoglows.org/geoserver', 
        username=GEOSERVER_USER, 
        password=GEOSERVER_PASS)



current_date = datetime.datetime.now() - datetime.timedelta(days=1)

