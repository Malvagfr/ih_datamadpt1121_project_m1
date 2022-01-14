#importing modules
#from p_acquisition import m_acquisition as a

#Importing libraries
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


if __name__ == "__main__":
    #imported_df = a.acquisition('../../../../datasets/data/vehicles.csv')

    #Importing function
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

    #Extracting raw data

    #bicimad
    bicimad_stations=pd.read_csv('../data/bicimad_stations.csv')

    bicimad_stations=bicimad_stations[["address","geometry_coordinates","name"]]
    bicimad_stations[["long_finish","lat_finish"]]=bicimad_stations['geometry_coordinates'].str.split(',', 1, expand=True)
    bicimad_stations["lat_finish"]=bicimad_stations["lat_finish"].str.replace("]","", regex=True)
    bicimad_stations["long_finish"]=bicimad_stations["long_finish"].str.replace("[","", regex=True)
    bicimad_stations = bicimad_stations.rename(columns={'address': 'Station location', 'name': 'BiciMAD station'})
    bicimad_stations = bicimad_stations.drop(columns='geometry_coordinates')

    #Interesting Points
    interest_points=pd.read_csv('../data/300356-0-monumentos-ciudad-madrid.csv', sep=';',encoding = "ISO-8859-1")

    interest_points=interest_points[["NOMBRE","NOMBRE-VIA","CLASE-VIAL","NUM","LATITUD","LONGITUD"]]
    interest_points = interest_points.rename(columns={'NOMBRE': 'Place of interest', 'NOMBRE-VIA': 'Place address Name', 'CLASE-VIAL': 'Place address Class','NUM': 'Place address Num','LATITUD': 'lat_start','LONGITUD': 'long_start'})
    interest_points["Type of place"] = "Monumentos de la ciudad de Madrid" 

    #Joining Data
    interest_points_bicimad = bicimad_stations.assign(key=0).merge(interest_points.assign(key=0), how='left', on = 'key')

    interest_points_bicimad[["long_finish", "lat_finish","lat_start","long_start"]] = interest_points_bicimad[["long_finish", "lat_finish","lat_start","long_start"]].apply(pd.to_numeric)

    interest_points_test= interest_points_bicimad[(interest_points_bicimad["Place of interest"]=="A las víctimas del Holocausto")]

    distance=interest_points_test.apply(lambda x: distance_meters(x['lat_start'], x['long_start'],x['lat_finish'], x['long_finish']), axis=1)

    interest_points_test["distance"]=distance

    print(interest_points_test)