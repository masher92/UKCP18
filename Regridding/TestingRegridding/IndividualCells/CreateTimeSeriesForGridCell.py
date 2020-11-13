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
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_geometry_functions import *

# Define string which is used to establish the filepath to the files 
# containing the regridded/reformatted files  
string = '_regridded_2.2km/NearestNeighbour/rg_'
# '_reformatted/rf_' , '_regridded_2.2km/LinearRegridding/rg_', '_regridded_2.2km/NearestNeighbour/rg_'

# Define target_crs, dependent on whether using reformatted or regridded data
if string == '_reformatted/rf_':
    target_crs = {'init' :'epsg:27700'}
else:
    target_crs = {'init' :'epsg:4326'}

# Coordinates of location of interest
sample_point = [('grid_latitude', 53.796638), ('grid_longitude', -1.592600)]

################################################################
# Create the spatial datafiles needed
################################################################   
# Create region with Leeds at the centre
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:27700'})
# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})

################################################################
# Reads in all monthly (either regridded or reformatted) CEH-GEAR data files 
# Create a cube trimmed to the oputline of the square area surrounding Leeds
# Containing this data over time 
################################################################   
cube = create_trimmed_cube(leeds_at_centre_gdf, string, target_crs)
    
################################################################
# Plot cubes to check the grid
# This won't highlight any cell
################################################################   
plot_grid_highlight_cells(cube, target_crs,  {'init' :'epsg:3785'}, sample_point, None )

################################################################
# Find the coordinates of the grid cell containing the point of interest
################################################################   
closest_coordinates = find_closest_coordinates(cube, sample_point, 1) 

############################################################################
# Create a cube containing just the timeseries for that location of interest
#############################################################################
# Use this closest lat, long pair to collapse the latitude and longitude dimensions
# of the concatenated cube to keep just the time series for this closest point 
if string == '_reformatted/rf_':
    time_series_cube = cube.extract(iris.Constraint(projection_y_coordinate=closest_coordinates[1], 
                                                          projection_x_coordinate= closest_coordinates[2]))
else:
    time_series_cube = cube.extract(iris.Constraint(grid_latitude=closest_coordinates[1], 
                                                      grid_longitude= closest_coordinates[2]))

#############################################################################
# Plot the grids highlighting the locations of the cells determined as being
# those closest to the location of interest
#############################################################################
plot_grid_highlight_cells(cube, target_crs,  {'init' :'epsg:3785'}, 
                               sample_point, closest_coordinates[0] )

#############################################################################
# Convert to dataframe
#############################################################################
# Define location to save dataframe to
if string == '_reformatted/rf_':
    filename = "Outputs/CEH-GEAR_reformatted/IndividualCells_data/rf_df.csv"
elif string =='_regridded_2.2km/LinearRegridding/rg_':
    filename = "Outputs/CEH-GEAR_regridded_2.2km/LinearRegridding/IndividualCells_data/rg_df_nn.csv"
elif string =='_regridded_2.2km/NearestNeighbour/rg_':
    filename = "Outputs/CEH-GEAR_regridded_2.2km/NearestNeighbour/IndividualCells_data/rg_df_lin.csv"
print("Creating dataframe")

# Save dataframe
df =pd.DataFrame({"time_stamp" : time_series_cube.coord('time').points,
                     "Rainfall": time_series_cube.data})
df['Date_formatted']  = pd.to_datetime(df['time_stamp'], unit='s')\
               .dt.strftime('%Y-%m-%d %H:%M:%S')
df.to_csv(filename, index = False)




