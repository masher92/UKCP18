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

############################################
# Create regions
#############################################
wys_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wys_gdf = wys_gdf[wys_gdf['cauth15cd'] == 'E47000003']
# Create the square around it
bounding_box = wys_gdf.envelope
wys_gdf = gpd.GeoDataFrame(gpd.GeoSeries(bounding_box), columns=['geometry'])
wys_gdf.crs = "epsg:4326"
wys_gdf = wys_gdf.to_crs({'init' :'epsg:3785'}) 

# Create geodataframe of West Yorks
uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
northern_gdf = northern_gdf.to_crs({'init' :'epsg:3785'}) 
# Merge the three regions into one
northern_gdf['merging_col'] = 0
northern_gdf = northern_gdf.dissolve(by='merging_col')

# Create region with Leeds at the centre
lons = [54.130260, 54.130260, 53.486836, 53.486836]
lats = [-2.138282, -0.895667, -0.895667, -2.138282]
polygon_geom = Polygon(zip(lats, lons))
leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:3785'}) 

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
