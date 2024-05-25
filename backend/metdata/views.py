import requests
import rasterio


from django.http import JsonResponse
import json
from rasterio.mask import mask
import geopandas as gpd
import numpy as np
import requests
import pandas as pd
from io import BytesIO


SERVER = "http://ec2-3-211-227-44.compute-1.amazonaws.com"
GEOSERVER = f"{SERVER}/geoserver"
ENDPOINT = f"{SERVER}:4200"

# /usr/share/geoserver/data_dir/data

def get_raster_value(gdf, raster):
    geometries = gdf.geometry.values
    out_image, out_transform = mask(raster, geometries, crop=True)
    out_image = out_image.astype(float)
    out_image[out_image == raster.nodata] = np.nan
    return(round(np.nanmean(out_image), 2))


# Create your views here.
def get_metdata(request):
    # Get request parameters
    product = request.GET.get('product')
    temporality = request.GET.get('temp')
    start = request.GET.get('start')
    end = request.GET.get('end')
    code = request.GET.get('code')

    # Obtain area
    if code.endswith("00"):
        url = f"{GEOSERVER}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Aprovincias&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON={code}"
    else:
        url = f"{GEOSERVER}/ecuador-limits/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=ecuador-limits%3Acantones&maxFeatures=50&outputFormat=application%2Fjson&CQL_FILTER=DPA_CANTON={code}"
    area = requests.get(url).json()
    gdf = gpd.GeoDataFrame.from_features(area["features"])

    # Obtain
    workspace = f"{product}-{temporality}"
    
    if(temporality=="daily"):
        dates = pd.date_range(start=start, end=end, freq='D')
    elif(temporality=="monthly"):
        dates = pd.date_range(start=start, end=end, freq='MS')
    elif(temporality=="annual"):
        dates = pd.date_range(start=start, end=end, freq='YS')

    results = []
    for date in dates:
        dd = date.strftime('%Y-%m-%d')
        url = f"{ENDPOINT}/{workspace}/{dd}/{dd}.geotiff"
        print(url)
        try:
            raster_bytes = BytesIO(requests.get(url).content)
            raster = rasterio.open(raster_bytes)
            value = get_raster_value(gdf, raster)
        except:
            value = 0
        results.append({'date': dd, 'value': value})
        print(dd, value)

    return JsonResponse(results, safe=False)




# http://localhost:8000/api/metdata/get-metdata?product=chirps&temp=monthly&start=2023-01-01&end=2023-12-31&code=1301

# http://localhost:8000/api/metdata/get-metdata?product=chirps&temp=daily&start=2023-01-01&end=2023-12-31&code=1300