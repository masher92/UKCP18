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
import datetime

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
# define whether to trim to JJA
jja_status = 'jja'

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
model_times_12km = pd.read_csv("Outputs/TimeSeries/UKCP18/12km/Baseline/leeds-at-centre/timestamps_jjaflag.csv")
model_times_2_2km = pd.read_csv("Outputs/TimeSeries/UKCP18/2.2km/Baseline/leeds-at-centre/timestamps_jjaflag.csv")
model_times_2_2km_regridded = pd.read_csv("Outputs/TimeSeries/UKCP18/2.2km_regridded_12km/Baseline/leeds-at-centre/timestamps_jjaflag.csv")

# Set value as NA for values not in required date range
# THis is to do with number of hours, so for 2.2km and 2.2km regridded it is the same
for i in range(0,78480):
    model_times_2_2km_regridded['times'][i] = '0'
for i in range(0,3270):
    model_times_12km['times'][i] = '0'
for i in range(0,78480):
    model_times_2_2km['times'][i] = '0'

# ################################################################
# # Loop through ensemble members and load in data for whole of leeds and trim
# # to contain only data from the overlapping time period
# ################################################################
# # Create a dictionary to store results
leeds_data_dict = {}
leeds_data_dict_overlapping = {}

# Loop through ensemble members
for resolution in ['2.2km', '12km', '2.2km_regridded_12km']:
    print(resolution)
    # Repeat this 1221 times to be the same length as the precip data for whole of Leeds
    # This is to do with the number of cells (so for 12km and 2.2km_regridded_12km it is 36)
    if resolution == '2.2km':
        model_times = pd.concat([model_times_2_2km]* 1221)
        #model_times = np.tile(model_times_2_2km, 1221)
    elif resolution == '2.2km_regridded_12km':
        model_times = pd.concat([model_times_2_2km_regridded]* 36)
         #model_times = np.tile(model_times_2_2km_regridded, 36)
    elif resolution == '12km':
        model_times = pd.concat([model_times_12km]* 36)
        #model_times = np.tile(times, 36)

    for em in ems:
        print(em)

        # Load in 20 years of model data for the whole of leeds
        # Join to corresponding dates/times
        leeds_data = pd.DataFrame({"Date" : model_times['times'],
                                   'Precipitation (mm/hr)' :np.load("Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/leeds-at-centre.npy".format(resolution, timeperiod, em))
                                   ,'jja' : model_times["in_jja"]})
        # JJA?
        if jja_status == 'jja':
            leeds_data = leeds_data[leeds_data['jja'].notna()]

        # Add to dictionary
        leeds_data_dict['EM{}_{}'.format(em, resolution)] = leeds_data

        # Keep only data from overlapping times
        leeds_data_overlapping = leeds_data.loc[leeds_data['Date'] != 0]

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
# 1km -- Repeat times 6083 times to be the same length as the precip data for whole of Leeds  (73 cells x 83 cells)
leeds_data_dict['Observations'] =  pd.DataFrame({"Date" :  pd.concat([pd.read_csv("Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/timestamps_jjaflag.csv")]*6059)['times'],
                                       "Precipitation (mm/hr)" : np.load("Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/leeds-at-centre.npy"),
                                        'jja': pd.concat([pd.read_csv("Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/timestamps_jjaflag.csv")]*6059)['in_jja']})


# 2.2km --- Repeat time data 1221 times to be the same length as the precip data for whole of Leeds
leeds_data_dict['Observations Regridded_2.2km'] =  pd.DataFrame({"Date" :  pd.concat([pd.read_csv("Outputs/TimeSeries/CEH-GEAR/2.2km/NearestNeighbour/leeds-at-centre/timestamps_jjaflag.csv")]*1221)['times'],
                                       "Precipitation (mm/hr)" : np.load("Outputs/TimeSeries/CEH-GEAR/2.2km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy"),
                                        'jja': pd.concat([pd.read_csv("Outputs/TimeSeries/CEH-GEAR/2.2km/NearestNeighbour/leeds-at-centre/timestamps_jjaflag.csv")]*1221)['in_jja']})

# 12km --- Repeat time data 1221 times to be the same length as the precip data for whole of Leeds
leeds_data_dict['Observations Regridded_12km'] =  pd.DataFrame({"Date" :  pd.concat([pd.read_csv("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps_jjaflag.csv")]*36)['times'],
                                       "Precipitation (mm/hr)" : np.load("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/leeds-at-centre.npy"),
                                        'jja': pd.concat([pd.read_csv("Outputs/TimeSeries/CEH-GEAR/12km/NearestNeighbour/leeds-at-centre/timestamps_jjaflag.csv")]*36)['in_jja']})


