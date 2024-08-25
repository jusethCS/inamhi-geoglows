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
import geoglows

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
    #
    # Initialize an empty DataFrame to store the results
    resultados = pd.DataFrame(columns=['subbasin', 'pacum'])
    #
    # Open the raster file
    with rasterio.open(raster_file) as src:
        # Reproject the shp to match the raster's coordinate reference system
        cuencas = cuencas.to_crs(src.crs)
        #
        # Read the raster values that intersect with the sub-basin geometries
        resultados_list = []
        for index, row in cuencas.iterrows():
            geom = row.geometry
            #
            # Mask the raster based on the sub-basin geometry
            out_image, out_transform = mask(src, [geom], crop=True)
            out_image[out_image < 0] = 0
            #
            # Calculate the average precipitation value within the sub-basin
            avg_precipitation = round(np.nanmean(out_image), 2)
            #
            # Append the results to the list
            resultados_list.append(
                {'subbasin': f"Rio {row[field]}", 'pacum': avg_precipitation}
            )
        #
        # Convert the list to a DataFrame and append it to the results
        resultados = pd.concat(
            [resultados, pd.DataFrame(resultados_list)], 
            ignore_index=True
        )
    #
    return resultados



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
    plt.title("Ecuador Continental", fontsize=18)
    #ax.tick_params(axis='both', which='major', labelsize=17)
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0.2)


def plot_area(raster, ec_gdf, paute_gdf, rp_gdf, rs_gdf, embalses_gdf, cor_factor, color_fun, out_path):
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
    show(out_image, transform=out_transform, ax=plt.gca(), cmap=cmap_custom)
    embalses_gdf.plot(ax=plt.gca(), color='red', markersize=50, label="Embalses")
    rs_gdf.plot(ax=plt.gca(), color='black', edgecolor='black', linewidth=0.2, label="Rios")
    rp_gdf.plot(ax=plt.gca(), color='black', edgecolor='black', linewidth=1)
    paute_gdf.plot(ax=plt.gca(), color='none', edgecolor='black', linewidth=2)
    embalses_gdf.plot(ax=plt.gca(), color='red', markersize=50)
    #
    # Establecer límites en los ejes x e y   
    plt.xlim(-79.4, -78.2)
    plt.ylim(-3.3, -2.25)
    plt.title("Cuenca del río Paute", fontsize=18)
    plt.legend(loc='lower right')
    plt.savefig(out_path, bbox_inches='tight', pad_inches=0.2)



def join_images(img1, img2, name):
    # Cargar las imágenes
    imagen1 = mpimg.imread(img1)
    imagen2 = mpimg.imread(img2)
    # Crear una nueva figura con una cuadrícula personalizada
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [1, 1]})
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
#                        PLOTTING FUNCTIONS GEOGLOWS                          #
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

def get_bias_corrected_data(sim, obs):
    outdf = geoglows.bias.correct_historical(sim, obs)
    outdf.index = pd.to_datetime(outdf.index)
    outdf.index = outdf.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    outdf.index = pd.to_datetime(outdf.index)
    return(outdf)


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

def get_corrected_forecast(simulated_df, ensemble_df, observed_df):
    monthly_simulated = simulated_df[simulated_df.index.month == (ensemble_df.index[0]).month].dropna()
    monthly_observed = observed_df[observed_df.index.month == (ensemble_df.index[0]).month].dropna()
    min_simulated = np.min(monthly_simulated.iloc[:, 0].to_list())
    max_simulated = np.max(monthly_simulated.iloc[:, 0].to_list())
    min_factor_df = ensemble_df.copy()
    max_factor_df = ensemble_df.copy()
    forecast_ens_df = ensemble_df.copy()
    for column in ensemble_df.columns:
      tmp = ensemble_df[column].dropna().to_frame()
      min_factor = tmp.copy()
      max_factor = tmp.copy()
      min_factor.loc[min_factor[column] >= min_simulated, column] = 1
      min_index_value = min_factor[min_factor[column] != 1].index.tolist()
      for element in min_index_value:
        min_factor[column].loc[min_factor.index == element] = tmp[column].loc[tmp.index == element] / min_simulated
      max_factor.loc[max_factor[column] <= max_simulated, column] = 1
      max_index_value = max_factor[max_factor[column] != 1].index.tolist()
      for element in max_index_value:
        max_factor[column].loc[max_factor.index == element] = tmp[column].loc[tmp.index == element] / max_simulated
      tmp.loc[tmp[column] <= min_simulated, column] = min_simulated
      tmp.loc[tmp[column] >= max_simulated, column] = max_simulated
      forecast_ens_df.update(pd.DataFrame(tmp[column].values, index=tmp.index, columns=[column]))
      min_factor_df.update(pd.DataFrame(min_factor[column].values, index=min_factor.index, columns=[column]))
      max_factor_df.update(pd.DataFrame(max_factor[column].values, index=max_factor.index, columns=[column]))
    corrected_ensembles = geoglows.bias.correct_forecast(forecast_ens_df, simulated_df, observed_df)
    corrected_ensembles = corrected_ensembles.multiply(min_factor_df, axis=0)
    corrected_ensembles = corrected_ensembles.multiply(max_factor_df, axis=0)
    return(corrected_ensembles)


