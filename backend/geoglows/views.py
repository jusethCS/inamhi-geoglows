from django.http import JsonResponse, HttpResponse
from .controllers.download import stream_file
from .controllers.fireforest import get_heatpoints_24h
from .controllers.geoglows import *

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

def download_layer(request):
    workspace = request.GET.get('workspace')
    layer = request.GET.get('layer')
    response = stream_file(workspace, layer, f"{workspace}-{layer}.tif")
    return response

def heatpoints_24h(request):
    data = get_heatpoints_24h()
    return JsonResponse(data)

def get_geoglows_flood_warnings(request):
    date = request.GET.get('date')
    data = get_flood_alerts(date)
    return JsonResponse(data)

def get_historical_simulation_plot(request):
    comid = request.GET.get('comid')
    plot = historical_simulation_plot(comid)
    return HttpResponse(plot)
