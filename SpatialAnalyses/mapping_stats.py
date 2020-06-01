import sys
import iris
import cartopy.crs as ccrs
import os
from scipy import spatial
import itertools
import iris.quickplot as qplt
import warnings
import copy
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
import numpy as np

# Provide root_fp as argument
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Plotting_functions import *

start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
em = '01'

#############################################
# Read in files
#############################################
# Create list of names of cubes for between the years specified
filenames =[]
for year in range(start_year,end_year+1):
    # Create filepath to correct folder using ensemble member and year
    general_filename = root_fp + 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
        filenames.append(filename)
        
monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
print(str(len(monthly_cubes_list)) + " cubes found for this time period.")

##############################################################################
#### Create a shapely geometry of the outline of Leeds
##############################################################################
# Convert outline of Leeds into a polygon
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})

#############################################
# Concat the cubes into one
#############################################
# Remove attributes which aren't the same across all the cubes.
for cube in monthly_cubes_list:
     for attr in ['creation_date', 'tracking_id', 'history']:
         if attr in cube.attributes:
             del cube.attributes[attr]
 
 # Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Remove ensemble member dimension
concat_cube = concat_cube[0,:,:,:]

############################################
# Trim to include only grid cells whose coordinates (which represents the centre
# point of the cell is within a certain region e.g. West Yorks)
#############################################
wy_cube = trim_to_wy(concat_cube)

##############################################################################
# Get arrays of lats and longs of left corners in Web Mercator projection
##############################################################################
hour_uk_cube = wy_cube[1,:,:] # one timeslice
coordinates_cornerpoints = find_cornerpoint_coordinates(hour_uk_cube)
lats_cornerpoints= coordinates_cornerpoints[0]
lons_cornerpoints= coordinates_cornerpoints[1]

# Cut off edge data to match size of corner points arrays.
# First row and column lost in process of finding bottom left corner points.
wy_cube = wy_cube[:,1:, 1:]

##############################################################################
#### Get arrays of lats and longs of centre points in Web Mercator projection
##############################################################################
# Get points in WGS84
lats_centrepoints = wy_cube.coord('latitude').points
lons_centrepoints = wy_cube.coord('longitude').points
# Convert to WM
lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)

#############################################
# Find stats
#############################################
means = wy_cube[0:1000,:,:].collapsed('time', iris.analysis.MEAN)
means.has_lazy_data()
#means.data

#############################################
# Blank out points not within Leeds
#############################################
centre_within_geometry = GridCells_within_geometry(lats_centrepoints.reshape(-1),lons_centrepoints.reshape(-1), leeds_gdf, wy_cube)
stats_array = np.where(centre_within_geometry, means.data, np.nan)  

#############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
#ax.plot(lons_centrepoints.reshape(-1), lats_centrepoints.reshape(-1), "bo", markersize =10)
ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, stats_array,
              linewidths=3, alpha = 1, edgecolor = 'black')
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, data)
leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='green', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')


centre_within_geometry = GridCells_within_geometry(lats_centrepoints.reshape(-1),lons_centrepoints.reshape(-1), wy_gdf, wy_cube)
stats_array = np.where(centre_within_geometry, means.data, np.nan)  

fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(wy_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
#ax.plot(lons_centrepoints.reshape(-1), lats_centrepoints.reshape(-1), "bo", markersize =10)
ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, stats_array,
              linewidths=3, alpha = 1, edgecolor = 'black')
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, data)
wy_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='green', color='none', linewidth=6)
leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='red', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')