####### Cut to overlapping period
leeds_data_dict_overlapping['Observations'] =  leeds_data_dict['Observations'][(leeds_data_dict['Observations']['Date'] >= '1990-01-01 00:00:00')
                                                & (leeds_data_dict['Observations']['Date']<= '2000-11-30 23:00:00 ')]
leeds_data_dict_overlapping['Observations Regridded_12km'] = leeds_data_dict['Observations Regridded_12km'][(leeds_data_dict['Observations Regridded_12km']['Date'] >= '1990-01-01 00:00:00')
                                                & (leeds_data_dict['Observations Regridded_12km']['Date'] <= '2000-11-30 23:00:00 ')]
leeds_data_dict_overlapping['Observations Regridded_2.2km'] =  leeds_data_dict['Observations Regridded_2.2km'][(leeds_data_dict['Observations Regridded_2.2km']['Date'] >= '1990-01-01 00:00:00')
                                                & (leeds_data_dict['Observations Regridded_2.2km']['Date'] <= '2000-11-30 23:00:00 ')]


### Trim to JJA
if jja_status == 'jja':
    for dict in [leeds_data_dict, leeds_data_dict_overlapping]:
        for resolution in ['Observations','Observations Regridded_12km','Observations Regridded_2.2km'  ]:
          print(resolution, len(dict[resolution]))
        # Extract df
          leeds_data =  dict[resolution]
          # Trim using JJA flag
          leeds_data = leeds_data[leeds_data['jja'].notna()]
          # Readd to dictionary
          dict[resolution] = leeds_data

##############################################################################
##############################################################################
# Plotting
##############################################################################
x_axis = 'linear'
y_axis = 'log'
bin_nos = 60 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
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
                  'Model 12km' : 'navy',
                  'Model 2.2km' : 'slateblue',
                  'Model 2.2km_regridded_12km': 'teal'}
    # Create patches
    patches= []
    for key, val in cols_dict.items():
        patch = mpatches.Patch(color= val, label= key)
        patches.append(patch)

    # Create plot
    #log_discrete_with_inset(dict, cols_dict, bin_nos, "Precipitation (mm/hr)",
    #                              patches, True, False)

    log_discrete_histogram_lesslegend(dict, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                      patches, True, xlim, x_axis, y_axis)
    #Save
    plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/RCMvsCPMvsObs/All{}_{}.png".format(overlapping_status, jja_status))

# ####### Plot - compring 2.2km model and 2.2km regridded observation
for dict, overlapping_status in zip([leeds_data_dict, leeds_data_dict_overlapping], ["","_Overlapping"]):
    print(dict.keys(), overlapping_status)
    just_2_2kms = dict.copy()
    del just_2_2kms['Model 12km'], just_2_2kms['Observations'], just_2_2kms['Observations Regridded_12km'], just_2_2kms['Model 2.2km_regridded_12km']
    cols_dict = {'Observations Regridded_2.2km' : 'tomato',
                  'Model 2.2km' : 'slateblue'}
    # Create patches
    patches= []
    for key, val in cols_dict.items():
        patch = mpatches.Patch(color= val, label= key)
        patches.append(patch)

    # Create plot
    log_discrete_histogram_lesslegend(just_2_2kms, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                      patches, True, False, x_axis, y_axis)
    plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs//ModelVsObs_2.2km_{}_{}.png".format(overlapping_status, jja_status))


# ####### Plot just Model, to see effect of regridding
for dict, overlapping_status in zip([leeds_data_dict, leeds_data_dict_overlapping], ["","_Overlapping"]):
    print(dict.keys(), overlapping_status)
    just_model = dict.copy()
    del just_model['Observations Regridded_2.2km'], just_model['Observations'], just_model['Observations Regridded_12km']
    cols_dict = {'Model 12km' : 'navy',
                  'Model 2.2km' : 'slateblue',
                  'Model 2.2km_regridded_12km': 'teal'}
    # Create patches
    patches= []
    for key, val in cols_dict.items():
        patch = mpatches.Patch(color= val, label= key)
        patches.append(patch)

    # Create plot
    log_discrete_histogram_lesslegend(just_model, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                      patches, True, False, x_axis, y_axis)
    plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/RCMvsCPMvsObs/JustModel_{}_{}.png".format(overlapping_status,jja_status))

# ###############################################################
####### Plot just Obs, to see effect of regridding
for dict, overlapping_status in zip([leeds_data_dict, leeds_data_dict_overlapping], ["","_Overlapping"]):
    print(dict.keys(), overlapping_status)

    just_obs = dict.copy()
    del just_obs['Model 12km'], just_obs['Model 2.2km'], just_obs['Model 2.2km_regridded_12km']

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
    plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/RCMvsCPMvsObs/JustObs_{}_{}.png".format(overlapping_status,jja_status))

