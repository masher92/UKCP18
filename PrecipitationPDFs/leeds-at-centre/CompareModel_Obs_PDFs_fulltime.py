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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/RegriddingObservations')
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

################################################################
# Load data
################################################################
# Observations
observations_nn = np.load("Outputs/RegriddingObservations/CEH-GEAR_regridded_2.2km/NearestNeighbour/leeds-at-centre_data/leeds-at-centre.npy")
observations = np.load("Outputs/RegriddingObservations/CEH-GEAR_reformatted/leeds-at-centre_data/leeds-at-centre.npy")
# Model ensemble members
leeds_em01 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/01/leeds-at-centre.npy")
leeds_em04 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/04/leeds-at-centre.npy")
leeds_em05 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/05/leeds-at-centre.npy")
leeds_em06 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/06/leeds-at-centre.npy")
leeds_em07 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/07/leeds-at-centre.npy")
leeds_em08 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/08/leeds-at-centre.npy")
leeds_em09 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/09/leeds-at-centre.npy")
leeds_em10 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/10/leeds-at-centre.npy")
leeds_em11 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/11/leeds-at-centre.npy")
leeds_em12 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/12/leeds-at-centre.npy")
leeds_em13 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/13/leeds-at-centre.npy")
leeds_em15 = np.load("Outputs/Timeseries_UKCP18/leeds-at-centre/15/leeds-at-centre.npy")

# Create one array containing all of the data
leeds_all_ems = np.concatenate([leeds_em01, leeds_em04, leeds_em05, leeds_em06, leeds_em07,
                                leeds_em08, leeds_em09, leeds_em10, leeds_em11, leeds_em12,
                                leeds_em13, leeds_em15])


################################################################
# Convert to dataframes
################################################################
observations_nn = pd.DataFrame({"Precipitation (mm/hr)" : observations_nn})
observations = pd.DataFrame({"Precipitation (mm/hr)" : observations})

leeds_em01 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em01})
leeds_em04 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em04})
leeds_em05 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em05})
leeds_em06 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em06})
leeds_em07 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em07})
leeds_em08 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em08})
leeds_em09 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em09})
leeds_em10 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em10})
leeds_em11 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em11})
leeds_em12 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em12})
leeds_em13 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em13})
leeds_em15 = pd.DataFrame({"Precipitation (mm/hr)" : leeds_em15})

leeds_all_ems = pd.DataFrame({"Precipitation (mm/hr)" : leeds_all_ems})

# ##############################################################################
# # Setting up dictionary
# ##############################################################################
my_dict = {}
my_dict['Observations'] = observations
my_dict['Observations Regridded'] = observations_nn

# Comment out this
my_dict['Model'] = leeds_all_ems

# Or this
# my_dict['EM01'] = leeds_em01
# my_dict['EM04'] = leeds_em04
# my_dict['EM05'] = leeds_em05
# my_dict['EM06'] = leeds_em06
# my_dict['EM07'] = leeds_em07
# my_dict['EM08'] = leeds_em08
# my_dict['EM09'] = leeds_em09
# my_dict['EM10'] = leeds_em10
# my_dict['EM11'] = leeds_em11
# my_dict['EM12'] = leeds_em12
# my_dict['EM13'] = leeds_em13
# my_dict['EM15'] = leeds_em15

##############################################################################
# Plotting
##############################################################################
cols_dict = {'Observations' : 'firebrick',
             'Observations Regridded' : 'green',
             'Model' : 'navy',
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
bin_nos =14
bins_if_log_spaced= bin_nos
          
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

