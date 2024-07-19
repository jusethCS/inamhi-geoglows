import os
import pandas as pd
import sqlalchemy as sql
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, select


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def init_db(pg_user:str, pg_pass:str, pg_file:str) -> None:
    """
    Initializes the PostgreSQL database by executing the SQL commands 
    from the provided SQL file.
    
    Parameters:
    pg_user (str): PostgreSQL username
    pg_pass (str): PostgreSQL password
    pg_file (str): Path to the SQL file containing the initialization commands

    """
    command = f"PGPASSWORD={pg_pass} psql -U {pg_user} -h localhost -f {pg_file}"
    os.system(command)



def insert_simple_table(table:str, con:sql.engine.base.Connection) -> None:
    """
    Inserts data from a CSV file into a simple table in the PostgreSQL database.
    
    Parameters:
    table (str): Name of the table into which data will be inserted
    con (Connection): SQLAlchemy Connection object
    
    """
    data = pd.read_csv(f"{table}.csv", sep=";")
    data.to_sql(table, con=con, if_exists='append', index=False)
    con.commit()



def insert_data_table(table: str, con: sql.engine.base.Connection, 
                      partitions: dict, var: str) -> None:
    """
    Inserts data from a CSV file into partitioned tables in the PostgreSQL 
    database.
    
    Parameters:
    table (str): Base name of the table into which data will be inserted
    con (Connection): SQLAlchemy Connection object
    partitions (dict): Dictionary mapping start dates to end dates for 
                       table partitions
    var (str): Name of the variable column in the melted dataframe

    """
    data = pd.read_csv(f"{table}.csv", sep=";")
    data['datetime'] = pd.to_datetime(data['datetime'])
    #
    # Convert the dataframe to long format
    data_long = data.melt(id_vars=['datetime'], var_name=var, 
                          value_name='value').dropna(subset=['value'])
    #
    for start_date, end_date in partitions.items():
        # Filter the data for the current partition
        mask = (data_long['datetime'] >= start_date) & (
               data_long['datetime'] < end_date)
        df_partition = data_long.loc[mask]
        #
        # Define the name of the partition table
        partition_table_name = f'{table}_{start_date[:4]}_{end_date[:4]}'
        #
        # Insert the data in chunks to avoid memory issues
        chunk_size = 1000
        for i in range(0, len(df_partition), chunk_size):
            chunk = df_partition.iloc[i:i+chunk_size]
            chunk.to_sql(partition_table_name, con=con, if_exists='append', 
                         index=False)
        #
        print(f"Inserted data from {start_date} to {end_date} into "
              f"{partition_table_name}!")


def insert_ensemble_forecast(data: pd.DataFrame, con: sql.engine.base.Connection) -> None:
    """
    Inserts ensemble forecast data from a DataFrame into partitioned tables in 
    the PostgreSQL database. The data is partitioned by month.

    Parameters:
    data (pd.DataFrame): DataFrame containing the ensemble forecast data. 
                         Must include 'datetime', 'comid', 'initialized' and
                         ensemble columns ('ensemble_01', 'ensemble_02', ...).
    con (Connection): SQLAlchemy Connection object for the PostgreSQL database.
    """
    # Define partitions
    partitions = {
        "2024-06-01": "2024-07-01",
        "2024-07-01": "2024-08-01",
        "2024-08-01": "2024-09-01",
        "2024-09-01": "2024-10-01",
        "2024-10-01": "2024-11-01",
        "2024-11-01": "2024-12-01",
        "2024-12-01": "2025-01-01",
        "2025-01-01": "2025-02-01",
        "2025-02-01": "2025-03-01",
        "2025-03-01": "2025-04-01",
        "2025-04-01": "2025-05-01",
        "2025-05-01": "2025-06-01"
    }
    table = "ensemble_forecast"
    #
    for start_date, end_date in partitions.items():
        # Filter the data for the current partition
        mask = (data['initialized'] >= start_date) & (data['initialized'] < end_date)
        df_partition = data.loc[mask]
        #
        if not df_partition.empty():
            # Define the name of the partition table
            partition_table_name = f'{table}_{start_date[:4]}_{start_date[5:7]}'
            #
            # Insert the data in chunks to avoid memory issues
            chunk_size = 1000
            for i in range(0, len(df_partition), chunk_size):
                chunk = df_partition.iloc[i:i + chunk_size]
                chunk.to_sql(partition_table_name, con=con, if_exists='append', index=False)
            #
            print(f"Inserted data from {start_date} to {end_date} into {partition_table_name}!")