def get_corrected_forecast_records(records_df, simulated_df, observed_df):
    date_ini = records_df.index[0]
    month_ini = date_ini.month
    date_end = records_df.index[-1]
    month_end = date_end.month
    meses = np.arange(month_ini, month_end + 1, 1)
    fixed_records = []
    for mes in meses:
        values = records_df.loc[records_df.index.month == mes]
        monthly_simulated = simulated_df[simulated_df.index.month == mes].dropna()
        monthly_observed = observed_df[observed_df.index.month == mes].dropna()
        min_simulated = np.min(monthly_simulated.iloc[:, 0].to_list())
        max_simulated = np.max(monthly_simulated.iloc[:, 0].to_list())
        min_factor_records_df = values.copy()
        max_factor_records_df = values.copy()
        fixed_records_df = values.copy()
        column_records = values.columns[0]
        tmp = records_df[column_records].dropna().to_frame()
        min_factor = tmp.copy()
        max_factor = tmp.copy()
        min_factor.loc[min_factor[column_records] >= min_simulated, column_records] = 1
        min_index_value = min_factor[min_factor[column_records] != 1].index.tolist()
        for element in min_index_value:
            min_factor[column_records].loc[min_factor.index == element] = tmp[column_records].loc[tmp.index == element] / min_simulated
        max_factor.loc[max_factor[column_records] <= max_simulated, column_records] = 1
        max_index_value = max_factor[max_factor[column_records] != 1].index.tolist()
        for element in max_index_value:
            max_factor[column_records].loc[max_factor.index == element] = tmp[column_records].loc[tmp.index == element] / max_simulated
        tmp.loc[tmp[column_records] <= min_simulated, column_records] = min_simulated
        tmp.loc[tmp[column_records] >= max_simulated, column_records] = max_simulated
        fixed_records_df.update(pd.DataFrame(tmp[column_records].values, index=tmp.index, columns=[column_records]))
        min_factor_records_df.update(pd.DataFrame(min_factor[column_records].values, index=min_factor.index, columns=[column_records]))
        max_factor_records_df.update(pd.DataFrame(max_factor[column_records].values, index=max_factor.index, columns=[column_records]))
        corrected_values = geoglows.bias.correct_forecast(fixed_records_df, simulated_df, observed_df)
        corrected_values = corrected_values.multiply(min_factor_records_df, axis=0)
        corrected_values = corrected_values.multiply(max_factor_records_df, axis=0)
        fixed_records.append(corrected_values)
    fixed_records = pd.concat(fixed_records)
    fixed_records.sort_index(inplace=True)
    return fixed_records



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


def forecast_geoglows_plot(stats, rperiods, comid, records, sim, titulo):
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
        title=titulo,
        yaxis={'title': 'Caudal (m<sup>3</sup>/s)', 'range': [0, 'auto']},
        xaxis={'title': 'Fecha (UTC +0:00)', 'range': [startdate, enddate], 'hoverformat': '%b %d %Y %H:%M',
               'tickformat': '%b %d %Y'},
    )
    figure = go.Figure(scatter_plots, layout=layout)
    figure.update_layout(template='simple_white', width=1000, height=400, showlegend=True)
    figure.update_yaxes(linecolor='gray', mirror=True, showline=True) 
    figure.update_xaxes(linecolor='gray', mirror=True, showline=True)
    figure.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    return figure.to_dict()


def geoglows_plot(comid, conn, outpath, titulo):
    now = dt.datetime.now() - dt.timedelta(days=1)
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
        sim = simulated_data,
        titulo=titulo)
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


