# Import libraries and dependencies
import os
import math
import datetime
import warnings
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
warnings.filterwarnings('ignore')


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




###############################################################################################################
#                                    Function to retrieve data from GESS API                                  #
###############################################################################################################
def get_data(comid):
    url = 'https://geoglows.ecmwf.int/api/ForecastEnsembles/?reach_id={0}&return_format=csv'.format(comid)
    status = False
    while not status:
      try:
        outdf = pd.read_csv(url, index_col=0)
        if(outdf.shape[1]==52):
           status = True
        else:
           raise ValueError("Dataframe has not 52 emsembles.")
      except:
        print("Trying to retrieve data...")
    # Filter and correct data
    outdf[outdf < 0] = 0
    outdf.index = pd.to_datetime(outdf.index)
    return(outdf)


###############################################################################################################
#                                     Function to insert data to database                                     #
###############################################################################################################
def insert_data(db, comid):
    # Get historical data
    forecast = get_data(comid)
    # Establish connection
    conn = db.connect()
    # Insert to database
    table = f'ef_{comid}'
    try:
        forecast.to_sql(table, con=conn, if_exists='replace', index=True)
    except:
       print(f"Error to insert data in comid={comid}")
    # Close conection
    conn.close()   



###############################################################################################################
#                                 Function to get and format the data from DB                                 #
###############################################################################################################
def get_format_data(sql_statement, conn):
    # Retrieve data from database
    data =  pd.read_sql(sql_statement, conn)
    # Datetime column as dataframe index
    data.index = data.datetime
    data = data.drop(columns=['datetime'])
    # Format the index values
    data.index = pd.to_datetime(data.index)
    # Return result
    return(data)



###############################################################################################################
#                                   Getting return periods from data series                                   #
###############################################################################################################
def gumbel_1(std: float, xbar: float, rp: int) -> float:
  return -math.log(-math.log(1 - (1 / rp))) * std * .7797 + xbar - (.45 * std)

def get_return_periods(comid, data):
    # Stats
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    mean_value = np.mean(max_annual_flow.iloc[:,0].values)
    std_value = np.std(max_annual_flow.iloc[:,0].values)
    # Return periods
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []
    # Compute the corrected return periods
    for rp in return_periods:
      return_periods_values.append(gumbel_1(std_value, mean_value, rp))
    # Parse to list
    d = {'rivid': [comid], 
         'return_period_100': [return_periods_values[0]], 
         'return_period_50': [return_periods_values[1]], 
         'return_period_25': [return_periods_values[2]], 
         'return_period_10': [return_periods_values[3]], 
         'return_period_5': [return_periods_values[4]], 
         'return_period_2': [return_periods_values[5]]}
    # Parse to dataframe
    corrected_rperiods_df = pd.DataFrame(data=d)
    corrected_rperiods_df.set_index('rivid', inplace=True)
    return(corrected_rperiods_df)



###############################################################################################################
#                                         Getting ensemble statistic                                          #
###############################################################################################################
def ensemble_quantile(ensemble, quantile, label):
    df = ensemble.quantile(quantile, axis=1).to_frame()
    df.rename(columns = {quantile: label}, inplace = True)
    return(df)

def get_ensemble_stats(ensemble):
    high_res_df = ensemble['ensemble_52_m^3/s'].to_frame()
    ensemble.drop(columns=['ensemble_52_m^3/s'], inplace=True)
    ensemble.dropna(inplace= True)
    high_res_df.dropna(inplace= True)
    high_res_df.rename(columns = {'ensemble_52_m^3/s':'high_res_m^3/s'}, inplace = True)
    stats_df = pd.concat([
        ensemble_quantile(ensemble, 1.00, 'flow_max_m^3/s'),
        ensemble_quantile(ensemble, 0.75, 'flow_75%_m^3/s'),
        ensemble_quantile(ensemble, 0.50, 'flow_avg_m^3/s'),
        ensemble_quantile(ensemble, 0.25, 'flow_25%_m^3/s'),
        ensemble_quantile(ensemble, 0.00, 'flow_min_m^3/s'),
        high_res_df
    ], axis=1)
    return(stats_df)