def get_geoglows_data(comid: int, data_type: str, 
                      date:dt.datetime = dt.datetime.now()) -> pd.DataFrame:
    """
    Fetches data from GEOGLOWS API for a given reach (comid).

    Args:
        comid (int): Reach identifier for which data are requested.
        data_type (str): Type of the requested data:
            - ForecastRecords
            - EnsembleForecast

    Returns:
        pandas.DataFrame: DataFrame containing the requested data.
    """
    # Get the current date
    current_date = date
    #
    # Determine the start and end date to request
    start_date = current_date - dt.timedelta(days=60)
    start_date = start_date.strftime('%Y%m%d')
    end_date = current_date.strftime('%Y%m%d')
    #
    # Construct the URL for data request
    if data_type == "ForecastRecords":
        url = 'https://geoglows.ecmwf.int/api/ForecastRecords'
        url = f'{url}/?reach_id={comid}&start_date={start_date}'
        url = f'{url}&end_date={end_date}&return_format=csv'
    #
    elif data_type == "EnsembleForecast":
        url = f'https://geoglows.ecmwf.int/api/ForecastEnsembles'
        url = f'{url}/?reach_id={comid}&date={end_date}&return_format=csv'
        
    #
    else:
        er = "data_type should be: ForecastRecords or EnsembleForecast"
        raise(er)
    #
    # Variable to check the status of the request
    status = False
    #
    # Try to fetch the data until successful
    while not status:
        try:
            # Read data from the URL
            df = pd.read_csv(url, index_col=0)
            status = True
        except Exception as e:
            # Handle any exception and retry
            print("Error retrieving data:", e)
            print("Retrying to fetch data...", end="\n")
    #
    # Filter and correct the data
    df[df < 0] = 0
    df.index = pd.to_datetime(df.index)
    df.index = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    if data_type == "EnsembleForecast":
        df["datetime"] = df.index
        columnas_ordenadas = ["datetime"] + [f'ensemble_{i:02d}_m^3/s' for i in range(1, 53)]
        df = df.reindex(columns=columnas_ordenadas)
    return df


def join_ensemble_forecast(comids: list, date:dt.datetime) -> pd.DataFrame:
    """
    Joins ensemble forecasts from GEOGLOWS API, for multiple reachs in 
    an single DataFrame.

    Parameters:
        - comids (list): A list of reach ids for which ensemble forecasts 
          are requested.

    Returns:
        - pd.DataFrame: DataFrame containing joined ensemble forecasts.
    """
    # Initialize an empty list to store ensemble forecast for each COMID
    ensemble_forecast = []
    #
    # Iterate over each COMID in the provided list
    for comid in comids:
        # Fetch forecast records for the current COMID
        df = get_geoglows_data(comid=comid, date=date, data_type="EnsembleForecast")
        df = df.round(3)
        print(f"Downloaded ensemble forecast, comid: {comid}")
        #
        # Add comid to data
        df['comid'] = comid
        df['initialized'] = date
        df.columns = [col.replace('_m^3/s', '') for col in df.columns]
        #
        # Append the DataFrame with renamed column to the list
        ensemble_forecast.append(df)
    #
    # Concatenate all DataFrames in the list along the row axis to join them
    print("Donwloaded forecast records data.")
    return pd.concat(ensemble_forecast, ignore_index=True)



def join_forecast_records(comids: list, date:dt.datetime) -> pd.DataFrame:
    """
    Joins forecast records from GEOGLOWS API, for multiple reachs in 
    an single DataFrame.

    Parameters:
        - comids (list): A list of reach ids for which forecast records 
          are requested.

    Returns:
        - pd.DataFrame: DataFrame containing joined forecast records.
    """
    # Initialize an empty list to store forecast records for each COMID
    forecast_records = []
    #
    # Iterate over each COMID in the provided list
    for comid in comids:
        # Fetch forecast records for the current COMID
        df = get_geoglows_data(comid=comid, date=date, data_type="ForecastRecords")
        df = df.round(3)
        print(f"Downloaded forecast records, comid: {comid}")
        #
        # Rename the column containing streamflow data to the COMID
        df.rename(columns={'streamflow_m^3/s': comid}, inplace=True)
        #
        # Append the DataFrame with renamed column to the list
        forecast_records.append(df)
    #
    # Concatenate all DataFrames in the list along the columns axis to join them
    print("Donwloaded forecast records data.")
    return pd.concat(forecast_records, axis=1)


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

# Initialize the database
sql_file = f"{workdir}/taskfiles/geoglows_v01/init_db.sql"
init_db(DB_USER, DB_PASS, sql_file)

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

# Change to database directory
os.chdir("taskfiles/geoglows_v01/data")

# Partitions
partitions_data = {
    '1980-01-01': '1990-01-01',
    '1990-01-01': '2000-01-01',
    '2000-01-01': '2010-01-01',
    '2010-01-01': '2020-01-01',
    '2020-01-01': '2030-01-01'
}

# Insert tables
insert_simple_table(table="drainage_network", con=con)
insert_simple_table(table="streamflow_stations", con=con)
insert_data_table(table="streamflow_data", con=con, partitions=partitions_data, var='code')
insert_simple_table(table="waterlevel_stations", con=con)
insert_data_table(table="waterlevel_data", con=con, partitions=partitions_data, var='code')
insert_data_table(table="historical_simulation", con=con, partitions=partitions_data, var="comid")

# Query comids from drainage network
drainage = pd.read_sql("select comid from drainage_network;", con)

# Download ensemble forecast for lasted 40 days
today = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
start = today - dt.timedelta(days=40)
date_range = pd.date_range(start=start, end=today, freq="D")
for date in date_range:
    ensemble_forecast = join_ensemble_forecast(comids=drainage.comid[0:5], date=date)
    insert_ensemble_forecast(data=ensemble_forecast, con=con)

# Download forecast records
forecast_records = join_forecast_records(drainage.comid[0:5], date=today)
#insert_data_table_file("forecast_records", con=con, data=forecast_records)