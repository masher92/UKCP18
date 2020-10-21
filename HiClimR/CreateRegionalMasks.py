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

def variablename(var):
     import itertools
     return [tpl[0] for tpl in 
     filter(lambda x: var is x[1], globals().items())]
 
 
# Set working directory - 2 options for remote server and desktop
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

#############################################
# Create regions
#############################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outline of the coast of the UK
uk_gdf = create_uk_outline({'init' :'epsg:3857'})

############################################
# Read in one cube
#############################################   
filename = 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc' 
#filename = root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc'
cube = iris.load(filename,'lwe_precipitation_rate')[0]
cube = cube[0,:,:,:]
print(cube)

#############################################
# Create a dataframe with the latitude and longitude of all locations in the
# bounding box of the northern England region
#############################################
square_northern_cube = trim_to_bbox_of_region(cube, northern_gdf)
square_northern_cube_df = pd.DataFrame({'lat': square_northern_cube.coord('latitude').points.reshape(-1),
                             'lon': square_northern_cube.coord('longitude').points.reshape(-1)})


for location in ["WY_square", "Northern", "leeds-at-centre"]:
    if location == 'WY_square':
        location_gdf = wys_gdf
    elif location =='Northern':
        location_gdf = northern_gdf
    elif location == 'leeds-at-centre':
        location_gdf = leeds_at_centre_gdf
        
    #############################################
    # Create a dataframe with the latitude and longitude of all locations in the
    # area of interest, along with a column marking them all to be within the region
    # (this is required for joining purposes)
    #############################################
    # Create a cube trimmed to the region of interest
    regional_cube = trim_to_bbox_of_region(square_northern_cube, location_gdf)
    # Convert this to dataframe format
    cube_mask_df = pd.DataFrame({'within_region': 1,
                                   'lat': regional_cube.coord('latitude').points.reshape(-1),
                                   'lon': regional_cube.coord('longitude').points.reshape(-1)})
    
    #############################################
    # Join this to the dataframe for the whole of Northern England BBOX
    # Latitude and Longitudes outwith the area of interest will have NA for column
    # specifying whether they are within the region
    #############################################
    joined = square_northern_cube_df.merge(cube_mask_df,  on=['lat', 'lon'], how="left")

    # Save to file
    joined.to_csv("Outputs/RegionalMasks/{}_mask.csv".format(location) , index = False, float_format='%.20f')
