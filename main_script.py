#############################################################################################################################
#                                                                                                                           #                       
#                                           Access to Madrid Monuments using BiciMAD                                        #     
#                                                                                                                           #
#                                             Ironhack Data Part Time --> Nov-2021                                          #
#                                                                                                                           #
#############################################################################################################################     


###################################################### Modules import #######################################################
from modules import data_adquisition as ad
from modules import filter_by_interest_point as fi
from modules import data_transformation as tr

# import libraries
import argparse                         #allow users to select multiple functionalities
from tabulate import tabulate           #for nice displaying by console
 

###################################################### Argument parser function ##############################################
#allow users to select between 2 different functionalities
def argument_parser():
    parser = argparse.ArgumentParser(description='Set operation type')
    parser.add_argument("-f", "--function", 
    help="Please select: 'all_points' for getting a table with the nearest BiciMAD Station to all places of interest \
    or 'specific_point' for getting table with the nearest BiciMAD Station of a specific place of interest" ,type=str)
    args = parser.parse_args()
    return args


###################################################### Main pipeline function ################################################
def main(arguments):
    print('----------------------- 1. starting application -----------------------')

    if arguments.function == 'all_points':
        bicimad_info=ad.get_bicimad_info()
        interest_points=ad.get_interest_points_info()
        interest_points_coordinades=tr.get_interest_points_info_coordinades(interest_points)
        result = tr.get_near_station(bicimad_info,interest_points_coordinades)

    elif arguments.function == 'specific_point':
        place = str(input('Please, enter the Place of interest:   '))
        bicimad_info=ad.get_bicimad_info()
        interest_points=ad.get_interest_points_info()
        interest_points_filter=fi.get_specific_interest_point(interest_points,place)
        print('interest_points_filter',interest_points_filter)
        interest_points_coordinades=tr.get_interest_points_info_coordinades(interest_points_filter)
        result = tr.get_near_station(bicimad_info,interest_points_coordinades)
    print('\n\n')
    print(f'The result is ==>')
    print(tabulate(result, headers='keys', tablefmt='psql'))
    print('\n')
    print('----------------------- 6. closing application -----------------------')
    print('----------------------- Find your results in /data/nearest_BiciMAD_station.csv -----------------------')

###################################################### Pipeline execution #####################################################
if __name__ == '__main__':
    main(argument_parser())