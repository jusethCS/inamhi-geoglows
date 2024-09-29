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


def get_bias_corrected_data(sim, obs):
    """
    Apply bias correction to simulated historical streamflow data based on 
    observed data.

    This function uses the GEOGloWS library to perform bias correction on 
    historical simulated data (`sim`) by adjusting it according to observed 
    data (`obs`). The function removes any NaN values from both datasets 
    before applying the correction.

    Parameters:
    -----------
    - sim : pandas.DataFrame or pandas.Series
        The simulated historical data that will undergo bias correction. This 
        dataset should have a datetime index and corresponding streamflow values.
    
    - obs : pandas.DataFrame or pandas.Series
        The observed historical data used for bias correction. This dataset must
        match the time period and format of the simulated data.

    Returns:
    --------
    - pandas.DataFrame or pandas.Series
        The bias-corrected simulated data, with the datetime index formatted
        as "%Y-%m-%d %H:%M:%S" and converted back to a pandas `DatetimeIndex`.
    """
    outdf = geoglows.bias.correct_historical(sim.dropna(), obs.dropna())
    outdf.index = pd.to_datetime(outdf.index)
    outdf.index = outdf.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    outdf.index = pd.to_datetime(outdf.index)
    return outdf


def get_corrected_forecast(simulated_df, ensemble_df, observed_df):
    """
    Correct the forecasted ensembles based on the simulated and observed 
    historical data.

    This function calculates correction factors for forecasted ensembles 
    based on simulated and observed data. It adjusts the forecast values 
    to lie within the range defined by the minimum and maximum of the 
    historical simulated data for the corresponding month.

    Parameters:
    -----------
    simulated_df : pandas.DataFrame
        A DataFrame containing simulated historical data with a datetime index.
    
    ensemble_df : pandas.DataFrame
        A DataFrame containing forecasted ensemble data with a datetime index.
    
    observed_df : pandas.DataFrame
        A DataFrame containing observed historical data with a datetime index.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the bias-corrected ensemble forecasts.

    """
    # Extract the month from the first entry in the ensemble DataFrame
    forecast_month = ensemble_df.index[0].month
    
    # Filter simulated and observed data for the corresponding month and drop NaNs
    monthly_simulated = simulated_df[simulated_df.index.month == forecast_month].dropna()
    monthly_observed = observed_df[observed_df.index.month == forecast_month].dropna()
    
    # Calculate the minimum and maximum of the simulated data for that month
    min_simulated = monthly_simulated.iloc[:, 0].min()
    max_simulated = monthly_simulated.iloc[:, 0].max()
    
    # Create copies of the ensemble DataFrame for correction factors
    min_factor_df = ensemble_df.copy()
    max_factor_df = ensemble_df.copy()
    forecast_ens_df = ensemble_df.copy()

    # Iterate through each column in the ensemble DataFrame
    for column in ensemble_df.columns:
        # Create a temporary DataFrame to avoid modifying the original ensemble
        tmp = ensemble_df[column].dropna().to_frame()

        # Calculate the minimum correction factor
        min_factor = (tmp[column] >= min_simulated).astype(float)
        min_factor[tmp[column] < min_simulated] = tmp[column][tmp[column] < min_simulated] / min_simulated
        
        # Calculate the maximum correction factor
        max_factor = (tmp[column] <= max_simulated).astype(float)
        max_factor[tmp[column] > max_simulated] = tmp[column][tmp[column] > max_simulated] / max_simulated

        # Update the temporary DataFrame to enforce limits
        tmp[column] = np.clip(tmp[column], min_simulated, max_simulated)

        # Update the forecast and correction factor DataFrames
        forecast_ens_df[column] = tmp[column]
        min_factor_df[column] = min_factor
        max_factor_df[column] = max_factor

    # Apply bias correction using the GEOGloWS library
    corrected_ensembles = geoglows.bias.correct_forecast(forecast_ens_df, simulated_df, observed_df)
    
    # Apply the minimum and maximum correction factors
    corrected_ensembles *= min_factor_df
    corrected_ensembles *= max_factor_df
    return corrected_ensembles


