from django.urls import path
from .controllers import get_streamflow_alerts, get_plot_data, get_forecast_table
from .controllers import get_forecast_csv, get_corrected_simulation_csv, get_historical_simulation_csv


urlpatterns = [
    path('streamflow-alerts', get_streamflow_alerts,  name="streamflow-alerts"),
    path('plot-data', get_plot_data,  name="plot-data"),
    path('forecast-table', get_forecast_table,  name="forecast-table"),
    path('historical-simulation-csv', get_historical_simulation_csv,  name="historical-simulation-csv"),
    path('corrected-simulation-csv', get_corrected_simulation_csv,  name="corrected-simulation-csv"),
    path('forecast-csv', get_forecast_csv,  name="forecast-csv"),
]
