import requests
import rasterio
import json
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
        print("Min value in raster:", np.nanmin(raster))
        print("Max value in raster:", np.nanmax(raster))
        print("Mean value in raster:", np.nanmean(raster))
        out_image, out_transform = mask(raster, geometries, crop=True)
        out_image = out_image.astype(float)
        if raster.nodata is not None:
            out_image[out_image == raster.nodata] = np.nan
        else:
            print("No nodata value found in raster")
        print("Min value in masked image:", np.nanmin(out_image))
        print("Max value in masked image:", np.nanmax(out_image))
        print("Mean value in masked image:", np.nanmean(out_image))
        mean_value = np.nanmean(out_image)
        return round(mean_value, 2)
    except Exception as e:
        print(f"Error: {e}")
        return 0


def fetch_raster_value(date, url, gdf):
    try:
        raster = rasterio.open(url)
        value = get_raster_value(gdf, raster)
    except:
        value = 0
    print(date, value)
    return {'date': date, 'value': value}

def get_metdata(request):
        layers = request.GET.get('layers')
        dates = request.GET.get('dates')
        code = request.GET.get('code')
        
        layers = json.loads(layers)
        dates = json.loads(dates)

        workspace = layers[0].split(':')[0]
        layer_names = [layer.split(':')[1] for layer in layers]
        urls = [f"{ENDPOINT}/{workspace}/{layer}/{layer}.geotiff" for layer in layer_names]
        
        if code.endswith("00"):
            area_url = f"{GEOSERVER}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Aprovincias&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON={code}"
        else:
            area_url = f"{GEOSERVER}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Acantones&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON={code}"
        #
        area = requests.get(area_url).json()
        gdf = gpd.GeoDataFrame.from_features(area["features"])
        # 
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(lambda date_url: fetch_raster_value(date_url[0], date_url[1], gdf), zip(dates, urls)))
        #
        return JsonResponse(results, safe=False)

        


#product = "chirps"
#temporality = "daily"
#start = "2024-01-01"
#end = "2024-06-01"
#code = "1500"