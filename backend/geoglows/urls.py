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

    path('firms-data-24', 
          heatpoints_24h, 
          name="firms-data-24"),

    path('goes-hotspots', 
          goes_hotspots, 
          name="goes-hotspots"),

    path('download-layer', 
          download_layer, 
          name="download-layer"),

    path('geoglows-flood-warnings', 
          get_geoglows_flood_warnings, 
          name="geoglows-flood-warnings"),

    path('geoglows-streamflow-warnings', 
          get_geoglows_streamflow_warnings, 
          name="geoglows-streamflow-warnings"),

    path('geoglows-waterlevel-warnings', 
          get_geoglows_waterlevel_warnings, 
          name="geoglows-waterlevel-warnings"),

    path('historical-simulation-plot', 
          get_historical_simulation_plot, 
          name="historical-simulation-plot"),

    path('geoglows-data-plot', 
          get_data_plot, 
          name="geoglows-data-plot"),

    path('geoglows-table', 
          get_probability_table, 
          name="geoglows-table"),

    path('get-historical-simulation-csv', 
          get_historical_simulation_csv, 
          name="get-historical-simulation-csv"),

    path('get-forecast-csv', 
          get_forecast_csv, 
          name="get-forecast-csv"),

    path('retrieve-daily-hydropower-report', 
          retrieve_daily_hydropower_report, 
          name="retrieve-daily-hydropower-report"),
      
]

