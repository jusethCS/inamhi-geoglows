import os
import math
import geoglows
import numpy as np
import pandas as pd
import sqlalchemy as sql
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine

import warnings
warnings.filterwarnings("ignore")


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
    #
    # Set the 'datetime' column as the DataFrame index
    data.index = pd.to_datetime(data['datetime'])
    #
    # Drop the 'datetime' column as it is now the index
    data = data.drop(columns=['datetime'])
    #
    # Format the index values to the desired datetime string format
    data.index = pd.to_datetime(data.index)
    data.index = data.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    data.index = pd.to_datetime(data.index)
    return(data)

def get_bias_corrected_data(sim, obs):
    outdf = geoglows.bias.correct_historical(sim.dropna(), obs.dropna())
    outdf.index = pd.to_datetime(outdf.index)
    outdf.index = outdf.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    outdf.index = pd.to_datetime(outdf.index)
    return(outdf)


def gumbel_1(sd: float, mean: float, rp: float) -> float:
    """
    Calculate the Gumbel Type I distribution value for a given return period.

    This function calculates the Gumbel Type I distribution value based on the
    provided standard deviation, mean, and return period.

    Parameters:
    sd (float): The standard deviation of the dataset.
    mean (float): The mean of the dataset.
    return_period (float): The return period for which the value is calculated.

    Returns:
    float: The calculated Gumbel Type I distribution value.

    Raises:
    ValueError: If standard_deviation is not positive or return_period is not 
    greater than 1.
    """
    try:
        # Validate input parameters
        if sd <= 0:
            raise ValueError("Standard deviation must be positive.")
        if rp <= 1:
            raise ValueError("Return period must be greater than 1.")
        #
        # Calculate the Gumbel reduced variate
        y = -math.log(-math.log(1 - (1 / rp)))
        #
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
    comid (int): The COMID (unique identifier for a river segment).
    data (pd.DataFrame): DataFrame containing flow data with a datetime index.

    Returns:
    pd.DataFrame: DataFrame containing the corrected return period values for 
    the specified COMID.

    Raises:
    ValueError: If the input data does not contain the necessary flow data.
    """
    if data.empty:
        raise ValueError("The input data is empty.")
    #
    # Calculate the maximum annual flow
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    #
    if max_annual_flow.empty:
        raise ValueError("No annual maximum flow data available.")
    #
    # Calculate the mean and standard deviation of the maximum annual flow
    mean_value = np.mean(max_annual_flow.iloc[:, 0].values)
    std_value = np.std(max_annual_flow.iloc[:, 0].values)
    #
    # Define the return periods to calculate
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []
    #
    # Compute the corrected return period values using the Gumbel Type I distribution
    for rp in return_periods:
        return_periods_values.append(gumbel_1(std_value, mean_value, rp))
    #
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
    #
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
    ensemble (pd.DataFrame): DataFrame containing the ensemble data.
    quantile (float): The quantile to compute (between 0 and 1).
    label (str): The label for the resulting quantile column.

    Returns:
    pd.DataFrame: DataFrame containing the computed quantile with the specified 
    label.
    """
    # Calculate the quantile along the columns (axis=1) and convert to a DataFrame
    quantile_df = ensemble.quantile(quantile, axis=1).to_frame()
    #
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
    ensemble (pd.DataFrame): DataFrame containing the ensemble data.

    Returns:
    pd.DataFrame: DataFrame containing the statistical measures and high-resolution
    flow data.
    """
    # Extract the high-resolution data and remove it from the ensemble
    high_res_df = ensemble['ensemble_52'].to_frame()
    ensemble.drop(columns=['ensemble_52'], inplace=True)
    #
    # Remove rows with NaN values in both the ensemble and high-resolution data
    ensemble.dropna(inplace=True)
    high_res_df.dropna(inplace=True)
    #
    # Rename the column for high-resolution data
    high_res_df.rename(columns={'ensemble_52': 'high_res'}, inplace=True)
    #
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

def get_corrected_forecast(simulated_df, ensemble_df, observed_df):
    monthly_simulated = simulated_df[simulated_df.index.month == (ensemble_df.index[0]).month].dropna()
    monthly_observed = observed_df[observed_df.index.month == (ensemble_df.index[0]).month].dropna()
    min_simulated = np.min(monthly_simulated.iloc[:, 0].to_list())
    max_simulated = np.max(monthly_simulated.iloc[:, 0].to_list())
    min_factor_df = ensemble_df.copy()
    max_factor_df = ensemble_df.copy()
    forecast_ens_df = ensemble_df.copy()
    for column in ensemble_df.columns:
      tmp = ensemble_df[column].dropna().to_frame()
      min_factor = tmp.copy()
      max_factor = tmp.copy()
      min_factor.loc[min_factor[column] >= min_simulated, column] = 1
      min_index_value = min_factor[min_factor[column] != 1].index.tolist()
      for element in min_index_value:
        min_factor[column].loc[min_factor.index == element] = tmp[column].loc[tmp.index == element] / min_simulated
      max_factor.loc[max_factor[column] <= max_simulated, column] = 1
      max_index_value = max_factor[max_factor[column] != 1].index.tolist()
      for element in max_index_value:
        max_factor[column].loc[max_factor.index == element] = tmp[column].loc[tmp.index == element] / max_simulated
      tmp.loc[tmp[column] <= min_simulated, column] = min_simulated
      tmp.loc[tmp[column] >= max_simulated, column] = max_simulated
      forecast_ens_df.update(pd.DataFrame(tmp[column].values, index=tmp.index, columns=[column]))
      min_factor_df.update(pd.DataFrame(min_factor[column].values, index=min_factor.index, columns=[column]))
      max_factor_df.update(pd.DataFrame(max_factor[column].values, index=max_factor.index, columns=[column]))
    corrected_ensembles = geoglows.bias.correct_forecast(forecast_ens_df, simulated_df, observed_df)
    corrected_ensembles = corrected_ensembles.multiply(min_factor_df, axis=0)
    corrected_ensembles = corrected_ensembles.multiply(max_factor_df, axis=0)
    return(corrected_ensembles)




def get_warnings(code, comid, date, con):
    """
    Retrieve and process hydrological data to generate warnings based on 
    ensemble forecast exceedances of return period thresholds.

    Parameters:
    - code (str): The indetifier for hydrological station.
    - comid (int): The identifier for the river reach.
    - date (str): The initialization date of the ensemble forecast.
    - con (sqlalchemy.engine.Connection): Database connection.

    Returns:
    - None
    """
    # Retrieve observed data
    sql = f"SELECT datetime, value FROM streamflow_data WHERE code='{code}'"
    observed_data = get_format_data(sql, con)
    observed_data[observed_data < 0.1] = 0.1
    #
    # Retrieve historical simulation and corrected data
    sql = f"SELECT datetime, value FROM historical_simulation WHERE comid={comid}"
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1
    corrected_data = get_bias_corrected_data(simulated_data, observed_data)
    #
    # Retrieve ensemble forecast data
    sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])
    # Corrected forecast
    corrected_ensemble_forecast = get_corrected_forecast(simulated_data, ensemble_forecast, observed_data)
    max_ensemble_forecast = corrected_ensemble_forecast.resample('D').max()
    return_periods = get_return_periods(comid, corrected_data)
    #
    # Initialize a list to store results
    results = []
    #
    # Threshold for triggering a warning
    cond = 20
    #
    # Iterate over each day in the resampled ensemble forecast
    for i, dts in enumerate(max_ensemble_forecast.index):
        # Count the number of ensemble members exceeding each return period threshold
        r2 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_2'].values[0]).sum() * 100/52
        r5 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_5'].values[0]).sum() * 100/52
        r10 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_10'].values[0]).sum() * 100/52
        r25 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_25'].values[0]).sum() * 100/52
        r50 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_50'].values[0]).sum() * 100/52
        r100 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_100'].values[0]).sum() * 100/52
        #
        # Determine the alert level based on the number of exceedances
        alert = "R0"
        if r2 >= cond:
            alert = "R2"
        if r5 >= cond:
            alert = "R5"
        if r10 >= cond:
            alert = "R10"
        if r25 >= cond:
            alert = "R25"
        if r50 >= cond:
            alert = "R50"
        if r100 >= cond:
            alert = "R100"
        #
        # Append the result to the list
        results.append({"alert": alert})
    #
    # Convert the list of results to a DataFrame
    out = pd.DataFrame(results)
    out = out.drop(out.index[-1]).T
    out["datetime"] = date
    out["code"] = code
    out = out.reset_index().drop(columns=['index'])
    new = {i: f'd{i+1:02d}' for i in range(15)}
    out.rename(columns=new, inplace=True)
    return(out)


def get_warnings_waterlevel(code, comid, date, con):
    """
    Retrieve and process hydrological data to generate warnings based on 
    ensemble forecast exceedances of return period thresholds.

    Parameters:
    - code (str): The indetifier for hydrological station.
    - comid (int): The identifier for the river reach.
    - date (str): The initialization date of the ensemble forecast.
    - con (sqlalchemy.engine.Connection): Database connection.

    Returns:
    - None
    """
    # Retrieve observed data
    sql = f"SELECT datetime, value FROM waterlevel_data WHERE code='{code}'"
    observed_data = get_format_data(sql, con)
    observed_data[observed_data < 0.1] = 0.1
    #
    # Retrieve historical simulation and corrected data
    sql = f"SELECT datetime, value FROM historical_simulation WHERE comid={comid}"
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1
    corrected_data = get_bias_corrected_data(simulated_data, observed_data)
    #
    # Retrieve ensemble forecast data
    sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])
    # Corrected forecast
    corrected_ensemble_forecast = get_corrected_forecast(simulated_data, ensemble_forecast, observed_data)
    max_ensemble_forecast = corrected_ensemble_forecast.resample('D').max()
    return_periods = get_return_periods(comid, corrected_data)
    #
    # Initialize a list to store results
    results = []
    #
    # Threshold for triggering a warning
    cond = 20
    #
    # Iterate over each day in the resampled ensemble forecast
    for i, dts in enumerate(max_ensemble_forecast.index):
        # Count the number of ensemble members exceeding each return period threshold
        r2 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_2'].values[0]).sum() * 100/52
        r5 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_5'].values[0]).sum() * 100/52
        r10 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_10'].values[0]).sum() * 100/52
        r25 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_25'].values[0]).sum() * 100/52
        r50 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_50'].values[0]).sum() * 100/52
        r100 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_100'].values[0]).sum() * 100/52
        #
        # Determine the alert level based on the number of exceedances
        alert = "R0"
        if r2 >= cond:
            alert = "R2"
        if r5 >= cond:
            alert = "R5"
        if r10 >= cond:
            alert = "R10"
        if r25 >= cond:
            alert = "R25"
        if r50 >= cond:
            alert = "R50"
        if r100 >= cond:
            alert = "R100"
        #
        # Append the result to the list
        results.append({"alert": alert})
    #
    # Convert the list of results to a DataFrame
    out = pd.DataFrame(results)
    out = out.drop(out.index[-1]).T
    out["datetime"] = date
    out["code"] = code
    out = out.reset_index().drop(columns=['index'])
    new = {i: f'd{i+1:02d}' for i in range(15)}
    out.rename(columns=new, inplace=True)
    return(out)


###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

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

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

# Generate current date
date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
#date = date - dt.timedelta(days=1)


# Determine the last date that was inserted into db
query = "select code,comid from streamflow_stations"
stations = pd.read_sql(query, con=con)

# Insert data per comid
for i in range(len(stations.code)):
    print(stations.code[i])
    try:
        warnigs = get_warnings(
            code = stations.code[i], 
            comid = stations.comid[i], 
            date=date, 
            con=con)
        warnigs.to_sql('alert_geoglows_streamflow', 
                    con=con, if_exists='append', index=False)
        con.commit()
    except:
        print(f"No se pudo generar alerta de caudal para {stations.code[i]}")
    


# Determine the last date that was inserted into db
query = "select code,comid from waterlevel_stations"
stations = pd.read_sql(query, con=con)

# Insert data per comid
for i in range(len(stations.code)):
    print(stations.code[i])
    try:
        warnigs = get_warnings(
            code = stations.code[i], 
            comid = stations.comid[i], 
            date=date, 
            con=con)
        warnigs.to_sql('alert_geoglows_waterlevel', 
                    con=con, if_exists='append', index=False)
        con.commit()
    except:
        print(f"No se pudo generar alerta de nivel para {stations.code[i]}")
    


# Close the connection
con.close()
