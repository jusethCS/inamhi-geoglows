###############################################################################
#                            LIBRARIES AND MODULES                            #
###############################################################################
# File system and environment management
import os
from dotenv import load_dotenv

# Date and time handling
import datetime as dt

# Mathematical and statistical operations
import math
import numpy as np
import scipy
import scipy.stats
import hydrostats as hs
import hydrostats.data as hd

# Data manipulation
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Databases and ORM
import sqlalchemy as sql
from sqlalchemy import create_engine

# Visualization
import plotly.io as pio
import plotly.graph_objects as go

# Web services and responses in Django
import jinja2
from django.http import JsonResponse, HttpResponse

# Custom
from .utils import correct_historical, correct_forecast



###############################################################################
#                 ENVIROMENTAL VARIABLES AND CONNECTION TOKEN                 #
###############################################################################
# Import enviromental variables
load_dotenv("/home/ubuntu/inamhi-geoglows/.env")
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)




###############################################################################
#                        MODULES AND CUSTOM FUNCTIONS                         #
###############################################################################
def get_format_data(sql_statement, conn):
    """
    Retrieve and format data from a database.

    This function executes an SQL query to retrieve data from a database,
    sets the 'datetime' column as the index of the DataFrame, formats the index
    to a specified datetime string format, and returns the formatted DataFrame.

    Parameters:
    sql_statement (str): SQL query to execute.
    conn (sqlalchemy.engine.base.Connection): Database connection object.

    Returns:
    pd.DataFrame: Formatted DataFrame with 'datetime' as the index.
    """
    # Retrieve data from the database using the SQL query
    data = pd.read_sql(sql_statement, conn)
    
    # Set the 'datetime' column as the DataFrame index
    data.index = pd.to_datetime(data['datetime'])
    
    # Drop the 'datetime' column as it is now the index
    data = data.drop(columns=['datetime'])
    
    # Format the index values to the desired datetime string format
    data.index = pd.to_datetime(data.index)
    data.index = data.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    data.index = pd.to_datetime(data.index)
    return(data)


def get_bias_corrected_data(sim, obs):
    """
    Apply bias correction to simulated historical streamflow data based on 
    observed data.

    This function uses the GEOGloWS library to perform bias correction on 
    historical simulated data (`sim`) by adjusting it according to observed 
    data (`obs`). The function removes any NaN values from both datasets 
    before applying the correction.

    Parameters:
    -----------
    - sim : pandas.DataFrame or pandas.Series
        The simulated historical data that will undergo bias correction. This 
        dataset should have a datetime index and corresponding streamflow values.
    
    - obs : pandas.DataFrame or pandas.Series
        The observed historical data used for bias correction. This dataset must
        match the time period and format of the simulated data.

    Returns:
    --------
    - pandas.DataFrame or pandas.Series
        The bias-corrected simulated data, with the datetime index formatted
        as "%Y-%m-%d %H:%M:%S" and converted back to a pandas `DatetimeIndex`.
    """
    outdf = correct_historical(sim.dropna(), obs.dropna())
    outdf.index = pd.to_datetime(outdf.index)
    outdf.index = outdf.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    outdf.index = pd.to_datetime(outdf.index)
    return outdf


def get_corrected_forecast(simulated_df, ensemble_df, observed_df):
    """
    Correct the forecasted ensembles based on the simulated and observed 
    historical data.

    This function calculates correction factors for forecasted ensembles 
    based on simulated and observed data. It adjusts the forecast values 
    to lie within the range defined by the minimum and maximum of the 
    historical simulated data for the corresponding month.

    Parameters:
    -----------
    simulated_df : pandas.DataFrame
        A DataFrame containing simulated historical data with a datetime index.
    
    ensemble_df : pandas.DataFrame
        A DataFrame containing forecasted ensemble data with a datetime index.
    
    observed_df : pandas.DataFrame
        A DataFrame containing observed historical data with a datetime index.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the bias-corrected ensemble forecasts.

    """
    # Extract the month from the first entry in the ensemble DataFrame
    forecast_month = ensemble_df.index[0].month
    
    # Filter simulated and observed data for the corresponding month and drop NaNs
    monthly_simulated = simulated_df[simulated_df.index.month == forecast_month].dropna()
    monthly_observed = observed_df[observed_df.index.month == forecast_month].dropna()
    
    # Calculate the minimum and maximum of the simulated data for that month
    min_simulated = monthly_simulated.iloc[:, 0].min()
    max_simulated = monthly_simulated.iloc[:, 0].max()
    
    # Create copies of the ensemble DataFrame for correction factors
    min_factor_df = ensemble_df.copy()
    max_factor_df = ensemble_df.copy()
    forecast_ens_df = ensemble_df.copy()

    # Iterate through each column in the ensemble DataFrame
    for column in ensemble_df.columns:
        # Create a temporary DataFrame to avoid modifying the original ensemble
        tmp = ensemble_df[column].dropna().to_frame()

        # Calculate the minimum correction factor
        min_factor = (tmp[column] >= min_simulated).astype(float)
        min_factor[tmp[column] < min_simulated] = tmp[column][tmp[column] < min_simulated] / min_simulated
        
        # Calculate the maximum correction factor
        max_factor = (tmp[column] <= max_simulated).astype(float)
        max_factor[tmp[column] > max_simulated] = tmp[column][tmp[column] > max_simulated] / max_simulated

        # Update the temporary DataFrame to enforce limits
        tmp[column] = np.clip(tmp[column], min_simulated, max_simulated)

        # Update the forecast and correction factor DataFrames
        forecast_ens_df[column] = tmp[column]
        min_factor_df[column] = min_factor
        max_factor_df[column] = max_factor

    # Apply bias correction using the GEOGloWS library
    corrected_ensembles = correct_forecast(forecast_ens_df, simulated_df, observed_df)
    
    # Apply the minimum and maximum correction factors
    corrected_ensembles *= min_factor_df
    corrected_ensembles *= max_factor_df
    return corrected_ensembles


