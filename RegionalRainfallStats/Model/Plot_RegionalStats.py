'''
This file plots regional statistics, using stats cubes created in UK_stats.py
and UK_stats_wethours.py. 

Each plot created contains 12 subplots for each of the 12 ensemble members.

It can plot using either Wet Hour stats or All Hour stats, depending on how 
the 'hours' parameter is set.

It is set up to plot within three regions, depending on how 'region' parameter is set:
- The UK (trimmed to the coastlines)
- The Northern region (North East, North West, Yorkshire and the Humber)
- A square region centred on Leeds

It can plot with either one shared color scale and bar for all 12 subplots (with the range
covering the full range of data values found within all 12 ensemble members) or
it can plot each subplot with its own seperate scale and colorbar (set to the
range of values found within just that ensemble member). This depends on how
the 'shared_axis' parameter is set.

'''

import iris.coord_categorisation
import iris
import numpy as np
import os
import geopandas as gpd
import sys
import matplotlib 
import numpy.ma as ma
import warnings
import iris.quickplot as qplt
import iris.plot as iplt
import cartopy.crs as ccrs
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

############################################
# Define variables and set up environment
#############################################
# List of ensemble members
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
# Whether to plot all subplots with axis with same range, or to plot an axis each
shared_axis = False
# Region over which to plot
region = 'leeds' #['Northern', 'leeds-at-centre', 'UK']
# Whether to include All hours or just Wet hours 
hours = 'all'


overlapping = '_overlapping'
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
# This is the outline of the coast of the UK
#uk_gdf = create_uk_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
uk_mask = np.load('Outputs/RegionalMasks/uk_mask_new.npy')  

##################################################################
# Create dictionaries storing the maximum and minimum values found for 
# each statistic, considering all ensemble members and all grid cells
##################################################################
# List of stats to loop through
if hours == 'all':
    stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']
elif hours == 'wet':
    stats = ['jja_max_wh', 'jja_mean_wh', 'jja_p95_wh', 'jja_p97_wh', 'jja_p99_wh', 'jja_p99.5_wh', 'jja_p99.75_wh', 'jja_p99.9_wh']
    
# Create a dictionary.
# The keys will be ensemble member numbers and the values will be dictionarys
# Each ensemble member's dictionary will in turn have statistic names as keys
# and the cube of that statistic as values
ems_dict = {}
# Create dictionaries to store max and min values for each stat
max_vals_dict = {}
min_vals_dict = {}

# Loop through ensemble members
for em in ems:
    print(em)
    # Create dictionary for that ensemble member to store results of differnet stats
    em_dict = {}
    # Loop through stats
    for stat in stats:
          # Load in netcdf files containing the stats data over the whole UK
          if hours == 'all':
              stat_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_' + stat + '.nc')[0] 
              stat_cube = stat_cube[0]    
          elif hours == 'wet':
              stat_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Wethours/EM_Data/em_'+ em+ '_' + stat + '.nc')[0] 
          # Trim to smaller area
          if region == 'Northern':
              stat_cube = trim_to_bbox_of_region(stat_cube, wider_northern_gdf)
          elif region == 'leeds-at-centre':
              stat_cube = trim_to_bbox_of_region(stat_cube, leeds_at_centre_gdf)
          elif region == 'leeds':
              stat_cube = trim_to_bbox_of_region(stat_cube, leeds_gdf)
              
          # Mask the data so as to cover any cells not within the specified region 
          if region == 'Northern':
              stat_cube.data = ma.masked_where(wider_northern_mask == 0, stat_cube.data)
              # Trim to the BBOX of Northern England
              # This ensures the plot shows only the bbox around northern england
              # but that all land values are plotted
              stat_cube = trim_to_bbox_of_region(stat_cube, northern_gdf)
          elif region == 'UK':
              #stat_cube = stat_cube
              uk_mask = uk_mask.reshape(458,383)
              stat_cube.data = ma.masked_where(uk_mask == 0, stat_cube.data)
              
          # If this is the first time through the loop e.g. the first ensemble member, 
          # then create dictionary which will store the max and min values for each 
          # statistic across all the ensemble members
          if em == '01':
            # Loop through stats setting max = 10000 and min = 0
            max_vals_dict[stat] = 0
            min_vals_dict[stat] = 10000
          # For all ensemble members store the file in a dictionary
          # And check if it's max/min value is higher/lower than the current value
          # and store it if it is
          print(stat)
          print (stat_cube.data.max()) 
          em_dict[stat] = stat_cube
          max_vals_dict[stat] = stat_cube.data.max() if stat_cube.data.max() > max_vals_dict[stat] else max_vals_dict[stat]
          min_vals_dict[stat] = stat_cube.data.min() if stat_cube.data.min() < min_vals_dict[stat] else min_vals_dict[stat]       
          
          # Save the dictionary of stat cubes to 
          ems_dict[em] = em_dict         

