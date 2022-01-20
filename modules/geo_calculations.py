

######################################################## import libraries ####################################################### 
from shapely.geometry import Point
import geopandas as gpd   


######################################################## to_mercator ############################################################  
# transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
def to_mercator(lat, long):  
    c = gpd.GeoSeries([Point(lat, long)], crs=4326)
    c = c.to_crs(3857)
    return c

######################################################## distance_meters ######################################################## 
# return the distance in metres between to latitude/longitude pair point in degrees (i.e.: 40.392436 / -3.6994487)
def distance_meters(start, finish):
    return start.distance(finish)