def gumbel_1(sd: float, mean: float, rp: float) -> float:
    """
    Calculate the Gumbel Type I distribution value for a given return period.

    This function calculates the Gumbel Type I distribution value based on the
    provided standard deviation, mean, and return period.

    Parameters:
    -----------
    - sd: float 
        The standard deviation of the dataset.
    - mean: float
        The mean of the dataset.
    - return_period: float
        The return period for which the value is calculated.

    Returns:
    --------
     - float: 
        The calculated Gumbel Type I distribution value.
    """
    try:
        # Validate input parameters
        if sd <= 0:
            raise ValueError("Standard deviation must be positive.")
        if rp <= 1:
            raise ValueError("Return period must be greater than 1.")
        
        # Calculate the Gumbel reduced variate
        y = -math.log(-math.log(1 - (1 / rp)))
        
        # Calculate the Gumbel Type I distribution value
        gumbel_value = y * sd * 0.7797 + mean - (0.45 * sd)
        return gumbel_value
    except Exception as e:
        print(e)
        return 0



def get_return_periods(comid: int, data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate return period values for a given COMID based on annual maximum 
    flow data.

    This function calculates the annual maximum flow statistics (mean and 
    standard deviation), computes the corrected return period values using the 
    Gumbel Type I distribution, and returns these values in a DataFrame.

    Parameters:
    -----------
    - comid: int
        The COMID (unique identifier for a river segment).
    - data: pd.DataFrame
        DataFrame containing flow data with a datetime index.

    Returns:
    --------
    - pd.DataFrame
        DataFrame containing the corrected return period values for the 
        specified COMID.

    """
    if data.empty:
        raise ValueError("The input data is empty.")
    
    # Calculate the maximum annual flow
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    if max_annual_flow.empty:
        raise ValueError("No annual maximum flow data available.")
    
    # Calculate the mean and standard deviation of the maximum annual flow
    mean_value = np.mean(max_annual_flow.iloc[:, 0].values)
    std_value = np.std(max_annual_flow.iloc[:, 0].values)
    
    # Define the return periods to calculate
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []
    
    # Compute the corrected return period values using the Gumbel Type I distribution
    for rp in return_periods:
        return_periods_values.append(gumbel_1(std_value, mean_value, rp))
    
    # Create a dictionary to store the return period values
    data_dict = {
        'rivid': [comid],
        'return_period_100': [return_periods_values[0]],
        'return_period_50': [return_periods_values[1]],
        'return_period_25': [return_periods_values[2]],
        'return_period_10': [return_periods_values[3]],
        'return_period_5': [return_periods_values[4]],
        'return_period_2': [return_periods_values[5]]
    }
    
    # Convert the dictionary to a DataFrame and set 'rivid' as the index
    rperiods_df = pd.DataFrame(data=data_dict)
    rperiods_df.set_index('rivid', inplace=True)
    return rperiods_df



def ensemble_quantile(ensemble: pd.DataFrame, quantile: float, 
                      label: str) -> pd.DataFrame:
    """
    Calculate the specified quantile for an ensemble and return it as a 
    DataFrame.

    This function computes the specified quantile for each row in the ensemble
    DataFrame and returns the results in a new DataFrame with the specified 
    label as the column name.

    Parameters:
    -----------
    - ensemble: pd.DataFrame
        DataFrame containing the ensemble data.
    - quantile: float
        The quantile to compute (between 0 and 1).
    - label:str 
        The label for the resulting quantile column.

    Returns:
    --------
    - pd.DataFrame
        DataFrame containing the computed quantile with the specified label.
    """
    # Calculate the quantile along the columns (axis=1) and convert to a DataFrame
    quantile_df = ensemble.quantile(quantile, axis=1).to_frame()
    
    # Rename the column to the specified label
    quantile_df.rename(columns={quantile: label}, inplace=True)
    return quantile_df



def get_ensemble_stats(ensemble: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various statistical measures for an ensemble and return them in a 
    DataFrame.

    This function calculates the maximum, 75th percentile, median, 25th percentile,
    and minimum flows for the ensemble. It also includes the high-resolution flow 
    data (ensemble_52).

    Parameters:
    -----------
    - ensemble: pd.DataFrame
        DataFrame containing the ensemble data.

    Returns:
    --------
    - pd.DataFrame
        DataFrame containing the statistical measures and high-resolution flow data.
    """
    # Extract the high-resolution data and remove it from the ensemble
    high_res_df = ensemble['ensemble_52'].to_frame()
    ensemble.drop(columns=['ensemble_52'], inplace=True)
    
    # Remove rows with NaN values in both the ensemble and high-resolution data
    ensemble.dropna(inplace=True)
    high_res_df.dropna(inplace=True)
    
    # Rename the column for high-resolution data
    high_res_df.rename(columns={'ensemble_52': 'high_res'}, inplace=True)
    
    # Calculate various quantiles and concatenate them into a single DataFrame
    stats_df = pd.concat([
        ensemble_quantile(ensemble, 1.00, 'flow_max'),
        ensemble_quantile(ensemble, 0.75, 'flow_75%'),
        ensemble_quantile(ensemble, 0.50, 'flow_avg'),
        ensemble_quantile(ensemble, 0.25, 'flow_25%'),
        ensemble_quantile(ensemble, 0.00, 'flow_min'),
        high_res_df
    ], axis=1)
    return stats_df



def get_corrected_forecast_records(records_df, simulated_df, observed_df):
    """
    Correct the forecasted records based on simulated and observed data.

    This function iterates through the months present in the input records 
    DataFrame, applies bias correction using the simulated and observed data, 
    and ensures that the corrected values fall within the range defined by 
    the historical simulated data.

    Parameters:
    -----------
    records_df : pandas.DataFrame
        A DataFrame containing forecasted records with a datetime index.
    
    simulated_df : pandas.DataFrame
        A DataFrame containing simulated historical data with a datetime index.
    
    observed_df : pandas.DataFrame
        A DataFrame containing observed historical data with a datetime index.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the bias-corrected forecast records.
    """    
    # Extract the starting and ending dates from the records DataFrame
    date_ini = records_df.index[0]
    date_end = records_df.index[-1]
    
    # Create a range of months from the initial month to the final month
    meses = np.arange(date_ini.month, date_end.month + 1, 1)
    fixed_records = pd.DataFrame()
    
    # Iterate through each month in the specified range
    for mes in meses:
        # Filter records, simulated, and observed data for the current month
        values = records_df.loc[records_df.index.month == mes]
        monthly_simulated = simulated_df[simulated_df.index.month == mes].dropna()
        monthly_observed = observed_df[observed_df.index.month == mes].dropna()
        
        # Calculate min and max of the simulated data for the current month
        min_simulated = monthly_simulated.iloc[:, 0].min()
        max_simulated = monthly_simulated.iloc[:, 0].max()

        # Create temporary DataFrame for the current month's values
        column_records = values.columns[0]
        tmp = values[column_records].dropna().to_frame()

        # Create min and max correction factors
        min_factor = np.where(tmp[column_records] >= min_simulated, 1,
                              tmp[column_records] / min_simulated)
        max_factor = np.where(tmp[column_records] <= max_simulated, 1,
                              tmp[column_records] / max_simulated)

        # Clip the values to ensure they are within the simulated range
        tmp[column_records] = tmp[column_records].clip(lower=min_simulated, upper=max_simulated)
        
        # Create a DataFrame to hold corrected values
        fixed_records_df = values.copy()
        fixed_records_df[column_records] = tmp[column_records]
        
        # Create DataFrames for correction factors
        min_factor_records_df = values.copy()
        max_factor_records_df = values.copy()
        min_factor_records_df[column_records] = min_factor
        max_factor_records_df[column_records] = max_factor
        
        # Apply bias correction using the GEOGloWS library
        corrected_values = correct_forecast(fixed_records_df, simulated_df, observed_df)
        
        # Multiply the corrected values by the min and max correction factors
        corrected_values *= min_factor_records_df
        corrected_values *= max_factor_records_df
        
        # Append the corrected values to the final DataFrame
        fixed_records = pd.concat([fixed_records, corrected_values])

    # Sort the index of the final DataFrame
    fixed_records.sort_index(inplace=True)
    return fixed_records


###############################################################################
#                             PLOTS AND TABLES                                #
###############################################################################
def _plot_colors():
    return {
        '2 Year': 'rgba(254, 240, 1, .4)',
        '5 Year': 'rgba(253, 154, 1, .4)',
        '10 Year': 'rgba(255, 56, 5, .4)',
        '20 Year': 'rgba(128, 0, 246, .4)',
        '25 Year': 'rgba(255, 0, 0, .4)',
        '50 Year': 'rgba(128, 0, 106, .4)',
        '100 Year': 'rgba(128, 0, 246, .4)',
    }


def _rperiod_scatters(startdate: str, enddate: str, rperiods: pd.DataFrame, 
                      y_max: float, max_visible: float = 0):
    colors = _plot_colors()
    x_vals = (startdate, enddate, enddate, startdate)
    r2 = round(rperiods['return_period_2'].values[0], 1)
    if max_visible > r2:
        visible = True
    else:
        visible = 'legendonly'
    #
    def template(name, y, color, fill='toself'):
        return go.Scatter(
            name=name,
            x=x_vals,
            y=y,
            legendgroup='returnperiods',
            fill=fill,
            visible=visible,
            mode="lines",
            line=dict(color=color, width=0))
    #
    r5 = round(rperiods['return_period_5'].values[0], 1)
    r10 = round(rperiods['return_period_10'].values[0], 1)
    r25 = round(rperiods['return_period_25'].values[0], 1)
    r50 = round(rperiods['return_period_50'].values[0], 1)
    r100 = round(rperiods['return_period_100'].values[0], 1)
    rmax = int(max(2 * r100 - r25, y_max))
    #
    return [
        template('Periodos de retorno', (rmax, rmax, rmax, rmax), 'rgba(0,0,0,0)', fill='none'),
        template(f'2 años: {r2}', (r2, r2, r5, r5), colors['2 Year']),
        template(f'5 años: {r5}', (r5, r5, r10, r10), colors['5 Year']),
        template(f'10 años: {r10}', (r10, r10, r25, r25), colors['10 Year']),
        template(f'25 años: {r25}', (r25, r25, r50, r50), colors['25 Year']),
        template(f'50 años: {r50}', (r50, r50, r100, r100), colors['50 Year']),
        template(f'100 años: {r100}', (r100, r100, rmax, rmax), colors['100 Year']),
    ]


def historical_plot(sim, cor, obs, code, name, width):
    dates = cor.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]
    full_date_range = pd.date_range(start=obs.index.min(), end=obs.index.max(), freq='D')
    obs = obs.reindex(full_date_range)
    obs = obs.where(pd.notnull(obs), "")

    simulated_data = {
        'x_datetime': sim.index.tolist(),
        'y_flow': sim.values.flatten().tolist(),  # Convert to list
    }
    corrected_data = {
        'x_datetime': cor.index.tolist(),
        'y_flow': cor.values.flatten().tolist(),  # Convert to list
    }
    observed_data = {
        'x_datetime': obs.index.tolist(),
        'y_flow': obs.values.flatten().tolist(),
    }
    
    scatter_plots = [
        go.Scatter(
            name='Simulación histórica', 
            x=simulated_data['x_datetime'], 
            y=simulated_data['y_flow']),
        go.Scatter(
            name='Simulación corregida', 
            x=corrected_data['x_datetime'], 
            y=corrected_data['y_flow']),
        go.Scatter(
            name='Datos observados', 
            x=observed_data['x_datetime'], 
            y=observed_data['y_flow'],
            connectgaps=False)
    ]
    
    layout = go.Layout(
        title=f"Simulación histórica <br>{str(code).upper()} - {name}",
        yaxis={
            'title': 'Caudal (m<sup>3</sup>/s)', 
            'range': [0, 'auto']},
        xaxis={
            'title': 'Fecha (UTC +0:00)', 
            'range': [startdate, enddate], 
            'hoverformat': '%b %d %Y', 
            'tickformat': '%Y'},
    )
    
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white', width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)    
    figure_dict = figure.to_dict()
    return figure_dict


