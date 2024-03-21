import os
import pandas as pd
import datetime as dt
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
TODAY = dt.datetime.now().strftime('%Y-%m-%d')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)

# Establish connection
db = create_engine(token)
con = db.connect()

# Query comids from drainage network
drainage = pd.read_sql("select comid from drainage_network;", con)


comid = drainage.comid[0]

def get_data(sql, con, dropcols=None):
    data =  pd.read_sql(sql, con)
    data.index = pd.to_datetime(data.datetime)
    data = data.drop(columns=['datetime'])
    if dropcols is not None:
        data = data.drop(columns=dropcols)
    return(data)


