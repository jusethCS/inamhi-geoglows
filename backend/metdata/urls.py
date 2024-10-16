from django.urls import path
from .views import get_metdata

urlpatterns = [
    path('get-metdata', get_metdata, name="login")
]

