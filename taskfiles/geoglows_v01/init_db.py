import os
import sys
import pandas as pd
import sqlalchemy as sql
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def init_db(pg_user:str, pg_pass:str, pg_db:str, pg_file:str) -> None:
    command = f"PGPASSWORD={pg_pass} psql -h localhost "
    command = f"-U {pg_user} -d {pg_db} -f {pg_file}"
    os.system(command)



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








# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

# Database directory
os.chdir("taskfiles/geoglows_v01/data")


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