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

# Set working directory - 2 options for remote server and desktop
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

#stats= ['Greatest_ten', 'Max','Mean', '95th Percentile', '97th Percentile', '99th Percentile', '99.5th Percentile']
stats = ['ValuesOverPercentile/99', 'ValuesOverPercentile/99.5', 'ValuesOverPercentile/99.9', 'ValuesOverPercentile/99.95', 'ValuesOverPercentile/99.99']
regions = ['leeds-at-centre']   
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

##############################################################################    
for region in regions:
    for em in ems:    
        for stat in stats:
            print(region, em, stat)
            #Read in data        
            stats_data = pd.read_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/{}/em_{}.csv".format(stat, em))
            mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
        
            # Join the mask with the stats 
            joined = pd.concat([mask, stats_data], axis=1)
            #joined = mask.merge(stats_data,  on=['lat', 'lon'], how="left")
            
            # Remove NAs - outside mask
            joined = joined.dropna()
           
            ddir = "Outputs/HiClimR_inputdata/{}/{}/".format(region, stat)
            if not os.path.isdir(ddir):
                os.makedirs(ddir)
            print(ddir + "em_{}.csv".format(em))
            # Save to file
            joined.to_csv(ddir + "em_{}.csv".format(em), index = False, float_format = '%.20f')
