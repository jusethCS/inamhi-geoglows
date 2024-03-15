import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

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
DB_PORT = 5433

# Database scripts directory
os.chdir("database/models")

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
conn = db.connect()

# Read streamflow stations and insert to database
data = pd.read_excel('streamflow_stations.xlsx', index_col=0) 
df = pd.DataFrame(data)
df.to_sql('streamflow_station', con=conn, if_exists='replace', index=False)

# Read water level stations and insert to database
data = pd.read_excel('waterLevel_stations.xlsx', index_col=0) 
df = pd.DataFrame(data)
df.to_sql('waterlevel_station', con=conn, if_exists='replace', index=False)


# Close connection
conn.close()