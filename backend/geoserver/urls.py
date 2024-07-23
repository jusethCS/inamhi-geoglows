from django.urls import path
from .views import download

urlpatterns = [
    path('download', download)
]

