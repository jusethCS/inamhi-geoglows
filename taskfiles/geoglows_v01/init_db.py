import os
import sys
import pandas as pd
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def init_db(pg_user:str, pg_pass:str, pg_file:str) -> None:
    command = f"PGPASSWORD={pg_pass} psql -U {pg_user} -h localhost -f {pg_file}"
    os.system(command)

def insert_simple_table(table:str, con:sql.engine.base.Connection) -> None:
    data = pd.read_csv(f"{table}.csv", sep=";")
    data.to_sql(table, con=con, if_exists='append', index=False)
    con.commit()

def insert_data_table(table:str, con:sql.engine.base.Connection, partitions:dict) -> None:
    data = pd.read_csv(f"{table}.csv", sep=";")
    data['datetime'] = pd.to_datetime(data['datetime'])
    data_long = data.melt(id_vars=['datetime'], var_name='code', value_name='value').dropna(subset=['value'])
    for start_date, end_date in partitions.items():
        mask = (data_long['datetime'] >= start_date) & (data_long['datetime'] < end_date)
        df_partition = data_long.loc[mask]
        partition_table_name = f'{table}_{start_date[:4]}_{end_date[:4]}'
        chunk_size = 1000
        for i in range(0, len(df_partition), chunk_size):
            chunk = df_partition.iloc[i:i+chunk_size]
            chunk.to_sql(partition_table_name, con=con, if_exists='append', index=False)
        print(f"Inserted from {start_date} to {end_date} into database!")


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
    '2010-01-01': '2020-01-01'
}

# Insert tables
insert_simple_table(table="drainage_network", con=con)
insert_simple_table(table="streamflow_stations", con=con)
insert_data_table(table="streamflow_data", con=con, partitions=partitions_data)

















# Insert drainage network table
data = pd.read_csv("drainage_network.csv", sep=";")
data.to_sql("drainage_network", con=con, if_exists='append', index=False)
con.commit()

# Insert streamflow station table
data = pd.read_csv("streamflow_stations.csv", sep=";")
data.to_sql("streamflow_station", con=con, if_exists='append', index=False)
con.commit()

# Insert streamflow data table
data = pd.read_csv("streamflow_data.csv", sep=";")
data['datetime'] = pd.to_datetime(data['datetime'])
data_long = data.melt(id_vars=['datetime'], var_name='code', value_name='value').dropna(subset=['value'])



for start_date, end_date in partitions.items():
    mask = (data_long['datetime'] >= start_date) & (data_long['datetime'] < end_date)
    df_partition = data_long.loc[mask]
    partition_table_name = f'streamflow_data_{start_date[:4]}_{end_date[:4]}'
    chunk_size = 1000
    for i in range(0, len(df_partition), chunk_size):
        chunk = df_partition.iloc[i:i+chunk_size]
        chunk.to_sql(partition_table_name, con=con, if_exists='append', index=False)
    print(f"Inserted from {start_date} to {end_date} into database!")


con.close()

















def insert_table(table:str, con:sql.engine.base.Connection) -> None:
    """
    Insert data from a CSV file into a specified table in a sql database.

    Args:
        table (str): Table name in the database where the data will be inserted.
        con (sqlalchemy conection): Connection object to the database.
    """
    # Define the chunk size for insertion
    chunk_size = 1000
    #
    # Read data from CSV into a DataFrame
    data = pd.read_csv(f"{table}.csv", sep=";")
    df = pd.DataFrame(data)
    df.columns = df.columns.str.lower()
    #
    # Drop the table if it exists
    con.execute(text(f"DROP TABLE IF EXISTS {table}"))
    #
    # Insert data into the database in chunks
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk.to_sql(table, con=con, if_exists='append', index=False)
        con.commit()
        print(f"Inserted rows: {i} - {i+chunk_size}", end='\r')
        sys.stdout.flush()
    print(f"Inserted {table} into database!")


def insert_historical(con:sql.engine.base.Connection):
    """
    Insert historical simulation data from a CSV file into a sql database.

    Args:
        con (sqlalchemy conection): Connection object to the database.
    """
    # Read data from CSV into a DataFrame
    data = pd.read_csv("historical_simulation.csv", sep=";")
    df = pd.DataFrame(data)
    #
    comids = df.columns.difference(["datetime"])
    for comid in comids[0:5]:
        table = f"hs_{comid}"
        con.execute(text(f"DROP TABLE IF EXISTS {table}"))
        table_data = df[["datetime", comid]]
        table_data.columns = ["datetime", "streamflow"]
        table_data.to_sql(table, con=con, if_exists='append', index=False)
        con.commit()
        print(f"Inserted historical simulation for comid: {comid}")
        sys.stdout.flush()
    print("Inserted historical simulation into database!")











# Inserting data
insert_table(table='drainage_network', con=con)
insert_table(table='streamflow_stations', con=con)
insert_table(table='waterlevel_stations', con=con)
insert_table(table='streamflow_data', con=con)
insert_table(table='waterlevel_data', con=con)

insert_historical(con=con)

#insert_table(table='historical_simulation', con=con, unstack=True, colname="comid")
#insert_into_db(table='forecast_records', con=con, unstack=True, colname="comid")
#insert_into_db(table='ensemble_forecast', con=con)

# Close connection
con.close()