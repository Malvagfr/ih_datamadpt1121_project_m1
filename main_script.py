##############################################################################
#                                                                            #                       
#   argparse — Parser for command-line options, arguments and sub-commands   #     
#                                                                            #
#   Ironhack Data Part Time --> Nov-2021                                     #
#                                                                            #
##############################################################################


# import libraries

#general 
import pandas as pd

#calculate geo distance
import geopandas as gpd
from shapely.geometry import Point

#import data from URL
import requests

#allow users to select multiple functionalities
import argparse

#allowing users to input interest points with flexibility 
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#for nice displaying
from tabulate import tabulate


# Script functions - calculate distance

# transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
def to_mercator(lat, long):  
    c = gpd.GeoSeries([Point(lat, long)], crs=4326)
    c = c.to_crs(3857)
    return c

# return the distance in metres between to latitude/longitude pair point in degrees (i.e.: 40.392436 / -3.6994487)
def distance_meters(start, finish):
    return start.distance(finish)
 




# Script functions - cañculates different dataframes

#return nearest_BiciMAD_station dataframe with the nearest BiciMAD station to a set of places of interest
def nearest_station_all_places():

    #Extracting raw data - Bicimad (comming from a csv)
    bicimad_stations=pd.read_csv('./data/bicimad_stations.csv')
    #Taking only the intersting columns needed for the project and filtering the data  
    bicimad_stations=bicimad_stations[["address","geometry_coordinates","name","dock_bikes"]]

    #Filtering out rows without geometry_coordinates:
    bicimad_stations=bicimad_stations[bicimad_stations.geometry_coordinates.notnull()]

    #Calculating coordinates
    bicimad_stations[["long_finish","lat_finish"]]=bicimad_stations['geometry_coordinates'].str.split(',', 1, expand=True)
    bicimad_stations["lat_finish"]=bicimad_stations["lat_finish"].str.replace("]","", regex=True)
    bicimad_stations["long_finish"]=bicimad_stations["long_finish"].str.replace("[","", regex=True)

    #Renaming field names
    bicimad_stations = bicimad_stations.rename(columns={'address': 'Station location', 'name': 'BiciMAD station'})

    #Deleting not needed columns
    bicimad_stations = bicimad_stations.drop(columns='geometry_coordinates')

    #Calculating coordenades
    bicimad_stations[["long_finish", "lat_finish"]] = bicimad_stations[["long_finish","lat_finish"]].apply(pd.to_numeric)

    coordinates_bicimad=bicimad_stations.apply(lambda x: to_mercator(x['lat_finish'],x['long_finish']), axis=1)
    bicimad_stations["coordinates_bicimad"]=coordinates_bicimad

    #Deleting not needed columns
    bicimad_stations.drop(['long_finish','lat_finish'], axis=1, inplace=True)

    #Storing dataframe
    bicimad_stations.to_csv('./data/bicimad_stations_clean.csv')

    #Extracting raw data - Interesting Points

    #Defining public url for accesing to the datasets
    url_interest_points = 'https://datos.madrid.es/egob/catalogo/300356-0-monumentos-ciudad-madrid.json'
    #Taking url information with requests
    response_interest_points = requests.get(url_interest_points)
    response_interest_points=response_interest_points.json()['@graph']

    #Converting json to pandas dataframe and taking only needed fields
    interest_points = pd.json_normalize(response_interest_points)
    interest_points=interest_points[["title","address.street-address","location.latitude","location.longitude"]]
    #Saving CSV
    interest_points.to_csv('./data/interest_points.csv')

    #Renaming and adding columns needed
    interest_points = interest_points.rename(columns={'title': 'Place of interest', 'address.street-address': 'Place address','location.latitude': 'lat_start','location.longitude': 'long_start'})
    interest_points["Type of place"] = "Monumentos de la ciudad de Madrid" 
    
    #Cleaning the dataframe (excluding rows without latitude or longitude information)
    interest_points=interest_points[interest_points.lat_start.notnull()]
    interest_points=interest_points[interest_points.long_start.notnull()]

    #Calculating coordinades
    interest_points[["long_start", "lat_start"]] = interest_points[["long_start", "lat_start"]].apply(pd.to_numeric)
    coordinates_interest_points=interest_points.apply(lambda x: to_mercator(x['lat_start'],x['long_start']), axis=1)
    interest_points["coordinates_interest_points"]=coordinates_interest_points

    #Deleting not needed columns
    interest_points.drop(['long_start','lat_start'], axis=1, inplace=True)

    #Storing dataframe
    interest_points.to_csv('./data/interest_points_clean.csv')

    #Joining data
    interest_points_bicimad = bicimad_stations.assign(key=0).merge(interest_points.assign(key=0), how='left', on = 'key')
    interest_points_bicimad.drop('key', axis=1, inplace=True)
    interest_points_bicimad.to_csv('./data/interest_points_bicimad.csv')

    #Calculating coordinades
    distance=interest_points_bicimad.apply(lambda x: distance_meters(x['coordinates_interest_points'],x['coordinates_bicimad']), axis=1)
    interest_points_bicimad["distance"]=distance

    #Deleting not needed columns
    interest_points_bicimad.drop(['coordinates_bicimad','coordinates_interest_points'], axis=1, inplace=True)

    #Sorting values
    interest_points_bicimad=interest_points_bicimad.sort_values(["Place of interest","Station location"])

    #Filtering by the minimun distanct
    nearest_BiciMAD_station=interest_points_bicimad[interest_points_bicimad['distance'] ==
                        interest_points_bicimad.groupby(['Place of interest','Place address'])['distance'].transform('min')]
    #Sorting the data
    nearest_BiciMAD_station=nearest_BiciMAD_station.sort_values(["Place of interest","Station location"])
    nearest_BiciMAD_station=nearest_BiciMAD_station.reset_index()
    column_names = ["Place of interest", "Type of place", "Place address","BiciMAD station","Station location","distance","dock_bikes"]
    nearest_BiciMAD_station = nearest_BiciMAD_station.reindex(columns=column_names)
    nearest_BiciMAD_station = nearest_BiciMAD_station.rename(columns={'dock_bikes': 'bikes availability','distance': 'distance(m)'})
    nearest_BiciMAD_station['distance(m)']=nearest_BiciMAD_station['distance(m)'].round(2)

    #Saving CSV
    nearest_BiciMAD_station.to_csv('./data/nearest_BiciMAD_station.csv')