#
# ###############################################################
# ####### Plot just 12km
just_12km = leeds_data_dict.copy()
del just_12km['Model 2.2km'], just_12km['Observations Regridded_2.2km'], just_12km['Observations']

cols_dict = {'Observations Regridded_12km' : 'darkred',
              'Model 12km' : 'navy',
              'Model 2.2km_regridded_12km': 'teal'}

# Create patches
patches= []
for key, val in cols_dict.items():
    patch = mpatches.Patch(color= val, label= key)
    patches.append(patch)

# Create plot
log_discrete_histogram_lesslegend(just_12km, cols_dict, bin_no, "Precipitation (mm/hr)",
                                  patches, True, False, x_axis, y_axis)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/RCMvsCPMvsObs/Just12kms_{}.png".format(jja_status))

# ##################### Plot just 12km -Better legend
for dict, overlapping_status in zip([leeds_data_dict, leeds_data_dict_overlapping], ["","_Overlapping"]):
    print(dict.keys(), overlapping_status)
    just_12km = dict.copy()
    del just_12km['Model 2.2km'], just_12km['Observations Regridded_2.2km'], just_12km['Observations']

    # Wet hours
    #for key in just_12km.keys():
    #    just_12km[key] = just_12km[key][just_12km[key]['Precipitation (mm/hr)'] > 0.1]

    cols_dict = {'Observations Regridded_12km' : 'darkred',
                 'Model 12km' : 'navy',
                 'Model 2.2km_regridded_12km': 'teal'}

    # Create patches
    patches= []
    patches.append(mpatches.Patch(color= 'darkred', label= 'CEH-GEAR'))
    patches.append(mpatches.Patch(color= 'navy', label= 'UKCP18 12km'))
    patches.append(mpatches.Patch(color= 'teal', label= 'UKCP18 2.2km'))

    # Create plot
    df = log_discrete_histogram_lesslegend(just_12km, cols_dict, bin_nos, "Precipitation (mm/hr)",
                                      patches, True, False)
    plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/RCMvsCPMvsObs/Just12kms_{}_{}.png".format(overlapping_status, jja_status))


# # ##########################################################################
# # # Percentile plots
# # ##########################################################################
navy_patch = mpatches.Patch(color='navy', label='Model 12km')
teal_patch = mpatches.Patch(color='teal', label='Model 2.2km')
darkred_patch = mpatches.Patch(color='darkred', label='Observations 1km')

for dict, overlapping_status in zip([leeds_data_dict, leeds_data_dict_overlapping], ["","_Overlapping"]):
    print(dict.keys(), overlapping_status)
    just_12km = dict.copy()
    del just_12km['Model 2.2km'], just_12km['Observations Regridded_2.2km'], just_12km['Observations']

    keys, p_99_9999, p_99_999, p_99_99, p_99_99, p_99_95, p_99_9, p_99_5, p_99, p_95, p_90, p_80, p_70, p_60, p_50, p_40, p_30, p_20, p_10 = [], [], [], [], [], [], [], [],[], [], [], [    ],[], [], [], [], [], [], []

    for key, value in just_12km.items():
        df = just_12km[key]
        keys.append(key)
        p_99_9999.append(df['Precipitation (mm/hr)'].quantile(0.999999))
        p_99_999.append(df['Precipitation (mm/hr)'].quantile(0.99999))
        p_99_99.append(df['Precipitation (mm/hr)'].quantile(0.9999))
        p_99_95.append(df['Precipitation (mm/hr)'].quantile(0.9995))
        p_99_9.append(df['Precipitation (mm/hr)'].quantile(0.999))
        p_99_5.append(df['Precipitation (mm/hr)'].quantile(0.995))
        p_99.append(df['Precipitation (mm/hr)'].quantile(0.99))
        p_95.append(df['Precipitation (mm/hr)'].quantile(0.95))
        p_90.append(df['Precipitation (mm/hr)'].quantile(0.9))
        p_80.append(df['Precipitation (mm/hr)'].quantile(0.8))
        p_70.append(df['Precipitation (mm/hr)'].quantile(0.7))
        p_60.append(df['Precipitation (mm/hr)'].quantile(0.6))
        p_50.append(df['Precipitation (mm/hr)'].quantile(0.5))
        p_40.append(df['Precipitation (mm/hr)'].quantile(0.4))
        p_30.append(df['Precipitation (mm/hr)'].quantile(0.3))
        p_20.append(df['Precipitation (mm/hr)'].quantile(0.2))
        p_10.append(df['Precipitation (mm/hr)'].quantile(0.1))

    df= pd.DataFrame({'Key':keys, '10': p_10,
                      '20': p_20,'30': p_30,
                      '40': p_40,  '50': p_50,
                      '60': p_60, '70': p_70,
                      '80': p_80, '90': p_90,
                      '95': p_95, '99': p_99,
                      '99.5': p_99_5, '99.9': p_99_9,
                    '99.95': p_99_95, '99.99': p_99_99,
                    '99.999': p_99_999, '99.9999': p_99_9999})

    test = df.transpose()
    test = test.rename(columns=test.iloc[0]).drop(test.index[0])

    # Plot
    #for x in [5,17,]
    for x, name in zip([5, 11,17], ["10-50", "10-99","10-99.9999"]):
        fig = plt.figure()
        for key, value in just_12km.items():
            print(key)
            if key == 'Model 12km':
                filtered = test[key]
                filtered = filtered[:x]
                plt.plot(filtered, color = 'navy')
            if key == 'Model 2.2km_regridded_12km':
                filtered = test[key]
                filtered = filtered[:x]
                plt.plot(filtered, color = 'teal')
            if key == 'Observations Regridded_12km':
                filtered = test[key]
                filtered = filtered[:x]
                plt.plot(filtered, color = 'darkred')
            plt.xlabel('Percentile')
            plt.ylabel('Precipitation (mm/hr)')
            plt.legend(handles=[darkred_patch, navy_patch, teal_patch])
            plt.yscale('linear')
            plt.xticks(rotation = 23)
        plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/PercentileThresholds/{}_{}_{}.png".format(name, overlapping_status, jja_status))
        plt.clf()

