### Does it matter that 12km model is daily rather than hourly?

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

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

################################################################
# Define variables and set up environment
################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from PDF_plotting_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_geometry_functions import *

# Define ensemble member numbers
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
# Define time period
timeperiod = 'Baseline'

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
# # Load in timestamps that relate to one cell's worth of data
model_times_2_2km_regridded = np.load('Outputs/TimeSeries/UKCP18/2.2km_regridded_12km/Baseline/leeds-at-centre/timestamps.npy'.format(timeperiod))
model_times_12km = np.load('Outputs/TimeSeries/UKCP18/12km/Baseline/leeds-at-centre/timestamps.npy'.format(timeperiod))
model_times_2_2km = np.load('Outputs/TimeSeries/UKCP18/2.2km/Baseline/leeds-at-centre/timestamps.npy'.format(timeperiod))

# Set value as NA for values not in required date range
# THis is to do with number of hours, so for 2.2km and 2.2km regridded it is the same
for i in range(0,78480):
    model_times_2_2km_regridded[i] = '0'
for i in range(0,2909):
    model_times_12km[i] = '0'
for i in range(0,78480):
    model_times_2_2km[i] = '0'

# Repeat this 1221 times to be the same length as the precip data for whole of Leeds
# THis is to do with the number of cells (so for 12km and 2.2km_regridded_12km it is 36)
model_times_2_2km = np.tile(model_times_2_2km, 1221)
model_times_2_2km_regridded= np.tile(model_times_2_2km_regridded, 36)
model_times_12km = np.tile(model_times_12km, 36)
#
# ################################################################
# # Loop through ensemble members and load in data for whole of leeds and trim
# # to contain only data from the overlapping time period
# ################################################################
# # Create a dictionary to store results
leeds_data_dict = {}
leeds_data_dict_overlapping = {}

# Loop through ensemble members
for resolution in ['2.2km', '12km', '2.2km_regridded_12km']:
    if resolution == '2.2km':
        model_times = model_times_2_2km
    elif resolution == '2.2km_regridded_12km':
         model_times = model_times_2_2km_regridded
    elif resolution == '12km':
        model_times = model_times_12km

    for em in ems:
        print(em)

        # Load in 20 years of model data for the whole of leeds
        leeds_data = np.load("Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/leeds-at-centre.npy".format(resolution, timeperiod, em))

        # Join to corresponding dates/times
        leeds_data = pd.DataFrame({"Date" : model_times,
                                   'Precipitation (mm/hr)' :leeds_data})

        # Add to dictionary
        leeds_data_dict['EM{}_{}'.format(em, resolution)] = leeds_data

        # Keep only data from overlapping times
        leeds_data_overlapping = leeds_data.loc[leeds_data['Date'] != '0']

        # Add data to dictionary
        leeds_data_dict_overlapping['EM{}_{}'.format(em, resolution)] = leeds_data_overlapping

        # delete varibles to save memory
        del leeds_data, leeds_data_overlapping

# Create a dataframe containing the data from across all ensemble members
for dict in [leeds_data_dict, leeds_data_dict_overlapping]:
    for resolution in ['2.2km', '12km', '2.2km_regridded_12km']:
        frames = [dict['EM01_{}'.format(resolution)], dict['EM04_{}'.format(resolution)], dict['EM05_{}'.format(resolution)], dict['EM06_{}'.format(resolution)],
                  dict['EM07_{}'.format(resolution)], dict['EM08_{}'.format(resolution)], dict['EM09_{}'.format(resolution)], dict['EM10_{}'.format(resolution)]
                  , dict['EM11_{}'.format(resolution)], dict['EM12_{}'.format(resolution)], dict['EM13_{}'.format(resolution)], dict['EM15_{}'.format(resolution)]]

        # Add the concat of all these frames to the dictionary
        dict['Combined EMs_{}'.format(resolution)] = pd.concat(frames)
        
        # Delete the individual ensemble member dataframes
        keys_to_remove =("EM01_{}".format(resolution), "EM04_{}".format(resolution), "EM05_{}".format(resolution), "EM06_{}".format(resolution), "EM07_{}".format(resolution), "EM08_{}".format(resolution),
                     "EM09_{}".format(resolution), "EM10_{}".format(resolution), "EM11_{}".format(resolution), "EM12_{}".format(resolution), "EM13_{}".format(resolution), "EM15_{}".format(resolution))
        for key in keys_to_remove:
            if key in dict:
                del dict[key]


################################################################
################################################################
# Trim observations data to also only include data from the overlapping time period
################################################################
################################################################
# Observations dates data
obs_times = np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True)

####### Regridded 12km
# Load in regridded precip data
observations_regridded_12km = np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy")
# Join dates data and precip data
# Repeat time data 1221 times to be the same length as the precip data for whole of Leeds
observations_regridded_12km = pd.DataFrame({"Precipitation (mm/hr)" : observations_regridded_12km,
                                       'Date' : np.tile(np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True), 36)})

####### Regridded 2.2km
# Load in regridded precip data
observations_regridded_2_2km = np.load("Outputs/TimeSeries/CEH-GEAR/2.2km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy")
# Join dates data and precip data
# Repeat time data 1221 times to be the same length as the precip data for whole of Leeds
observations_regridded_2_2km = pd.DataFrame({"Precipitation (mm/hr)" : observations_regridded_2_2km,
                                       'Date' : np.tile(np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True), 1221)})

