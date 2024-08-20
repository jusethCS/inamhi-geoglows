# File handling, date management, and environment variables
import os
from dotenv import load_dotenv
import datetime as dt
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# Data processing and statistical analysis
import numpy as np
import pandas as pd
import math
import sqlalchemy as sql
from sqlalchemy import create_engine

# Geospatial data manipulation
import geopandas as gpd
from shapely.geometry import Point
import rasterio
from rasterio.mask import mask
from rasterio.plot import show

# Visualization and plotting
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import matplotlib.image as mpimg
import plotly.graph_objs as go
import plotly.graph_objects as go
import plotly.io as pio

# Report generation
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Table
from reportlab.platypus import TableStyle, PageBreak
from reportlab.platypus.paragraph import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from functools import partial

# Email management
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders



###############################################################################
#                                    UTILS                                    #
###############################################################################
def get_value(raster_file:str, shp_file:gpd.GeoDataFrame, 
              field:str) -> pd.DataFrame:
    """
    Extracts average values from a raster file based on the geometries in a 
    shapefile.

    Parameters:
    - raster_file (str): Path to the raster file
    - shp_file (geopandas.GeoDataFrame): GeoDataFrame containing the shapefile 
        data, typically representing sub-basins.
    - field (str): The field in the shapefile to use for labeling the sub-basins

    Returns:
    - pandas.DataFrame: A DataFrame containing geometries names and their 
        corresponding average  values.
    """
    # Load the shapefile containing watershed (sub-basin) geometries
    cuencas = shp_file

    # Initialize an empty DataFrame to store the results
    resultados = pd.DataFrame(columns=['subbasin', 'pacum'])

    # Open the raster file
    with rasterio.open(raster_file) as src:
        # Reproject the shp to match the raster's coordinate reference system
        cuencas = cuencas.to_crs(src.crs)

        # Read the raster values that intersect with the sub-basin geometries
        resultados_list = []
        for index, row in cuencas.iterrows():
            geom = row.geometry

            # Mask the raster based on the sub-basin geometry
            out_image, out_transform = mask(src, [geom], crop=True)
            out_image[out_image < 0] = 0
            
            # Calculate the average precipitation value within the sub-basin
            avg_precipitation = round(np.nanmean(out_image), 2)
            
            # Append the results to the list
            resultados_list.append(
                {'subbasin': f"Rio {row[field]}", 'pacum': avg_precipitation}
            )
        
        # Convert the list to a DataFrame and append it to the results
        resultados = pd.concat(
            [resultados, pd.DataFrame(resultados_list)], 
            ignore_index=True
        )
    
    return resultados


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
#                        PLOTTING FUNCTIONS GEOGLOWS                          #
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


def get_date_values(startdate, enddate, df):
    date_range = pd.date_range(start=startdate, end=enddate)
    month_day = date_range.strftime("%m-%d")
    pddf = pd.DataFrame(index=month_day)
    pddf.index.name = "datetime"
    combined_df = pd.merge(pddf, df, how='left', left_index=True, right_index=True)
    combined_df.index = pd.to_datetime(date_range)
    return combined_df


