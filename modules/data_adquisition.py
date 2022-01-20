
######################################################## import libraries ####################################################### 
# import libraries
import pandas as pd                     #general
import requests                         #import data from URL

######################################################## import modules ############################################################  
from modules import geo_calculations as geo

################################################# get bicimad stations information from API #####################################  
def get_bicimad_info():
    print('--//--- Taking BiciMAD stations info from API ---//--')
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

    coordinates_bicimad=bicimad_stations.apply(lambda x: geo.to_mercator(x['lat_finish'],x['long_finish']), axis=1)
    bicimad_stations["coordinates_bicimad"]=coordinates_bicimad

    #Deleting not needed columns
    bicimad_stations.drop(['long_finish','lat_finish'], axis=1, inplace=True)

    #Storing dataframe
    bicimad_stations.to_csv('./data/intermediate/bicimad_stations_clean.csv')
    return bicimad_stations


################################################# get Interesting Points info from API ##############################################
def get_interest_points_info():
    print('--//--- Taking Interesting Points info from API ---//--')
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
