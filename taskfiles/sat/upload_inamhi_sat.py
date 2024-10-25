import os
import pandas as pd
import geopandas as gpd


###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("data/sat/")

ecuador = gpd.read_file("ecuador.shp")

categorical_order = pd.CategoricalDtype( 
    categories=["Medio", "Alto", "Muy Alto"],
    ordered=True
)
'''

# Temperature
warning = gpd.read_file("nowcast23.shp")
warning = warning.dropna(subset=['Nivel'])
warning = gpd.overlay(ecuador, warning, how="union")
warning["Nivel"] = warning["Nivel"].astype(categorical_order)
warning = warning.sort_values(by="Nivel")
warning.to_file("/usr/share/geoserver/data_dir/data/inamhi/advertencia_temp.shp")

'''
# Precipitation
warning = gpd.read_file("nowcast23.shp")
warning = warning.dropna(subset=['Nivel'])
warning = gpd.overlay(ecuador, warning, how="union")
warning["Nivel"] = warning["Nivel"].astype(categorical_order)
warning = warning.sort_values(by="Nivel")
warning.to_file("/usr/share/geoserver/data_dir/data/inamhi/advertencia_pacum.shp")
