import os
import pandas as pd
import sqlalchemy as sql
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine


###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def update_forecast_records(comid, con):
    # Construct the url data
    url = 'https://geoglows.ecmwf.int/api/ForecastRecords'
    url = f'{url}/?reach_id={comid}&start_date={start_date}'
    url = f'{url}&end_date={end_date}&return_format=csv'
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
            df["comid"] = comid
            df.rename(columns={"streamflow_m^3/s":"value"}, inplace=True)
            status = True
        except Exception as e:
                # Handle any exception and retry
                print("Error retrieving data:", e)
                print("Retrying to fetch data...", end="\n")
    #
    # Insert data for each comid
    for i in range(len(df.datetime)):
        temp_df = df.iloc[i].to_frame().T
        temp_df['comid'] = temp_df['comid'].astype(int)
        temp_df['value'] = temp_df['value'].astype(float)
        datetime = temp_df.datetime.iloc[0]
        query = f"select COUNT(*) as reg from forecast_records where comid={comid} and datetime='{datetime}'"
        cond =  pd.read_sql(query, con=con).reg.iloc[0] > 0
        if not cond:
            try:
                temp_df.to_sql('forecast_records', con=con, if_exists='append', index=False)
                con.commit()
                print(f"Inserted forecast record for comid: {comid}, date: {datetime}")
            except:
                print("Can not be inserted data!")


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

# Generate datetimes
end_date = dt.datetime.today()
start_date = end_date - dt.timedelta(days=10)
start_date = start_date.strftime('%Y%m%d')
end_date = end_date.strftime('%Y%m%d')

# Insert data per comid
for comid in comids:
     update_forecast_records(comid=comid, con=con)

# Close the connection
con.close()