#############################################################################################################################
#                                                                                                                           #                       
#   argparse — Parser for command-line options, arguments and sub-commands                                                  #     
#                                                                                                                           #
#   Ironhack Data Part Time --> Nov-2021                                                                                    #
#                                                                                                                           #
#############################################################################################################################                      


# import libraries
import pandas as pd                     #general
import geopandas as gpd                 #calculate geo distance
from shapely.geometry import Point      #""
import requests                         #import data from URL
import argparse                         #allow users to select multiple functionalities
from fuzzywuzzy import fuzz             #allowing users to input interest points with flexibility 
from fuzzywuzzy import process          #""
from tabulate import tabulate           #for nice displaying


######################################################## Geo functions #######################################################  
# transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
def to_mercator(lat, long):  
    c = gpd.GeoSeries([Point(lat, long)], crs=4326)
    c = c.to_crs(3857)
    return c

# return the distance in metres between to latitude/longitude pair point in degrees (i.e.: 40.392436 / -3.6994487)
def distance_meters(start, finish):
    return start.distance(finish)
 

################################################# get bicimad stations information from API #####################################  
def get_bicimad_info():
    # getting token
    login_url = 'https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/'
    login_headers = {'email': 'malva.gonzalez@ironhack.com','password': 'Bicimad2022'}
    accessToken=requests.get(login_url,headers=login_headers).json()['data'][0]['accessToken']

    #Getting stations information
    stations_url = 'https://openapi.emtmadrid.es/v1/transport/bicimad/stations/'
    stations_headers = {'accessToken':accessToken }
    bicimad_stations_json=requests.get(stations_url,headers=stations_headers).json()['data']
    bicimad_stations=pd.json_normalize(bicimad_stations_json)

    #Taking only the intersting columns needed for the project and filtering the data  
    bicimad_stations=bicimad_stations[["address","geometry.coordinates","name","dock_bikes","free_bases"]]
    bicimad_stations = bicimad_stations.rename(columns={'geometry.coordinates': 'geometry_coordinates'})

    #Filtering out rows without geometry_coordinates:
    bicimad_stations=bicimad_stations[bicimad_stations.geometry_coordinates.notnull()]

    #Calculating coordinates
    def left_split(x):
        return x[0]
    def right_split(x):
        return x[-1]
    long_finish=bicimad_stations.apply(lambda x: left_split(x['geometry_coordinates']), axis=1)
    lat_finish=bicimad_stations.apply(lambda x: right_split(x['geometry_coordinates']), axis=1)
    bicimad_stations["long_finish"]=long_finish
    bicimad_stations["lat_finish"]=lat_finish

    #Renaming field names
    bicimad_stations = bicimad_stations.rename(columns={'address': 'Station location', 'name': 'BiciMAD station'})

    #Deleting not needed columns
    bicimad_stations = bicimad_stations.drop(columns='geometry_coordinates')

    #Calculating coordenades
    bicimad_stations[["long_finish", "lat_finish"]] = bicimad_stations[["long_finish", "lat_finish"]].apply(pd.to_numeric)

    coordinates_bicimad=bicimad_stations.apply(lambda x: to_mercator(x['lat_finish'],x['long_finish']), axis=1)
    bicimad_stations["coordinates_bicimad"]=coordinates_bicimad

    #Deleting not needed columns
    bicimad_stations.drop(['long_finish','lat_finish'], axis=1, inplace=True)

    #Storing dataframe
    bicimad_stations.to_csv('./data/intermediate/bicimad_stations_clean.csv')
    return bicimad_stations

################################################# get Interesting Points info from API ##############################################
def get_interest_points_info():
    #Extracting raw data - Interesting Points
    #Defining public url for accesing to the datasets
    url_interest_points = 'https://datos.madrid.es/egob/catalogo/300356-0-monumentos-ciudad-madrid.json'
    #Taking url information with requests
    response_interest_points = requests.get(url_interest_points)
    response_interest_points=response_interest_points.json()['@graph']

    #Converting json to pandas dataframe and taking only needed fields
    interest_points = pd.json_normalize(response_interest_points)
    interest_points=interest_points[["title","address.street-address","location.latitude","location.longitude"]]
    
    #Renaming and adding columns needed
    interest_points = interest_points.rename(columns={'title': 'Place of interest', 'address.street-address': 'Place address','location.latitude': 'lat_start','location.longitude': 'long_start'})
    interest_points["Type of place"] = "Monumentos de la ciudad de Madrid" 

    #Cleaning the dataframe (excluding rows without latitude or longitude information)
    interest_points=interest_points[interest_points.lat_start.notnull()]
    interest_points=interest_points[interest_points.long_start.notnull()]
    
    #Saving CSV
    interest_points.to_csv('./data/intermediate/interest_points.csv')
    return interest_points


