import requests
import rasterio
from concurrent.futures import ThreadPoolExecutor
from django.http import JsonResponse
import json
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import pandas as pd
from io import BytesIO

SERVER = "http://ec2-3-211-227-44.compute-1.amazonaws.com"
GEOSERVER = f"{SERVER}/geoserver"
ENDPOINT = f"{SERVER}:4200"

def get_raster_value(gdf, raster):
    geometries = gdf.geometry.values
    out_image, out_transform = mask(raster, geometries, crop=True)
    out_image = out_image.astype(float)
    out_image[out_image == raster.nodata] = np.nan
    return round(np.nanmean(out_image), 2)

def fetch_raster_value(date, workspace, gdf):
    dd = date.strftime('%Y-%m-%d')
    url = f"{ENDPOINT}/{workspace}/{dd}/{dd}.geotiff"
    print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we catch HTTP errors
        raster_bytes = BytesIO(response.content)
        raster = rasterio.open(raster_bytes)
        value = get_raster_value(gdf, raster)
    except requests.RequestException:
        value = 0
    except rasterio.errors.RasterioError:
        value = 0
    print(dd, value)
    return {'date': dd, 'value': value}

def get_metdata(request):
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

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda date: fetch_raster_value(date, workspace, gdf), dates))

    return JsonResponse(results, safe=False)
