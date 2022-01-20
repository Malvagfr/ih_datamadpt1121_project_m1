
######################################################## import libraries ####################################################### 
# import libraries
import pandas as pd                     #general

######################################################## import modules ############################################################  
from modules import geo_calculations as geo

###################################################### for calculating interest points distance ########################################
def get_interest_points_info_coordinades(dataframe):
    #Calculating coordinades
    dataframe[["long_start", "lat_start"]] = dataframe[["long_start", "lat_start"]].apply(pd.to_numeric)
    coordinates_interest_points=dataframe.apply(lambda x: geo.to_mercator(x['lat_start'],x['long_start']), axis=1)
    dataframe["coordinates_interest_points"]=coordinates_interest_points

    #Deleting not needed columns
    dataframe.drop(['long_start','lat_start'], axis=1, inplace=True)

    #Storing dataframe
    dataframe.to_csv('./data/interest_points_clean.csv')
    interest_points_coordinades=dataframe
    return interest_points_coordinades


###################################################### calculating nearest station ####################################################
def get_near_station(bicimad_stations,dataframe):
    print('--//--- Calculating nearest station ---//--')
    #Joining data
    interest_points_bicimad = bicimad_stations.assign(key=0).merge(dataframe.assign(key=0), how='left', on = 'key')
    interest_points_bicimad.drop('key', axis=1, inplace=True)
    interest_points_bicimad.to_csv('./data/interest_points_bicimad.csv')

    #Calculating coordinades
    distance=interest_points_bicimad.apply(lambda x: geo.distance_meters(x['coordinates_interest_points'],x['coordinates_bicimad']), axis=1)
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
    nearest_BiciMAD_station.to_csv('./data/nearest_BiciMAD_station.csv')
    return nearest_BiciMAD_station