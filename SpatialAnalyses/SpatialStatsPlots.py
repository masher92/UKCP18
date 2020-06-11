'''
Creates a cube over a 20 year time period
Trims this to the square covering the WY extent
For each of the grid squares in this extent - calculates statistics incl. mean 
and various percentiles of hourly rainfall.
Plots these spatially, using pcolormesh and the bottom left corner coordinates
'''


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
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"

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
#### Create a shapely geometry of the outline of Leeds and West Yorks
##############################################################################
# Convert outline of Leeds into a polygon
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})

# Create geodataframe of the outline of West Yorkshire
# Data from https://data.opendatasoft.com/explore/dataset/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england%40ons-public/export/
wy_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
wy_gdf = wy_gdf.to_crs({'init' :'epsg:3785'}) 
 
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
# Find stats - means and percentiles
# Might it be better to un-lazy the data at the start?
#############################################
means = wy_cube.collapsed('time', iris.analysis.MEAN)
means.has_lazy_data()

percentiles = wy_cube.collapsed('time', iris.analysis.PERCENTILE, percent=[90, 95, 97, 99])
p_90 = percentiles[0,:,:]
p_95 = percentiles[1,:,:]
p_97 = percentiles[2,:,:]
p_99 = percentiles[3,:,:]
percentiles.has_lazy_data()

# Select which stat to use for plotting
stat= means
stats_array = stat.data

#############################################
# Blank out points not within Leeds - skip this step to get whole area
#############################################
centre_within_geometry = GridCells_within_geometry(lats_centrepoints.reshape(-1),lons_centrepoints.reshape(-1), leeds_gdf, wy_cube)
stats_array = np.where(centre_within_geometry, stat.data, np.nan)  

#############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
# Add points at corners of grids
#ax.plot(lons_centrepoints.reshape(-1), lats_centrepoints.reshape(-1), "bo", markersize =10)
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, stats_array,
              linewidths=3, alpha = 1, edgecolor = 'black')
plt.colorbar(plot,fraction=0.046, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='green', color='none', linewidth=6)
plot =ax.tick_params(labelsize='xx-large')
#plt.title("99th percentile",fontsize=50)


#############################################################################
#### # Plot - West Yorks
##############################################################################
#centre_within_geometry = GridCells_within_geometry(lats_centrepoints.reshape(-1),lons_centrepoints.reshape(-1), wy_gdf, wy_cube)
#stats_array = np.where(centre_within_geometry, stat.data, np.nan)  

fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(wy_gdf, buffer=5)
#plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
# Add points at corners of grids
#ax.plot(lons_centrepoints.reshape(-1), lats_centrepoints.reshape(-1), "bo", markersize =10)
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, stats_array,
              linewidths=3, alpha = 1, edgecolor = 'black')
plt.colorbar(plot,fraction=0.046, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =wy_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='green', color='none', linewidth=6)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='red', color='none', linewidth=6)
plot =ax.tick_params(labelsize='xx-large')
#plt.title("99th percentile",fontsize=50)