###############################################################################################################
#                                    Warning if exceed x return period                                        #
###############################################################################################################
def is_warning(arr):
    cond = [i >= 40 for i in arr].count(True) > 0
    return(cond)

def get_excced_rp(stats: pd.DataFrame, ensem: pd.DataFrame, rperiods: pd.DataFrame):
    dates = stats.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]
    span = enddate - startdate
    uniqueday = [startdate + datetime.timedelta(days=i) for i in range(span.days + 2)]
    # get the return periods for the stream reach
    rp2 = rperiods['return_period_2'].values
    rp5 = rperiods['return_period_5'].values
    rp10 = rperiods['return_period_10'].values
    rp25 = rperiods['return_period_25'].values
    rp50 = rperiods['return_period_50'].values
    rp100 = rperiods['return_period_100'].values
    # fill the lists of things used as context in rendering the template
    days = []
    r2 = []
    r5 = []
    r10 = []
    r25 = []
    r50 = []
    r100 = []
    for i in range(len(uniqueday) - 1):  # (-1) omit the extra day used for reference only
        tmp = ensem.loc[uniqueday[i]:uniqueday[i + 1]]
        days.append(uniqueday[i].strftime('%b %d'))
        num2 = 0
        num5 = 0
        num10 = 0
        num25 = 0
        num50 = 0
        num100 = 0
        for column in tmp:
            column_max = tmp[column].to_numpy().max()
            if column_max > rp100:
                num100 += 1
            if column_max > rp50:
                num50 += 1
            if column_max > rp25:
                num25 += 1
            if column_max > rp10:
                num10 += 1
            if column_max > rp5:
                num5 += 1
            if column_max > rp2:
                num2 += 1
        r2.append(round(num2 * 100 / 52))
        r5.append(round(num5 * 100 / 52))
        r10.append(round(num10 * 100 / 52))
        r25.append(round(num25 * 100 / 52))
        r50.append(round(num50 * 100 / 52))
        r100.append(round(num100 * 100 / 52))
    alarm = "R0"
    if(is_warning(r2)):
        alarm = "R2"
    if(is_warning(r5)):
        alarm = "R5"
    if(is_warning(r10)):
        alarm = "R10"
    if(is_warning(r25)):
        alarm = "R25"
    if(is_warning(r50)):
        alarm = "R50"
    if(is_warning(r100)):
        alarm = "R100"
    return(alarm)







###############################################################################################################
#                                              Main routine                                                   #
###############################################################################################################

# Setting the connetion to db
db = create_engine(token)

# Establish connection
conn = db.connect()

# Getting stations
drainage = pd.read_sql("select * from drainage_network;", conn)

# Number of stations
n = len(drainage)

for i in range(n):
    # State variable
    comid = drainage.comid[i]
    # Progress
    prog = round(100 * i/n, 3)
    # Insert data to db
    try:
        insert_data(db, comid)
    except:
        insert_data(db, comid)
    # Query to database
    simulated_data = get_format_data(f"select * from hs_{comid};", conn)
    ensemble_forecast = get_format_data(f"select * from ef_{comid};", conn)
    # Return period
    return_periods = get_return_periods(comid, simulated_data)
    # Forecast stats
    ensemble_stats = get_ensemble_stats(ensemble_forecast)
    # Warning if excced a given return period in 40% of emsemble
    alld = get_excced_rp(ensemble_stats, ensemble_forecast, return_periods)
    drainage.loc[i, ['alert']] = alld
    # Print progress and alert
    print(f"Progress: {prog} %. Comid: {comid}. Alert: {alld}")
    

# Insert to database
drainage.to_sql('drainage_network', con=conn, if_exists='replace', index=False)

# Close connection
conn.close()