def gumbel_1(sd: float, mean: float, rp: float) -> float:
    """
    Calculate the Gumbel Type I distribution value for a given return period.

    This function calculates the Gumbel Type I distribution value based on the
    provided standard deviation, mean, and return period.

    Parameters:
    -----------
    - sd: float 
        The standard deviation of the dataset.
    - mean: float
        The mean of the dataset.
    - return_period: float
        The return period for which the value is calculated.

    Returns:
    --------
     - float: 
        The calculated Gumbel Type I distribution value.
    """
    try:
        # Validate input parameters
        if sd <= 0:
            raise ValueError("Standard deviation must be positive.")
        if rp <= 1:
            raise ValueError("Return period must be greater than 1.")
        
        # Calculate the Gumbel reduced variate
        y = -math.log(-math.log(1 - (1 / rp)))
        
        # Calculate the Gumbel Type I distribution value
        gumbel_value = y * sd * 0.7797 + mean - (0.45 * sd)
        return gumbel_value
    except Exception as e:
        print(e)
        return 0



def get_return_periods(comid: int, data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate return period values for a given COMID based on annual maximum 
    flow data.

    This function calculates the annual maximum flow statistics (mean and 
    standard deviation), computes the corrected return period values using the 
    Gumbel Type I distribution, and returns these values in a DataFrame.

    Parameters:
    -----------
    - comid: int
        The COMID (unique identifier for a river segment).
    - data: pd.DataFrame
        DataFrame containing flow data with a datetime index.

    Returns:
    --------
    - pd.DataFrame
        DataFrame containing the corrected return period values for the 
        specified COMID.

    """
    if data.empty:
        raise ValueError("The input data is empty.")
    
    # Calculate the maximum annual flow
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    if max_annual_flow.empty:
        raise ValueError("No annual maximum flow data available.")
    
    # Calculate the mean and standard deviation of the maximum annual flow
    mean_value = np.mean(max_annual_flow.iloc[:, 0].values)
    std_value = np.std(max_annual_flow.iloc[:, 0].values)
    
    # Define the return periods to calculate
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []
    
    # Compute the corrected return period values using the Gumbel Type I distribution
    for rp in return_periods:
        return_periods_values.append(gumbel_1(std_value, mean_value, rp))
    
    # Create a dictionary to store the return period values
    data_dict = {
        'rivid': [comid],
        'return_period_100': [return_periods_values[0]],
        'return_period_50': [return_periods_values[1]],
        'return_period_25': [return_periods_values[2]],
        'return_period_10': [return_periods_values[3]],
        'return_period_5': [return_periods_values[4]],
        'return_period_2': [return_periods_values[5]]
    }
    
    # Convert the dictionary to a DataFrame and set 'rivid' as the index
    rperiods_df = pd.DataFrame(data=data_dict)
    rperiods_df.set_index('rivid', inplace=True)
    return rperiods_df




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



def get_plot_data(request):
    # Query request param and initialize the db connection
    comid = request.GET.get('comid')
    code = request.GET.get('code')
    date = request.GET.get('date')
    width = request.GET.get('width')
    width = float(width)
    width2 = width/2
    db = create_engine(token)
    con = db.connect()

    # Retrieve observed data
    sql = f"SELECT datetime, value FROM streamflow_data WHERE code='{code}'"
    observed_data = get_format_data(sql, con)
    observed_data[observed_data < 0.1] = 0.1
    
    # Retrieve historical simulation and corrected data
    sql = f"SELECT datetime, value FROM historical_simulation WHERE comid={comid}"
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1
    corrected_data = get_bias_corrected_data(simulated_data, observed_data)

    # Retrieve ensemble forecast data
    sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])

    # Corrected forecast
    corrected_ensemble_forecast = get_corrected_forecast(simulated_data, ensemble_forecast, observed_data)
    return_periods = get_return_periods(comid, corrected_data)
    return HttpResponse("Funciona todo!")





    
    #return_periods = get_return_periods(comid, historical_simulation)
    #sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    #ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])
    #stats = get_ensemble_stats(ensemble_forecast)
    #sql = f"SELECT datetime,value FROM forecast_records where comid={comid}"
    #records = get_format_data(sql, con)
    #hs = hs_plot(historical_simulation, return_periods, comid, width)
    #dp = daily_plot(historical_simulation, comid, width)
    #mp = monthly_plot(historical_simulation, comid, width)
    #vp = volumen_plot(historical_simulation, comid, width2)
    #fd = fd_plot(historical_simulation, comid, width2)
    #fp = forecast_plot(stats, return_periods, comid, records, historical_simulation, width)
    #tb = get_probabilities_table(stats, ensemble_forecast, return_periods)
    #con.close()
    #return({"hs":hs, "dp":dp, "mp":mp, "vp":vp, "fd": fd, "fp":fp})