################################################ for calculating specific interesting point ###########################################
def get_specific_interest_point(dataframe,input_var):
    def compare_strings(input_var,x):
        return fuzz.partial_ratio(input_var,x)
    similarity=dataframe.apply(lambda x: compare_strings(x['Place of interest'],input_var), axis=1)
    dataframe["similarity"]=similarity
    specific_interest_point=dataframe[dataframe["similarity"]>80]
    return specific_interest_point


###################################################### for calculating distance ########################################################
def get_interest_points_info_coordinades(dataframe):
    #Calculating coordinades
    dataframe[["long_start", "lat_start"]] = dataframe[["long_start", "lat_start"]].apply(pd.to_numeric)
    coordinates_interest_points=dataframe.apply(lambda x: to_mercator(x['lat_start'],x['long_start']), axis=1)
    dataframe["coordinates_interest_points"]=coordinates_interest_points

    #Deleting not needed columns
    dataframe.drop(['long_start','lat_start'], axis=1, inplace=True)

    #Storing dataframe
    dataframe.to_csv('./data/interest_points_clean.csv')
    interest_points_coordinades=dataframe
    return interest_points_coordinades


###################################################### calculating nearest station ####################################################
def get_near_station(bicimad_stations,dataframe):
    #Joining data
    interest_points_bicimad = bicimad_stations.assign(key=0).merge(dataframe.assign(key=0), how='left', on = 'key')
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
    column_names = ["Place of interest", "Type of place", "Place address","BiciMAD station","Station location","distance","dock_bikes","free_bases"]
    nearest_BiciMAD_station = nearest_BiciMAD_station.reindex(columns=column_names)
    nearest_BiciMAD_station = nearest_BiciMAD_station.rename(columns={'dock_bikes': 'bikes availability','distance': 'distance(m)','free_bases': 'bases availability'})
    nearest_BiciMAD_station['distance(m)']=nearest_BiciMAD_station['distance(m)'].round(2)

    #Saving CSV
    nearest_BiciMAD_station.to_csv('./data/output/nearest_BiciMAD_station.csv')
    return nearest_BiciMAD_station

# Argument parser function
def argument_parser():
    parser = argparse.ArgumentParser(description='Set operation type')
    parser.add_argument("-f", "--function", help="Please select: 'all' to get a table for every Place of interest  or 'specific' to get a table for a specific Place of interest" , type=str)
    args = parser.parse_args()
    return args


###################################################### Main pipeline function ########################################################
def main(arguments):
    print('--//--- starting application ---//--')
    print('\n')

    if arguments.function == 'all':
        #result = nearest_station_all_places()
        bicimad_info=get_bicimad_info()
        interest_points=get_interest_points_info()
        interest_points_coordinades=get_interest_points_info_coordinades(interest_points)
        result = get_near_station(bicimad_info,interest_points_coordinades)

    elif arguments.function == 'specific':
        place = str(input('Please, enter the Place of interest:   '))
        bicimad_info=get_bicimad_info()
        interest_points=get_interest_points_info()
        interest_points_filter=get_specific_interest_point(interest_points,place)
        interest_points_coordinades=get_interest_points_info_coordinades(interest_points_filter)
        result = get_near_station(bicimad_info,interest_points_coordinades)
        #nearest_station_all_places()
        #result = nearest_station_specific_place(place)
    print('\n\n')
    print(f'The result is ==>')
    print(tabulate(result, headers='keys', tablefmt='psql'))
    print('\n')
    print('--//--- closing application ---//--')

###################################################### Pipeline execution ##########################################################
if __name__ == '__main__':
    main(argument_parser())