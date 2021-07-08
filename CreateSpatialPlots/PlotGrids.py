#############################################################################
# Set up environment
#############################################################################
import numpy as np
import os
import pandas as pd
import glob
from shapely.geometry import Point, Polygon
import sys
from pyproj import Proj, transform
import iris.plot as iplt
import matplotlib as mpl
import warnings
from datetime import datetime
import pandas as pd
import matplotlib.patches as mpatches
import iris
import numpy.ma as ma

root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *
from Pr_functions import *
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *
from PDF_plotting_functions import *

########################################################################################
northern_gdf = create_northern_outline({'init' :'epsg:3857'})

########################################################################################
########################################################################################
# Plot CEH-GEAR
########################################################################################
########################################################################################
filename = 'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_201412.nc'
obs_cube = iris.load(filename,'rainfall_amount')[0]

# Get cube containing one hour worth of data
hour_uk_cube = obs_cube[0,:,:]

# Trim
hour_uk_cube = trim_to_bbox_of_region_obs(hour_uk_cube, northern_gdf)

# Set all the values to 0
test_data = np.full((hour_uk_cube.shape),0,dtype = int)

# Mask out all values that aren't 1
test_data = ma.masked_where(test_data<1,test_data)

# Set the dummy data back on the cube
hour_uk_cube.data = test_data

# Find cornerpoint coordinates (for use in plotting)
lats_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[0]
lons_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[1]

# Trim the data timeslice to be the same dimensions as the corner coordinates
hour_uk_cube = hour_uk_cube[1:,1:]
test_data = hour_uk_cube.data

# Create location in web mercator for plotting
print('Creating plot')

# Create a colormap
cmap = matplotlib.colors.ListedColormap(['yellow'])

fig, ax = plt.subplots(figsize=(45,30))
extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
plot =plotter.plot(ax)
# # Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
      linewidths=2, alpha = 1, cmap = cmap, edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plt.savefig("Scripts/UKCP18/CreateSpatialPlots/Figs/CEH-GEAR.png", bbox_inches = 'tight')

########################################################################################
########################################################################################
# Plot UKCP18 grid -2.2km
########################################################################################
########################################################################################
filename = "datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_20001101-20001130.nc"
em_cube = iris.load(filename, 'lwe_precipitation_rate')[0]

# Get cube containing one hour worth of data
hour_uk_cube = em_cube[0,0,:,:]

# Trim to region
hour_uk_cube = trim_to_bbox_of_region(hour_uk_cube, northern_gdf)

# Set all the values to 0
test_data = np.full((hour_uk_cube.shape),0,dtype = int)

# Mask out all values that aren't 1
test_data = ma.masked_where(test_data<1,test_data)

# Set the dummy data back on the cube
hour_uk_cube.data = test_data

# Find cornerpoint coordinates (for use in plotting)
lats_cornerpoints = find_cornerpoint_coordinates(hour_uk_cube)[0]
lons_cornerpoints = find_cornerpoint_coordinates(hour_uk_cube)[1]

# Trim the data timeslice to be the same dimensions as the corner coordinates
hour_uk_cube = hour_uk_cube[1:,1:]
test_data = hour_uk_cube.data

# Create location in web mercator for plotting
print('Creating plot')

# Create a colormap
cmap = matplotlib.colors.ListedColormap(['yellow'])

fig, ax = plt.subplots(figsize=(45,30))
extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
plot =plotter.plot(ax)
# # Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
      linewidths=2, alpha = 1, cmap = cmap, edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plt.savefig("Scripts/UKCP18/CreateSpatialPlots/Figs/UKCP18_2.2km.png")

########################################################################################
########################################################################################
# Plot UKCP18 grid - 12km
########################################################################################
filename = 'datadir/UKCP18/12km/15/pr_rcp85_land-rcm_uk_12km_15_day_20701201-20801130.nc'
em_cube = iris.load(filename, 'lwe_precipitation_rate')[0]

# Get cube containing one hour worth of data
hour_uk_cube = em_cube[0,0,:,:]

# Trim to region
hour_uk_cube = trim_to_bbox_of_region_obs(hour_uk_cube, northern_gdf)

# Set all the values to 0
test_data = np.full((hour_uk_cube.shape),0,dtype = int)

# Mask out all values that aren't 1
test_data = ma.masked_where(test_data==0,test_data)

# Set the dummy data back on the cube
hour_uk_cube.data = test_data

# Find cornerpoint coordinates (for use in plotting)
lats_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[0]
lons_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[1]

# Trim the data timeslice to be the same dimensions as the corner coordinates
hour_uk_cube = hour_uk_cube[1:,1:]
test_data = hour_uk_cube.data

# Create location in web mercator for plotting
print('Creating plot')

# Create a colormap
cmap = matplotlib.colors.ListedColormap(['yellow'])

fig, ax = plt.subplots(figsize=(45,30))
extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
plot =plotter.plot(ax)
# # Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
      linewidths=3, alpha = 1, cmap = cmap, edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plt.savefig("Scripts/UKCP18/CreateSpatialPlots/Figs/UKCP18_12km.png")