def forecast_geoglows_plot(stats, rperiods, comid, records, sim):
    # Define los registros
    records = records.loc[records.index >= pd.to_datetime(stats.index[0] - dt.timedelta(days=8))]
    records = records.loc[records.index <= pd.to_datetime(stats.index[0])]
    #
    # Comienza el procesamiento de los inputs
    dates_forecast = stats.index.tolist()
    dates_records = records.index.tolist()
    startdate = dates_forecast[0] #Esta linea quitar
    #try:
    #    startdate = dates_records[0]
    #except IndexError:
    #    startdate = dates_forecast[0]
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
        #scatter_plots += records_plot
    #
    #scatter_plots += rperiod_scatters
    layout = go.Layout(
        yaxis={'title': 'Caudal (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Fecha (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y %H:%M',
               'tickformat': '%b %d %Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white', width=1000, height=400, showlegend=False)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    figure.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    return figure.to_dict()


def geoglows_plot(comid, conn, outpath):
    now = dt.datetime.now()
    date = now.strftime("%Y-%m-%d")
    simulated_data = get_format_data(f"SELECT datetime,value FROM historical_simulation where comid={comid}", conn)
    ensemble_forecast = get_format_data(f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}", conn).drop(columns=['comid', "initialized"])
    forecast_records = get_format_data(f"SELECT datetime,value FROM forecast_records where comid={comid}", conn)
    ensemble_stats = get_ensemble_stats(ensemble_forecast)
    return_periods = get_return_periods(comid, simulated_data)
    forecast_plot = forecast_geoglows_plot(
        stats = ensemble_stats,
        rperiods = return_periods,
        comid = comid,
        records=forecast_records,
        sim = simulated_data)
    pio.write_image(forecast_plot, outpath)
    #
    daily_avg = ensemble_stats.resample('D').mean().round(2)
    daily_avg.index = pd.to_datetime(daily_avg.index)
    daily_avg.index = daily_avg.index.to_series().dt.strftime("%d/%m")
    daily_avg = daily_avg[['flow_avg', "high_res"]]
    daily_avg = daily_avg.rename(columns={  'flow_avg': 'Caudal medio (m3/s)', 
                                            "high_res": "Alta resolución (m3/s)"})
    daily_avg = daily_avg.dropna().T.reset_index()
    daily_avg = daily_avg.rename(columns={"index": "Día/Mes"})
    return(daily_avg)



###############################################################################
#                             COLOR BAR FUNCTIONS                             #
###############################################################################
def color_pacum(pixelValue:float) -> str:
    """
    Returns the corresponding color for a given precipitation value (pixelValue)
    based on predefined ranges.

    Parameters:
    pixelValue (float): The precipitation value to determine the color.

    Returns:
    str: The color in hexadecimal format corresponding to the precipitation.
    """
    if pixelValue == 0:
        return "none"
    elif 0.01 <= pixelValue <= 0.5:
        return "#B4D7FF"
    elif 0.5 < pixelValue <= 1:
        return "#75BAFF"
    elif 1 < pixelValue <= 2:
        return "#359AFF"
    elif 2 < pixelValue <= 3:
        return "#0482FF"
    elif 3 < pixelValue <= 4:
        return "#0069FF"
    elif 4 < pixelValue <= 5:
        return "#00367F"
    elif 5 < pixelValue <= 7:
        return "#148F1B"
    elif 7 < pixelValue <= 10:
        return "#1ACF05"
    elif 10 < pixelValue <= 15:
        return "#63ED07"
    elif 15 < pixelValue <= 20:
        return "#FFF42B"
    elif 20 < pixelValue <= 25:
        return "#E8DC00"
    elif 25 < pixelValue <= 30:
        return "#F06000"
    elif 30 < pixelValue <= 35:
        return "#FF7F27"
    elif 35 < pixelValue <= 40:
        return "#FFA66A"
    elif 40 < pixelValue <= 45:
        return "#F84E78"
    elif 45 < pixelValue <= 50:
        return "#F71E54"
    elif 50 < pixelValue <= 60:
        return "#BF0000"
    elif 60 < pixelValue <= 70:
        return "#880000"
    elif 70 < pixelValue <= 80:
        return "#640000"
    elif 80 < pixelValue <= 90:
        return "#C200FB"
    elif 90 < pixelValue <= 100:
        return "#DD66FF"
    elif 100 < pixelValue <= 125:
        return "#EBA6FF"
    elif 125 < pixelValue <= 150:
        return "#F9E6FF"
    elif 150 < pixelValue <= 300:
        return "#D4D4D4"
    elif pixelValue > 300:
        return "#000000"
    else:
        return "none"


def color_percent(pixelValue:float) -> str:
    """
    Returns the corresponding color for a given percent value (pixelValue)
    based on predefined ranges.

    Parameters:
    pixelValue (float): The precipitation value to determine the color.

    Returns:
    str: The color in hexadecimal format corresponding to the percent value.
    """
    if pixelValue <= 0:
        return "none"
    if 0 < pixelValue <= 10:
        return "#F9F788"
    elif 10 < pixelValue <= 20:
        return "#D6D309"
    elif 20 < pixelValue <= 30:
        return "#B08C00"
    elif 30 < pixelValue <= 40:
        return "#B6F8A9"
    elif 40 < pixelValue <= 50:
        return "#1DD41C"
    elif 50 < pixelValue <= 60:
        return "#005200"
    elif 60 < pixelValue <= 70:
        return "#359AFF"
    elif 70 < pixelValue <= 80:
        return "#0069D2"
    elif 80 < pixelValue <= 90:
        return "#00367F"
    elif 90 < pixelValue <= 100:
        return "#100053"
    else:
        return "none"



###############################################################################
#                               PLOTS FUNCTIONS                               #
###############################################################################
def plot_ec(raster, cor_factor, ec_gdf, prov_gdf, area_gdf, color_fun, out_path):
    # Abre el raster utilizando rasterio
    with rasterio.open(raster) as src:
        # Realiza el enmascaramiento del raster
        out_image, out_transform  = mask(src, ec_gdf.geometry, crop=True)
        out_image = out_image * cor_factor
    #
    # Crear una lista de valores entre 0 y 1
    mmin = out_image.min()
    mmax = out_image.max()
    rang = int(100 * (mmax - mmin))
    values = np.linspace(int(mmin), int(mmax), rang)
    #
    # Crear un objeto ListedColormap basado en la lista de colores
    colors = [color_fun(value) for value in values]
    cmap_custom = ListedColormap(colors)
    #
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    plt.figure(figsize=(8, 8))
    plt.margins(0)
    ax = plt.gca()
    show(out_image, transform=out_transform, ax=plt.gca(), cmap=cmap_custom)
    prov_gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=0.2)
    ec_gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=1)
    area_gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=2)
    #
    # Formatear y guardar  
    plt.xlim(-81.3, -74.9)
    plt.ylim(-5.2, 1.6)
    ax.tick_params(axis='both', which='major', labelsize=17)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0.2)




