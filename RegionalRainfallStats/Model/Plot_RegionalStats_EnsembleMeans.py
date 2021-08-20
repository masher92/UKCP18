'''
This file plots ensemble summary plots using NetCDFs created in Calculate_UK_Stats_EnsembleMeans.py

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
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Set up variables
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
yrs_range = "1980_2001" 
region = 'leeds' #['Northern', 'leeds-at-centre', 'UK']
regions = ['leeds', 'leeds-at-centre', 'Northern', 'UK']

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  
uk_mask = uk_mask.reshape(458,383)

##################################################################
# Loop through stats:
##################################################################
# List of stats to loop through
stats = ['whprop' , 'jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

#############################################################################  
# Loop through stats and EM summary metrics
# Trim to the region specified
# Plot
#############################################################################
for region in ['UK']:
    for overlapping in ['_overlapping', '']:
        for stat in stats:
          print(stat)
          # Define the two different metrics
          em_cube_stats = ["EM_mean", "EM_spread"]
          # For each of the two different metrics
          for em_cube_stat in em_cube_stats:
              print(em_cube_stat)
             
              # Load in the cube for the correct statistic and ensemble summary metric 
              stats_cube = iris.load("Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Summaries/{}_{}{}.nc".format(stat, em_cube_stat, overlapping))[0]
                
              # Trim to smaller area
              if region == 'Northern':
                      stats_cube = trim_to_bbox_of_region(stats_cube, wider_northern_gdf)
              elif region == 'leeds-at-centre':
                      stats_cube = trim_to_bbox_of_region(stats_cube, leeds_at_centre_gdf)
              elif region == 'leeds':
                      stats_cube = trim_to_bbox_of_region(stats_cube, leeds_gdf)    
                      
              # Mask the data so as to cover any cells not within the specified region 
              if region == 'Northern':
                      stats_cube.data = ma.masked_where(wider_northern_mask == 0, stats_cube.data)
                      # Trim to the BBOX of Northern England
                      # This ensures the plot shows only the bbox around northern england
                      # but that all land values are plotted
                      stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)
              elif region == 'UK':
                      stats_cube.data = ma.masked_where(uk_mask == 0, stats_cube.data)  
        
              # Find the minimum and maximum values to define the spread of the pot
              local_min = stats_cube.data.min()
              local_max = stats_cube.data.max()
              contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)
        
              #############################################################################
              # Set up environment for plotting
              #############################################################################
              # Set up plotting colours
              precip_colormap = create_precip_cmap()   
              # Set up a plotting figurge with Web Mercator projection
              proj = ccrs.Mercator.GOOGLE
              fig = plt.figure(figsize=(20,20), dpi=200)
              ax = fig.add_subplot(122, projection = proj)
             
              # Define number of decimal places to use in the rounding of the colour bar
              # This ensures smaller numbers have decimal places, but not bigger ones.  
              if stats_cube.data.max() >10:
                  n_decimal_places = 0
              elif stats_cube.data.max() < 0.1:
                  n_decimal_places  =3
              else:
                  n_decimal_places =2
                  
              #############################################################################
              # Plot
              #############################################################################
              mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min, vmax = local_max)
                   
              # Add regional outlines, depending on which region is being plotted
              if region == 'Northern':
                     leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
                     northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
                     cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03, boundaries = contour_levels)
              elif region == 'leeds-at-centre' or region == 'leeds':
                     leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2.3)
                     cb1 = plt.colorbar(mesh, ax=ax, fraction=0.041, pad=0.03, 
                                       boundaries = contour_levels)
              elif region == 'UK':
                     plt.gca().coastlines(linewidth =0.5)
                     cb1 = plt.colorbar(mesh, ax=ax, fraction=0.049, pad=0.03, 
                                       boundaries = contour_levels)
              cb1.ax.tick_params(labelsize=15)
              if stat != 'whprop':
                  cb1.set_label('mm/hr', size = 25)
              elif stat == 'whprop':
                  cb1.set_label('%', size = 25)
              cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])   
                
              # Save files
              filename = "Scripts/UKCP18/RegionalRainfallStats/Model/Figs/{}/AllHours_EM_Difference/{}_{}{}.png".format(region, stat, em_cube_stat, overlapping)
              fig.savefig(filename, bbox_inches = 'tight')
            
              
        
