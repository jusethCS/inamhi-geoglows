from django.urls import path
from .views import *

urlpatterns = [
    path('daily-precipitation', 
          download_daily_precipitaion, 
          name="daily-precipitation"),

    path('days-without-precipitation', 
          download_days_without_precipitation, 
          name="days-without-precipitation")
]

