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

# ################################################################
# # Loop through ensemble members and load in data for whole of leeds and trim
# # to contain only data from the overlapping time period
# ################################################################
# # Create a dictionary to store results
leeds_data_dict = {}
leeds_data_dict_overlapping = {}

# Loop through ensemble members
for resolution in ['2.2km', '12km', '2.2km_regridded_12km']:
    # Repeat this 1221 times to be the same length as the precip data for whole of Leeds
    # This is to do with the number of cells (so for 12km and 2.2km_regridded_12km it is 36)
    if resolution == '2.2km':
        model_times = np.tile(model_times_2_2km, 1221)
    elif resolution == '2.2km_regridded_12km':
         model_times = np.tile(model_times_2_2km_regridded, 36)
    elif resolution == '12km':
        model_times = np.tile(model_times_12km, 36)

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
        dict['Model {}'.format(resolution)] = pd.concat(frames)
        
        # Delete the individual ensemble member dataframes
        keys_to_remove =("EM01_{}".format(resolution), "EM04_{}".format(resolution), "EM05_{}".format(resolution), "EM06_{}".format(resolution), "EM07_{}".format(resolution), "EM08_{}".format(resolution),
                     "EM09_{}".format(resolution), "EM10_{}".format(resolution), "EM11_{}".format(resolution), "EM12_{}".format(resolution), "EM13_{}".format(resolution), "EM15_{}".format(resolution))
        for key in keys_to_remove:
            if key in dict:
                del dict[key]

################################################################
################################################################
####### Add both native and regridded observations data to dictionary
################################################################
################################################################
print("Making dicts")
# Repeat times 6083 times to be the same length as the precip data for whole of Leeds  (73 cells x 83 cells)
leeds_data_dict['Observations'] =  pd.DataFrame({"Precipitation (mm/hr)" :  np.load("Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/leeds-at-centre.npy"),
                                       'Date' : np.tile(np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True), 6059)})
# Repeat time data 1221 times to be the same length as the precip data for whole of Leeds
leeds_data_dict['Observations Regridded_12km'] =  pd.DataFrame({"Precipitation (mm/hr)" : np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy"),
                                       'Date' : np.tile(np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True), 36)})
