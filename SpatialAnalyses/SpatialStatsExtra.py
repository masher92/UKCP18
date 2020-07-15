## Trying to ccomibne multiple ensemble members
# But concatenate not working because it says ther is some difference in their
#ensemble member coordinate
'''
Creates a cube over a 20 year time period
Trims this to the square covering the WY extent
For each of the grid squares in this extent - calculates statistics incl. mean 
and various percentiles of hourly rainfall.
Plots these spatially, using pcolormesh and the bottom left corner coordinates
'''

import sys
import iris
import cartopy.crs as ccrs
import os
from scipy import spatial
import itertools
import iris.quickplot as qplt
import warnings
import copy
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
import numpy as np
from shapely.geometry import Polygon


# Provide root_fp as argument
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
em = '01'

##############################################################################
#### Create a shapely geometry of the outline of Leeds and West Yorks
##############################################################################
# Convert outline of Leeds into a polygon
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})

# Create geodataframe of the outline of West Yorkshire
# Data from https://data.opendatasoft.com/explore/dataset/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england%40ons-public/export/
wy_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
wy_gdf = wy_gdf.to_crs({'init' :'epsg:3785'}) 
 
# Create geodataframe of the square outline of West Yorkshire (in OGSB36)
lats = [384411, 384411, 456892 ,456892]
lons = [399892, 458800, 458800, 399892]
polygon_geom = Polygon(zip(lats, lons))
crs = {'init': 'epsg:27700'}
polygon = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom])       
polygon= polygon.to_crs({'init' :'epsg:3785'}) 

# Create geodataframe of the square outline of Leeds (in web mercator)
lons_wm = [7111000, 7111000, 7163000 ,7163000]
lats_wm = [-202000, -140000, -140000, -202000]
polygon_geom_wm = Polygon(zip(lats_wm, lons_wm))
crs = {'init': 'epsg:3785'}
polygon_wm = gpd.GeoDataFrame(index=[0], crs=crs, geometry=[polygon_geom_wm])       
crs = {'init': 'epsg:27700'}

# Location of centre of Leeds (Millenium Square)
lcc_lon = -173285.69
lcc_lat = 7132610.01

##############################################################################
#### 
##############################################################################
members = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
wy_cubes = []
for em in members:
    print (em)
    # Create list of names of cubes for between the years specified
    filenames =[]
    for year in range(start_year,end_year+1):
        # Create filepath to correct folder using ensemble member and year
        general_filename = root_fp + 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
        #print(general_filename)
        # Find all files in directory which start with this string
        for filename in glob.glob(general_filename):
            #print(filename)
            filenames.append(filename)
            
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    print(str(len(monthly_cubes_list)) + " cubes found for this time period.")
    
    #############################################
    # Concat the cubes into one
    #############################################
    # Remove attributes which aren't the same across all the cubes.
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
     
    # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    #
    # Remove ensemble member dimension
    #concat_cube = concat_cube[0,:,:,:]
    
    ############################################
    # Trim to include only grid cells whose coordinates (which represents the centre
    # point of the cell is within a certain region e.g. West Yorks)
    #############################################
    #wy_cube = trim_to_wy(concat_cube)
    wy_cube = trim_to_gdf_em(concat_cube, polygon)
    wy_cubes.append(wy_cube)
    
# Concatenate the cubes into one
wy_cubes_iris = iris.cube.CubeList(wy_cubes)
concat_ems = wy_cubes_iris.concatenate_cube()

test = wy_cubes[5].coord('ensemble_member').points
concat_ems = wy_cubes_iris.merge_cube()