##############################################################################
##############################################################################
# Table with proportion of values which are 0, <0.1 etc
###########################################################################
###########################################################################
just_12km = leeds_data_dict_overlapping.copy()
del just_12km['Model 2.2km'], just_12km['Observations Regridded_2.2km'], just_12km['Observations']

# ## Proportion of values in each which are 0
# Should this be with regridded data?
less_low_hours_lst = []
low_hours_lst = []
dry_hours_lst = []
zero_hours_lst= []
more_than_1_hours_lst= []
wet_hours_lst = []
for key, value in just_12km.items():
    print(value)
    df= value
    
    zero_hours_lst.append(round((len(value[value['Precipitation (mm/hr)'] ==0])/len(value) *100  ),1))
    dry_hours_lst.append(round((len(value[(value['Precipitation (mm/hr)'] <0.11) & value['Precipitation (mm/hr)']>0])/len(value) *100  ),1))
    low_hours_lst.append(round((len(value[(value['Precipitation (mm/hr)'] <0.51) & value['Precipitation (mm/hr)']>0])/len(value) *100  ),1))
    less_low_hours_lst.append(round((len(value[(value['Precipitation (mm/hr)'] <1) & value['Precipitation (mm/hr)']>0])/len(value) *100  ),1))    
    more_than_1_hours_lst.append(round((len(value[value['Precipitation (mm/hr)'] >1])/len(value) *100  ),1))
    wet_hours_lst.append(round((len(value[value['Precipitation (mm/hr)'] >0.1])/len(value) *100  ),1))

zeros_df = pd.DataFrame({'Key': list(just_12km.keys()), '% hours 0': zero_hours_lst, '% hours <0.1': dry_hours_lst ,'% hours <0.5': low_hours_lst,
                         '% hours <1': less_low_hours_lst, '% hours >1': more_than_1_hours_lst,
                        '% hours >0.1': wet_hours_lst})



###########################################################################
###########################################################################
# Histogram
###########################################################################
###########################################################################
model_12km = just_12km['Model 12km']
model_2_2km = just_12km['Model 2.2km_regridded_12km']
obs = just_12km['Observations Regridded_12km']
bins = [0.01, 0.11, 0.21, 0.31, 0.41,0.51, 0.61,0.71,0.81,0.91,1]
bins = [0.01, 0.21, 0.41, 0.61, 0.81, 1.01, 1.21, 1.41, 1.61 ,1.81, 2.01]
bins = [2.01, 4.01, 6.01, 8.01, 10.01, 12.01, 14.01, 16.01, 18.01, 20.01]
bins = [10.01, 12.01, 14.01, 16.01, 18.01, 20.01, 22.01, 24.01, 26.01]

bins = [20.01, 25.01, 30.01, 35.01, 40.01, 45.01, 50.01, 55.01, 60.01]


plt.hist([obs['Precipitation (mm/hr)'], model_12km['Precipitation (mm/hr)'], model_2_2km['Precipitation (mm/hr)']],
          label = ['CEH-GEAR', 'UKCP18 12km', 'UKCP18 2.2km'],bins = bins,
          density = True, color = ['firebrick', 'navy',  'teal'])
plt.xlabel('mm/hr')
plt.ylabel('Probability density')
plt.legend()
plt.xticks(bins)


