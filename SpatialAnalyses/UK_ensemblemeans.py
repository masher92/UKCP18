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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Set up variables
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
yrs_range = "1980_2001" 

#Plotting region
#region = ['Northern', 'leeds-at-centre', 'UK']
region = 'leeds-at-centre'
hours = 'wet'

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
uk_gdf = create_uk_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
#uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  

##################################################################
# Set up plotting colours
##################################################################
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      
precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="white")

##################################################################
# Create dictionaries storing the maximum and minimum values found for 
# each statistic, considering all ensemble members and all grid cells
##################################################################

##################################################################
# List of stats to loop through
if hours == 'all':
    stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']
elif hours == 'wet':
    stats = ['jja_max_wh', 'jja_mean_wh', 'jja_p95_wh', 'jja_p97_wh', 'jja_p99_wh', 'jja_p99.5_wh', 'jja_p99.75_wh', 'jja_p99.9_wh']
    
#  Loop through stats   
for stat in stats:

  # Load in files
  filenames = []
  for em in ems:
      if hours == 'all':
          filename= '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Allhours/em_'+ em+ '_' + stat + '.nc'
      elif hours == 'wet':
          filename= '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Wethours/em_'+ em+ '_' + stat + '.nc'          
      filenames.append(filename)

  # Load 12 ensemble member files into a cube list
  cubes_list = iris.load(filenames,'lwe_precipitation_rate')
  # Concatenate the cubes into one
  cubes = cubes_list.concatenate_cube()
      
  # Remove time dimension (only had one value)
  if hours == 'all':
      cubes = cubes[:,0,:,:]

#############################################################################
# Calculate and plot:
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
        
      # Trim to smaller area
      if region == 'Northern':
              stats_cube = trim_to_bbox_of_region(stats_cube, wider_northern_gdf)
      elif region == 'leeds-at-centre':
              stats_cube = trim_to_bbox_of_region(stats_cube, leeds_at_centre_gdf)
          
      # Mask the data so as to cover any cells not within the specified region 
      if region == 'Northern':
              stats_cube.data = ma.masked_where(wider_northern_mask == 0, stats_cube.data)
              # Trim to the BBOX of Northern England
              # This ensures the plot shows only the bbox around northern england
              # but that all land values are plotted
              stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)
      elif region == 'UK':
              stats_cube.data = ma.masked_where(uk_mask == 0, stats_cube.data)  
        
        
      # # Trim to bbox of wider northern region
      # stats_cube = trim_to_bbox_of_region(stats_cube, wider_northern_gdf)            
      # # Mask out data outwith this region (including the sea)
      # masked_data = ma.masked_where(mask == 0, stats_cube.data)
      # # Set this masked data as the cube's data
      # stats_cube.data = masked_data
      
      # # Trim the data to the bbox of northern GDF 
      # # This zooms in on only the northern_gdf region
      # stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)

      # Find the minimum and maximum values to define the spread of the pot
      local_min = stats_cube.data.min()
      local_max = stats_cube.data.max()
      contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)

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
     
      # Plot
      mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min, vmax = local_max)
           
      # Add regional outlines, depending on which region is being plotted
      if region == 'Northern':
             leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
             northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
             cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03, boundaries = contour_levels)
      elif region == 'leeds-at-centre':
             leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2.3)
             cb1 = plt.colorbar(mesh, ax=ax, fraction=0.041, pad=0.03, 
                               boundaries = contour_levels)
      elif region == 'UK':
             plt.gca().coastlines(linewidth =0.5)
             cb1 = plt.colorbar(mesh, ax=ax, fraction=0.049, pad=0.03, 
                               boundaries = contour_levels)
      cb1.ax.tick_params(labelsize=15)
      cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])   
        
      # Save files
      if hours == 'all':
          filename = "Outputs/Stats_Spatial_plots/{}/AllHours_EM_Difference/{}_{}.png".format(region, stat, em_cube_stat)
      elif hours == 'wet':
           filename = "Outputs/Stats_Spatial_plots/{}/WetHours_EM_Difference/{}_{}.png".format(region, stat, em_cube_stat)         
      fig.savefig(filename, bbox_inches = 'tight')
    
      

