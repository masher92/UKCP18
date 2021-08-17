'''
For all defined regions, statistics and ensemble members this file processes the
outputs of the FindStats*.py scripts. These outputs all refer to the region of the
bounding box of the North of England. This script uses masks created in CreateRegionalMasks.py
to trim these
'''

############################################
# Set up environment
#############################################
import sys
import iris
import os
import iris.quickplot as qplt
import warnings
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
from shapely.geometry import Polygon
import iris.coord_categorisation
import time 
warnings.filterwarnings("ignore")

##############################################################################
# Define variables and set up environment
##############################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)
stats= ['Max','Mean', '95th Percentile', '97th Percentile', '99th Percentile', '99.5th Percentile',  '99.75th Percentile', '99.9th Percentile']
regions = ['leeds-at-centre-narrow']    #'leeds-at-centre', 'Northern'
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

############################################################################## 
# Loop through all the define regions:
#   Loop through the ensemble members:
#       Loop through the statistics:
#               In each case, read in the data and the mask
#               This mask has each location within the bounding box of the northern
#               region and a flag to determine whether that location is within the
#               the region to which the mask refers.
#               This mask is used to keep only the statistic values for the locations
#               within this specified region.
##############################################################################
for region in regions:
    for em in ems:    
        for stat in stats:
            print(region, em, stat)
            #Read in data        
            stats_data = pd.read_csv("Outputs/RainfallRegionalisation/HiClimR_inputdata/NorthernSquareRegion/Allhours/{}/em_{}.csv".format(stat, em))
            mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
        
            # Join the mask with the stats 
            joined = pd.concat([mask, stats_data], axis=1)

            # Remove NAs - outside mask
            joined = joined.dropna()
            # Remove duplicate of lat/lon columns
            joined = joined.loc[:,~joined.columns.duplicated()]
            # Remove within_region columns
            joined.drop(joined.columns[2], axis =1, inplace = True)         
           
            ddir = "Outputs/RainfallRegionalisation/HiClimR_inputdata/{}/Allhours/{}/".format(region, stat)
            if not os.path.isdir(ddir):
                os.makedirs(ddir)
            print(ddir + "em_{}.csv".format(em))
            # Save to file
            joined.to_csv(ddir + "em_{}.csv".format(em), index = False, float_format = '%.20f')
