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
import plotly.io as pio
import plotly.graph_objects as go

# Web services and responses in Django
import jinja2
from django.http import JsonResponse, HttpResponse

# Custom
from .utils import correct_historical, correct_forecast



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
    outdf = correct_historical(sim.dropna(), obs.dropna())
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
    corrected_ensembles = correct_forecast(forecast_ens_df, simulated_df, observed_df)
    
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



def ensemble_quantile(ensemble: pd.DataFrame, quantile: float, 
                      label: str) -> pd.DataFrame:
    """
    Calculate the specified quantile for an ensemble and return it as a 
    DataFrame.

    This function computes the specified quantile for each row in the ensemble
    DataFrame and returns the results in a new DataFrame with the specified 
    label as the column name.

    Parameters:
    -----------
    - ensemble: pd.DataFrame
        DataFrame containing the ensemble data.
    - quantile: float
        The quantile to compute (between 0 and 1).
    - label:str 
        The label for the resulting quantile column.

    Returns:
    --------
    - pd.DataFrame
        DataFrame containing the computed quantile with the specified label.
    """
    # Calculate the quantile along the columns (axis=1) and convert to a DataFrame
    quantile_df = ensemble.quantile(quantile, axis=1).to_frame()
    
    # Rename the column to the specified label
    quantile_df.rename(columns={quantile: label}, inplace=True)
    return quantile_df



