import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

###############################################################################
#                             AUXILIAR FUNCTIONS                              #
###############################################################################

# Function to retrieve data from GESS API
def get_data(comid):
    url = 'https://geoglows.ecmwf.int/api/HistoricSimulation/'
    url = f'{url}?reach_id={comid}&return_format=csv'
    status = False
    while not status:
      try:
        outdf = pd.read_csv(url, index_col=0) 
        if(outdf.shape[0]>0):
           status = True
        else:
           raise ValueError("Dataframe has not data.")
      except:
        print("Trying to retrieve data...")
    # Filter and correct data
    outdf[outdf < 0] = 0
    outdf.index = pd.to_datetime(outdf.index)
    print("Returning data...")
    return(outdf)


# Function to insert data to database
def insert_data(db, comid):
    # Get historical data
    historical = get_data(comid)
    # Establish connection
    conn = db.connect()
    # Define the table and delete if exist
    table = f'hs_{comid}'
    # Insert to database
    try:
        historical.to_sql(table, con=conn, if_exists='replace', index=True)
        print("Successfully inserted data...")
    except:
       print(f"Error to insert data in comid={comid}")
    # Close conection
    conn.close()



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
DB_PORT = 5433

# Database scripts directory
os.chdir("database/models")

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)
  
# Establish connection
db = create_engine(token)

# Retrieve comids
conn = db.connect()
data = pd.read_sql("select comid from drainage_network", conn);
conn.close()    

# Insert data into DB
n = len(data.comid)
for i in range(n):
    # State variable
    comid = data.comid[i]
    # Progress
    prog = round(100 * (i)/n, 3)
    print("Progress: {0} %. Comid: {1}".format(prog, comid))
    try:
        insert_data(db, comid)
    except:
        insert_data(db, comid)