def nearest_station_specific_place(place):
    nearest_BiciMAD_station=pd.read_csv('./data/nearest_BiciMAD_station.csv')
    def compare_strings(place,x):
        return fuzz.ratio(place,x)
    similarity=nearest_BiciMAD_station.apply(lambda x: compare_strings(x['Place of interest'],place), axis=1)
    nearest_BiciMAD_station["similarity"]=similarity
    nearest_BiciMAD_station_filtered=nearest_BiciMAD_station[(nearest_BiciMAD_station["similarity"]>60)]
    print(tabulate(nearest_BiciMAD_station_filtered, headers='keys', tablefmt='psql'))
    #nearest_BiciMAD_station_filtered=nearest_BiciMAD_station[nearest_BiciMAD_station["Place of interest"]==place]
    #nearest_BiciMAD_station_filtered.to_csv('./data/nearest_BiciMAD_station_filtered.csv')

    return nearest_BiciMAD_station_filtered
    

# Argument parser function
def argument_parser():
    parser = argparse.ArgumentParser(description='Set operation type')
    parser.add_argument("-f", "--function", help="function type. Options are: 'all' to get a table for every Place of interest and 'specific' to get a table for a specific Place of interest imputed" , type=str)
    args = parser.parse_args()
    return args


# Main pipeline function

def main(arguments):
    print('--//--- starting application ---//--')
    print('\n')

    if arguments.function == 'all':
        result = nearest_station_all_places()
    elif arguments.function == 'specific':
        place = str(input('Please, enter the Place of interest:   '))
        nearest_station_all_places()
        result = nearest_station_specific_place(place)
    print('\n\n')
    print(f'The result is ==> {result}')
    print('\n')
    print('--//--- closing application ---//--')



# Pipeline execution

if __name__ == '__main__':
    main(argument_parser())