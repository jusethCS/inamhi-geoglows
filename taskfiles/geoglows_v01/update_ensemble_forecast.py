import os
import math
import numpy as np
import pandas as pd
import sqlalchemy as sql
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def update_ensemble_forecast(comid, date, con):
    # Construct the url data
    str_date = date.strftime('%Y%m%d')
    url = f'https://geoglows.ecmwf.int/api/ForecastEnsembles'
    url = f'{url}/?reach_id={comid}&date={str_date}&return_format=csv'
    #
    # Try to fetch the data until successful
    status = False
    while not status:
        try:
            # Read and format data
            df = pd.read_csv(url, index_col=0)
            df[df < 0] = 0
            df.index = pd.to_datetime(df.index)
            df["datetime"] = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
            columnas_ordenadas = ["datetime"] + [f'ensemble_{i:02d}_m^3/s' for i in range(1, 53)]
            df = df.reindex(columns=columnas_ordenadas)
            df['comid'] = comid
            df['initialized'] = date
            df.columns = [col.replace('_m^3/s', '') for col in df.columns]
            status = True
        except Exception as e:
                # Handle any exception and retry
                print("Error retrieving data:", e)
                print("Retrying to fetch data...", end="\n")
    #
    # Insert data into DB
    try:
        df.to_sql('ensemble_forecast', con=con, if_exists='append', index=False)
        con.commit()
        print(f"Inserted ensemble forecast data for commid {comid}, initialized on {date}")
    except:
        print("Retry insert ensemble forecast data into database")
        try:
            df.to_sql('ensemble_forecast', con=con, if_exists='append', index=False)
            con.commit()
        except Exception as e:
            # Handle any exception and retry
            print("Error:", e)



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




def get_warnings(comid, date, con):
    """
    Retrieve and process hydrological data to generate warnings based on 
    ensemble forecast exceedances of return period thresholds.

    Parameters:
    - comid (int): The identifier for the river reach.
    - date (str): The initialization date of the ensemble forecast.
    - con (sqlalchemy.engine.Connection): Database connection.

    Returns:
    - None
    """
    # Retrieve historical simulation data
    sql = f"SELECT datetime, value FROM historical_simulation WHERE comid={comid}"
    simulated_data = get_format_data(sql, con)
    #
    # Retrieve ensemble forecast data
    sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])
    max_ensemble_forecast = ensemble_forecast.resample('D').max()
    #
    # Retrieve return periods data
    return_periods = get_return_periods(comid, simulated_data)
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
        r2 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_2'].values[0]).sum()
        r5 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_5'].values[0]).sum()
        r10 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_10'].values[0]).sum()
        r25 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_25'].values[0]).sum()
        r50 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_50'].values[0]).sum()
        r100 = (max_ensemble_forecast.iloc[i] > return_periods['return_period_100'].values[0]).sum()
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
    out["comid"] = comid
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

# Determine the last date that was inserted into db
query = "select comid from drainage_network"
comids = pd.read_sql(query, con=con).comid

# Generate current date
date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)

# Insert data per comid
for comid in comids:
    update_ensemble_forecast(comid=comid, date=date, con=con)
    warnigs = get_warnings(comid, date, con)
    warnigs.to_sql('alert_geoglows', con=con, if_exists='append', index=False)
    con.commit()

# Close the connection
con.close()
