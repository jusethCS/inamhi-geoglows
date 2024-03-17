import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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

# Database scripts directory
os.chdir("database/models")

# Establish connection
db = create_engine(token)
con = db.connect()



# Function to insert data
def insert_into_db(table, con, tible=False, var=None):
    # Define the chunk size
    chunk_size = 1000

    # Contruct the data
    data = pd.read_csv(f"{table}.csv", index_col=0)
    df = pd.DataFrame(data)
    if tible:
        df = df.stack().reset_index()
        df.columns = ['datetime', var, 'streamflow']

    # Drop table if exist
    con.execute(text(f"DROP TABLE IF EXISTS {table}"))

    # Insert data
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        chunk.to_sql(table, con=con, if_exists='append', index=False)
        con.commit()
        print(f"Insert row: {i} - {i+chunk_size}")
    print(f"Inserted {table} into database!")



# Inserting data
insert_into_db(table='drainage_network', con=con)
insert_into_db(table='streamflow_stations', con=con)
insert_into_db(table='waterlevel_stations', con=con)
insert_into_db(table='streamflow_data', con=con, tible=True, var="code")
insert_into_db(table='waterlevel_data', con=con, tible=True, var="code")
insert_into_db(table='historical_simulation', con=con, tible=True, var="comid")
insert_into_db(table='forecast_records', con=con, tible=True, var="comid")
insert_into_db(table='ensemble_forecast', con=con)

# Close connection
con.close()