####### Orignal data
# Load in native precip data
observations = np.load("Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/leeds-at-centre.npy")
# Join dates data and precip data
# repeat times 6083 times to be the same length as the precip data for whole of Leeds  (73 cells x 83 cells)
observations = pd.DataFrame({"Precipitation (mm/hr)" : observations,
                                       'Date' : np.tile(np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True), 6059)})

################################################################
################################################################
####### Add both native and regridded observations data to dictionary
################################################################
################################################################
print("Making dicts")
# leeds_data_dict['Observations'] = observations
# leeds_data_dict['Observations Regridded_12km'] = observations_regridded_12km
# leeds_data_dict['Observations Regridded_2.2km'] = observations_regridded_2_2km

# # Remove data not in the overlapping time period#
observations_regridded_2_2km_overlapping = observations_regridded_2_2km[(observations_regridded_2_2km['Date'] >= '1990-01-01 00:00:00')
                                                & (observations_regridded_2_2km['Date'] <= '2000-11-30 23:00:00 ')]

# observations_regridded_12km_overlapping = observations_regridded_12km[(observations_regridded_12km['Date'] >= '1990-01-01 00:00:00')
#                                                 & (observations_regridded_12km['Date'] <= '2000-11-30 23:00:00 ')]
#
# observations_overlapping = observations[(observations['Date'] >= '1990-01-01 00:00:00')
#                                                 & (observations['Date']<= '2000-11-30 23:00:00 ')]
#
# ####### Add both native and regridded observations data to dictionary
# leeds_data_dict_overlapping['Observations'] = observations_overlapping
# leeds_data_dict_overlapping['Observations Regridded_2.2km'] = observations_regridded_2_2km_overlapping
# leeds_data_dict_overlapping['Observations Regridded_12km'] = observations_regridded_12km_overlapping

##############################################################################
##############################################################################
# Create dictionaries
##############################################################################
##############################################################################
# Model AND Observations data, Full time period, All ensemble members
# Combined ensemble members
# combined_ems_obs_dict= leeds_data_dict.copy()
# for reso
# keys_to_remove =("EM01", "EM04", "EM05", "EM06", "EM07", "EM08",
#                  "EM09", "EM10", "EM11", "EM12", "EM13", "EM15")
# for key in keys_to_remove:
#     if key in combined_ems_obs_dict:
#         del combined_ems_obs_dict[key]

############# Overlappping time period
# # Combined ensemble members
# combined_ems_obs_dict_overlapping = leeds_data_dict_overlapping.copy()
# keys_to_remove =("EM01", "EM04", "EM05", "EM06", "EM07", "EM08",
#                  "EM09", "EM10", "EM11", "EM12", "EM13", "EM15")
# for key in keys_to_remove:
#     if key in combined_ems_obs_dict_overlapping:
#         del combined_ems_obs_dict_overlapping[key]


##############################################################################
# Plotting
##############################################################################
####### Add both native and regridded observations data to dictionary

del dict
del leeds_data
del leeds_data_overlaping
del leeds_all_ems
del leeds_data_overlapping
del leeds_data_withtimes
del model_times_2_2km_regridded
del model_times_2_2km_regridded_allcells
del model_times_2_2km_allcells
del obs_times_allcells
del obs_times_allcells_regridded_2_2km
del observations
del obs_times
del observations_regridded_2_2km
del observations_regridded_12km
del model_times
del obs_times_allcells_regridded_12km
del combined_ems_2_2km

just_12kms = combined_ems_obs_dict.copy()
del just_12kms['Observations Regridded_2.2km']
del just_12kms['Combined EMs_2.2km']
del just_12kms['Observations']


combined_ems_obs_dict['Observations'] = observations
combined_ems_obs_dict['Observations Regridded_12km'] = observations_regridded_12km
combined_ems_obs_dict['Observations Regridded_2.2km'] = observations_regridded_2_2km

cols_dict = {'Observations' : 'lawngreen',
             'Observations Regridded_2.2km' : 'limegreen',
             'Observations Regridded_12km' : 'darkgreen',
             'Combined EMs_12km' : 'navy',
             'Combined EMs_2.2km' : 'slateblue',
             'Combined EMs_2.2km_regridded_12km': 'firebrick'}

x_axis = 'linear'
y_axis = 'log'
bin_nos = 20 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = 250
bins_if_log_spaced= bin_nos

#################### Full time period
####### Just ensemble members
patches= []#=
####### Combined ensemble members + Obs
patches= []
patch = mpatches.Patch(color='slateblue', label='Model (2.2km)')
patches.append(patch)
patch = mpatches.Patch(color='navy', label='Model (12km)')
patches.append(patch)
patch = mpatches.Patch(color='rebeccapurple', label='Model (Regridded 12km)')
patches.append(patch)
patch = mpatches.Patch(color='limegreen', label='Observations Regridded 2.2km')
patches.append(patch)
patch = mpatches.Patch(color='darkgreen', label='Observations Regridded 12km')
patches.append(patch)
patch = mpatches.Patch(color='lawngreen', label='Observations Original 1km')
patches.append(patch)

log_discrete_histogram_lesslegend(combined_ems_obs_dict, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                  patches, True, xlim, x_axis, y_axis)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/PDFs/FullTimePeriod_RCMvsCPMvsObs/All.png")


