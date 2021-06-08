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
from datetime import datetime  

################################################################
# Define variables and set up environment
################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from PDF_plotting_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/RegriddingObservations')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_geometry_functions import *

# Define ensemble member numbers
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

################################################################
# Load in model times, and define which times are within the period which overlaps between 
# model and observations (1990-01-01 00:00:00 and 2000-11-30 23:00:00 )

# This is tricky to do as the model date uses a 360 day calendar, with each month having 30 days
# Consequently, February has 30 days and these dates cannot be recognised by the Datetime function
# and so it is not possible to trim the data using datetime dates
# Instead, find the index positions of the dates which are within this time period
# and assign these a value of '0' in the array
# This array is then stacked on top of itself 1221 times (this is how many cells 
# there are in the leeds-at-centre array)
# This creates an array of the same length as the leeds-at-centre.npy array which
# contains the precip values.
# These two arrays can then be joined as a dataframe, and all those rows with a '0'
# in the date column are then deleted to leave only the precip values within the
# overlapping time period
################################################################
# Load in timestamps that relate to one cell's worth of data
# baseline_times = np.load('Outputs/TimeSeries/UKCP18/Baseline/leeds-at-centre/timestamps.npy')
# future_near_times = np.load('Outputs/TimeSeries/UKCP18/Future_near/leeds-at-centre/timestamps.npy')

# # Set value as NA for values not in required date range
# for i in range(0,78480):
#     print(i)
#     baseline_times[i] = '0'
#     future_near_times[i] = '0'

# Repeat this 1221 times to be the same length as the precip data for whole of Leeds 
#baseline_times_allcells = np.tile(baseline_times, 1221)    
#future_near_times_allcells = np.tile(future_near_times, 1221)   


################################################################
# Loop through ensemble members and load in data for whole of leeds 
################################################################
# Create a dictionary to store results
#baseline_dict = {}
#future_near_dict = {}
all_dict= {}

# Loop through ensemble members
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
for em in ems:
    for timeperiod in ['Baseline', 'Future_near', 'Future_far']:
        print(em)
        
        # Load in 20 years of model data for the whole of leeds
        leeds_data = np.load("Outputs/TimeSeries/UKCP18/{}/leeds-at-centre/{}/leeds-at-centre.npy".format(timeperiod, em))
        all_dict['EM{}_{}'.format(em, timeperiod)] = leeds_data  
        
        # if timeperiod == 'Baseline':
        #     # Join to corresponding dates/times
        #     leeds_data_withtimes = pd.DataFrame({"Date" : baseline_times_allcells, 'Precipitation (mm/hr)' :leeds_data})
        #     # Add to dictionary
        #     #baseline_dict['EM{}'.format(em)] = leeds_data_withtimes
        #     all_dict['EM{}_{}'.format(em, timeperiod)] = leeds_data_withtimes    
        
        # elif timeperiod == 'Future_near':
        #     # Join to corresponding dates/times
        #     leeds_data_withtimes = pd.DataFrame({"Date" : future_near_times_allcells, 'Precipitation (mm/hr)' :leeds_data})
        #     # Add to dictionary
        #     #future_near_dict['EM{}'.format(em)] = leeds_data_withtimes        
        #     all_dict['EM{}_{}'.format(em, timeperiod)] = leeds_data_withtimes    

##############################################################################
##############################################################################
# Plotting - plot a line for each ensemble member
##############################################################################
##############################################################################
# Create dictionary to specify colours            
cols_dict = {} 
for timeperiod in ['Baseline', 'Future_near', 'Future_far']:
    for em in ems:
        if timeperiod == 'Baseline':
            cols_dict['EM' + em + '_' + timeperiod] = "firebrick"
        elif timeperiod == 'Future_near':        
            cols_dict['EM' + em + '_' + timeperiod] = 'green'
        elif timeperiod == 'Future_far':
            cols_dict['EM' + em + '_' + timeperiod] = 'blue'
    
# Create patches for creating legend
patches= []
patch = mpatches.Patch(color='firebrick', label='1980-2001')
patches.append(patch)
patch = mpatches.Patch(color='green', label='2020-2041')
patches.append(patch)
patch = mpatches.Patch(color='blue', label='2060-2081')
patches.append(patch)

# Define plotting parameters
x_axis = 'linear'
y_axis = 'log'
bin_nos = 30 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = 250
bins_if_log_spaced= bin_nos

# Plot
log_discrete_histogram_lesslegend_array(all_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 

numbers_in_each_bin = log_discrete_with_inset_array(all_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                                  patches, True, xlim = False) 
                

##############################################################################
##############################################################################
# Plotting - combining values from across all ensemble members
##############################################################################
##############################################################################
# Create a dataframe containing the data from across all ensemble members
for timeperiod in ['Baseline', 'Future_near', 'Future_far']:
    # Define frames
    frames = []
    for em in ems:
        frames.append(all_dict['EM{}_{}'.format(em, timeperiod)])
    # join them
    #leeds_all_ems = pd.concat(frames)
    leeds_all_ems = np.concatenate(frames)
    
    all_dict['Combined_ems_{}'.format(timeperiod)]  = leeds_all_ems  

# Create dictionary to specify colours
cols_dict = {'Combined_ems_Baseline' : 'firebrick',
             'Combined_ems_Future_near' : 'green',
             'Combined_ems_Future_far' : 'blue'}

# Define plotting parameters
x_axis = 'linear'
y_axis = 'log'
bin_nos = 30 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = 250
bins_if_log_spaced= bin_nos

# Create a dictionary containing just the df containing the data from across 
# all the ensemble members combined 
just_combined_dict = all_dict.copy()

keys_to_remove = []
for timeperiod in ['Baseline', 'Future_near', 'Future_far']:
    for em in ems:
        keys_to_remove.append('EM{}_{}'.format(em, timeperiod))
for key in keys_to_remove:
    if key in just_combined_dict:
        del just_combined_dict[key]

# Plot
log_discrete_histogram_lesslegend_array(just_combined_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 

numbers_in_each_bin = log_discrete_with_inset_array(just_combined_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                                  patches, True, xlim = False) 


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