def plot_area(raster, cor_factor, ec_gdf, rp_gdf, rs_gdf, puntos_gdf, color_fun, out_path):
    # Abre el raster utilizando rasterio
    with rasterio.open(raster) as src:
        # Realiza el enmascaramiento del raster
        out_image, out_transform  = mask(src, ec_gdf.geometry, crop=True)
        out_image = out_image * cor_factor
    #
    # Crear una lista de valores entre 0 y 1
    mmin = out_image.min()
    mmax = out_image.max()
    rang = int(100 * (mmax - mmin))
    values = np.linspace(int(mmin), int(mmax), rang)
    #
    # Crear un objeto ListedColormap basado en la lista de colores
    colors = [color_fun(value) for value in values]
    cmap_custom = ListedColormap(colors)
    #
    # Crea una figura de Matplotlib y muestra el raster enmascarado
    plt.figure(figsize=(8, 8))
    plt.margins(0)
    ax = plt.gca()
    show(out_image, transform=out_transform, ax=plt.gca(), cmap=cmap_custom)
    puntos_gdf.plot(ax=plt.gca(), color='red', markersize=10, label="Puntos afectados")
    rs_gdf.plot(ax=plt.gca(), color='black', edgecolor='black', linewidth=0.2, label="Rios")
    rp_gdf.plot(ax=plt.gca(), color='black', edgecolor='black', linewidth=1)
    puntos_gdf.plot(ax=plt.gca(), color='red', markersize=10)
    #
    # Formatear y guardar  
    plt.xlim(-78.55, -78.05)
    plt.ylim(-1.5, -1.3)
    ax.tick_params(axis='both', which='major', labelsize=9)
    plt.legend(loc='lower right')
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0.2)


