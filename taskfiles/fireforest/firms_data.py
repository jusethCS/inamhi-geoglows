import os
import pandas as pd
import datetime as dt
import geopandas as gpd
from shapely.geometry import Point
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Change the work directory
user = os.getlogin()
workdir = os.path.expanduser('~{}'.format(user))
workdir = os.path.join(workdir, 'inamhi-geoglows') 
os.chdir(workdir)

# Import enviromental variables
load_dotenv("db.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Read Ecuador shapefile
ecu = gpd.read_file("taskfiles/shp/ecuador.shp")
ecu = ecu.to_crs(epsg=4326)

# URL
url = ("https://firms.modaps.eosdis.nasa.gov/mapserver/wfs/South_America/"
       "75d41dd1e5a2735af15f180c3ef8af81/?SERVICE=WFS&REQUEST=GetFeature&"
       "VERSION=2.0.0&TYPENAME=ms:fires_noaa20_24hrs&STARTINDEX=0&COUNT="
       "10000&SRSNAME=urn:ogc:def:crs:EPSG::4326&BBOX=-5.3,-92,2,-74.9,urn:"
       "ogc:def:crs:EPSG::4326&outputformat=csv")

# Leer el archivo CSV desde la URL
data = pd.read_csv(url)
data = data.drop(columns=['WKT', "acq_date", "acq_time"])
dts = pd.to_datetime(data['acq_datetime']) - pd.to_timedelta(5, unit='h')
data['acq_datetime'] = dts.apply(lambda x:x.strftime("%Y-%m-%d %H:%M:00"))
data['acq_datetime'] = pd.to_datetime(data['acq_datetime'])

# Generate a geopandas dataframe
geometry = [Point(xy) for xy in zip(data['longitude'], data['latitude'])]
gdf = gpd.GeoDataFrame(data, geometry=geometry)
gdf = gdf.set_crs(epsg=4326, inplace=True)

# Filter the points within ecuador
gdf = gdf[gdf.geometry.within(ecu.geometry.union_all())]
data = gdf.drop(columns='geometry')


# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

out = pd.DataFrame()
for i in range(len(data.acq_datetime)):
    temp_df = pd.DataFrame(data.iloc[i].to_frame().T)
    latitude = temp_df.latitude.iloc[0]
    longitude = temp_df.longitude.iloc[0]
    acq_datetime = temp_df.acq_datetime.iloc[0]
    query = f"""
                SELECT COUNT(*) as c
                FROM heatpoint
                WHERE latitude={latitude} AND 
                      longitude={longitude} AND 
                      acq_datetime='{acq_datetime}'
            """
    cond =  pd.read_sql(query, con=con).c[0] > 0
    if not cond:
        out = pd.concat([out, temp_df])

out = out.astype(str)
print(out)

# Insert data into db
out.to_sql('heatpoint', con=con, if_exists='append', index=False)
print("Inserted VIIRS data!")
con.commit()
con.close()
