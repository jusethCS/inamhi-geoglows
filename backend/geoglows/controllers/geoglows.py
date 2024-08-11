import os
import math
import numpy as np
import pandas as pd
import sqlalchemy as sql
import datetime as dt
from dotenv import load_dotenv
from sqlalchemy import create_engine
import geopandas as gpd
from shapely.geometry import Point
import geoglows
import numpy as np
import math
import plotly.graph_objs as go
import datetime as dt
import pandas as pd
import jinja2
import os
import plotly.io as pio
import scipy
import scipy.stats
import plotly.graph_objects as go




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
    #
    # Set the 'datetime' column as the DataFrame index
    data.index = pd.to_datetime(data['datetime'])
    #
    # Drop the 'datetime' column as it is now the index
    data = data.drop(columns=['datetime'])
    #
    # Format the index values to the desired datetime string format
    data.index = pd.to_datetime(data.index)
    data.index = data.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    data.index = pd.to_datetime(data.index)
    return(data)



def gumbel_1(sd: float, mean: float, rp: float) -> float:
    """
    Calculate the Gumbel Type I distribution value for a given return period.

    This function calculates the Gumbel Type I distribution value based on the
    provided standard deviation, mean, and return period.

    Parameters:
    sd (float): The standard deviation of the dataset.
    mean (float): The mean of the dataset.
    return_period (float): The return period for which the value is calculated.

    Returns:
    float: The calculated Gumbel Type I distribution value.

    Raises:
    ValueError: If standard_deviation is not positive or return_period is not 
    greater than 1.
    """
    try:
        # Validate input parameters
        if sd <= 0:
            raise ValueError("Standard deviation must be positive.")
        if rp <= 1:
            raise ValueError("Return period must be greater than 1.")
        #
        # Calculate the Gumbel reduced variate
        y = -math.log(-math.log(1 - (1 / rp)))
        #
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
    comid (int): The COMID (unique identifier for a river segment).
    data (pd.DataFrame): DataFrame containing flow data with a datetime index.

    Returns:
    pd.DataFrame: DataFrame containing the corrected return period values for 
    the specified COMID.

    Raises:
    ValueError: If the input data does not contain the necessary flow data.
    """
    if data.empty:
        raise ValueError("The input data is empty.")
    #
    # Calculate the maximum annual flow
    max_annual_flow = data.groupby(data.index.strftime("%Y")).max()
    #
    if max_annual_flow.empty:
        raise ValueError("No annual maximum flow data available.")
    #
    # Calculate the mean and standard deviation of the maximum annual flow
    mean_value = np.mean(max_annual_flow.iloc[:, 0].values)
    std_value = np.std(max_annual_flow.iloc[:, 0].values)
    #
    # Define the return periods to calculate
    return_periods = [100, 50, 25, 10, 5, 2]
    return_periods_values = []
    #
    # Compute the corrected return period values using the Gumbel Type I distribution
    for rp in return_periods:
        return_periods_values.append(gumbel_1(std_value, mean_value, rp))
    #
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
    #
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
    ensemble (pd.DataFrame): DataFrame containing the ensemble data.
    quantile (float): The quantile to compute (between 0 and 1).
    label (str): The label for the resulting quantile column.

    Returns:
    pd.DataFrame: DataFrame containing the computed quantile with the specified 
    label.
    """
    # Calculate the quantile along the columns (axis=1) and convert to a DataFrame
    quantile_df = ensemble.quantile(quantile, axis=1).to_frame()
    #
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
    ensemble (pd.DataFrame): DataFrame containing the ensemble data.

    Returns:
    pd.DataFrame: DataFrame containing the statistical measures and high-resolution
    flow data.
    """
    # Extract the high-resolution data and remove it from the ensemble
    high_res_df = ensemble['ensemble_52'].to_frame()
    ensemble.drop(columns=['ensemble_52'], inplace=True)
    #
    # Remove rows with NaN values in both the ensemble and high-resolution data
    ensemble.dropna(inplace=True)
    high_res_df.dropna(inplace=True)
    #
    # Rename the column for high-resolution data
    high_res_df.rename(columns={'ensemble_52': 'high_res'}, inplace=True)
    #
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





###############################################################################
#                             PLOTTING FUNCTIONS                              #
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

def hs_plot(hist, rperiods, comid, width):
    dates = hist.index.tolist()
    startdate = dates[0]
    enddate = dates[-1]
    # Convert ndarray to list
    y_flow = hist.values.flatten().tolist()
    y_max = float(max(hist.values))  # Ensure that y_max is a float
    plot_data = {
        'x_datetime': dates,
        'y_flow': y_flow,
        'y_max': y_max,
    }
    # Convert rperiods to dictionary and ensure all values are serializable
    rperiods_dict = rperiods.to_dict(orient='index')
    for key, value in rperiods_dict.items():
        if isinstance(value, np.ndarray):
            rperiods_dict[key] = value.tolist()
    plot_data.update(rperiods_dict)
    rperiod_scatters = _rperiod_scatters(startdate, enddate, rperiods, y_max, y_max)
    scatter_plots = [go.Scatter(
        name='Simulación histórica',
        x=plot_data['x_datetime'],
        y=plot_data['y_flow'])
    ]
    scatter_plots += rperiod_scatters
    layout = go.Layout(
        title=f"Simulación histórica <br>COMID: {comid}",
        yaxis={'title': 'Caudal (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Fecha (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y', 'tickformat': '%Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white', width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    # Convert the figure to a dictionary
    figure_dict = figure.to_dict()
    return figure_dict



def daily_plot(sim, comid, width):
    # Generate the average values
    daily = sim.groupby(sim.index.strftime("%m/%d"))
    day25_df = daily.quantile(0.25)
    day75_df = daily.quantile(0.75)
    dayavg_df = daily.quantile(0.5)
    #
    # Convertir ndarrays a listas
    x_data_75_25 = np.concatenate([day75_df.index, day25_df.index[::-1]]).tolist()
    y_data_75_25 = np.concatenate([day75_df.iloc[:, 0].values, day25_df.iloc[:, 0].values[::-1]]).tolist()
    x_data_75 = day75_df.index.tolist()
    y_data_75 = day75_df.iloc[:, 0].values.tolist()
    x_data_25 = day25_df.index.tolist()
    y_data_25 = day25_df.iloc[:, 0].values.tolist()
    x_data_avg = dayavg_df.index.tolist()
    y_data_avg = dayavg_df.iloc[:, 0].values.tolist()
    #
    # Plot
    layout = go.Layout(
        title=f'Caudal medio multi-diario<br>COMID: {comid}',
        xaxis=dict(title='Día del año'), 
        yaxis=dict(title='Caudal (m<sup>3</sup>/s)', autorange=True),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='simple_white',
        showlegend=True
    )
    #
    hydroviewer_figure = go.Figure(layout=layout)
    hydroviewer_figure.add_trace(go.Scatter(
        name='Percentil 25-75',
        x=x_data_75_25,
        y=y_data_75_25,
        legendgroup='percentile_flow',
        line=dict(color='lightgreen'),
        fill='toself'
    ))
    #
    hydroviewer_figure.add_trace(go.Scatter(
        name='75%',
        x=x_data_75,
        y=y_data_75,
        legendgroup='percentile_flow',
        showlegend=False,
        line=dict(color='lightgreen')
    ))
    #
    hydroviewer_figure.add_trace(go.Scatter(
        name='25%',
        x=x_data_25,
        y=y_data_25,
        legendgroup='percentile_flow',
        showlegend=False,
        line=dict(color='lightgreen')
    ))
    #
    hydroviewer_figure.add_trace(go.Scatter(
        name='Caudal medio',
        x=x_data_avg,
        y=y_data_avg,
        line=dict(color='blue')
    ))
    #
    hydroviewer_figure.update_layout(template='simple_white', width=width)
    hydroviewer_figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    hydroviewer_figure.update_xaxes(linecolor='gray', mirror=True, showline=True) 
    return hydroviewer_figure.to_dict()



def monthly_plot(sim, comid, width):
    # Generar los valores promedio
    daily = sim.groupby(sim.index.strftime("%m"))
    day25_df = daily.quantile(0.25)
    day75_df = daily.quantile(0.75)
    dayavg_df = daily.quantile(0.5)
    #
    # Convertir ndarrays a listas para JSON
    x_data_75_25 = np.concatenate([day75_df.index, day25_df.index[::-1]]).tolist()
    y_data_75_25 = np.concatenate([day75_df.iloc[:, 0].values, day25_df.iloc[:, 0].values[::-1]]).tolist()
    x_data_75 = day75_df.index.tolist()
    y_data_75 = day75_df.iloc[:, 0].values.tolist()
    x_data_25 = day25_df.index.tolist()
    y_data_25 = day25_df.iloc[:, 0].values.tolist()
    x_data_avg = dayavg_df.index.tolist()
    y_data_avg = dayavg_df.iloc[:, 0].values.tolist()
    #
    # Configuración de la gráfica
    layout = go.Layout(
        title=f'Caudal medio multi-mensual<br>COMID: {comid}',
        xaxis=dict(title='Mes'), 
        yaxis=dict(title='Caudal (m<sup>3</sup>/s)', autorange=True),
        plot_bgcolor='white',
        paper_bgcolor='white',
        template='simple_white',
        showlegend=True
    )
    #
    hydroviewer_figure = go.Figure(layout=layout)
    hydroviewer_figure.add_trace(go.Scatter(
        name='Percentil 25-75',
        x=x_data_75_25,
        y=y_data_75_25,
        legendgroup='percentile_flow',
        line=dict(color='lightgreen'),
        fill='toself'
    ))
    #
    hydroviewer_figure.add_trace(go.Scatter(
        name='75%',
        x=x_data_75,
        y=y_data_75,
        legendgroup='percentile_flow',
        showlegend=False,
        line=dict(color='lightgreen')
    ))
    #
    hydroviewer_figure.add_trace(go.Scatter(
        name='25%',
        x=x_data_25,
        y=y_data_25,
        legendgroup='percentile_flow',
        showlegend=False,
        line=dict(color='lightgreen')
    ))
    #
    hydroviewer_figure.add_trace(go.Scatter(
        name='Caudal medio',
        x=x_data_avg,
        y=y_data_avg,
        line=dict(color='blue')
    ))
    #
    hydroviewer_figure.update_layout(template='simple_white', width=width)
    hydroviewer_figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    hydroviewer_figure.update_xaxes(linecolor='gray', mirror=True, showline=True) 
    return hydroviewer_figure.to_dict()




def volumen_plot(sim, comid, width):
    # Parse dataframe to array
    sim_array = sim.iloc[:, 0].values * 0.0864  # Conversión de m3/s a Hm3
    sim_volume = sim_array.cumsum()  # Cálculo del volumen acumulado
    #
    # Convertir a listas para garantizar la serialización JSON
    x_data = sim.index.tolist()
    y_data = sim_volume.tolist()
    #
    # Generar traza para el volumen simulado
    simulated_volume = go.Scatter(
        x=x_data, 
        y=y_data, 
        name='Simulated'
    )
    #
    # Configuración de la gráfica
    layout = go.Layout(
        title=f'Volumen acumulado simulado <br>COMID:{comid}',
        xaxis=dict(title='Fecha'), 
        yaxis=dict(title='Volumen (Mm<sup>3</sup>)', autorange=True),
        showlegend=False,
        template='simple_white'
    )
    #
    # Integrando la gráfica
    hydroviewer_figure = go.Figure(data=[simulated_volume], layout=layout)
    hydroviewer_figure.update_layout(template='simple_white', width=width)
    hydroviewer_figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    hydroviewer_figure.update_xaxes(linecolor='gray', mirror=True, showline=True) 
    #
    # Convertir la figura a un diccionario JSON serializable
    return hydroviewer_figure.to_dict()




def fd_plot(hist, comid, width):
    # Procesar el DataFrame hist para crear la curva de duración de caudales
    sorted_hist = hist.values.flatten()
    sorted_hist.sort()
    #
    # Rango de datos de menor a mayor
    ranks = len(sorted_hist) - scipy.stats.rankdata(sorted_hist, method='average')
    #
    # Calcular la probabilidad de cada rango
    prob = [(ranks[i] / (len(sorted_hist) + 1)) for i in range(len(sorted_hist))]
    #
    # Convertir arrays de NumPy a listas de Python
    plot_data = {
        'x_probability': prob,
        'y_flow': sorted_hist.tolist(),  # Convertir a lista
        'y_max': sorted_hist[0],  # El primer elemento es un valor escalar
    }
    #
    scatter_plots = [
        go.Scatter(
            name='Flow Duration Curve',
            x=plot_data['x_probability'],
            y=plot_data['y_flow'])
    ]
    #
    layout = go.Layout(
        xaxis={'title': 'Probabilidad de excedencia'},
        yaxis={'title': 'Caudal (m<sup>3</sup>/s)', 'range': [0, 'auto']},
    )
    #
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(
        title=f"Curva de duración de caudales <br>COMID: {comid}",
        template='simple_white',
        width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    return figure.to_dict()



def get_date_values(startdate, enddate, df):
    date_range = pd.date_range(start=startdate, end=enddate)
    month_day = date_range.strftime("%m-%d")
    pddf = pd.DataFrame(index=month_day)
    pddf.index.name = "datetime"
    combined_df = pd.merge(pddf, df, how='left', left_index=True, right_index=True)
    combined_df.index = pd.to_datetime(date_range)
    return combined_df


def forecast_plot(stats, rperiods, comid, records, sim, width):
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
    daily = sim.groupby(sim.index.strftime("%m-%d"))
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
        title=f"Pronóstico de caudales <br>COMID:{comid}",
        yaxis={'title': 'Caudal (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Fecha (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y %H:%M',
               'tickformat': '%b %d %Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white', width=width)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    return figure.to_dict()




def get_probabilities_table(stats, ensem, rperiods):
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
    path = "/home/ubuntu/inamhi-geoglows/backend/geoglows/controllers/probabilities_table.html"
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




###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################
def get_flood_alerts(date):
    # Establish connection
    db = create_engine(token)
    con = db.connect()
    #
    # Determine the last date that was inserted into db
    sql = f"""SELECT 
                    dn.comid, dn.latitude, dn.longitude, dn.river,
                    dn.location1, dn.location2, ag.datetime,
                    ag.d01, ag.d02, ag.d03, ag.d04, 
                    ag.d05, ag.d06, ag.d07, ag.d08, 
                    ag.d09, ag.d10, ag.d11, ag.d12, 
                    ag.d13, ag.d14, ag.d15
                FROM 
                    drainage_network dn
                JOIN 
                    alert_geoglows ag
                ON 
                    dn.comid = ag.comid
                WHERE 
                    ag.datetime = '{date}'
            """
    query = pd.read_sql(sql, con=con)
    #query = pd.read_csv("/home/ubuntu/datos.csv", sep=";")
    con.close()
    query['geometry'] = query.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
    gdf = gpd.GeoDataFrame(query, geometry='geometry')
    geojson_dict = gdf.__geo_interface__
    return(geojson_dict)



def historical_simulation_plot(comid):
    db = create_engine(token)
    con = db.connect()
    sql = f"SELECT datetime,value FROM historical_simulation where comid={comid}"
    historical_simulation = get_format_data(sql, con)
    return_periods = get_return_periods(comid, historical_simulation)
    plot = hs_plot(historical_simulation, return_periods, comid)
    con.close()
    return(plot)




def all_data_plot(comid, date, width):
    width = float(width)
    width2 = width/2
    db = create_engine(token)
    con = db.connect()
    sql = f"SELECT datetime,value FROM historical_simulation where comid={comid}"
    historical_simulation = get_format_data(sql, con)
    return_periods = get_return_periods(comid, historical_simulation)
    sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])
    stats = get_ensemble_stats(ensemble_forecast)
    sql = f"SELECT datetime,value FROM forecast_records where comid={comid}"
    records = get_format_data(sql, con)
    hs = hs_plot(historical_simulation, return_periods, comid, width)
    dp = daily_plot(historical_simulation, comid, width)
    mp = monthly_plot(historical_simulation, comid, width)
    vp = volumen_plot(historical_simulation, comid, width2)
    fd = fd_plot(historical_simulation, comid, width2)
    fp = forecast_plot(stats, return_periods, comid, records, historical_simulation, width)
    #tb = get_probabilities_table(stats, ensemble_forecast, return_periods)
    con.close()
    return({"hs":hs, "dp":dp, "mp":mp, "vp":vp, "fd": fd, "fp":fp})


def probability_table(comid, date):
    db = create_engine(token)
    con = db.connect()
    sql = f"SELECT datetime,value FROM historical_simulation where comid={comid}"
    historical_simulation = get_format_data(sql, con)
    return_periods = get_return_periods(comid, historical_simulation)
    sql = f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}"
    ensemble_forecast = get_format_data(sql, con).drop(columns=['comid', "initialized"])
    stats = get_ensemble_stats(ensemble_forecast)
    sql = f"SELECT datetime,value FROM forecast_records where comid={comid}"
    tb = get_probabilities_table(stats, ensemble_forecast, return_periods)
    con.close()
    return(tb)


#a = all_data_plot(9027193, "2024-08-10")



