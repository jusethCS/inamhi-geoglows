from .controllers.download import stream_file

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