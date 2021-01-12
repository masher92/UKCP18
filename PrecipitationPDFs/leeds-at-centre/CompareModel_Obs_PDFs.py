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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/PointLocationStats/PlotPDFs')
from PDF_plotting_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/RegriddingObservations')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
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
model_times = np.load('Outputs/Timeseries_UKCP18/leeds-at-centre/timestamps.npy')

# Set value as NA for values not in required date range
for i in range(78480,172800):
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

# Loop through ensemble members
for em in ems:
    print(em)
    
    # Load in 20 years of model data for the whole of leeds
    leeds_data = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/{}/leeds-at-centre.npy".format(em))
    # Join to corresponding dates/times
    leeds_data_withtimes = pd.DataFrame({"Date" : model_times_allcells,
                                   'Precipitation (mm/hr)' :leeds_data})

    # Keep only data from overlapping times 
    leeds_data_overlapping = leeds_data_withtimes.loc[leeds_data_withtimes['Date'] != '0']
    
    # Add formatted date
    #leeds_data_overlapping['Date_formatted'] =  pd.to_datetime(leeds_data_overlapping['Date'], format='%Y%m%d%H',  errors='coerce')

    # Add data to dictionary
    leeds_data_dict['EM{}'.format(em)] = leeds_data_overlapping


frames = [leeds_data_dict['EM01'], leeds_data_dict['EM04'], leeds_data_dict['EM05'], leeds_data_dict['EM06'],
          leeds_data_dict['EM07'], leeds_data_dict['EM08'], leeds_data_dict['EM09'], leeds_data_dict['EM10']
          , leeds_data_dict['EM11'], leeds_data_dict['EM12'], leeds_data_dict['EM13'], leeds_data_dict['EM15']] 
leeds_all_ems = pd.concat(frames)

################################################################
# Trim observations data to also only include data from the overlapping time period
################################################################
# Observations dates data
#obs_times = np.load("Outputs/RegriddingObservations/CEH-GEAR_reformatted/leeds-at-centre_data/timestamps.npy")
obs_times = np.load("Outputs/RegriddingObservations/CEH-GEAR_regridded_2.2km/NearestNeighbour/leeds-at-centre_data/timestamps.npy", allow_pickle = True)

# Format date column
#obs_times_ls = [datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in obs_times]
#obs_times = np.array(obs_times_ls)

# Repeat this 1221 times to be the same length as the precip data for whole of Leeds 
obs_times_allcells_regridded = np.tile(obs_times, 1221)    
obs_times_allcells = np.tile(obs_times, 6059) # 73*83 

# Observations
observations_regridded = np.load("Outputs/RegriddingObservations/CEH-GEAR_regridded_2.2km/NearestNeighbour/leeds-at-centre_data/leeds-at-centre.npy")
observations = np.load("Outputs/RegriddingObservations/CEH-GEAR_reformatted/leeds-at-centre_data/leeds-at-centre.npy")

# Join dates data and precip data
observations_regridded = pd.DataFrame({"Precipitation (mm/hr)" : observations_regridded,
                                       'Date' : obs_times_allcells_regridded})
    
# Remove data not in the overlapping time period
observations_regridded_overlapping = observations_regridded[(observations_regridded['Date'] > '1990-01-01 00:00:00') 
                                                & (observations_regridded['Date']< '2000-11-30 23:00:00 ')]


# Add to dictionary
leeds_data_dict['Observations'] = observations
leeds_data_dict['Observations Regridded'] = observations_regridded_overlapping

# ##############################################################################
# # Setting up dictionary
# ##############################################################################
my_dict = {}
my_dict['Observations'] = observations
my_dict['Observations Regridded'] = observations_regridded_overlapping

my_dict['Model'] = leeds_all_ems


##############################################################################
# Plotting
##############################################################################
cols_dict = {'Observations' : 'firebrick',
             'Observations Regridded' : 'green',
             'Model' : 'navy'}
             'EM01': "navy",
             'EM04': 'navy',
             'EM05': 'navy',
             'EM06': 'navy',
             'EM07': 'navy',
             'EM08': 'navy',
             'EM09': 'navy',  
             'EM10': 'navy',
             'EM11': 'navy',
             'EM12': 'navy',
             'EM13': 'navy',                      
             'EM15': 'navy'}

x_axis = 'linear'
y_axis = 'log'
bin_nos =40
bins_if_log_spaced= bin_nos

# Equal spaced   
equal_spaced_histogram(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis)

# Log spaced histogram
log_spaced_histogram(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis)    
 
# Fractional contribution
fractional_contribution(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis) 
             
# Log histogram with adaptation     
log_discrete_histogram(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis) 

# Log histogram with adaptation     
log_discrete_histogram_lesslegend(my_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", x_axis, y_axis) 


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


