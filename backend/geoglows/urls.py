from django.urls import path
from .views import *

urlpatterns = [
    path('daily-precipitation', 
          download_daily_precipitation, 
          name="daily-precipitation"),

    path('days-without-precipitation', 
          download_days_without_precipitation, 
          name="days-without-precipitation"),

    path('3days-precipitation', 
          download_3days_precipitation, 
          name="days-without-precipitation"),

    path('soil-moisture', 
          download_soil_moisture, 
          name="soil-moisture"),
      


]

