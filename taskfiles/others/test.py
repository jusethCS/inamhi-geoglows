import requests
import pandas as pd
from datetime import datetime, timedelta

def download_firms_data(region='global', date_range='24h', save_path='firms_data.csv'):
    """
    Descarga datos de focos de calor de FIRMS de la NASA.

    Parámetros:
    region (str): La región de interés ('global', 'usa', 'canada', 'southamerica', 'africa', 'europe', 'asia', 'australia', 'centralamerica').
    date_range (str): Rango de fechas ('24h', '48h', '7d', '10d', 'month').
    save_path (str): Ruta donde se guardará el archivo CSV descargado.
    """
    base_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/"
    params = {
        'region': region,
        'period': date_range
    }
    # Solicitud de los datos
    response = requests.get(base_url, params=params)
    # Verificación del éxito de la solicitud
    if response.status_code == 200:
        with open(save_path, 'w') as f:
            f.write(response.text)
        print(f"Datos guardados en {save_path}")
    else:
        print(f"Error en la solicitud: {response.status_code}")

# Uso de la función
download_firms_data()
