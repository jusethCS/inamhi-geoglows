import requests
import rasterio
from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd

SERVER = "http://ec2-3-211-227-44.compute-1.amazonaws.com"
GEOSERVER = f"{SERVER}/geoserver"
ENDPOINT = "/usr/share/geoserver/data_dir/data"

def get_raster_value(gdf, raster):
    try:
        geometries = gdf.geometry.values
        out_image, out_transform = mask(raster, geometries, crop=True)
        out_image = out_image.astype(float)
        out_image[out_image == raster.nodata] = np.nan
        return round(np.nanmean(out_image), 2)
    except:
        return(0)

def fetch_raster_value(date, workspace, gdf):
    try:
        dd = date.strftime('%Y-%m-%d')
        url = f"{ENDPOINT}/{workspace}/{dd}/{dd}.geotiff"
        raster = rasterio.open(url)
        value = get_raster_value(gdf, raster)
    except:
        value = 0
    print(dd, value)
    return {'date': dd, 'value': value}

def get_metdata(request):
    try:
        product = request.GET.get('product')
        temporality = request.GET.get('temp')
        start = request.GET.get('start')
        end = request.GET.get('end')
        code = request.GET.get('code')

        if code.endswith("00"):
            url = f"{GEOSERVER}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Aprovincias&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON={code}"
        else:
            url = f"{GEOSERVER}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Acantones&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON={code}"

        area = requests.get(url).json()
        gdf = gpd.GeoDataFrame.from_features(area["features"])

        workspace = f"{product}-{temporality}"
        if temporality == "daily":
            dates = pd.date_range(start=start, end=end, freq='D')
        elif temporality == "monthly":
            dates = pd.date_range(start=start, end=end, freq='MS')
        elif temporality == "annual":
            dates = pd.date_range(start=start, end=end, freq='YS')

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda date: fetch_raster_value(date, workspace, gdf), dates))

        return JsonResponse(results, safe=False)

    except ValueError as e:
        return JsonResponse({"error": e})
    



#product = "chirps"
#temporality = "daily"
#start = "2024-01-01"
#end = "2024-06-01"
#code = "1500"