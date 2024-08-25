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