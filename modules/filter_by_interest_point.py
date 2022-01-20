
######################################################## import libraries ####################################################### 
import pandas as pd                     #general
from fuzzywuzzy import fuzz             #allowing users to input interest points with flexibility 
from fuzzywuzzy import process          #""

################################################ for calculating specific interesting point ###########################################
def get_specific_interest_point(dataframe,input_var):
    print('--//--- Calculating Place of interest ---//--')
    def compare_strings(input_var,x):
        return fuzz.ratio(input_var,x)
    similarity=dataframe.apply(lambda x: compare_strings(x['Place of interest'],input_var), axis=1)
    dataframe["similarity"]=similarity
    specific_interest_point=dataframe[dataframe["similarity"]>80]
    return specific_interest_point
