#Importing libraries
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
import argparse

if __name__ == "__main__":
     #Importing function for calculating geo distance
     from shapely.geometry import Point
     import geopandas as gpd   # conda install -c conda-forge geopandas
     
     def to_mercator(lat, long):
        # transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
        c = gpd.GeoSeries([Point(lat, long)], crs=4326)
        c = c.to_crs(3857)
        return c
        
     def distance_meters(lat_start, long_start, lat_finish, long_finish):
        # return the distance in metres between to latitude/longitude pair point in degrees (i.e.: 40.392436 / -3.6994487)
        start = to_mercator(lat_start, long_start)
        finish = to_mercator(lat_finish, long_finish)
        return start.distance(finish)

     def distance_meters_from_mercator(start, finish):
        # return the distance in metres between to latitude/longitude pair point in degrees (i.e.: 40.392436 / -3.6994487)
        return start.distance(finish)

     #EXTRACTING RAW DATA AND CALCULATING COORDINATES - Bicimad
     bicimad_stations=pd.read_csv('./data/bicimad_stations.csv')
     bicimad_stations=bicimad_stations[["address","geometry_coordinates","name","dock_bikes"]]
     #Calculating coordinates
     bicimad_stations[["long_finish","lat_finish"]]=bicimad_stations['geometry_coordinates'].str.split(',', 1, expand=True)
     bicimad_stations["lat_finish"]=bicimad_stations["lat_finish"].str.replace("]","", regex=True)
     bicimad_stations["long_finish"]=bicimad_stations["long_finish"].str.replace("[","", regex=True)

     bicimad_stations = bicimad_stations.rename(columns={'address': 'Station location', 'name': 'BiciMAD station'})
     bicimad_stations = bicimad_stations.drop(columns='geometry_coordinates')

     bicimad_stations[["long_finish", "lat_finish"]] = bicimad_stations[["long_finish","lat_finish"]].apply(pd.to_numeric)

     coordinates_bicimad=bicimad_stations.apply(lambda x: to_mercator(x['lat_finish'],x['long_finish']), axis=1)
     bicimad_stations["coordinates_bicimad"]=coordinates_bicimad
     bicimad_stations.drop(['long_finish','lat_finish'], axis=1, inplace=True)
     bicimad_stations.to_csv('./data/bicimad_stations.csv')

     #EXTRACTING RAW DATA AND CALCULATING COORDINATES - Interesting Points
     url_interest_points = 'https://datos.madrid.es/egob/catalogo/300356-0-monumentos-ciudad-madrid.json'
     response_interest_points = requests.get(url_interest_points)
     response_interest_points=response_interest_points.json()['@graph']

     interest_points = pd.json_normalize(response_interest_points)
     interest_points=interest_points[["title","address.street-address","location.latitude","location.longitude"]]
     interest_points = interest_points.rename(columns={'title': 'Place of interest', 'address.street-address': 'Place address','location.latitude': 'lat_start','location.longitude': 'long_start'})
     interest_points["Type of place"] = "Monumentos de la ciudad de Madrid" 

     interest_points[["long_start", "lat_start"]] = interest_points[["long_start", "lat_start"]].apply(pd.to_numeric)
     coordinates_interest_points=interest_points.apply(lambda x: to_mercator(x['lat_start'],x['long_start']), axis=1)
     interest_points["coordinates_interest_points"]=coordinates_interest_points
     interest_points.drop(['long_start','lat_start'], axis=1, inplace=True)
     interest_points.to_csv('./data/interest_points.csv')

     #JOINING DATA
     interest_points_bicimad = bicimad_stations.assign(key=0).merge(interest_points.assign(key=0), how='left', on = 'key')
     interest_points_bicimad.drop('key', axis=1, inplace=True)
     interest_points_bicimad.to_csv('./data/interest_points_bicimad.csv')

     #CALCULATING DISTANCE
     distance=interest_points_bicimad.apply(lambda x: distance_meters_from_mercator(x['coordinates_interest_points'],x['coordinates_bicimad']), axis=1)
     interest_points_bicimad["distance"]=distance
     interest_points_bicimad.drop(['coordinates_bicimad','coordinates_interest_points'], axis=1, inplace=True)

     #FILTERING BY THE MINIMUN DISTANCT
     interest_points_bicimad_min=interest_points_bicimad.groupby(['Place of interest'])['distance'].min()
     interest_points_bicimad_min = pd.DataFrame(interest_points_bicimad_min)
     nearest_BiciMAD_station=interest_points_bicimad.merge(interest_points_bicimad_min, how='inner', on = ['Place of interest','distance'])

     #SAVING CSV
     nearest_BiciMAD_station.to_csv('./data/nearest_BiciMAD_station.csv')




