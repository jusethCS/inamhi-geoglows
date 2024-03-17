import os
import sys
import pandas as pd
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def insert_into_db(table:str, con:sql.engine.base.Connection, 
                   unstack:bool = False, colname:str = None) -> None:

    """
    Insert data from a CSV file into a specified table in a sql database.

    Args:
        table (str): Table name in the database where the data will be inserted.
        con (sqlalchemy conection): Connection object to the database.
        unstack (bool): If True, unstack the DataFrame before insertion.
        colname (str): Name of the column to be created after unstacking.
    """
    # Define the chunk size for insertion
    chunk_size = 1000

    # Read data from CSV into a DataFrame
    data = pd.read_csv(f"{table}.csv", index_col=0)
    df = pd.DataFrame(data)

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

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Database directory
os.chdir("database/models")

# Establish connection
db = create_engine(token)
con = db.connect()

# Inserting data
insert_into_db(table='drainage_network', con=con)
insert_into_db(table='streamflow_stations', con=con)
insert_into_db(table='waterlevel_stations', con=con)
insert_into_db(table='streamflow_data', con=con, unstack=True, colname="code")
insert_into_db(table='waterlevel_data', con=con, unstack=True, colname="code")
insert_into_db(table='historical_simulation', con=con, unstack=True, colname="comid")
insert_into_db(table='forecast_records', con=con, unstack=True, colname="comid")
insert_into_db(table='ensemble_forecast', con=con)

# Close connection
con.close()