def join_images(img1, img2, name):
    # Cargar las imágenes
    imagen1 = mpimg.imread(img1)
    imagen2 = mpimg.imread(img2)
    # Crear una nueva figura con una cuadrícula personalizada
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={'width_ratios': [1, 2]})
    # Mostrar la primera imagen en la primera subtrama
    ax1.imshow(imagen1)
    ax1.axis('off')
    ax1.set_aspect(aspect='auto')
    # Mostrar la segunda imagen en la segunda subtrama
    ax2.imshow(imagen2)
    ax2.axis('off')
    ax2.set_aspect(aspect='auto')
    # Ajustar el espacio entre las subtramas
    plt.tight_layout()
    # Guardar la figura en un archivo de imagen
    plt.savefig(name)


###############################################################################
def header(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.topMargin)
    content.drawOn(canvas, doc.leftMargin, doc.height + doc.bottomMargin + doc.topMargin - h)
    canvas.restoreState()

def footer(canvas, doc, content):
    canvas.saveState()
    w, h = content.wrap(doc.width, doc.bottomMargin)
    content.drawOn(canvas, doc.leftMargin, h)
    canvas.restoreState()

def header_and_footer(canvas, doc, header_content, footer_content):
    header(canvas, doc, header_content)
    footer(canvas, doc, footer_content)

def get_datetime():
    # Obtener la fecha y hora actual
    now = datetime.now() + timedelta(hours=-5)
    # Mapeo de nombres de meses en inglés a español
    meses_ingles_a_espanol = {
        "January": "enero",
        "February": "febrero",
        "March": "marzo",
        "April": "abril",
        "May": "mayo",
        "June": "junio",
        "July": "julio",
        "August": "agosto",
        "September": "septiembre",
        "October": "octubre",
        "November": "noviembre",
        "December": "diciembre"
    }
    # Formatear la fecha y hora de emisión
    emision = "<b>Hora y fecha de emision:</b> " + now.strftime("%d de %B del %Y, %H:%M")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        emision = emision.replace(mes_ingles, mes_espanol)
    #
    # Formatear dia anterior
    anterior = (now + timedelta(days=-1)).strftime("%d de %B del %Y (07H00)")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        anterior = anterior.replace(mes_ingles, mes_espanol)
    # Formatear dia actual
    actual = (now).strftime("%d de %B del %Y (07H00)")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        actual = actual.replace(mes_ingles, mes_espanol)
    # Formatear dia futuro
    futuro = (now + timedelta(days=1)).strftime("%d de %B del %Y (07H00)")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        futuro = futuro.replace(mes_ingles, mes_espanol)
    #
    # Calcular la vigencia para 24 horas
    inicio_vigencia = now.strftime("desde 07:00 del %d de %B")
    fin_vigencia = (now + timedelta(days=1)).strftime("hasta las 07:00 del %d de %B del %Y")
    for mes_ingles, mes_espanol in meses_ingles_a_espanol.items():
        inicio_vigencia = inicio_vigencia.replace(mes_ingles, mes_espanol)
        fin_vigencia = fin_vigencia.replace(mes_ingles, mes_espanol)
    #
    # Formatear la vigencia
    vigencia = f"<b>Vigencia:</b> {inicio_vigencia} {fin_vigencia}"
    return(emision, vigencia, anterior, actual, futuro)