# Repeat time data 1221 times to be the same length as the precip data for whole of Leeds
leeds_data_dict['Observations Regridded_2.2km'] = pd.DataFrame({"Precipitation (mm/hr)" :  np.load("Outputs/TimeSeries/CEH-GEAR/2.2km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy"),
                                       'Date' : np.tile(np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps.npy", allow_pickle = True), 1221)})

####### Add both native and regridded observations data to dictionary
leeds_data_dict_overlapping['Observations'] =  observations[(observations['Date'] >= '1990-01-01 00:00:00')
                                                & (observations['Date']<= '2000-11-30 23:00:00 ')]
leeds_data_dict_overlapping['Observations Regridded_2.2km'] =  observations_regridded_2_2km[(observations_regridded_2_2km['Date'] >= '1990-01-01 00:00:00')
                                                & (observations_regridded_2_2km['Date'] <= '2000-11-30 23:00:00 ')]
leeds_data_dict_overlapping['Observations Regridded_12km'] = observations_regridded_12km[(observations_regridded_12km['Date'] >= '1990-01-01 00:00:00')
                                                & (observations_regridded_12km['Date'] <= '2000-11-30 23:00:00 ')]


##############################################################################

##############################################################################
# Plotting
##############################################################################
x_axis = 'linear'
y_axis = 'log'
bin_nos = 20 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = 250
bins_if_log_spaced= bin_nos

##############################################################
# All resolutions
##############################################################
for dict, overlapping_status in zip([leeds_data_dict, leeds_data_dict_overlapping], ["","_Overlapping"]):
    print(dict.keys(), overlapping_status)
    cols_dict = {'Observations' : 'darkgoldenrod',
                 'Observations Regridded_2.2km' : 'tomato',
                 'Observations Regridded_12km' : 'darkred',
                 'Combined EMs_12km' : 'navy',
                 'Combined EMs_2.2km' : 'slateblue',
                 'Combined EMs_2.2km_regridded_12km': 'teal'}
    # Create patches
    patches= []
    for key, val in cols_dict.items():
        patch = mpatches.Patch(color= val, label= key)
        patches.append(patch)

    # Create plot
    log_discrete_histogram_lesslegend(dict, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                      patches, True, xlim, x_axis, y_axis)
    #Save 
    plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/PDFs/FullTimePeriod_RCMvsCPMvsObs/All{}.png".format(overlapping_status))


####### Plot just Model, to see effect of regridding
just_model = leeds_data_dict.copy()
del just_model['Observations Regridded_2.2km'], just_model['Observations'], just_model['Observations Regridded_12km']

cols_dict = {'Combined EMs_12km' : 'navy',
             'Combined EMs_2.2km' : 'slateblue',
             'Combined EMs_2.2km_regridded_12km': 'teal'}
# Create patches
patches= []
for key, val in cols_dict.items():
    patch = mpatches.Patch(color= val, label= key)
    patches.append(patch)

# Create plot
log_discrete_histogram_lesslegend(just_model, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                  patches, True, False, x_axis, y_axis)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/PDFs/FullTimePeriod_RCMvsCPMvsObs/JustModel.png")


###############################################################
####### Plot just Obs, to see effect of regridding
just_obs = leeds_data_dict.copy()
del just_obs['Combined EMs_12km'], just_obs['Combined EMs_2.2km'], just_obs['Combined EMs_2.2km_regridded_12km']

cols_dict = {'Observations' : 'darkgoldenrod',
                 'Observations Regridded_2.2km' : 'tomato',
                 'Observations Regridded_12km' : 'darkred'}
# Create patches
patches= []
for key, val in cols_dict.items():
    patch = mpatches.Patch(color= val, label= key)
    patches.append(patch)

# Create plot
log_discrete_histogram_lesslegend(just_obs, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                  patches, True, False, x_axis, y_axis)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/PDFs/FullTimePeriod_RCMvsCPMvsObs/JustObs.png")


###############################################################
####### Plot just 12km
just_12km = leeds_data_dict.copy()
del just_12km['Combined EMs_2.2km'], just_12km['Observations Regridded_2.2km'], just_12km['Observations']

cols_dict = {'Observations Regridded_12km' : 'darkred',
             'Combined EMs_12km' : 'navy',
             'Combined EMs_2.2km_regridded_12km': 'teal'}

# Create patches
patches= []
for key, val in cols_dict.items():
    patch = mpatches.Patch(color= val, label= key)
    patches.append(patch)

# Create plot
log_discrete_histogram_lesslegend(just_12km, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                  patches, True, False, x_axis, y_axis)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/PDFs/FullTimePeriod_RCMvsCPMvsObs/Just12kms.png")

##################### Better legend
just_12km = leeds_data_dict.copy()
del just_12km['Combined EMs_2.2km'], just_12km['Observations Regridded_2.2km'], just_12km['Observations']

cols_dict = {'Observations Regridded_12km' : 'darkred',
             'Combined EMs_12km' : 'navy',
             'Combined EMs_2.2km_regridded_12km': 'teal'}

# Create patches
patches= []    
patches.append(mpatches.Patch(color= 'darkred', label= 'CEH-GEAR'))
patches.append(mpatches.Patch(color= 'navy', label= 'UKCP18 12km'))
patches.append(mpatches.Patch(color= 'teal', label= 'UKCP18 2.2km'))

# Create plot
log_discrete_histogram_lesslegend(just_12km, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                  patches, True, False, x_axis, y_axis)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/PDFs/FullTimePeriod_RCMvsCPMvsObs/Just12kms.png")
