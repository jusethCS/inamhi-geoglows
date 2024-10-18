import os
import datetime as dt
from io import BytesIO, StringIO
import matplotlib.pyplot as plt
from .utils import plot_daily_forecast, extract_raster_values_to_points
from django.http import HttpResponse


def get_hydropower_daily_forecast(request):
    try:
        now = dt.datetime.now()
        tomorrow = now + dt.timedelta(days=1)
        a = now.strftime("%Y-%m-%d00Z-24H-")
        b = tomorrow.strftime("%Y%m%d07h00")
        datestr = f"{a}{b}"
        url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
        fig = plot_daily_forecast(url)
    except:
        now = dt.datetime.now() - dt.timedelta(days=2)
        tomorrow = now + dt.timedelta(days=2)
        a = now.strftime("%Y-%m-%d00Z-24H-")
        b = tomorrow.strftime("%Y%m%d07h00")
        datestr = f"{a}{b}"
        url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
        fig = plot_daily_forecast(url)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')


def get_hydropower_daily_forecast_csv(request):
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

    # Create a CSV in memory
    csv_buffer = StringIO()
    data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Create a HttpResponse object with CSV data
    response = HttpResponse(csv_buffer, content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=hydropower_daily_forecast.csv'
    return response