def daily_average_plot(obs, sim, cor, code, name, width):
    daily_avg_obs = hd.daily_average(obs)
    daily_avg_sim = hd.daily_average(sim)
    daily_avg_cor = hd.daily_average(cor)

    daily_avg_obs_Q = go.Scatter(
        x=daily_avg_obs.index.tolist(),  # Convert index to list
        y=daily_avg_obs.iloc[:, 0].values.flatten().tolist(),  # Convert values to list
        name='Observado'
    )
    daily_avg_sim_Q = go.Scatter(
        x=daily_avg_sim.index.tolist(),  # Convert index to list
        y=daily_avg_sim.iloc[:, 0].values.flatten().tolist(),  # Convert values to list
        name='Simulado'
    )
    daily_avg_cor_Q = go.Scatter(
        x=daily_avg_cor.index.tolist(),  # Convert index to list
        y=daily_avg_cor.iloc[:, 0].values.flatten().tolist(),  # Convert values to list
        name='Corregido'
    )

    layout = go.Layout(
        title='Caudal medio multi-diario<br>{0} - {1}'.format(str(code).upper(), name),
        xaxis=dict(title='Día del año'), 
        yaxis=dict(title='Caudal (m<sup>3</sup>/s)', autorange=True),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='simple_white',
        showlegend=True
    )

    figure = go.Figure(data=[daily_avg_sim_Q, daily_avg_cor_Q, daily_avg_obs_Q], layout=layout)
    figure.update_layout(template='simple_white', width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True) 
    return figure.to_dict()