def corrected_geoglows_plot(comid, obs_path, conn, outpath, titulo):
    now = dt.datetime.now() - dt.timedelta(days=1)
    date = now.strftime("%Y-%m-%d")
    #
    # Observed data
    observed_data = pd.read_csv(obs_path, sep="\t", header=0)
    observed_data.index = observed_data.datetime
    observed_data = observed_data.drop(columns=['datetime'])
    observed_data.index = pd.to_datetime(observed_data.index)
    observed_data.index = observed_data.index.to_series().dt.strftime("%Y-%m-%d %H:%M:%S")
    observed_data.index = pd.to_datetime(observed_data.index)
    #
    # Simulated data and bias correction
    simulated_data = get_format_data(f"SELECT datetime,value FROM historical_simulation where comid={comid}", conn)
    corrected_data = get_bias_corrected_data(simulated_data, observed_data)
    #
    # Raw forecast
    ensemble_forecast = get_format_data(f"SELECT * FROM ensemble_forecast WHERE initialized='{date}' AND comid={comid}", conn).drop(columns=['comid', "initialized"])
    forecast_records = get_format_data(f"SELECT datetime,value FROM forecast_records where comid={comid}", conn)
    #
    # Corrected forecast
    corrected_ensemble_forecast = get_corrected_forecast(simulated_data, ensemble_forecast, observed_data)
    corrected_forecast_records = get_corrected_forecast_records(forecast_records, simulated_data, observed_data)
    corrected_return_periods = get_return_periods(comid, corrected_data)
    #
    # Ensemble stats and forecast plot
    corrected_ensemble_stats = get_ensemble_stats(corrected_ensemble_forecast).dropna()
    forecast_plot = forecast_geoglows_plot(
        stats = corrected_ensemble_stats,
        rperiods = corrected_return_periods,
        comid = comid,
        records = corrected_forecast_records,
        sim = observed_data,
        titulo=titulo)
    pio.write_image(forecast_plot, outpath)
    #
    daily_avg = corrected_ensemble_stats.resample('D').mean().round(2)
    daily_avg.index = pd.to_datetime(daily_avg.index)
    daily_avg.index = daily_avg.index.to_series().dt.strftime("%d/%m")
    daily_avg = daily_avg[['flow_avg', "high_res"]]
    daily_avg = daily_avg.rename(columns={  'flow_avg': 'Caudal medio (m3/s)', 
                                            "high_res": "Alta resolución (m3/s)"})
    daily_avg = daily_avg.dropna().T.reset_index()
    daily_avg = daily_avg.rename(columns={"index": "Día/Mes"})
    return(daily_avg)






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
assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/celec/assets"
paute = gpd.read_file(f"{assets_path}/paute.shp")
prov = gpd.read_file(f"{assets_path}/ecuador.shp")
ec = gpd.read_file(f"{assets_path}/ecuador_diss.shp")
rp = gpd.read_file(f"{assets_path}/rios_principales.shp")
rs = gpd.read_file(f"{assets_path}/rios_secundarios.shp")
embalses = gpd.read_file(f"{assets_path}/embalses.shp")
subcuencas = gpd.read_file(f"{assets_path}/paute_subcuencas_2.shp")

# Change the work directory
os.chdir(user_dir)
os.chdir("data/celec")

# Datos satelitales
url = "/home/ubuntu/data/fireforest/persiann1d.tif"
os.system(f"gdalwarp -tr 0.01 0.01 -r bilinear {url} pacum.tif")
plot_ec("pacum.tif", 1, ec, prov, paute, color_pacum, "pacum_ecuador.png")
plot_area("pacum.tif", paute, paute, rp, rs, embalses, 1, color_pacum, "pacum_paute.png")
join_images("pacum_ecuador.png", "pacum_paute.png", "pacum.png")
os.remove("pacum_ecuador.png")
os.remove("pacum_paute.png")

#Compute precipitation values
pacum_subbasins = get_value("pacum.tif", subcuencas, "SC")
pacum_subbasins = pacum_subbasins.reindex([0,2,1,3,4])
pacum_subbasins = pacum_subbasins.rename(
    columns={
        'subbasin': 'Subcuenca', 
        'pacum': 'Precipitación media diaria (mm)'
    })
pacum_basin = get_value("pacum.tif", paute, "Subcuenca")
os.remove("pacum.tif")

# Create geoglows forecast plot
paute_table = geoglows_plot(9033441, conn, "paute.png", "Pronóstico corregido de caudales del Rio Paute")
cuenca_table = corrected_geoglows_plot(9033449, f"{assets_path}/data-pte-europa.dat", conn, "cuenca.png",  "Pronóstico corregido de caudales del Rio Cuenca (Pte. Europa)")
gualaceo_table = corrected_geoglows_plot(9033577, f"{assets_path}/data-sta-barbara.dat", conn, "gualaceo.png", "Pronóstico corregido de caudales del Rio Gualaceo (Sta. Barbara)")
mazar_table = geoglows_plot(9032447, conn, "mazar.png", "Pronóstico de caudales del Rio Mazar")
juval_table = geoglows_plot(9032294, conn, "juval.png", "Pronóstico de caudales del Rio Juval")
palmira_table = geoglows_plot(9032324, conn, "palmira.png", "Pronóstico de caudales del Rio Palmira")


