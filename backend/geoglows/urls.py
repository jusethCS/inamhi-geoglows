from django.urls import path
from .views import download_daily_precipitaion

urlpatterns = [
    path('daily-precipitation', download_daily_precipitaion, name="download")
]