def monthly_average_plot(obs, sim, cor, code, name, width):
    daily_avg_obs = hd.monthly_average(obs)
    daily_avg_sim = hd.monthly_average(sim)
    daily_avg_cor = hd.monthly_average(cor)

    daily_avg_obs_Q = go.Scatter(
        x=daily_avg_obs.index.tolist(),  # Convert index to list
        y=daily_avg_obs.iloc[:, 0].values.flatten().tolist(),  # Convert values to list
        name='Observado'
    )
    daily_avg_sim_Q = go.Scatter(
        x=daily_avg_sim.index.tolist(),  # Convert index to list
        y=daily_avg_sim.iloc[:, 0].values.flatten().tolist(),  # Convert values to list
        name='Simulado'
    )
    daily_avg_cor_Q = go.Scatter(
        x=daily_avg_cor.index.tolist(),  # Convert index to list
        y=daily_avg_cor.iloc[:, 0].values.flatten().tolist(),  # Convert values to list
        name='Corregido'
    )

    layout = go.Layout(
        title='Caudal medio multi-mensual<br>{0} - {1}'.format(str(code).upper(), name),
        xaxis=dict(title='Mes'), 
        yaxis=dict(title='Caudal (m<sup>3</sup>/s)', autorange=True),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='simple_white',
        showlegend=True
    )

    figure = go.Figure(data=[daily_avg_sim_Q, daily_avg_cor_Q, daily_avg_obs_Q], layout=layout)
    figure.update_layout(template='simple_white', width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True) 
    return figure.to_dict()



