from django.urls import path
from .controllers import get_hydropower_daily_forecast, get_hydropower_daily_forecast_csv, get_hydropower_weekly_forecast, get_hydropower_weekly_forecast_csv
urlpatterns = [
    path('get-hydropower-daily-forecast', get_hydropower_daily_forecast,  name="get-hydropower-daily-forecast"),
    path('get-hydropower-daily-forecast-csv', get_hydropower_daily_forecast_csv,  name="get-hydropower-daily-forecast-csv"),
    path('get-hydropower-weekly-forecast', get_hydropower_weekly_forecast,  name="get-hydropower-weekly-forecast"),
    path('get-hydropower-weekly-forecast-csv', get_hydropower_weekly_forecast_csv,  name="get-hydropower-weekly-forecast-csv"),
]