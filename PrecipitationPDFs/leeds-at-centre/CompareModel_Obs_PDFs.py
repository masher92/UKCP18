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
# Create the spatial datafiles needed
################################################################   
# Create region with Leeds at the centre
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:27700'})
# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})

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
model_times = np.load('Outputs/TimeSeries/UKCP18/{}/leeds-at-centre/timestamps.npy'.format(timeperiod))

# Set value as NA for values not in required date range
for i in range(0,78480):
    print(i)
    model_times[i] = '0'

# Repeat this 1221 times to be the same length as the precip data for whole of Leeds 
model_times_allcells = np.tile(model_times, 1221)    

################################################################
# Loop through ensemble members and load in data for whole of leeds and trim
# to contain only data from the overlapping time period
################################################################
# Create a dictionary to store results
leeds_data_dict = {}
leeds_data_dict_overlapping = {}

# Loop through ensemble members
for em in ems:
    print(em)
    
    # Load in 20 years of model data for the whole of leeds
    leeds_data = np.load("Outputs/TimeSeries/UKCP18/{}/leeds-at-centre/{}/leeds-at-centre.npy".format(timeperiod, em))
    # Join to corresponding dates/times
    leeds_data_withtimes = pd.DataFrame({"Date" : model_times_allcells,
                                   'Precipitation (mm/hr)' :leeds_data})
    
    leeds_data_dict['EM{}'.format(em)] = leeds_data_withtimes

    # Keep only data from overlapping times 
    leeds_data_overlapping = leeds_data_withtimes.loc[leeds_data_withtimes['Date'] != '0']
    
    # Add data to dictionary
    leeds_data_dict_overlapping['EM{}'.format(em)] = leeds_data_overlapping


# Create a dataframe containing the data from across all ensemble members
for dict in [leeds_data_dict, leeds_data_dict_overlapping]:

    frames = [dict['EM01'], dict['EM04'], dict['EM05'], dict['EM06'],
              dict['EM07'], dict['EM08'], dict['EM09'], dict['EM10']
              , dict['EM11'], dict['EM12'], dict['EM13'], dict['EM15']] 
    leeds_all_ems = pd.concat(frames)
    
    # Add this to the dictionary
    dict['Combined EMs'] = leeds_all_ems

################################################################
# Trim observations data to also only include data from the overlapping time period
################################################################
# Observations dates data
obs_times = np.load("Outputs/TimeSeries/CEH-GEAR_regridded/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True)

####### Regridded data
# Repeat time data 1221 times to be the same length as the precip data for whole of Leeds 
obs_times_allcells_regridded = np.tile(obs_times, 1221)    
# Load in regridded precip data
observations_regridded = np.load("Outputs/TimeSeries/CEH-GEAR_regridded/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy")

# Join dates data and precip data
observations_regridded = pd.DataFrame({"Precipitation (mm/hr)" : observations_regridded,
                                       'Date' : obs_times_allcells_regridded})
####### Native data
# Repeat this 6083 times to be the same length as the precip data for whole of Leeds  (73 cells x 83 cells)
obs_times_allcells = np.tile(obs_times, 6059) 
# Load in native precip data
observations = np.load("Outputs/TimeSeries/CEH-GEAR/leeds-at-centre/leeds-at-centre.npy")

# Join dates data and precip data
observations = pd.DataFrame({"Precipitation (mm/hr)" : observations,
                                       'Date' : obs_times_allcells})


####### Add both native and regridded observations data to dictionary
leeds_data_dict['Observations'] = observations
leeds_data_dict['Observations Regridded'] = observations_regridded
    
# Remove data not in the overlapping time period
observations_regridded_overlapping = observations_regridded[(observations_regridded['Date'] >= '1990-01-01 00:00:00') 
                                                & (observations_regridded['Date'] <= '2000-11-30 23:00:00 ')]

observations_overlapping = observations[(observations['Date'] >= '1990-01-01 00:00:00') 
                                                & (observations['Date']<= '2000-11-30 23:00:00 ')]

####### Add both native and regridded observations data to dictionary
leeds_data_dict_overlapping['Observations'] = observations_overlapping
leeds_data_dict_overlapping['Observations Regridded'] = observations_regridded_overlapping

##############################################################################
# Create dictionaries 
##############################################################################
################# Just model data
just_ems_dict = leeds_data_dict.copy()
del just_ems_dict['Combined EMs']
del just_ems_dict['Observations']
del just_ems_dict['Observations Regridded']

################# Model AND Observations data
############# Ful time period
# All ensemble members
all_ems_obs_dict  = leeds_data_dict.copy()
del all_ems_obs_dict['Combined EMs']

# Combined ensemble members
combined_ems_obs_dict= leeds_data_dict.copy()
keys_to_remove =("EM01", "EM04", "EM05", "EM06", "EM07", "EM08",
                 "EM09", "EM10", "EM11", "EM12", "EM13", "EM15")
for key in keys_to_remove:
    if key in combined_ems_obs_dict:
        del combined_ems_obs_dict[key]
        
############# Overlappping time period
# All ensemble members
all_ems_obs_dict_overlapping  = leeds_data_dict_overlapping.copy()
del all_ems_obs_dict_overlapping['Combined EMs']

# Combined ensemble members
combined_ems_obs_dict_overlapping = leeds_data_dict_overlapping.copy()
keys_to_remove =("EM01", "EM04", "EM05", "EM06", "EM07", "EM08",
                 "EM09", "EM10", "EM11", "EM12", "EM13", "EM15")
for key in keys_to_remove:
    if key in combined_ems_obs_dict_overlapping:
        del combined_ems_obs_dict_overlapping[key]


##############################################################################
# Plotting
##############################################################################
cols_dict = {'Observations' : 'firebrick',
             'Observations Regridded' : 'green',
             'Combined EMs' : 'navy',
             'EM01': "navy", 'EM04': 'navy', 'EM05': 'navy','EM06': 'navy',
             'EM07': 'navy','EM08': 'navy','EM09': 'navy',  'EM10': 'navy',
             'EM11': 'navy','EM12': 'navy','EM13': 'navy','EM15': 'navy'}

x_axis = 'linear'
y_axis = 'log'
bin_nos = 30 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = 250
bins_if_log_spaced= bin_nos

#################### Full time period
####### Just ensemble members
patches= []#=
#patch = mpatches.Patch(color='navy', label='Model')
#patches.append(patch)
log_discrete_histogram_lesslegend(just_ems_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 

####### Combined ensemble members + Obs
patches= []
patch = mpatches.Patch(color='navy', label='Model')
patches.append(patch)
patch = mpatches.Patch(color='green', label='Observations Regridded')
patches.append(patch)
patch = mpatches.Patch(color='firebrick', label='Observations')
patches.append(patch)

log_discrete_histogram_lesslegend(combined_ems_obs_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 

####### All ensemble members + Obs
log_discrete_histogram_lesslegend(all_ems_obs_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, False, xlim, x_axis, y_axis) 

#################### Overlapping time period
####### Combined ensemble members + Obs
log_discrete_histogram_lesslegend(combined_ems_obs_dict_overlapping, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, False, xlim, x_axis, y_axis) 
####### All ensemble members + Obs
log_discrete_histogram_lesslegend(all_ems_obs_dict_overlapping, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, False,xlim, x_axis, y_axis) 



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