def get_ensemble_stats(ensemble: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various statistical measures for an ensemble and return them in a 
    DataFrame.

    This function calculates the maximum, 75th percentile, median, 25th percentile,
    and minimum flows for the ensemble. It also includes the high-resolution flow 
    data (ensemble_52).

    Parameters:
    -----------
    - ensemble: pd.DataFrame
        DataFrame containing the ensemble data.

    Returns:
    --------
    - pd.DataFrame
        DataFrame containing the statistical measures and high-resolution flow data.
    """
    # Extract the high-resolution data and remove it from the ensemble
    high_res_df = ensemble['ensemble_52'].to_frame()
    ensemble.drop(columns=['ensemble_52'], inplace=True)
    
    # Remove rows with NaN values in both the ensemble and high-resolution data
    ensemble.dropna(inplace=True)
    high_res_df.dropna(inplace=True)
    
    # Rename the column for high-resolution data
    high_res_df.rename(columns={'ensemble_52': 'high_res'}, inplace=True)
    
    # Calculate various quantiles and concatenate them into a single DataFrame
    stats_df = pd.concat([
        ensemble_quantile(ensemble, 1.00, 'flow_max'),
        ensemble_quantile(ensemble, 0.75, 'flow_75%'),
        ensemble_quantile(ensemble, 0.50, 'flow_avg'),
        ensemble_quantile(ensemble, 0.25, 'flow_25%'),
        ensemble_quantile(ensemble, 0.00, 'flow_min'),
        high_res_df
    ], axis=1)
    return stats_df



def get_corrected_forecast_records(records_df, simulated_df, observed_df):
    """
    Correct the forecasted records based on simulated and observed data.

    This function iterates through the months present in the input records 
    DataFrame, applies bias correction using the simulated and observed data, 
    and ensures that the corrected values fall within the range defined by 
    the historical simulated data.

    Parameters:
    -----------
    records_df : pandas.DataFrame
        A DataFrame containing forecasted records with a datetime index.
    
    simulated_df : pandas.DataFrame
        A DataFrame containing simulated historical data with a datetime index.
    
    observed_df : pandas.DataFrame
        A DataFrame containing observed historical data with a datetime index.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the bias-corrected forecast records.
    """    
    # Extract the starting and ending dates from the records DataFrame
    date_ini = records_df.index[0]
    date_end = records_df.index[-1]
    
    # Create a range of months from the initial month to the final month
    meses = np.arange(date_ini.month, date_end.month + 1, 1)
    fixed_records = pd.DataFrame()
    
    # Iterate through each month in the specified range
    for mes in meses:
        # Filter records, simulated, and observed data for the current month
        values = records_df.loc[records_df.index.month == mes]
        monthly_simulated = simulated_df[simulated_df.index.month == mes].dropna()
        monthly_observed = observed_df[observed_df.index.month == mes].dropna()
        
        # Calculate min and max of the simulated data for the current month
        min_simulated = monthly_simulated.iloc[:, 0].min()
        max_simulated = monthly_simulated.iloc[:, 0].max()

        # Create temporary DataFrame for the current month's values
        column_records = values.columns[0]
        tmp = values[column_records].dropna().to_frame()

        # Create min and max correction factors
        min_factor = np.where(tmp[column_records] >= min_simulated, 1,
                              tmp[column_records] / min_simulated)
        max_factor = np.where(tmp[column_records] <= max_simulated, 1,
                              tmp[column_records] / max_simulated)

        # Clip the values to ensure they are within the simulated range
        tmp[column_records] = tmp[column_records].clip(lower=min_simulated, upper=max_simulated)
        
        # Create a DataFrame to hold corrected values
        fixed_records_df = values.copy()
        fixed_records_df[column_records] = tmp[column_records]
        
        # Create DataFrames for correction factors
        min_factor_records_df = values.copy()
        max_factor_records_df = values.copy()
        min_factor_records_df[column_records] = min_factor
        max_factor_records_df[column_records] = max_factor
        
        # Apply bias correction using the GEOGloWS library
        corrected_values = correct_forecast(fixed_records_df, simulated_df, observed_df)
        
        # Multiply the corrected values by the min and max correction factors
        corrected_values *= min_factor_records_df
        corrected_values *= max_factor_records_df
        
        # Append the corrected values to the final DataFrame
        fixed_records = pd.concat([fixed_records, corrected_values])

    # Sort the index of the final DataFrame
    fixed_records.sort_index(inplace=True)
    return fixed_records


###############################################################################
#                             PLOTS AND TABLES                                #
###############################################################################
def historical_plot(cor, obs, code, name):
    dates = cor.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]
    corrected_data = {
        'x_datetime': cor.index.tolist(),
        'y_flow': cor.values.flatten(),
    }
    observed_data = {
        'x_datetime': obs.index.tolist(),
        'y_flow': obs.values.flatten(),
    }
    scatter_plots = [
        go.Scatter(
            name='Simulación histórica corregida', 
            x=corrected_data['x_datetime'], 
            y=corrected_data['y_flow']),
        go.Scatter(
            name='Datos observados', 
            x=observed_data['x_datetime'], 
            y=observed_data['y_flow'])
    ]
    layout = go.Layout(
        title=f"Simulación histórica <br>{str(code).upper()} - {name}",
        yaxis={
            'title': 'Nivel (m)', 
            'range': [0, 'auto']},
        xaxis={
            'title': 'Fecha (UTC +0:00)', 
            'range': [startdate, enddate], 
            'hoverformat': '%b %d %Y', 
            'tickformat': '%Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white')
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    figure_dict = figure.to_dict()
    return figure_dict
    



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
    name = request.GET.get('name')
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
    corrected_return_periods = get_return_periods(comid, corrected_data)
    corrected_stats = get_ensemble_stats(corrected_ensemble_forecast)

    # Forecast records
    sql = f"SELECT datetime,value FROM forecast_records where comid={comid}"
    forecast_records = get_format_data(sql, con)
    corrected_forecast_records = get_corrected_forecast_records(forecast_records, simulated_data, observed_data)

    #Plots
    hs = historical_plot(corrected_data, observed_data, code, name)
    return HttpResponse("Funciona")





    

    
    #hs = hs_plot(historical_simulation, return_periods, comid, width)
    #dp = daily_plot(historical_simulation, comid, width)
    #mp = monthly_plot(historical_simulation, comid, width)
    #vp = volumen_plot(historical_simulation, comid, width2)
    #fd = fd_plot(historical_simulation, comid, width2)
    #fp = forecast_plot(stats, return_periods, comid, records, historical_simulation, width)
    #tb = get_probabilities_table(stats, ensemble_forecast, return_periods)
    #con.close()
    #return({"hs":hs, "dp":dp, "mp":mp, "vp":vp, "fd": fd, "fp":fp})