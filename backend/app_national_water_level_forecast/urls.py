from django.urls import path
from .controllers import get_water_level_alerts

urlpatterns = [
    path('water-level-alerts', get_water_level_alerts,  name="water-level-alerts")
]
