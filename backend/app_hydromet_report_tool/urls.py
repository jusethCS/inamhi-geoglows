from django.urls import path
from .controllers import *

urlpatterns = [
    path('hydropower-daily-forecast', get_hydropower_daily_forecast,  name="hydropower-daily-forecast"),
    path('hydropower-weekly-forecast', get_hydropower_weekly_forecast,  name="hydropower-weekly-forecast"),
    path('hydropower-daily-forecast-report', get_hydropower_daily_forecast_report,  name="hydropower-daily-forecast-report"),
    path('hydropower-weekly-forecast-report', get_hydropower_weekly_forecast_report,  name="hydropower-weekly-forecast-report"),
]