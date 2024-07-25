from django.http import JsonResponse
from .controllers.download import stream_file
from .controllers.fireforest import get_heatpoints_24h

def download_daily_precipitation(request):
    response = stream_file(
        "fireforest", "daily_precipitation", "daily-precipitation.tif")
    return response

def download_days_without_precipitation(request):
    response = stream_file(
        "fireforest", "no_precipitation_days", "days-without-precipitation.tif")
    return response

def download_3days_precipitation(request):
    response = stream_file(
        "fireforest", "3days_precipitation", "3days-precipitation.tif")
    return response

def download_soil_moisture(request):
    response = stream_file(
        "fireforest", "soil_moisture", "soil_moisture.tif")
    return response

def heatpoints_24h(request):
    data = get_heatpoints_24h()
    return JsonResponse(data, safe=False)
