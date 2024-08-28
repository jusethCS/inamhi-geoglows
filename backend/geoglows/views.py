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


###

def get_geoglows_flood_warnings(request):
    date = request.GET.get('date')
    data = get_flood_alerts(date)
    return JsonResponse(data)

def get_geoglows_streamflow_warnings(request):
    date = request.GET.get('date')
    data = get_streamflow_alerts(date)
    return JsonResponse(data)

def get_historical_simulation_plot(request):
    comid = request.GET.get('comid')
    plot = historical_simulation_plot(comid)
    return JsonResponse(plot)

def get_data_plot(request):
    comid = request.GET.get('comid')
    date = request.GET.get('date')
    width = request.GET.get('width')
    plot = all_data_plot(comid, date, width)
    return JsonResponse(plot)

def get_probability_table(request):
    comid = request.GET.get('comid')
    date = request.GET.get('date')
    table = probability_table(comid, date)
    return HttpResponse(table)

def get_historical_simulation_csv(request):
    comid = request.GET.get('comid')
    historical_simulation = historical_data_csv(comid)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="historical_simulation_{comid}.csv"'
    historical_simulation.to_csv(path_or_buf=response, index=True)
    return response

def get_forecast_csv(request):
    comid = request.GET.get('comid')
    date = request.GET.get('date')
    forecast = forecast_csv(comid, date)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="ensemble_forecast_{comid}.csv"'
    forecast.to_csv(path_or_buf=response, index=True)
    return response