def scatter_plot(sim, cor, obs, code, name, log, width):
    x_values = cor.iloc[:, 0].values.flatten().tolist()  # Convert to list
    y_values = obs.iloc[:, 0].values.flatten().tolist()  # Convert to list
    z_values = sim.iloc[:, 0].values.flatten().tolist()  # Convert to list

    scatter_data = go.Scatter(
        x=z_values,
        y=y_values,
        mode='markers',
        name='Simulado',
        marker=dict(color='#ef553b')
    )
    scatter_data2 = go.Scatter(
        x=x_values,
        y=y_values,
        mode='markers',
        name='Corregido',
        marker=dict(color='#00cc96')
    )
    
    min_value = min(min(y_values), min(x_values), min(z_values))
    max_value = max(max(y_values), max(x_values), max(z_values))
    
    line_45 = go.Scatter(
        x=[min_value, max_value],  # Use list for x-axis
        y=[min_value, max_value],  # Use list for y-axis
        mode='lines',
        name='Linea 1:1',
        line=dict(color='black')
    )
    
    if log:
        layout = go.Layout(
            title="Gráfica de dispersión (escala logarítmica) <br>{0} - {1}".format(code.upper(), name),
            xaxis=dict(title='Caudal simulado (m<sup>3</sup>/s)', type='log'),
            yaxis=dict(title='Caudal observado (m<sup>3</sup>/s)', type='log', autorange=True),
            showlegend=True,
            template='simple_white'
        )
    else:
        layout = go.Layout(
            title="Gráfica de dispersión <br>{0} - {1}".format(code.upper(), name),
            xaxis=dict(title='Caudal simulado (m<sup>3</sup>/s)'),
            yaxis=dict(title='Caudal observado (m<sup>3</sup>/s)', autorange=True),
            showlegend=True,
            template='simple_white'
        )
    
    # Plotting data
    figure = go.Figure(data=[scatter_data, scatter_data2, line_45], layout=layout)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True)
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    figure.update_layout(template='simple_white', width=width)
    return figure.to_dict()  # Ensure the result is JSON serializable



def get_date_values(startdate, enddate, df):
    date_range = pd.date_range(start=startdate, end=enddate)
    month_day = date_range.strftime("%m-%d")
    pddf = pd.DataFrame(index=month_day)
    pddf.index.name = "datetime"
    combined_df = pd.merge(pddf, df, how='left', left_index=True, right_index=True)
    combined_df.index = pd.to_datetime(date_range)
    return combined_df


