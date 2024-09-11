import os
import json
import pandas as pd
import datetime as dt
import geopandas as gpd
from shapely.geometry import Point
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Import enviromental variables
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)


def assign_icon(frp):
    if 0 <= frp < 1:
        return 'F01'
    elif 1 <= frp < 5:
        return 'F02'
    elif 5 <= frp < 10:
        return 'F03'
    elif 10 <= frp < 20:
        return 'F04'
    elif 20 <= frp < 40:
        return 'F05'
    elif 40 <= frp < 70:
        return 'F06'
    elif 70 <= frp < 100:
        return 'F07'
    elif 100 <= frp < 150:
        return 'F08'
    elif 150 <= frp < 300:
        return 'F09'
    elif 300 <= frp < 500:
        return 'F10'
    else:
        return None

def get_heatpoints_24h():
    now = dt.datetime.now() - dt.timedelta(hours=5)
    start = (now - dt.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:00")
    con = db.connect()
    sql = f"select * from heatpoint where acq_datetime>'{start}' order by frp ASC"
    query = pd.read_sql(sql, con)
    query['icon'] = query['frp'].apply(assign_icon)
    query['acq_datetime'] = query['acq_datetime'].apply(lambda x:x.strftime("%Y-%m-%d %H:%M:00"))
    con.close()
    query['geometry'] = query.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    gdf = gpd.GeoDataFrame(query, geometry='geometry')
    geojson_dict = gdf.__geo_interface__
    return(geojson_dict)


def get_goes_hotspots():
    now = dt.datetime.now()
    start = (now - dt.timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:00")
    con = db.connect()
    sql = f"select distinct * from goes_hotspots where datetime > '{start}' order by datetime"
    query = pd.read_sql(sql, con)
    con.close()
    query['datetime'] = pd.to_datetime(query['datetime']) + dt.timedelta(minutes=10)
    query['datetime'] = query['datetime'].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:00"))
    query['geometry'] = query.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    #
    # Asignar códigos d01, d02, d03, etc., basado en el día
    query['datetime_full'] = pd.to_datetime(query['datetime'])
    unique_datetimes = query['datetime_full'].drop_duplicates().reset_index(drop=True)
    datetime_map = {dt: i for i, dt in enumerate(unique_datetimes)}
    query['step'] = query['datetime_full'].map(datetime_map)
    query = query.drop('datetime_full', axis=1)
    #
    # Crear GeoDataFrame
    gdf = gpd.GeoDataFrame(query, geometry='geometry')
    geojson_dict = gdf.__geo_interface__
    return geojson_dict


#a = get_goes_hotspots()


