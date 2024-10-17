from django.urls import path
from .controllers import get_hydropower_daily_forecast, get_hydropower_daily_forecast_csv
urlpatterns = [
    path('get-hydropower-daily-forecast', get_hydropower_daily_forecast,  name="get-hydropower-daily-forecast"),
    path('get-hydropower-daily-forecast-csv', get_hydropower_daily_forecast_csv,  name="get-hydropower-daily-forecast-csv"),
]

# https://inamhi.geoglows.org/api/hydromet-report-tool/get-hydropower-daily-forecast