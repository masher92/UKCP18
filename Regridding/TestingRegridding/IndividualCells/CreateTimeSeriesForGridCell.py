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

################################################################
# Create the spatial datafiles needed
################################################################   
# Create region with Leeds at the centre
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:27700'})
# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})

# Define string which is used to establish the filepath to the files 
# containing the regridded/reformatted files  
strings_dict  = {'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_': '1km',
            'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/LinearRegridding/rg_': '2.2km/LinearRegridding',
             'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_': '2.2km/NearestNeighbour'}

# Coordinates of location of interest
sample_point = [('grid_latitude', 53.796638), ('grid_longitude', -1.592600)]

# Create dictionary to store results
my_dict = {}

# Loop through 3 options
for string1, string2 in strings_dict.items():
  print(string1)
  print(string2)

   # Define target_crs, dependent on whether using reformatted or regridded data
  if string1 =='datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_':
        target_crs = {'init' :'epsg:27700'}
  else:
        target_crs = {'init' :'epsg:4326'}

  ################################################################
  # Reads in all monthly (either regridded or reformatted) CEH-GEAR data files 
  # Create a cube trimmed to the oputline of the square area surrounding Leeds
  # Containing this data over time 
  ################################################################   
  cube = create_trimmed_cube(leeds_at_centre_gdf, string1, target_crs)
      
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
  if string1 == 'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_':
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
  #output_filename = "Outputs/TimeSeries/CEH-GEAR/{}/Random_GridCells/{}_{}.csv".format(string2, sample_point[0], samplepoint[1])
  
  # Save dataframe
  df =pd.DataFrame({"time_stamp" : time_series_cube.coord('time').points,
                       "Rainfall": time_series_cube.data})
  df['Date_formatted']  = pd.to_datetime(df['time_stamp'], unit='s')\
                 .dt.strftime('%Y-%m-%d %H:%M:%S')
  #df.to_csv(output_filename, index = False)

  # Save to dictionary
  my_dict["{}".format(string2)] = df

##############################################################################
# Setting up colours dictionary
##############################################################################
# Set up colours dictionary to use in plotting
cols_dict = {'Original 1km':"navy",
             '2.2km/LinearRegridding': 'firebrick',
             '2.2km/NearestNeighbour': 'olive'}

##############################################################################
# Plotting - complex PDFs
##############################################################################
x_axis = 'linear'
y_axis = 'log'
bin_nos =30
bins_if_log_spaced= bin_nos

# Equal spaced   
equal_spaced_histogram(my_dict, cols_dict, bin_nos, x_axis, y_axis)

# Log spaced histogram
log_spaced_histogram(my_dict, cols_dict, bin_nos,x_axis, y_axis)    
 
# Fractional contribution
fractional_contribution(my_dict, cols_dict,bin_nos,x_axis, y_axis) 
             
# Log histogram with adaptation     
log_discrete_histogram(my_dict, cols_dict, bin_nos, x_axis, y_axis) 
plt.savefig("Scripts/UKCP18/Regridding/TestingRegridding/IndividualCells/Figs/{}_{}.png".format(string2, sample_point[0], samplepoint[1])


##############################################################################
# Plotting - simple histograms
##############################################################################
# plt.hist(rf_df['Precipitation (mm/hr)'], bins = 200)

# bin_density, bin_edges = np.histogram(rf_df['Precipitation (mm/hr)'], bins= 20, density=True)
# print (bin_edges)

# import matplotlib.pyplot as plt
# plt.bar(bin_edges[:-1], bin_density, width = 1)
# plt.xlim(min(bin_edges), max(bin_edges))
# plt.show()  

# ##########################################################################
# # Percentile plots
# ##########################################################################
# keys = []
# p_99_99 = []
# p_99_95 = []
# p_99_9 = []
# p_99_5 = []
# p_99 = []
# p_95 =[]
# p_90 = []
# p_80 = []
# p_70 = []
# p_60 = []
# p_50 = []
# for key, value in my_dict.items():
#     df = my_dict[key]
#     p_99_99.append(df['Precipitation (mm/hr)'].quantile(0.9999))
#     p_99_95.append(df['Precipitation (mm/hr)'].quantile(0.9995))
#     p_99_9.append(df['Precipitation (mm/hr)'].quantile(0.999))
#     p_99_5.append(df['Precipitation (mm/hr)'].quantile(0.995))
#     p_99.append(df['Precipitation (mm/hr)'].quantile(0.99))
#     p_95.append(df['Precipitation (mm/hr)'].quantile(0.95))
#     p_90.append(df['Precipitation (mm/hr)'].quantile(0.9))
#     p_80.append(df['Precipitation (mm/hr)'].quantile(0.8))
#     p_70.append(df['Precipitation (mm/hr)'].quantile(0.7))
#     p_60.append(df['Precipitation (mm/hr)'].quantile(0.6))
#     p_50.append(df['Precipitation (mm/hr)'].quantile(0.5))
#     keys.append(key)
    
    
# df= pd.DataFrame({'Key':keys, '50': p_50,
#                  '60': p_60, '70': p_70,  
#                   '80': p_80, '90': p_90,
#                  '95': p_95, '99': p_99,
#                  '99.5': p_99_5, '99.9': p_99_9,
#                 '99.95': p_99_95, '99.99': p_99_99}) 


# test = df.transpose()
# test = test.rename(columns=test.iloc[0]).drop(test.index[0])

# # Plot
# navy_patch = mpatches.Patch(color='navy', label='Original 1km')
# red_patch = mpatches.Patch(color='firebrick', label='Regridded 2.2km')

# for key, value in my_dict.items():
#     print(key)
#     if key == 'Original 1km':
#         plt.plot(test[key], color = 'navy')
#     if key == 'Regridded 2.2km':
#         plt.plot(test[key], color = 'firebrick')
#     plt.xlabel('Percentile')
#     plt.ylabel('Precipitation (mm/hr)')
#     plt.legend(handles=[red_patch, navy_patch])
#     plt.yscale('log')
#     plt.xticks(rotation = 23)



