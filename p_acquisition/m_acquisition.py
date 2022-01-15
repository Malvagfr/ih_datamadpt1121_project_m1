#Importing libraries
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests

#Bicimad information (comming from a csv stored in data folder)

#Importing bicimad dataset from a csv
bicimad_stations=pd.read_csv('../data/bicimad_stations.csv')

#Taking only the intersting columns needed for the project:
bicimad_stations=bicimad_stations[["address","geometry_coordinates","name","dock_bikes"]]

#Interesting Points (comming from a URL)
#Defining public url for accesing to the datasets and take information using response
url_interest_points = 'https://datos.madrid.es/egob/catalogo/300356-0-monumentos-ciudad-madrid.json'
response_interest_points = requests.get(url_interest_points)
response_interest_points=response.json()['@graph']

#Converting json to pandas dataframe:
interest_points = pd.json_normalize(response_interest_points)
interest_points=interest_points[["title","address.street-address","location.latitude","location.longitude"]]
interest_points = interest_points.rename(columns={'title': 'Place of interest', 'address.street-address': 'Place address','location.latitude': 'lat_start','location.longitude': 'long_start'})