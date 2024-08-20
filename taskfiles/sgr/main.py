import os
import numpy as np
import geopandas as gpd
from dotenv import load_dotenv
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


# Raster handling and geospatial operations
import rasterio
from rasterio.mask import mask
from rasterio.plot import show

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
def plot_ec(raster, ec_gdf, prov_gdf, area_gdf, color_fun):
    # Abre el raster utilizando rasterio
    with rasterio.open(raster) as src:
        # Realiza el enmascaramiento del raster
        out_image, out_transform  = mask(src, ec_gdf.geometry, crop=True)
    #
    # Crear una lista de valores entre 0 y 1
    mmin = out_image.min()
    mmax = out_image.max()
    rang = int(100 * (mmax - mmin))
    values = np.linspace(int(mmin), int(mmax), rang)
    #
    # Crear una lista de colores utilizando la función color
    colors = [color_fun(value) for value in values]
    #
    # Crear un objeto ListedColormap basado en la lista de colores
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
    # Establecer límites en los ejes x e y   
    plt.xlim(-81.3, -74.9)
    plt.ylim(-5.2, 1.6)
    #
    # Ajustar el tamaño de los números de los ejes
    ax.tick_params(axis='both', which='major', labelsize=17)
    #
    # Añadir un título a la figura
    #plt.title("Ecuador Continental", fontsize=22)
    #
    # Save the figure
    plt.savefig("ecuador.png", bbox_inches='tight', pad_inches=0.2)



# Change the work directory
user = os.getlogin()
user_dir = os.path.expanduser('~{}'.format(user))
os.chdir(user_dir)
os.chdir("inamhi-geoglows")

# Load enviromental variables - credentials
load_dotenv()
MAIL_USER = os.getenv('MAIL_USER')
MAIL_PASS = os.getenv('MAIL_PASS')

# Read SHP files
assets_path = "/home/ubuntu/inamhi-geoglows/taskfiles/sgr/assets"
ec = gpd.read_file(f"{assets_path}/ecuador_diss.shp")
prov = gpd.read_file(f"{assets_path}/ecuador.shp")
area = gpd.read_file(f"{assets_path}/area_afectada.shp")
drainage = gpd.read_file(f"{assets_path}/drainage.shp")
rios_principales = gpd.read_file(f"{assets_path}/rios_principales_banos.shp")
rios_secundarios = gpd.read_file(f"{assets_path}/rios_secundarios_banos.shp")
puntos_afectados = gpd.read_file(f"{assets_path}/puntos_afectados.shp")


# Datos satelitales
url = "https://inamhi.geoglows.org/fireforest/daily_precipitation/daily_precipitation.geotiff"
os.system(f"wget {url} -O pacum.tif")
os.system("gdalwarp -tr 0.01 0.01 -r bilinear pacum.tif pacumres.tif")

#plot.pacum_ec(raster="pacumres.tif", ec_gdf=ec, prov_gdf=prov, paute_gdf=area)
#plot.pacum_area(raster="pacumres.tif", ec_gdf=ec, rp_gdf=rios_principales, rs_gdf=rios_secundarios, puntos_gdf=puntos_afectados)
#plot.join_images("ecuador.png", "area.png", "pacum_sat.png")
#pacum_satellite = plot.get_pacum_subbasin("pacumres.tif", area, "id").pacum[0]
