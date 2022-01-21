<p align="left"><img src="https://cdn-images-1.medium.com/max/184/1*2GDcaeYIx_bQAZLxWM4PsQ@2x.png"></p>


# __Access to Madrid Monuments using BiciMAD 🏛 🚴__

- This project is part of Ironhack Madrid - Data Analytics Part Time - November 2021 - Project Module 1

- This project is a Real time Python App that calculates nearest BiciMAD station to most important monuments in Madrid City

## **🎯 Objectives:**
Provide the user with to the nearest BiciMAD station to different monuments of Madrid City, so they:
- Know in real time which is the nearest BiciMAD station to a specific monument they input or to all important monument in Madrid City.
- Know if the station has free bikes or free bases to left the bike.
- Have all addresses and the distances in meters.

By using a python app (data pipeline) for getting all data sources and provide results in real time.


## **👩🏻‍💻 Resources:**
- Python 3.7 and libraries ([Pandas](https://pandas.pydata.org/pandas-docs/stable/reference/index.html), [Requests](https://requests.readthedocs.io/),[fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/), geometry, geopandas, [Argparse](https://docs.python.org/3.7/library/argparse.html) and tabulate)
- Access to [Madrid City Monument official data](https://datos.madrid.es/nuevoMadrid/swagger-ui-master-2.2.10/dist/index.html?url=/egobfiles/api.datos.madrid.es.json#!/Monumentos32de32la32ciudad32de32Madrid/monumentos_ciudad_madrid_json) (through API)
- Access to [EMT BiciMAD official data](https://mobilitylabs.emtmadrid.es/sip/es/oauth/register?client_id=f2f08cad-4c18-4538-ae18-11da67819299&redirect_uri=aHR0cHM6Ly9tb2JpbGl0eWxhYnMuZW10bWFkcmlkLmVzL2Rlc2EvZXMvbG9naW4vYXV0aG9yaXplZA==&scope=&context=cG9ydGFs) (through API)

> __IMPORTANT =>__ It is needed to create an account for using EMT BiciMAD official data

## **👤 User experience:**
2 options for the end user:
- **all_points**: provides a list with all interest points and the nearest bicimad station (also with the distance, both addresses and number of free bikes and free bases).
- **specific_point**: gets a interest point provided by the user and returns the interest points with similar title (depending on the user accurate this can return more than one place or even none). Again with the nearest bicimad station (also with the distance, both addresses and number of free bikes and free bases).

-  They need to include *python main_script.py -h* for the help and *python main_script.py -h < option > for executing the program.

- They get a table like the following and a csv stored in data/results folder: *

| Place of interest | Type of place | Place address | BiciMAD station | Station location |  distance(m) | free bikes |  free bases |
|---------|----------|-------|------------|----------|-------|------------|----------|
| A los abuelos  | Monumentos de la ciudad de Madrid | C Alicún | Manuel Caldeiro | Paseo de la Castellana nº 298 |2633.11 |  9 |  15 |

*This example is for **specific_point** option 

## **🗄 Folder structure:**
```
 └── project
    ├── .gitignore
    ├── README.md
    ├── main_script.py
    ├── notebooks
    │   ├── nearest_BiciMAD_station_calculation.ipynb
    │   └── near_BiciMAD_calculation_functions.ipynb
    ├── modules
    │   ├── data_adquisition.py
    │   └── data_transformation.py
    │   └── filter_by_interest_point.py
    │   └── geo_calculations.py
    └── data
        ├── raw
        ├── processed
        └── results
 ```

- data: for storing intermediate and final data (in csv so it’s easy to access, storing intermediate data is helpful for testing purposes.)
- modules: includes python scripts where functions are defined.
- notebooks: sometimes using jupyter notebook for developing is helpful, but this files are not part of the final project.
- main_script.py: this file includes the ejecutable part and is related with all modules files.
 

 ## **🧩 Modules:**
- **data_acquisition**: gets information from APIS, cleans it and does some calculations.
- **filter_by_interest_point**: gets the point of interest the user indicates and provide the point of interests information (name, address, latitude, longitude…) for the most similar one/ones.
- **data_transformation**: calculates the distance of each interest point to each BiciMAD stations and provides the result with the nearest BiciMAD station.
- **geo_calculation**: applies specific functions for calculating coordinates in degrees and distance between 2 points in meters.


## **👑 Main script -Functions flow:**
**all_points:**
- get_bicimad_info
- get_interest_points_info
- get_interest_points_info_coordinades
- get_near_station

**specific_point:** 
- get_bicimad_info
- get_interest_points_info
- get_specific_interest_point (filtering first the dataframe)
- get_interest_points_info_coordinades
- get_near_station









 


 

