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
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
#root_fp = "/nfs/a319/gy17m2a/"

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
filename = root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc'
cube = iris.load(filename,'lwe_precipitation_rate')[0]
cube = cube[0,:,:,:]
print(cube)

#############################################
# Trim the cube to the BBOX of the region of interest
#############################################
regional_cube = trim_to_bbox_of_region(cube, northern_gdf)

#############################################
# Trim to the smaller areas
#############################################
def create_mask_df (regional_gdf, regional_cube):
    masked_cube = mask_by_region(regional_cube, regional_gdf)
    cube_mask_df = pd.DataFrame({'mask': masked_cube.reshape(-1), 
                                       'lat': regional_cube.coord('latitude').points.reshape(-1),
                                       'lon': regional_cube.coord('longitude').points.reshape(-1)})
    cube_mask_df.replace(0, np.nan, inplace=True)
    return(cube_mask_df)

# Create
northern_mask_df = create_mask_df(northern_gdf, regional_cube)
wys_mask_df = create_mask_df(wys_gdf, regional_cube)
leeds_at_centre_mask_df = create_mask_df(leeds_at_centre_gdf, regional_cube)

# Check number of values
wys_mask_df['mask'].value_counts()
leeds_at_centre_mask_df['mask'].value_counts()
northern_mask_df['mask'].value_counts()

# Save to file
wys_mask_df.to_csv("Outputs/RegionalMasks/wy_mask.csv" , index = False, float_format='%.20f')
northern_mask_df.to_csv("Outputs/RegionalMasks/northern_mask.csv" , index = False, float_format='%.20f')
leeds_at_centre_mask_df.to_csv("Outputs/RegionalMasks/leeds_at_centre_mask.csv" , index = False, float_format='%.20f')
