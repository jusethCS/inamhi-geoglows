import os
import math
import numpy as np
import pandas as pd
import sqlalchemy as sql
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine
import geopandas as gpd
from shapely.geometry import Point


# Import enviromental variables
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)


def get_flood_alerts(date):
    # Establish connection
    db = create_engine(token)
    con = db.connect()
    #
    # Determine the last date that was inserted into db
    sql = f"""SELECT 
                    dn.comid, dn.latitude, dn.longitude, dn.river,
                    dn.location1, dn.location2, ag.datetime,
                    ag.d01, ag.d02, ag.d03, ag.d04, 
                    ag.d05, ag.d06, ag.d07, ag.d08, 
                    ag.d09, ag.d10, ag.d11, ag.d12, 
                    ag.d13, ag.d14, ag.d15
                FROM 
                    drainage_network dn
                JOIN 
                    alert_geoglows ag
                ON 
                    dn.comid = ag.comid
                WHERE 
                    ag.datetime = '{date}'
            """
    query = pd.read_sql(sql, con=con)
    con.close()
    query['geometry'] = query.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    gdf = gpd.GeoDataFrame(query, geometry='geometry')
    geojson_dict = gdf.__geo_interface__
    return(geojson_dict)

