'''
This 
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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/PointLocationStats/PlotPDFs')
from PDF_plotting_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_geometry_functions import *

# Define string which is used to establish the filepath to the files 
# containing the regridded/reformatted files  
string = '_regridded_2.2km/NearestNeighbour/rg_'
# '_reformatted/rf_' , '_regridded_2.2km/LinearRegridding/rg_'

# Define target_crs, dependent on whether using reformatted or regridded data
if string == '_reformatted/rf_':
    target_crs = {'init' :'epsg:27700'}
else:
    target_crs = {'init' :'epsg:4326'}

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
################################################################   
cube = create_trimmed_cube(leeds_at_centre_gdf, string, target_crs)

################################################################
# Trim even more for testing
################################################################
#cube= cube[:,1:2, 1:2]
# test plotting
#iplt.pcolormesh(cube[18,:,:])

################################################################
# Create a numpy array containing all the precipitation values from across
# all 20 years of data and all positions in the cube
################################################################
# # Load data
print("Loading data")
data = cube.data
print("Loaded data")

# # Define length of variables defining spatial positions
lat_length= cube.shape[1]
lon_length= cube.shape[2]
print("Defined length of coordinate dimensions")
print(lat_length, lon_length)

# Create an empty array to fill with data
all_the_data = np.array([])

# Loop through each position in the cube (define by combination of i (lat_length)
# and j (lon_length)) 
print("entering loop through coordinates")
total = 0
for i in range(0,lat_length):
    for j in range(0,lon_length):
        # Print the position
        print(i,j)
        # Define the filename
        # If a file of this name already exists saved, then read in this file
        filename = basic_filepath  + "interim/{}_{}.npy".format(i,j)
        if os.path.isfile(filename):
            data_slice = np.load(basic_filepath + "interim/{}_{}.npy".format(i,j))
            total = total + data_slice.shape[0]
            print("File exists")
        # If a file of this name does not already exist, then:
        # Take just this slice from the data and save it 
        else:
            # Take slice from loaded data
            data_slice = data[:,i,j]
            # Remove mask
            data_slice = data_slice.data
            # Save to file
            np.save(basic_filepath + "interim/{}_{}.npy".format(i,j), data_slice) 
            total = total + data_slice.shape[0]
            print("File does not exist")
        # Add the slice to the array containing all the data from all the locations
        all_the_data = np.append(all_the_data,data_slice)

# Delete na values -
# This is why the length of the output "leeds-at-centre.npy" does not match
# the number of 33 * 37 * 219144
# RG -- First 10 values in each of the (33*37) cells are NA
# RF -- first 10 values in each of the (73*83) cells are NA
all_the_data = all_the_data[~np.isnan(all_the_data)]

### Save as numpy array
print("saving data")
np.save(basic_filepath + "leeds-at-centre.npy", all_the_data)   
print("saved data")

#----------------------------------------------------------------------
# Load data, and convert to dataframe
#----------------------------------------------------------------------
# Load data
# leeds_rg = np.load("Outputs/CEH-GEAR_regridded_2.2km/leeds-at-centre.npy")
# leeds_rf = np.load("Outputs/CEH-GEAR_reformatted/leeds-at-centre.npy")

# # Convert to dataframe
# leeds_rg = pd.DataFrame({"Precipitation (mm/hr)" : leeds_rg})
# leeds_rf = pd.DataFrame({"Precipitation (mm/hr)" : leeds_rf})

# ##############################################################################
# # Setting up dictionary
# ##############################################################################
# my_dict = {}
# my_dict['Original 1km'] = leeds_rf
# my_dict['Regridded 2.2km'] = leeds_rg

# ##############################################################################
# # Plotting
# ##############################################################################
# x_axis = 'linear'
# y_axis = 'log'
# bin_nos =40
# bins_if_log_spaced= bin_nos

# # Equal spaced   
# equal_spaced_histogram(my_dict, bin_nos, x_axis, y_axis)

# # Log spaced histogram
# log_spaced_histogram(my_dict, bin_nos,x_axis, y_axis)    
 
# # Fractional contribution
# fractional_contribution(my_dict, bin_nos,x_axis, y_axis) 
             
# # Log histogram with adaptation     
# log_discrete_histogram(my_dict, 100,x_axis, y_axis) 

# np.histogram(df['Precipitation (mm/hr)'], bins=bin_nos, density=True)
# plt.hist(df['Precipitation (mm/hr)'], bins =40)

# # ##########################################################################
# # # Percentile plots
# # ##########################################################################
# keys = []
# p_99_9999 = []
# p_99_999 = []
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
#     keys.append(key)
#     p_99_9999.append(df['Precipitation (mm/hr)'].quantile(0.999999))
#     p_99_999.append(df['Precipitation (mm/hr)'].quantile(0.99999))
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
    
    
# df= pd.DataFrame({'Key':keys, '50': p_50,
#                   '60': p_60, '70': p_70,  
#                   '80': p_80, '90': p_90,
#                   '95': p_95, '99': p_99,
#                   '99.5': p_99_5, '99.9': p_99_9,
#                 '99.95': p_99_95, '99.99': p_99_99,
#                 '99.999': p_99_999, '99.9999': p_99_9999}) 


# test = df.transpose()
# test = test.rename(columns=test.iloc[0]).drop(test.index[0])

# # Plot
# navy_patch = mpatches.Patch(color='navy', label='Original 1km')
# red_patch = mpatches.Patch(color='firebrick', label='Regridded 2.2km')

# for key, value in my_dict.items():
#     print(key)
#     if key == 'Original 1km':
#         filtered = test[key]
#         filtered = filtered[5:]
#         plt.plot(filtered, color = 'navy')
#     if key == 'Regridded 2.2km':
#         filtered = test[key]
#         filtered = filtered[5:]
#         plt.plot(filtered, color = 'firebrick')
#     plt.xlabel('Percentile')
#     plt.ylabel('Precipitation (mm/hr)')
#     plt.legend(handles=[red_patch, navy_patch])
#     plt.yscale('linear')
#     plt.xticks(rotation = 23)


