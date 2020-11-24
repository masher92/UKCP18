'''
This file plots ensemble summary plots using stats cubes created in UK_stats.py
and UK_stats_wethours.py. 

Plotting for each statistic produces two plots:
- The ensemble mean, calculated across all 12 ensemble members
- The ensemble spread, or standard deviation, calculated across all 12 ensemble members

It can plot using either Wet Hour stats or All Hour stats, depending on how 
the 'hours' parameter is set.

It is set up to plot within three regions, depending on how 'region' parameter is set:
- The UK (trimmed to the coastlines)
- The Northern region (North East, North West, Yorkshire and the Humber)
- A square region centred on Leeds

'''

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
import numpy.ma as ma

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Set up variables
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
yrs_range = "1980_2001" 
hours = 'All' #['Wet', 'All']

##################################################################
# Load mask for UK
# This masks out cells outwith the wider northern region
uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  
# Reshape into shape
uk_mask_reshaped = uk_mask.reshape(458, 383)

##################################################################
# Loop through stats:
##################################################################
# List of stats to loop through
if hours == 'All':
    stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']
elif hours == 'Wet':
    stats = ['wet_prop', 'jja_max_wh', 'jja_mean_wh', 'jja_p95_wh', 'jja_p97_wh', 'jja_p99_wh', 'jja_p99.5_wh', 'jja_p99.75_wh', 'jja_p99.9_wh']

#############################################################################  
# For each stat, load in cubes containing this data for each of the ensemble members
# And concatenate all the ensemble member statistic cubes into one. 
#############################################################################
for stat in stats:
  # Load in files
  filenames = []
  for em in ems:
      if hours == 'All':
          filename= '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_{}_{}.nc'.format(em, stat)
      elif hours == 'Wet':
          filename= '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Wethours/EM_Data/em_{}_{}.nc'.format(em, stat)    
      filenames.append(filename)

  # Load 12 ensemble member files into a cube list
  cubes_list = iris.load(filenames,'lwe_precipitation_rate')
  # Concatenate the cubes into one
  cubes = cubes_list.concatenate_cube()
      
  # Remove time dimension (only had one value)
  if hours == 'All':
      cubes = cubes[:,0,:,:]
      
  #############################################################################
  # Calculate:
  # The ensemble mean
  # The ensemble spread (standard deviation)
  #############################################################################
  # Define the two different metrics
  em_cube_stats = ["EM_mean", "EM_spread"]
  # For each of the two different metrics
  for em_cube_stat in em_cube_stats:
      print(em_cube_stat)
     # Collapse them to contain one mean value across 12 ensemble members
      if em_cube_stat == "EM_mean":
          stats_cube = cubes.collapsed(['ensemble_member'], iris.analysis.MEAN)
      elif em_cube_stat == "EM_spread":
          stats_cube = cubes.collapsed(['ensemble_member'], iris.analysis.STD_DEV)

      # Mask out data points outside UK
      stats_cube.data = ma.masked_where(uk_mask_reshaped == 0, stats_cube.data)  
    
      #############################################################################
      # Save netCDF files
      #############################################################################
      iris.save(stats_cube, 'Outputs/RegionalRainfallStats/NetCDFs/Model/{}hours/EM_Summaries/{}_{}.nc'.format(hours, stat, em_cube_stat))
