from django.urls import path
from .controllers import get_waterlevel_alerts

urlpatterns = [
    path('waterlevel-alerts', get_waterlevel_alerts,  name="waterlevel-alerts")
]
