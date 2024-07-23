import os
import pandas as pd
import datetime as dt
import geopandas as gpd
from shapely.geometry import Point



# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)

# 
ecu = gpd.read_file("inamhi-geoglows/taskfiles/shp/ecuador.shp")

# URL
url = ("https://firms.modaps.eosdis.nasa.gov/mapserver/wfs/South_America/"
       "75d41dd1e5a2735af15f180c3ef8af81/?SERVICE=WFS&REQUEST=GetFeature&"
       "VERSION=2.0.0&TYPENAME=ms:fires_noaa20_7days&STARTINDEX=0&COUNT="
       "10000&SRSNAME=urn:ogc:def:crs:EPSG::4326&BBOX=-5.3,-92,2,-74.9,urn:"
       "ogc:def:crs:EPSG::4326&outputformat=csv")

# Leer el archivo CSV desde la URL
data = pd.read_csv(url)
data = data.drop(columns=['WKT', "acq_date", "acq_time"])
dts = pd.to_datetime(data['acq_datetime'])
data['acq_datetime'] = dts.apply(lambda x:x.strftime("%Y-%m-%d %H:%M"))


geometry = [Point(xy) for xy in zip(data['longitude'], data['latitude'])]
geo_df = gpd.GeoDataFrame(data, geometry=geometry)

# Asegurarse de que ambos GeoDataFrames tengan la misma referencia espacial
geo_df.set_crs(epsg=4326, inplace=True)
ecu = ecu.to_crs(epsg=4326)

# Filtrar los puntos que están dentro del shapefile de Ecuador
points_within_ecuador = geo_df[geo_df.geometry.within(ecu.unary_union)]











# URL del archivo CSV
url = "https://firms.modaps.eosdis.nasa.gov/mapserver/wfs/South_America/75d41dd1e5a2735af15f180c3ef8af81/?SERVICE=WFS&REQUEST=GetFeature&VERSION=2.0.0&TYPENAME=ms:fires_noaa20_24hrs&STARTINDEX=0&COUNT=10000&SRSNAME=urn:ogc:def:crs:EPSG::4326&BBOX=-7.5,-94,4,-70,urn:ogc:def:crs:EPSG::4326&outputformat=csv"

# Leer el archivo CSV desde la URL
data = pd.read_csv(url)
data = data.drop(columns=['WKT'])
data['acq_datetime'] = pd.to_datetime(data['acq_datetime'])
data['acq_datetime'] = data['acq_datetime'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))


# Mostrar los primeros registros del DataFrame
print(data.head())