#############################################
# Plotting
#############################################
print("plotting")
# Create a colourmap                                   
precip_colormap = create_precip_cmap()

for stat in stats:
    print(stat)
    # Extract the max, min values across all 12 ensemble members
    # For shared axis plotting
    global_max = max_vals_dict[stat]
    global_min = min_vals_dict[stat]
    
    # Define the contour levels to use in plotting (match the number to the number of precip_colours)
    contour_levels_overall = np.linspace(global_min, global_max, 11,endpoint = True)
        
    # Set up plot size (dependent upon spatial extent)
    if region == 'Northern':
        plt.figure(figsize=(48,30), dpi=200)
    elif region == 'leeds-at-centre':
        plt.figure(figsize=(48, 24), dpi=200)
    elif region == 'leeds':
        plt.figure(figsize=(48, 24), dpi=200)        
    elif region == 'UK':
        plt.figure(figsize=(46,29), dpi=200)
      
    # Set up the the spacings which are used when creating subplots 
    # Vary this depending on whether each subplot will have a colourbar
    if shared_axis == True:
        plt.gcf().subplots_adjust(hspace=0.1, wspace=0.05, top=0.55, bottom=0.3, left=0.825, right=0.925)
    if shared_axis == False:
        plt.gcf().subplots_adjust(hspace=0.01, wspace=0.3, top=0.59, bottom=0.39, left=0.825, right=0.925)

    # Set up counter
    i=1

    # Loop through ensemble members   
    for em in ems:
        print(em)
        # Extract data for correct ensemble member and stat
        em_dict = ems_dict[em]
        stats_cube = em_dict[stat]
       
        # Define the contour levels to use in plotting where the axis is not shared
        local_min = stats_cube.data.min()
        local_max = stats_cube.data.max()       
        contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)
         
        # Define number of decimal places to use in the rounding of the colour bar
        # This ensures smaller numbers have decimal places, but not bigger ones.
        if local_max >10:
          n_decimal_places = 0
        else:
          n_decimal_places = 2
         
        ## If plots will have one color bar between them:         
        if shared_axis == True:
           # Create projection system in Web Mercator
           proj = ccrs.Mercator.GOOGLE
           # Create axis using this WM projection
           ax = plt.subplot(4,3,i, projection=proj)
           # Plot
           mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = global_min,
                                  vmax = global_max)
           # Add regional outlines, depending on which region is being plotted
           if region == 'Northern':
                leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.5)
                northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.4)
           elif region == 'leeds-at-centre' or region == 'leeds':
                leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
           elif region == 'UK':
                plt.gca().coastlines(linewidth =0.5)

        ## If plots will have one color bar each:
        elif shared_axis == False:
           # Create projection system in Web Mercator
           proj = ccrs.Mercator.GOOGLE
           # Create axis using this WM projection
           ax = plt.subplot(4,3,i, projection=proj)
           # Plot
           mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min, 
                                  vmax = local_max)
           # Add regional outlines, depending on which region is being plotted
           if region == 'Northern':
                leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.5)
                northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.4)
                cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03, boundaries = contour_levels)
                #cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  
           elif region == 'leeds-at-centre' or region == 'leeds':
                leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
                cb1 = plt.colorbar(mesh, ax=ax, fraction=0.039, pad=0.03, boundaries = contour_levels)
                #cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()]) 
           elif region == 'UK':
                plt.gca().coastlines(linewidth =0.5)
                cb1 = plt.colorbar(mesh, ax=ax, fraction=0.049, pad=0.01, boundaries = contour_levels)
                #cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  
           cb1.ax.tick_params(labelsize=8)
           cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  
           #cb1.update_ticks()
                    
        # Move counter on to next ensemble member
        i = i+1
      
    # Create a shared color bar
    # Determine filename for saving file
    if shared_axis == True:
        # make an axes to put the shared colorbar in. [1,2 are coordinates of lower left corner of plot; 3,4 are width and height of subplot]
        colorbar_axes = plt.gcf().add_axes([0.927, 0.3, 0.005, 0.25])
        colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical',  boundaries = contour_levels_overall)  
        if stat == 'wet_prop':
            colorbar.set_label('Wet hour percentage', size = 15)
        else:
            colorbar.set_label('%s' % stats_cube.units, size = 15)
        colorbar.ax.tick_params(labelsize=15)
        colorbar.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in colorbar.get_ticks()])    
        if hours == 'all':
            filename = "Outputs/RegionalRainfallStats/Plots/Model/{}/Allhours/{}.png".format(region, stat)
        elif hours == 'wet':
            filename = "Outputs/RegionalRainfallStats/Plots/Model/{}/Wethours/{}.png".format(region, stat)
  
    # Determine filename for saving file
    elif shared_axis == False:
        if hours == 'all':
            filename = "Outputs/RegionalRainfallStats/Plots/Model/{}/Allhours/{}_diffscales.png".format(region, stat)
        elif hours == 'wet':
            filename = "Outputs/RegionalRainfallStats/Plots/Model/{}/Wethours/{}_diffscales.png".format(region, stat)
            
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')