def forecast_plot(stats, rperiods, comid, records, obs, width):
    # Define los registros
    records = records.loc[records.index >= pd.to_datetime(stats.index[0] - dt.timedelta(days=8))]
    records = records.loc[records.index <= pd.to_datetime(stats.index[0])]
    #
    # Comienza el procesamiento de los inputs
    dates_forecast = stats.index.tolist()
    dates_records = records.index.tolist()
    try:
        startdate = dates_records[0]
    except IndexError:
        startdate = dates_forecast[0]
    enddate = dates_forecast[-1]
    #
    # Genera los valores promedio
    daily = obs.groupby(obs.index.strftime("%m-%d"))
    daymin_df = get_date_values(startdate, enddate, daily.min())
    daymax_df = get_date_values(startdate, enddate, daily.max()) 
    #
    plot_data = {
        'x_stats': stats['flow_avg'].dropna(axis=0).index.tolist(),
        'x_hires': stats['high_res'].dropna(axis=0).index.tolist(),
        'y_max': max(stats['flow_max']),
        'flow_max': stats['flow_max'].dropna(axis=0).tolist(),
        'flow_75%': stats['flow_75%'].dropna(axis=0).tolist(),
        'flow_avg': stats['flow_avg'].dropna(axis=0).tolist(),
        'flow_25%': stats['flow_25%'].dropna(axis=0).tolist(),
        'flow_min': stats['flow_min'].dropna(axis=0).tolist(),
        'high_res': stats['high_res'].dropna(axis=0).tolist(),
    }
    #
    plot_data.update(rperiods.to_dict(orient='index').items())
    max_visible = max(max(plot_data['flow_max']), max(plot_data['flow_avg']), max(plot_data['high_res']))
    rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, plot_data['y_max'], max_visible)
    #
    scatter_plots = [
        go.Scatter(
            name='Máximos y mínimos históricos',
            x=list(daymax_df.index) + list(daymin_df.index[::-1]),
            y=list(daymax_df.iloc[:, 0].values) + list(daymin_df.iloc[:, 0].values[::-1]),
            legendgroup='historical',
            fill='toself',
            line=dict(color='lightgrey', dash='dash'),
            mode="lines",
        ),
        go.Scatter(
            name='Maximum',
            x=daymax_df.index.tolist(),
            y=daymax_df.iloc[:, 0].values.tolist(),
            legendgroup='historical',
            showlegend=False,
            line=dict(color='grey', dash='dash'),
            mode="lines",
        ),
        go.Scatter(
            name='Minimum',
            x=daymin_df.index.tolist(),
            y=daymin_df.iloc[:, 0].values.tolist(),
            legendgroup='historical',
            showlegend=False,
            line=dict(color='grey', dash='dash'),
            mode="lines",
        ),
        go.Scatter(
            name='Máximos y mínimos pronosticados',
            x=(plot_data['x_stats'] + plot_data['x_stats'][::-1]),
            y=(plot_data['flow_max'] + plot_data['flow_min'][::-1]),
            legendgroup='boundaries',
            fill='toself',
            line=dict(color='lightblue', dash='dash'),
        ),
        go.Scatter(
            name='Máximo pronosticado',
            x=plot_data['x_stats'],
            y=plot_data['flow_max'],
            legendgroup='boundaries',
            showlegend=False,
            line=dict(color='darkblue', dash='dash'),
        ),
        go.Scatter(
            name='Mínimo pronosticado',
            x=plot_data['x_stats'],
            y=plot_data['flow_min'],
            legendgroup='boundaries',
            showlegend=False,
            line=dict(color='darkblue', dash='dash'),
        ),
        go.Scatter(
            name='Rango percentílico 25%-75%',
            x=(plot_data['x_stats'] + plot_data['x_stats'][::-1]),
            y=(plot_data['flow_75%'] + plot_data['flow_25%'][::-1]),
            legendgroup='percentile_flow',
            fill='toself',
            line=dict(color='lightgreen'), 
        ),
        go.Scatter(
            name='75%',
            x=plot_data['x_stats'],
            y=plot_data['flow_75%'],
            showlegend=False,
            legendgroup='percentile_flow',
            line=dict(color='green'), 
        ),
        go.Scatter(
            name='25%',
            x=plot_data['x_stats'],
            y=plot_data['flow_25%'],
            showlegend=False,
            legendgroup='percentile_flow',
            line=dict(color='green'), 
        ),
        go.Scatter(
            name='Pronóstico de alta resolución',
            x=plot_data['x_hires'],
            y=plot_data['high_res'],
            line={'color': 'black'}, 
        ),
        go.Scatter(
            name='Promedio del ensamble',
            x=plot_data['x_stats'],
            y=plot_data['flow_avg'],
            line=dict(color='blue'), 
        ),
    ]
    #
    if len(records.index) > 0:
        records_plot = [go.Scatter(
            name='Condiciones antecedentes',
            x=records.index.tolist(),
            y=records.iloc[:, 0].values.tolist(),
            line=dict(color='#FFA15A'),
        )]
        scatter_plots += records_plot
    #
    scatter_plots += rperiod_scatters
    layout = go.Layout(
        title=f"Pronóstico de Caudales <br>COMID:{comid}",
        yaxis={'title': 'Caudal (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Fecha (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y %H:%M',
               'tickformat': '%b %d %Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white', width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    return figure.to_dict()



def probabilities_table(stats, ensem, rperiods):
    dates = stats.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]
    span = enddate - startdate
    uniqueday = [startdate + dt.timedelta(days=i) for i in range(span.days + 2)]
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
    for i in range(len(uniqueday) - 2):  # (-1) omit the extra day used for reference only
        tmp = ensem.loc[uniqueday[i]:uniqueday[i + 1]]
        days.append(uniqueday[i].strftime('%b %d'))
        num2 = 0
        num5 = 0
        num10 = 0
        num25 = 0
        num50 = 0
        num100 = 0
        for column in tmp:
            if not tmp[column].empty:
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
    path = "/home/ubuntu/inamhi-geoglows/backend/app_national_water_level_forecast/probabilities_table.html"
    with open(path) as template:
        return jinja2.Template(template.read()).render(
            days=days, 
            r2=r2, 
            r5=r5, 
            r10=r10, 
            r25=r25, 
            r50=r50, 
            r100=r100,
            colors=_plot_colors())



def get_metrics_table(sim, cor, my_metrics):
    # Metrics for simulated data
    table_sim = hs.make_table(sim, my_metrics)
    table_sim = table_sim.rename(index={'Full Time Series': 'Serie Simulada'})
    table_sim = table_sim.transpose()
    
    # Metrics for corrected simulation data
    table_cor = hs.make_table(cor, my_metrics)
    table_cor = table_cor.rename(index={'Full Time Series': 'Serie Corregida'})
    table_cor = table_cor.transpose()
    
    # Merging data, adding suffixes to avoid column name overlap
    table_final = pd.merge(table_sim, table_cor, right_index=True, left_index=True, 
                           suffixes=('_sim', '_cor'))
    
    # Rounding and converting to HTML
    table_final = table_final.round(decimals=2)
    table_final = table_final.to_html(
        classes="table table-hover table-striped", 
        table_id="corrected_1")
    
    # Adjusting the table HTML output
    table_final = table_final.replace(
        'border="1"', 'border="0"').replace(
        '<tr style="text-align: right;">', '<tr style="text-align: left;">')
    
    return table_final





###############################################################################
#                                CONTROLLERS                                  #
###############################################################################
def get_streamflow_alerts(request):
    """
    Retrieve streamflow alerts for a specified date from the database and 
    return them as a GeoJSON response.

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain a 'date' 
        parameter in the GET request.

    Returns:
    --------
    - JsonResponse
        A Django JsonResponse object containing the GeoJSON data of water 
        level alerts for the given date.
    """
    # Query request param and initialize the db connection
    date = request.GET.get('date')
    db = create_engine(token)
    con = db.connect()

    # SQL query to retrieve streamflow data for the specified date
    sql = f"""SELECT 
                    dn.code, dn.comid, dn.name, dn.latitude, dn.longitude, 
                    dn.river, dn.location1, dn.location2, ag.datetime,
                    ag.d01, ag.d02, ag.d03, ag.d04, 
                    ag.d05, ag.d06, ag.d07, ag.d08, 
                    ag.d09, ag.d10, ag.d11, ag.d12, 
                    ag.d13, ag.d14, ag.d15
                FROM 
                    streamflow_stations dn
                JOIN 
                    alert_geoglows_streamflow ag
                ON 
                    dn.code = ag.code
                WHERE 
                    ag.datetime = '{date}'
            """
    
    # Execute the query and load the data into a pandas DataFrame
    query = pd.read_sql(sql, con=con)
    con.close() 

    # Create Point geometries for each row based on longitude and latitude
    query['geometry'] = query.apply(
        lambda row: Point(row['longitude'], row['latitude']), axis=1)

    # Convert the DataFrame to GeoJSON format
    gdf = gpd.GeoDataFrame(query, geometry='geometry')
    data = gdf.__geo_interface__
    return JsonResponse(data)



def get_plot_data(request):
    """
    Retrieve streamflow data (observed, simulated, corrected, and forecast) 
    from the database, generate plots and metrics, and return them as a JSON 
    response.

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain the following 
        parameters in the GET request:
        - 'comid' : str
            A unique identifier for the location.
        - 'code' : str
            A code that identifies the dataset for observed streamflow data.
        - 'name' : str
            The name associated with the location or dataset.
        - 'date' : str
            The initialization date for the forecast.
        - 'width' : str
            The width used for plotting, which is later converted to a float.

    Returns:
    --------
    - JsonResponse
        A Django JsonResponse object containing various types of streamflow 
        plots and statistical metrics.
    """

    # Query request param and initialize the db connection
    comid = request.GET.get('comid')
    code = request.GET.get('code')
    name = request.GET.get('name')
    date = request.GET.get('date')
    width = request.GET.get('width')
    width = float(width)
    width2 = width/2
    db = create_engine(token)
    con = db.connect()

    # Retrieve observed data
    sql = f""" 
        SELECT datetime, value 
        FROM streamflow_data 
        WHERE code='{code}'
    """
    observed_data = get_format_data(sql, con)
    observed_data[observed_data < 0.1] = 0.1
    
    # Retrieve historical simulation and corrected data
    sql = f"""
        SELECT datetime, value 
        FROM historical_simulation 
        WHERE comid={comid}
    """
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1
    corrected_data = get_bias_corrected_data(simulated_data, observed_data)

    # Retrieve ensemble forecast data
    sql = f"""
        SELECT * FROM ensemble_forecast 
        WHERE initialized='{date}' AND comid={comid}
    """
    ensemble_forecast = get_format_data(sql, con)
    ensemble_forecast = ensemble_forecast.drop(columns=['comid', "initialized"])

    # Corrected forecast
    corrected_ensemble_forecast = get_corrected_forecast(
        simulated_data, 
        ensemble_forecast, 
        observed_data
    )
    corrected_return_periods = get_return_periods(comid, corrected_data)
    corrected_stats = get_ensemble_stats(corrected_ensemble_forecast)

    # Forecast records
    sql = f"SELECT datetime,value FROM forecast_records where comid={comid}"
    forecast_records = get_format_data(sql, con)
    corrected_forecast_records = get_corrected_forecast_records(
        forecast_records, 
        simulated_data, 
        observed_data)
    con.close()

    # Merged data
    merged_sim = hd.merge_data(sim_df = simulated_data, obs_df = observed_data)
    merged_cor = hd.merge_data(sim_df = corrected_data, obs_df = observed_data)
    metrics_table = get_metrics_table(
        sim = merged_sim,
        cor = merged_cor,
        my_metrics = [
            "ME", "RMSE", "NRMSE (Mean)", "NSE", "KGE (2009)", "KGE (2012)", 
            "R (Pearson)", "R (Spearman)", "r2"])

    #Plots
    hs = historical_plot(simulated_data, corrected_data, observed_data, code, name, width)
    dp = daily_average_plot(observed_data, simulated_data, corrected_data, code, name, width)
    mp = monthly_average_plot(observed_data, simulated_data, corrected_data, code, name, width)
    vp = scatter_plot(simulated_data,corrected_data, observed_data, code, name, False, width2)
    fd = scatter_plot(simulated_data,corrected_data, observed_data, code, name, True, width2)
    fp = forecast_plot(
        corrected_stats, 
        corrected_return_periods, 
        comid, 
        corrected_forecast_records, 
        observed_data, 
        width)
    return JsonResponse({
        "hs":hs, "dp":dp, "mp": mp, "vp":vp, "fd": fd, "fp":fp, 
        "table": metrics_table
    })


def get_forecast_table(request):
    """
    Retrieve forecast data, correct it, and return a table with probabilities
    based on the ensemble forecast, historical simulation, and observed data.

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain the following
        parameters in the GET request:
        - 'comid' : str
            A unique identifier for the location.
        - 'code' : str
            A code that identifies the dataset for observed streamflow data.
        - 'date' : str
            The initialization date for the ensemble forecast.

    Returns:
    --------
    - HttpResponse
        A Django HttpResponse object containing the forecast probabilities
        table based on corrected ensemble forecast data.
    """    
    # Query request parameters and initialize the database connection
    comid = request.GET.get('comid')
    code = request.GET.get('code')
    date = request.GET.get('date')
    db = create_engine(token)  # Initialize the database engine
    con = db.connect()  # Establish the database connection

    # Retrieve observed data
    sql = f"""
            SELECT datetime, value 
            FROM streamflow_data 
            WHERE code='{code}'
        """
    observed_data = get_format_data(sql, con) 
    observed_data[observed_data < 0.1] = 0.1  

    # Retrieve historical simulation and apply bias correction
    sql = f"""
            SELECT datetime, value 
            FROM historical_simulation 
            WHERE comid={comid}
        """
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1  
    corrected_data = get_bias_corrected_data(simulated_data, observed_data) 

    # Retrieve ensemble forecast data
    sql = f"""
            SELECT * 
            FROM ensemble_forecast 
            WHERE initialized='{date}' AND comid={comid}
        """
    ensemble_forecast = get_format_data(sql, con) 
    ensemble_forecast = ensemble_forecast.drop(columns=['comid', "initialized"]) 

    # Apply corrections to the forecast data
    corrected_ensemble_forecast = get_corrected_forecast(simulated_data, 
                                                         ensemble_forecast, 
                                                         observed_data)  
    # Correct the ensemble forecast
    corrected_return_periods = get_return_periods(comid, corrected_data) 
    corrected_stats = get_ensemble_stats(corrected_ensemble_forecast)
    con.close() 
    
    # Generate the probabilities table based on corrected forecast data
    pt = probabilities_table(corrected_stats, corrected_ensemble_forecast, 
                             corrected_return_periods)
    return HttpResponse(pt)



def get_historical_simulation_csv(request):
    """
    Retrieve historical simulation data for a specified 'comid' and return it 
    as a CSV file.

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain a 'comid'
        parameter in the GET request.

    Returns:
    --------
    - HttpResponse
        A Django HttpResponse object that contains the historical simulation 
        data in CSV format. The response is sent as an attachment for download.
    """
    
    # Query the 'comid' parameter from the request
    comid = request.GET.get('comid')

    # Initialize the database connection
    db = create_engine(token) 
    con = db.connect()

    # SQL query to retrieve the historical simulation 
    sql = f"""
            SELECT datetime, value 
            FROM historical_simulation 
            WHERE comid={comid}
        """
    
    # Fetch and format the historical simulation data
    historical_simulation = get_format_data(sql, con)
    
    # Close the database connection
    con.close()

    # Prepare the HTTP response with content type set to CSV
    response = HttpResponse(content_type='text/csv')
    
    # Set the content-disposition to indicate a file attachment
    response['Content-Disposition'] = (
        f'attachment; filename="historical_simulation_{comid}.csv"'
    )
    
    # Write the historical simulation data to the CSV response
    historical_simulation.to_csv(path_or_buf=response, index=True)
    return response





def get_corrected_simulation_csv(request):
    """
    Retrieve corrected simulation data for a specified 'comid' and return it 
    as a CSV file.

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain 'comid'
         and 'code' parameters in the GET request.

    Returns:
    --------
    - HttpResponse
        A Django HttpResponse object that contains the historical simulation 
        data in CSV format. The response is sent as an attachment for download.
    """
    # Query request parameters and initialize the database connection
    comid = request.GET.get('comid')
    code = request.GET.get('code')
    db = create_engine(token)
    con = db.connect()

    # Retrieve observed data
    sql = f"""
            SELECT datetime, value 
            FROM streamflow_data 
            WHERE code='{code}'
        """
    observed_data = get_format_data(sql, con) 
    observed_data[observed_data < 0.1] = 0.1  

    # Retrieve historical simulation and apply bias correction
    sql = f"""
            SELECT datetime, value 
            FROM historical_simulation 
            WHERE comid={comid}
        """
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1  
    corrected_data = get_bias_corrected_data(simulated_data, observed_data) 

    # Prepare the HTTP response with content type set to CSV
    response = HttpResponse(content_type='text/csv')
    
    # Set the content-disposition to indicate a file attachment
    response['Content-Disposition'] = (
        f'attachment; filename="corrected_simulation_{comid}.csv"'
    )
    
    # Write the historical simulation data to the CSV response
    corrected_data.to_csv(path_or_buf=response, index=True)
    return response



def get_forecast_csv(request):
    """
    Retrieve forecast data, correct it, and return it as a CSV file

    Parameters:
    -----------
    - request : HttpRequest
        The HTTP request object from Django, which should contain the following
        parameters in the GET request:
        - 'comid' : str
            A unique identifier for the location.
        - 'code' : str
            A code that identifies the dataset for observed streamflow data.
        - 'date' : str
            The initialization date for the ensemble forecast.

    Returns:
    --------
    - HttpResponse
        A Django HttpResponse object that contains the corrected forecast 
        data in CSV format. The response is sent as an attachment for download.
    """    
    # Query request parameters and initialize the database connection
    comid = request.GET.get('comid')
    code = request.GET.get('code')
    date = request.GET.get('date')
    db = create_engine(token)  # Initialize the database engine
    con = db.connect()  # Establish the database connection

    # Retrieve observed data
    sql = f"""
            SELECT datetime, value 
            FROM streamflow_data 
            WHERE code='{code}'
        """
    observed_data = get_format_data(sql, con) 
    observed_data[observed_data < 0.1] = 0.1  

    # Retrieve historical simulation and apply bias correction
    sql = f"""
            SELECT datetime, value 
            FROM historical_simulation 
            WHERE comid={comid}
        """
    simulated_data = get_format_data(sql, con)
    simulated_data[simulated_data < 0.1] = 0.1  
    corrected_data = get_bias_corrected_data(simulated_data, observed_data) 

    # Retrieve ensemble forecast data
    sql = f"""
            SELECT * 
            FROM ensemble_forecast 
            WHERE initialized='{date}' AND comid={comid}
        """
    ensemble_forecast = get_format_data(sql, con) 
    ensemble_forecast = ensemble_forecast.drop(columns=['comid', "initialized"]) 

    # Apply corrections to the forecast data
    corrected_ensemble_forecast = get_corrected_forecast(simulated_data, 
                                                         ensemble_forecast, 
                                                         observed_data)  
    corrected_stats = get_ensemble_stats(corrected_ensemble_forecast)
    con.close() 

    # Prepare the HTTP response with content type set to CSV
    response = HttpResponse(content_type='text/csv')
    
    # Set the content-disposition to indicate a file attachment
    response['Content-Disposition'] = (
        f'attachment; filename="corrected_forecast_{comid}.csv"'
    )
    
    # Write the historical simulation data to the CSV response
    corrected_stats.to_csv(path_or_buf=response, index=True)
    return response
