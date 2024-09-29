###############################################################################
#                            LIBRARIES AND MODULES                            #
###############################################################################
# File system and environment management
import os
from dotenv import load_dotenv

# Date and time handling
import datetime as dt

# Mathematical and statistical operations
import math
import numpy as np
import scipy
import scipy.stats

# Data manipulation
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Databases and ORM
import sqlalchemy as sql
from sqlalchemy import create_engine

# Visualization
import geoglows
import plotly.io as pio
import plotly.graph_objects as go

# Web services and responses in Django
import jinja2
from django.http import JsonResponse, HttpResponse




###############################################################################
#                 ENVIROMENTAL VARIABLES AND CONNECTION TOKEN                 #
###############################################################################
# Import enviromental variables
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)




###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def get_format_data(sql_statement, conn):
    """
    Retrieve and format data from a database.

    This function executes an SQL query to retrieve data from a database,
    sets the 'datetime' column as the index of the DataFrame, formats the index
    to a specified datetime string format, and returns the formatted DataFrame.

    Parameters:
    sql_statement (str): SQL query to execute.
    conn (sqlalchemy.engine.base.Connection): Database connection object.

    Returns:
    pd.DataFrame: Formatted DataFrame with 'datetime' as the index.
    """
    # Retrieve data from the database using the SQL query
    data = pd.read_sql(sql_statement, conn)
    
    # Set the 'datetime' column as the DataFrame index
    data.index = pd.to_datetime(data['datetime'])
    
    # Drop the 'datetime' column as it is now the index
    data = data.drop(columns=['datetime'])
    
    # Format the index values to the desired datetime string format
    data.index = pd.to_datetime(data.index)
    data.index = data.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    data.index = pd.to_datetime(data.index)
    return(data)






###############################################################################
#                                CONTROLLERS                                  #
###############################################################################
def get_water_level_alerts(request):
    """
    Retrieve water level alerts for a specified date from the database and 
    return them as a GeoJSON response.

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain a 'date' 
        parameter in the GET request.

    Returns:
    --------
    - JsonResponse
        A Django JsonResponse object containing the GeoJSON data of water 
        level alerts for the given date.
    
    Notes:
    ------
    - The function assumes that `create_engine(token)` is correctly defined 
      and that `token` contains valid database connection information.
    - GeoPandas is used to handle geospatial data and generate GeoJSON format.
    
    """
    # Query request param and initialize the db connection
    date = request.GET.get('date')
    db = create_engine(token)
    con = db.connect()

    # SQL query to retrieve water level data for the specified date
    sql = f"""SELECT 
                    dn.code, dn.comid, dn.latitude, dn.longitude, dn.river,
                    dn.location1, dn.location2, ag.datetime,
                    ag.d01, ag.d02, ag.d03, ag.d04, 
                    ag.d05, ag.d06, ag.d07, ag.d08, 
                    ag.d09, ag.d10, ag.d11, ag.d12, 
                    ag.d13, ag.d14, ag.d15
                FROM 
                    waterlevel_stations dn
                JOIN 
                    alert_geoglows_waterlevel ag
                ON 
                    dn.code = ag.code
                WHERE 
                    ag.datetime = '{date}'
            """
    
    # Execute the query and load the data into a pandas DataFrame
    query = pd.read_sql(sql, con=con)
    con.close() 

    # Create Point geometries for each row based on longitude and latitude
    query['geometry'] = query.apply(
        lambda row: Point(row['longitude'], row['latitude']), axis=1)

    # Convert the DataFrame to GeoJSON format
    gdf = gpd.GeoDataFrame(query, geometry='geometry')
    data = gdf.__geo_interface__
    return JsonResponse(data)
