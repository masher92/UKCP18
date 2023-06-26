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
from Spatial_geometry_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *

# Define ensemble member numbers
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

# Define whether to filter out JJA
jja_status = 'jja'

################################################################
# Loop through ensemble members and load in data for whole of leeds 
################################################################
# Create a dictionary to store results
all_dict= {}

# Loop through ensemble members
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
for em in ems:
    for timeperiod in ['Baseline', 'Future_near', 'Future_far']:
        print(em)
        
        ################################################################
        # Load in timestamps that relate to one cell's worth of data
        baseline_times_with_jjaflag = pd.read_csv("Outputs/TimeSeries/UKCP18/2.2km/Baseline/leeds-at-centre/timestamps_jjaflag.csv")
        baseline_times_with_jjaflag = pd.concat([baseline_times_with_jjaflag]* 1221)
        
        if timeperiod == 'Baseline':
            times = baseline_times_with_jjaflag
        
        elif timeperiod ==  'Future_near' or timeperiod == 'Future_far':
            times = np.load('Outputs/TimeSeries/UKCP18/2.2km/{}/leeds-at-centre/timestamps.npy'.format(timeperiod))
            # Repeat this 1221 times to be the same length as the precip data for whole of Leeds 
            times = np.tile(times, 1221)   
            # Add JJA flag
            times = pd.DataFrame({'times':times,
                                'in_jja': baseline_times_with_jjaflag['in_jja']})
        
                
        # Load in 20 years of model data for the whole of leeds
        leeds_data = np.load("Outputs/TimeSeries/UKCP18/2.2km/{}/leeds-at-centre/{}/leeds-at-centre.npy".format(timeperiod, em))
       
        # Join to corresponding dates/times
        leeds_data_withtimes = pd.DataFrame({"Date" : times['times'], 
                                                 'Precipitation (mm/hr)':leeds_data,
                                                 'jja':times['in_jja']})
        # JJA?
        if jja_status == 'jja':
            leeds_data_withtimes = leeds_data_withtimes.dropna()
            
        # Add to dictionary
        all_dict['EM{}_{}'.format(em, timeperiod)] = leeds_data_withtimes    

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
log_discrete_histogram_lesslegend(all_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/BaselineVsFuture/AllEMs.png".format(jja_status))

####################################################################
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
    leeds_all_ems = pd.concat(frames)
    #leeds_all_ems = np.concatenate(frames)
    
    all_dict['Combined_ems_{}'.format(timeperiod)]  = leeds_all_ems  

# Create dictionary to specify colours
cols_dict = {'Combined_ems_Baseline' : 'firebrick',
             'Combined_ems_Future_near' : 'green',
             'Combined_ems_Future_far' : 'blue'}

# Define plotting parameters
x_axis = 'linear'
y_axis = 'log'
bin_nos = 60 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
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
log_discrete_histogram_lesslegend(just_combined_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/BaselineVsFuture/CombinedEMs_{}_{}.png".format(jja_status, bin_nos))

# ##########################################################################
# # Percentile plots
# ##########################################################################
keys = []
p_99_9999,  = []
p_99_999 = []
p_99_99 = []
p_99_95 = []
p_99_9 = []
p_99_5 = []
p_99 = []
p_95 =[]
p_90 = []
p_80 = []
p_70 = []
p_60 = []
p_50 = []

for key, value in just_combined_dict.items():
    df = just_combined_dict[key]
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
    
    
df= pd.DataFrame({'Key':keys, '50': p_50,
                  '60': p_60, '70': p_70,  
                  '80': p_80, '90': p_90,
                  '95': p_95, '99': p_99,
                  '99.5': p_99_5, '99.9': p_99_9,
                '99.95': p_99_95, '99.99': p_99_99,
                '99.999': p_99_999, '99.9999': p_99_9999}) 


test = df.transpose()
test = test.rename(columns=test.iloc[0]).drop(test.index[0])

# Plot
firebrick_patch = mpatches.Patch(color='firebrick', label='Baseline')
green_patch = mpatches.Patch(color='green', label='Future (near)')
navy_patch = mpatches.Patch(color='navy', label='Future (far)')

for key, value in just_combined_dict.items():
    print(key)
    if key == 'Combined_ems_Baseline':
        filtered = test[key]
        filtered = filtered[5:]
        plt.plot(filtered, color = 'firebrick')
    elif key == 'Combined_ems_Future_near':
        filtered = test[key]
        filtered = filtered[5:]
        plt.plot(filtered, color = 'green')
    elif key == 'Combined_ems_Future_far':
        filtered = test[key]
        filtered = filtered[5:]
        plt.plot(filtered, color = 'navy')        
    plt.xlabel('Percentile')
    plt.ylabel('Precipitation (mm/hr)')
    plt.legend(handles=[firebrick_patch, green_patch, navy_patch])
    plt.yscale('linear')
    plt.xticks(rotation = 23)
plt.savefig("Scripts/UKCP18/PrecipitationPDFs/leeds-at-centre/Figs/BaselineVsFuture/PercentilePlots.png".format(jja_status, bin_nos))


