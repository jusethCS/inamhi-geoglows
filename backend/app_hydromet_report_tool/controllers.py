import os
import datetime as dt
from io import BytesIO, StringIO
import matplotlib.pyplot as plt
from .utils import extract_raster_values_to_points
from .report import report_hydropower_forecast
from django.http import HttpResponse, JsonResponse


def get_hydropower_daily_forecast(request):
    try:
        now = dt.datetime.now()
        tomorrow = now + dt.timedelta(days=1)
        a = now.strftime("%Y-%m-%d00Z-24H-")
        b = tomorrow.strftime("%Y%m%d07h00")
        datestr = f"{a}{b}"
        url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
        data = extract_raster_values_to_points(url)
    except:
        now = dt.datetime.now() - dt.timedelta(days=1)
        tomorrow = now + dt.timedelta(days=2)
        a = now.strftime("%Y-%m-%d00Z-24H-")
        b = tomorrow.strftime("%Y%m%d07h00")
        datestr = f"{a}{b}"
        url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
        data = extract_raster_values_to_points(url)

    response_data = {'forecasts': data}
    return JsonResponse(response_data)


def get_hydropower_weekly_forecast(request):
    try:
        now = dt.datetime.now()
        tomorrow = now + dt.timedelta(days=7)
        a = now.strftime("%Y-%m-%d12Z-1W-")
        b = tomorrow.strftime("%Y%m%d07h00")
        datestr = f"{a}{b}"
        url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
        data = extract_raster_values_to_points(url)
    except:
        now = dt.datetime.now() - dt.timedelta(days=1)
        tomorrow = now + dt.timedelta(days=7)
        a = now.strftime("%Y-%m-%d12Z-1W-")
        b = tomorrow.strftime("%Y%m%d07h00")
        datestr = f"{a}{b}"
        url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
        data = extract_raster_values_to_points(url)

    response_data = {'forecasts': data}
    return JsonResponse(response_data)



def get_hydropower_daily_forecast_report(request):
    img_path = "/path_to_img"
    legend_path = "/path_to_legend"
    data = [1,1,1,1,1,1,1,1]
    pdf = report_hydropower_forecast(img_path, legend_path, data, "daily")
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="boletin_hidrometeorologico.pdf"'
    return response


def get_hydropower_weekly_forecast_report(request):
    img_path = "/path_to_img"
    legend_path = "/path_to_legend"
    data = [1,1,1,1,1,1,1,1]
    pdf = report_hydropower_forecast(img_path, legend_path, data, "weekly")
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="boletin_hidrometeorologico.pdf"'
    return response