def agregar_tabla(datos):
    datos_tabla = [datos.columns.tolist()] + datos.values.tolist()
    tabla = Table(datos_tabla)
    tabla.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                               ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                               ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                               ('FONTSIZE', (0, 0), (-1, -1), 7),
                               ('BOTTOMPADDING', (0,0), (-1,0), 2),
                               ('BACKGROUND', (0,1), (-1,-1), colors.white),
                               ('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
    return(tabla)


def report(filename, pacum, forecast, asm, tables):
    # Vars
    header_path = "report_header.png"
    footer_path = "report_footer.png"
    titulo = "<b>Boletín Hidrometeorológico Especial Baños</b>"
    emision, vigencia, anterior, actual, futuro = get_datetime()
    parrafo_1 = "La <b>DIRECCIÓN DE PRONÓSTICOS Y ALERTAS HIDROMETEOROLÓGICAS DEL INAMHI</b>, basándose en la información obtenida de la plataforma INAMHI GEOGLOWS emite el siguiente boletín de vigilancia y predicción de condiciones hidrometeorológicas:"
    subtitulo_1 = "<b>Precipitación acumulada diaria</b>"
    subtitulo_2 = "<b>Pronóstico de precipitación</b>"
    subtitulo_3 = "<b>Humedad del suelo</b>"
    subtitulo_4 = "<b>Pronóstico hidrológico (GEOGLOWS)</b>"
    parrafo_2 = f"De acuerdo con los datos del hidroestimador satelital <b>PERSIANN PDIR Now</b>, en la zona de interés se registró una precipitación media de <b>{pacum} mm</b> entre el <b>{anterior}</b> y el <b>{actual}.</b>"
    parrafo_3 = f"Según los datos del <b>modelo WRF (INAMHI)</b>, se pronostica una precipitación media de <b>{forecast} mm</b> en la zona de interés, entre el <b>{actual}</b> y el <b>{futuro}.</b>"
    parrafo_4 = f"De acuerdo con la plataforma Flash Flood Guidance System <b>(FFGS)</b>, en la zona de interés se registró una humedad media del suelo de <b>{100*asm} %</b> entre el <b>{anterior}</b> y el <b>{actual}.</b>"
    # Configurar estilos
    estilos = getSampleStyleSheet()
    #
    estilo_titulo = ParagraphStyle(
        name = 'Title',
        fontSize = 14,
        textColor = colors.Color(31/255, 73/255, 125/255),
        alignment = TA_CENTER)
    #
    estilo_subtitulo = ParagraphStyle(
        name = 'Subtitle',
        fontSize = 11,
        textColor = colors.Color(31/255, 73/255, 125/255),
        alignment = TA_LEFT,
        spaceAfter = 4)
    #
    estilo_fecha = ParagraphStyle(
        name = 'Dates',
        fontSize = 9,
        alignment = TA_CENTER,
        spaceBefore = 3,
        spaceAfter = 3)
    #
    estilo_parrafo = ParagraphStyle(
        name = 'P01',
        fontSize = 9,
        alignment = TA_CENTER,
        spaceBefore = 5,
        spaceAfter = 5,
        leading = 15)
    #
    estilo_parrafo2 = ParagraphStyle(
        name = 'P02',
        fontSize = 9,
        alignment = TA_JUSTIFY,
        spaceBefore = 5,
        spaceAfter = 5,
        leading = 15)
    #
    # Crear el documento PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    #
    # Definir el encabezado y pie de pagina
    header_content = Image(header_path, width=doc.width, height=2.5*cm)
    footer_content = Image(footer_path, width=doc.width, height=1.5*cm)
    #
    # Agregar elementos al contenido del PDF
    elementos = [
        Paragraph(titulo, estilo_titulo),
        Spacer(1, 12),
        Paragraph(emision, estilo_fecha),
        Paragraph(vigencia, estilo_fecha),
        Spacer(1, 10),
        Paragraph(parrafo_1, estilo_parrafo),
        Spacer(1, 10),
        Paragraph(subtitulo_1, estilo_subtitulo),
        Image("pacum.png", width=doc.width, height=5*cm),
        Image("pacum24.png", width=14*cm, height=0.7*cm),
        Paragraph(parrafo_2, estilo_parrafo2),
        Spacer(1, 20),
        Paragraph(subtitulo_2, estilo_subtitulo),
        Image("forecast.png", width=doc.width, height=5*cm),
        Image("pacum24.png", width=14*cm, height=0.7*cm),
        Paragraph(parrafo_3, estilo_parrafo2),
        ##
        PageBreak(),
        Paragraph(subtitulo_3, estilo_subtitulo),
        Image("asm.png", width=doc.width, height=5*cm),
        Image("soilmoisture_legend.png", width=10*cm, height=1*cm),
        Paragraph(parrafo_4, estilo_parrafo2),
        Spacer(1, 30),
        Paragraph(subtitulo_4, estilo_subtitulo),
        Paragraph("Con base en la información del modelo hidrológico GEOGLOWS, se emite el siguiente pronóstico hidrológico", estilo_parrafo2),
        Paragraph("<b>1. Rio Patate</b>", estilo_parrafo2),
        Image("forecast_9028087.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 1.</b> Caudales pronosticados para el río Patate", estilo_parrafo),
        agregar_tabla(tables[0]),
        ##
        PageBreak(),
        Paragraph("<b>2. Rio Chambo</b>", estilo_parrafo2),
        Image("forecast_9028483.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 2.</b> Caudales pronosticados para el río Chambo", estilo_parrafo),
        agregar_tabla(tables[1]),
        Spacer(1, 20),

        Paragraph("<b>3. Rio Verde Chico</b>", estilo_parrafo2),
        Image("forecast_9028041.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 3.</b> Caudales pronosticados para el río Verde Chico", estilo_parrafo),
        agregar_tabla(tables[2]),
        ##
        PageBreak(),
        Paragraph("<b>4. Rio Verde</b>", estilo_parrafo2),
        Image("forecast_9028088.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 4.</b> Caudales pronosticados para el río Verde", estilo_parrafo),
        agregar_tabla(tables[3]),
        Spacer(1, 20),
        ##
        Paragraph("<b>5. Rio Topo</b>", estilo_parrafo2),
        Image("forecast_9028099.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 5.</b> Caudales pronosticados para el río Topo", estilo_parrafo),
        agregar_tabla(tables[4]),
        ##
        PageBreak(),
        Paragraph("<b>6. Rio Pastaza (tramo 1)</b>", estilo_parrafo2),
        Image("forecast_9028091.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 6.</b> Caudales pronosticados del tramo 1 del río Pastaza", estilo_parrafo),
        agregar_tabla(tables[5]),
        Spacer(1, 20),
        ##
        Paragraph("<b>7. Rio Pastaza (tramo 2)</b>", estilo_parrafo2),
        Image("forecast_9028095.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 7.</b> Caudales pronosticados del tramo 2 del río Pastaza", estilo_parrafo),
        agregar_tabla(tables[6]),
        ##
        PageBreak(),
        Paragraph("<b>8. Rio Pastaza (tramo 3)</b>", estilo_parrafo2),
        Image("forecast_9028125.png", width=doc.width, height=4*cm),
        Image("leyenda.png", width=10*cm, height=1*cm),
        Paragraph("<b>Tabla 8.</b> Caudales pronosticados del tramo 3 del río Pastaza", estilo_parrafo),
        agregar_tabla(tables[5]),
        ]
    #
    # Contruir el pdf
    doc.build(
        elementos, 
        onFirstPage=partial(header_and_footer, header_content=header_content, footer_content=footer_content), 
        onLaterPages=partial(header_and_footer, header_content=header_content, footer_content=footer_content))



###############################################################################
#                                EMAIL ROUTNES                                #
###############################################################################
def send_report(subject, body, attachment_file, sender, password):
    # Users to send email
    recipients = [
        "sala.chimborazo@gestionderiesgos.gob.ec",
        "sala.tungurahua@gestionderiesgos.gob.ec",
        "sala.pastaza@gestionderiesgos.gob.ec",
        "sala.nacional@gestionderiesgos.gob.ec",
        "subsecretario.informacionyanalisis@gestionderiesgos.gob.ec",
        "prediccion@inamhi.gob.ec",
        "jusethchancay@ecociencia.org"]
    #
    # SMTP server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    #
    # Configure the message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = ", ".join(recipients)
    message['Subject'] = subject
    #
    # Attach the email body
    message.attach(MIMEText(body, 'plain'))
    #
    # Attach the PDF file
    attachment = open(attachment_file, 'rb')
    attachment_part = MIMEBase('application', 'octet-stream')
    attachment_part.set_payload((attachment).read())
    encoders.encode_base64(attachment_part)
    attachment_part.add_header('Content-Disposition', "attachment; filename= %s" % attachment_file)
    message.attach(attachment_part)
    #
    # Connect to the SMTP server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipients, message.as_string())
    server.quit()


def send_error(error, sender, password):
    # Users to send email
    recipients = [ "prediccion@inamhi.gob.ec", "jusethchancay@ecociencia.org"]
    #
    # SMTP server
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    #
    # Configure the message
    message = MIMEMultipart()
    message['From'] = sender
    message['To'] = ", ".join(recipients)
    message['Subject'] = "Error en el envío de reporte automático a SGR"
    #
    # Attach the email body
    body = f"Existió un error en el envío del reporte automático a SGR\n {error} \n\nPonerse en contacto con Juseth, lo antes posible...\nSaludos coordiales,\nINAMHI GEOGLOWS"
    message.attach(MIMEText(body, 'plain'))
    #
    # Connect to the SMTP server and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipients, message.as_string())
    server.quit()



###############################################################################
#                                MAIN ROUTINE                                 #
###############################################################################

# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("inamhi-geoglows")

# Load enviromental variables - credentials
load_dotenv()
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASS = os.getenv('MAIL_PASS')
DB_USER = os.getenv('POSTGRES_USER')
DB_PASS = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_PORT = os.getenv('POSTGRES_PORT')

# Generate the conection token
token = "postgresql+psycopg2://{0}:{1}@localhost:{2}/{3}"
token = token.format(DB_USER, DB_PASS, DB_PORT, DB_NAME)
db = create_engine(token)
conn = db.connect()

# Read SHP files
assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/sgr/assets"
ec = gpd.read_file(f"{assets_path}/ecuador_diss.shp")
prov = gpd.read_file(f"{assets_path}/ecuador.shp")
area = gpd.read_file(f"{assets_path}/area_afectada.shp")
drainage = gpd.read_file(f"{assets_path}/drainage.shp")
rios_principales = gpd.read_file(f"{assets_path}/rios_principales_banos.shp")
rios_secundarios = gpd.read_file(f"{assets_path}/rios_secundarios_banos.shp")
puntos_afectados = gpd.read_file(f"{assets_path}/puntos_afectados.shp")


# Change the work directory
os.chdir(user_dir)
os.chdir("data/sgr")

try:
    # Datos satelitales
    url = "/home/ubuntu/data/fireforest/persiann1d.tif"
    os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} pacum.tif")
    plot_ec("pacum.tif", 1, ec, prov, area, color_pacum, "pacum_ecuador.png")
    plot_area("pacum.tif", 1, ec, rios_principales, rios_secundarios, puntos_afectados, color_pacum, "pacum_area.png")
    join_images("pacum_ecuador.png", "pacum_area.png", "pacum.png")
    pacum_satellite = get_value("pacum.tif", area, "id").pacum[0]
    os.remove("pacum.tif")
    os.remove("pacum_ecuador.png")
    os.remove("pacum_area.png")

    # Pronóstico
    now = dt.datetime.now()
    datestr = now.strftime("%Y-%m-%d00Z-24H-%Y%m%d07h00")
    url = f"/usr/share/geoserver/data_dir/data/wrf-precipitation/{datestr}/{datestr}.geotiff"
    os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} forecast.tif")
    plot_ec("forecast.tif", 1, ec, prov, area, color_pacum, "forecast_ecuador.png")
    plot_area("forecast.tif", 1, ec, rios_principales, rios_secundarios, puntos_afectados, color_pacum, "forecast_area.png")
    join_images("forecast_ecuador.png", "forecast_area.png", "forecast.png")
    pacum_wrf = get_value("forecast.tif", area, "id").pacum[0]
    os.remove("forecast.tif")
    os.remove("forecast_ecuador.png")
    os.remove("forecast_area.png")

    # Humedad del suelo
    url = "/home/ubuntu/data/fireforest/soilmoisture.tif"
    os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} asm.tif")
    plot_ec("asm.tif", 100, ec, prov, area, color_percent, "asm_ecuador.png")
    plot_area("asm.tif", 100, ec, rios_principales, rios_secundarios, puntos_afectados, color_percent, "asm_area.png")
    join_images("asm_ecuador.png", "asm_area.png", "asm.png")
    asm_value = get_value("asm.tif", area, "id").pacum[0]
    os.remove("asm.tif")
    os.remove("asm_ecuador.png")
    os.remove("asm_area.png")

    # Hydrological forecasting
    t9028087 = geoglows_plot(9028087, conn, "9028087.png")
    join_images("loc/9028087.png", "9028087.png", "forecast_9028087.png")
    os.remove("9028087.png")

    t9028483 = geoglows_plot(9028483, conn, "9028483.png")
    join_images("loc/9028483.png", "9028483.png", "forecast_9028483.png")
    os.remove("9028483.png")

    t9028041 = geoglows_plot(9028041, conn, "9028041.png")
    join_images("loc/9028041.png", "9028041.png", "forecast_9028041.png")
    os.remove("9028041.png")

    t9028088 = geoglows_plot(9028088, conn, "9028088.png")
    join_images("loc/9028088.png", "9028088.png", "forecast_9028088.png")
    os.remove("9028088.png")

    t9028099 = geoglows_plot(9028099, conn, "9028099.png")
    join_images("loc/9028099.png", "9028099.png", "forecast_9028099.png")
    os.remove("9028099.png")

    t9028091 = geoglows_plot(9028091, conn, "9028091.png")
    join_images("loc/9028091.png", "9028091.png", "forecast_9028091.png")
    os.remove("9028091.png")

    t9028095 = geoglows_plot(9028095, conn, "9028095.png")
    join_images("loc/9028095.png", "9028095.png", "forecast_9028095.png")
    os.remove("9028095.png")

    t9028125 = geoglows_plot(9028125, conn, "9028125.png")
    join_images("loc/9028125.png", "9028125.png", "forecast_9028125.png")
    os.remove("9028125.png")

    tables = [t9028087, t9028483, t9028041, t9028088, t9028099, t9028091, t9028095, t9028125]

    #Email
    nowstr = now.strftime("%Y-%m-%d")
    report(filename=f"reporte-{nowstr}.pdf", pacum=pacum_satellite, forecast=pacum_wrf, asm=asm_value, tables=tables)
    subject = f"PRUEBA: Boletín Hidrometeorológico Especial Baños: {nowstr}"
    body = "ESTO ES UNA PRUEBA DE FUNCIONAMIENTO NO RESPONDA A ESTE CORREO: \nLa DIRECCIÓN DE PRONÓSTICOS Y ALERTAS HIDROMETEOROLÓGICAS DEL INAMHI, basándose en la información obtenida de la plataforma INAMHI GEOGLOWS emite el siguiente boletín de vigilancia y predicción de condiciones hidrometeorológicas."
    send_report(subject=subject, body=body, attachment_file=f"reporte-{nowstr}.pdf",sender=MAIL_USER, password=MAIL_PASS)
except Exception as e:
    send_error(e,sender=MAIL_USER, password=MAIL_PASS)