# ##########################################
# # Code to check whether grid lines are due to changing projection
# ##########################################
# Extract data for correct ensemble member and stat
#em_dict = ems_dict[em]
#stats_cube = em_dict[stat]
   
# Define the contour levels to use in plotting where the axis is not shared
#local_min = stats_cube.data.min()
#local_max = stats_cube.data.max()       
#contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)
 
## Define number of decimal places to use in the rounding of the colour bar
## This ensures smaller numbers have decimal places, but not bigger ones.
#if local_max >10:
#  n_decimal_places = 0
#else:
#  n_decimal_places = 2
 
########################### Plot in Web Mercator
#proj = ccrs.Mercator.GOOGLE
##proj = ccrs.PlateCarree()
## Think this needs to match the 
#data_crs = ccrs.Mercator.GOOGLE

## Create axis using this WM projection
#ax = plt.subplot(122, projection=proj)
## Plot
#mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min,
#                        vmax = local_max)
# Add regional outlines, depending on which region is being plotted
# if region == 'Northern':
#      leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.5)
#      northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.4)
# elif region == 'leeds-at-centre':
#      leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
# elif region == 'UK':
#      plt.gca().coastlines(linewidth =0.5)

################## Plot without specifying projection
# ax = plt.subplot(122)
# # Plot
# mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min,
#                         vmax = local_max)

# leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.5)


# ###
# from pyproj.crs import CRS
# cube_crs = stats_cube.coord('grid_latitude').coord_system.as_cartopy_crs()
# proj_crs = CRS.from_dict(cube_crs.proj4_params)
# leeds_gdf = leeds_gdf.to_crs(proj_crs)
# leeds_gdf.plot()


# lons_wrapped = []
# lons=stats_cube.coord('grid_longitude').points
# for lon in lons:
#     if lon >360:
#         new_lon=lon-360
#         lons_wrapped.append(new_lon)
#     else:
#         lons_wrapped.append(lon)
# stats_cube.coord('grid_longitude').points = lons_wrapped

