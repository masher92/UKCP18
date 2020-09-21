'''
This file is for comparing the regridded observations against the native observations
to discern the influence of the regridding process on the data.
'''

import numpy.ma as ma
import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import os
import geopandas as gpd
import time 
import sys
import iris.quickplot as qplt
import cartopy.crs as ccrs
import matplotlib 
import iris.plot as iplt
from scipy import spatial
import itertools
from shapely.geometry import Point, Polygon
from pyproj import Proj, transform
import matplotlib.pyplot as plt
import pandas as pd
import tilemapbase
import matplotlib as mpl

################################################################
# Define variables and set up environment
################################################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import create_leeds_outline
sys.path.insert(0, root_fp + 'Scripts/UKCP18/PlotPDFs/')
from PDF_plotting_functions import *

# Define strings 
rg_string = '_regridded_2.2km/rg_'
rf_string = '_reformatted/rf_'

# Coordinates of location of interest
sample_point = [('grid_latitude', 53.796638), ('grid_longitude', -1.592600)]

################################################################
# Create a cube trimmed to the oputline of the square area surrounding Leeds
################################################################   
rf_cube = create_trimmed_cube(leeds_at_centre_gdf, rf_string, {'init' :'epsg:27700'})
rg_cube = create_trimmed_cube(leeds_at_centre_gdf, rg_string, {'init' :'epsg:4326'})
    
################################################################
# Plot cubes to check the grid
################################################################   
#check_location_of_closestpoint(rg_cube, {'init' :'epsg:4326'},  {'init' :'epsg:3785'}, sample_point )
#check_location_of_closestpoint(rf_cube, {'init' :'epsg:4326'},  {'init' :'epsg:3785'}, sample_point )

################################################################
# Find the coordinates of the grid cell containing the point of interest
################################################################   
rg_closest_coordinates = find_closest_coordinates(rg_cube, sample_point, 1) 
rf_closest_coordinates =  find_closest_coordinates(rf_cube, sample_point,1)    

############################################################################
# Create a cube containing just the timeseries for that location of interest
#############################################################################
# Use this closest lat, long pair to collapse the latitude and longitude dimensions
# of the concatenated cube to keep just the time series for this closest point 
rg_time_series_cube = rg_cube.extract(iris.Constraint(grid_latitude=rg_closest_coordinates[1], 
                                                      grid_longitude= rg_closest_coordinates[2]))
rf_time_series_cube = rf_cube.extract(iris.Constraint(projection_y_coordinate=rf_closest_coordinates[1], 
                                                      projection_x_coordinate= rf_closest_coordinates[2]))

#############################################################################
# Plot the grids highlighting the locations of the cells determined as being
# those closest to the location of interest
#############################################################################
plot_grid_highlight_cells(rg_cube, {'init' :'epsg:4326'},  {'init' :'epsg:3785'}, 
                               sample_point, rg_closest_coordinates[0] )
plot_grid_highlight_cells(rf_cube, {'init' :'epsg:27700'},  {'init' :'epsg:3785'} , 
                               sample_point, rf_closest_coordinates[0])

#############################################################################
# Convert to dataframe
#############################################################################
print("Creating dataframe")
rg_df =pd.DataFrame({"time_stamp" : rg_time_series_cube.coord('time').points,
                     "Rainfall": rg_time_series_cube.data})
rg_df['Date_formatted']  = pd.to_datetime(rg_df['time_stamp'], unit='s')\
               .dt.strftime('%Y-%m-%d %H:%M:%S')
rg_df.to_csv("rg_df_westleeds.csv", index = False)

print("Creating dataframe")
rf_df =pd.DataFrame({"time_stamp" : rf_time_series_cube.coord('time').points,
                     "Rainfall": rf_time_series_cube.data})
rf_df['Date_formatted']  = pd.to_datetime(rf_df['time_stamp'], unit='s')\
                .dt.strftime('%Y-%m-%d %H:%M:%S')
rf_df.to_csv("rf_df_westleeds.csv", index = False)


