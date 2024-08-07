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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from PDF_plotting_functions import *
from Spatial_geometry_functions import *

################################################################
# Create the spatial datafiles needed
################################################################   
# Create region with Leeds at the centre
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:27700'})
# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})
 
################################################################
# Load data, and convert to dataframe
################################################################
# Load data
leeds_rg_nn = np.load("Outputs/TimeSeries/CEH-GEAR/2.2km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy")
leeds_rg_lin = np.load("Outputs/TimeSeries/CEH-GEAR/2.2km/LinearRegridding/leeds-at-centre/leeds-at-centre.npy")
leeds_rf = np.load("Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/leeds-at-centre.npy")

# Convert to dataframe
leeds_rg_nn = pd.DataFrame({"Precipitation (mm/hr)" : leeds_rg_nn})
leeds_rg_lin = pd.DataFrame({"Precipitation (mm/hr)" : leeds_rg_lin})
leeds_rf = pd.DataFrame({"Precipitation (mm/hr)" : leeds_rf})

# ##############################################################################
# # Setting up dictionary
# ##############################################################################
my_dict = {}
my_dict['Original 1km'] = leeds_rf
my_dict['Regridded 2.2km - nearest neighbour'] = leeds_rg_nn
my_dict['Regridded 2.2km - linear'] = leeds_rg_lin

##############################################################################
# Plotting
##############################################################################
cols_dict = {'Original 1km': "navy",
             'Regridded 2.2km - nearest neighbour': 'firebrick',
             'Regridded 2.2km - linear': 'olive'}

x_axis = 'linear'
y_axis = 'log'
bin_nos =50
bins_if_log_spaced= bin_nos

# Equal spaced   
#equal_spaced_histogram(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis)

# Log spaced histogram
log_spaced_histogram(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis)    
plt.savefig("Scripts/UKCP18/Regridding/TestingRegridding/leeds-at-centre/Figs/log_spaced.png")
 
 
# Fractional contribution
fractional_contribution(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis) 
plt.savefig("Scripts/UKCP18/Regridding/TestingRegridding/leeds-at-centre/Figs/fract_contribution.png")
             
# Log histogram with adaptation     
log_discrete_histogram(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis) 
plt.savefig("Scripts/UKCP18/Regridding/TestingRegridding/leeds-at-centre/Figs/log_discrete.png")


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


