import os
import sys
import pandas as pd
import datetime as dt
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def get_geoglows_data(comid: int, data_type: str) -> pd.DataFrame:
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
    current_date = dt.datetime.now()

    # Determine the start and end date to request
    start_date = current_date - dt.timedelta(days=80)
    start_date = start_date.strftime('%Y%m%d')
    end_date = current_date.strftime('%Y%m%d')

    # Construct the URL for data request
    if data_type == "ForecastRecords":
        url = 'https://geoglows.ecmwf.int/api/ForecastRecords'
        url = f'{url}/?reach_id={comid}&start_date={start_date}'
        url = f'{url}&end_date={end_date}&return_format=csv'

    elif data_type == "EnsembleForecast":
        url = f'https://geoglows.ecmwf.int/api/ForecastEnsembles'
        url = f'{url}/?reach_id={comid}&return_format=csv'

    else:
        er = "data_type should be: ForecastRecords or EnsembleForecast"
        raise(er)

    # Variable to check the status of the request
    status = False

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

    # Filter and correct the data
    df[df < 0] = 0
    df.index = pd.to_datetime(df.index)
    df.index = df.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    if data_type == "EnsembleForecast":
        df["datetime"] = df.index
        columnas_ordenadas = ["datetime"] + [f'ensemble_{i:02d}_m^3/s' for i in range(1, 53)]
        df = df.reindex(columns=columnas_ordenadas)
    return df


def join_ensemble_forecast(comids: list) -> pd.DataFrame:
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

    # Iterate over each COMID in the provided list
    for comid in comids:
        # Fetch forecast records for the current COMID
        df = get_geoglows_data(comid=comid, data_type="EnsembleForecast")
        df = df.round(3)
        print(f"Downloaded ensemble forecast, comid: {comid}")
        #sys.stdout.flush()

        # Add comid to data
        df['comid'] = comid

        # Append the DataFrame with renamed column to the list
        ensemble_forecast.append(df)

    # Concatenate all DataFrames in the list along the row axis to join them
    print("Donwloaded forecast records data.  ")
    return pd.concat(ensemble_forecast, ignore_index=True)


def insert_into_db(df: pd.DataFrame, table: str, con: sql.engine.base.Connection,
                   unstack: bool = False, colname: str = None) -> None:
    """
    Insert data from a CSV file into a specified table in a sql database.

    Args:
        df (pd.Dataframe): Data for the table that will be inserted
        table (str): Table name in the database where the data will be inserted.
        con (sqlalchemy conection): Connection object to the database.
        unstack (bool): If True, unstack the DataFrame before insertion.
        colname (str): Name of the column to be created after unstacking.
    """
    # Define the chunk size for insertion
    chunk_size = 1000

    # Optionally unstack the DataFrame
    if unstack:
        df = df.stack().reset_index()
        df.columns = ['datetime', colname, 'value']

    # Drop the table if it exists
    con.execute(text(f"DROP TABLE IF EXISTS {table}"))

    # Insert data into the database in chunks
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk.to_sql(table, con=con, if_exists='append', index=False)
        con.commit()
        print(f"Inserted rows: {i} - {i+chunk_size}", end='\r')
        sys.stdout.flush()

    print(f"Inserted {table} into database!")


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
TODAY = dt.datetime.now().strftime('%Y-%m-%d')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Database directory
os.chdir("database/archive")

# Establish connection
db = create_engine(token)
con = db.connect()

# Query comids from drainage network
drainge = pd.read_sql("select comid from drainage_network;", con)

# Download ensemble forecast
ensemble_forecast = join_ensemble_forecast(drainge.comid)
ensemble_forecast.to_csv(f"ensemble_forecast/{TODAY}.csv", index=False)
insert_into_db(ensemble_forecast, table='ensemble_forecast', con=con)

# Close connection
con.close()
