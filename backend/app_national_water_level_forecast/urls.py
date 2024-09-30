from django.urls import path
from .controllers import get_water_level_alerts, get_plot_data, get_forecast_table

urlpatterns = [
    path('water-level-alerts', get_water_level_alerts,  name="water-level-alerts"),
    path('plot-data', get_plot_data,  name="plot-data"),
    path('forecast-table', get_forecast_table,  name="forecast-table"),
]
