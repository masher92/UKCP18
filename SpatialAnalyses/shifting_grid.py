#############################################################################
# netCDF files contain arrays of latitude and longitudes which correspond to
# the centre point of 2.2km grid cells for which the precipitation values are 
# given in a values array.

# The python pcolormesh function can be used to plot values spatially, however
# it uses the coordinates to plot the bottom left corners of the grid. 

# To correctly plot the netCDF data is therefore necessary to derive the coordinates
# for the bottom left point of each grid cell. 

# This is done here by finding the difference between each value in a list of 
# lats and longs in rotated pole coordinates* and using this to create new coordinates
# at the midpoints. This results in losing the first row and column of the data
# *(because in rotated pole the longs are constant moving around different lats 
# and vice versa, which is no longer true in either wgs84 or web mercator).

# The precipitation values dataset is trimmed to also remove the first row and 
# column. 

# This results in a new array of lats and lons and associated precipitation values
# in which the lat, lon coordinate pair refers to the bottom left of the 2.2km
# grid cell to which it refers.

# To test this: a fake values data array is generated filled with all the same
# number. The index of 

##############################################################################
import matplotlib.pyplot as plt
import tilemapbase
import os
import iris
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
from matplotlib import colors as c
from pyproj import Proj, transform
import folium
import pandas as pd
import sys
from timeit import default_timer as timer
import glob

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"

# Define the local directory 
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/")

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
#os.chdir("/nfs/a319/gy17m2a/Scripts")

from Plotting_functions import *

##############################################################################
### Create a cube containing one timeslice 
##############################################################################
# Create a cube creating on hour's worth of data.
filename = "datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc"
month_uk_cube = iris.load(filename,'lwe_precipitation_rate')[0]
# Remove ensemble member dimension 
month_uk_cube = month_uk_cube[0, :,:,:]

#### Get just one timeslice
hour_uk_cube = month_uk_cube[1,:,:]

##############################################################################
#### Create a cube containing 20 years worth of data
##############################################################################
start_year = 1980
end_year = 2000 
# Create list of names of cubes for between the years specified
filenames =[]
for year in range(start_year,end_year+1):
    print(year)
    # Create filepath to correct folder using ensemble member and year
    general_filename = root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_{}*'.format(year)
    print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        print(filename)
        filenames.append(filename)

# CReate list of all cubes over 20 years
twentyyears_cubes_list = iris.load(filenames,'lwe_precipitation_rate')

# Remove attributes 20years_cubes_list are different between cubes to allow joining
for cube in twentyyears_cubes_list:
    for attr in ['creation_date', 'tracking_id', 'history']:
        if attr in cube.attributes:
            del cube.attributes[attr]

# Join all the cubes in the list together
concat_cube = twentyyears_cubes_list.concatenate_cube()

# Trim the cube to the same latitude and longitude dimensions and remove ensemble member dimensio
twentyyears_cubes = concat_cube[0,:,:605,:483]

#### Get just one timeslice
hour_uk_cube = twentyyears_cubes[1,:,:]

##############################################################################
#### Get arrays of lats and longs of centre points in Web Mercator projection
##############################################################################
# Get points in WGS84
lats_centrepoints = hour_uk_cube.coord('latitude').points
lons_centrepoints = hour_uk_cube.coord('longitude').points

# Convert to WM
lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)

# Cut off edge data to match size of corner points arrays.
# First row and column lost in process of finding bottom left corner points.
lons_centrepoints = lons_centrepoints[1:,1:]
lats_centrepoints = lats_centrepoints[1:,1:]

data = hour_uk_cube.data[1:,1:]

##############################################################################
# Get arrays of lats and longs of left corners in Web Mercator projection
##############################################################################
coordinates_cornerpoints = find_midpoint_coordinates(hour_uk_cube)
lats_cornerpoints= coordinates_cornerpoints[0]
lons_cornerpoints= coordinates_cornerpoints[1]

##############################################################################
# Create a dataframe containing the value and the associated central coordinate
# AND bottom left coordinate
############################################################################## 
df = pd.DataFrame({"Precipitation" : data.reshape(-1),
                   "Lat_bottomleft" :lats_cornerpoints.reshape(-1),
                   "Lon_bottomleft" :lons_cornerpoints.reshape(-1),
                   "Lat_centre" :lats_centrepoints.reshape(-1),
                   "Lon_centre" :lons_centrepoints.reshape(-1)})

##############################################################################
#### Create a shapely geometry of the outline of Leeds
##############################################################################
# Convert outline of Leeds into a polygon
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})

##############################################################################
#### Find which centre point locations are within Leeds boundary
##############################################################################
centre_within_geometry = GridCells_within_geometry(df, leeds_gdf, data)

##############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
#ax.plot(lons_centrepoints_1d, lats_centrepoints_1d,"ko", markersize =10)
ax.plot(df['Lat_bottomleft'], df['Lon_bottomleft'], "bo", markersize =10)
#ax.plot(lons_wm_1d[idx], lats_wm_1d[idx], "go", markersize =20)
ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, centre_within_geometry, cmap =c.ListedColormap(['firebrick']),
              linewidths=3, alpha = 0.5, edgecolor = 'black')
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, data)
leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')


##############################################################################
#### Find indices of points within Leeds
##############################################################################
index = np.where(centre_within_geometry== 1)

##############################################################################
#### Testing
##############################################################################
# Create test data array where all points are 0
# test_data = np.full((data.shape), 0, dtype=int)

# # Set the value of one point within Leeds to 500
# test_data[index[0][0], index[1][0]] = 500

# # Check where the highlighted cell is and where the centre point is
# fig, ax = plt.subplots(figsize=(20,20))
# extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
# plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
# plotter.plot(ax)
# leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
# ax.plot(df['Lat_bottomleft'], df['Lon_bottomleft'], "bo", markersize =10)
# ax.plot(lons_centrepoints[index[0][0], index[1][0]], lats_centrepoints[index[0][0], index[1][0]], "bo", markersize =10)
# ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data, linewidths=3, alpha = 0.5, edgecolor = 'black')

##############################################################################
#### Find mean and percentile values for each grid box (over a month)
##############################################################################
# # Trim monthly cube using same constraints (i.e. removing first row and column of
# # lats and longs)
# month_uk_cube_test = month_uk_cube[:,:605,:483]

# # Create a cube where each grid value is now the mean value for that grid cell
# # over the whole time period
# mean_cube = month_uk_cube_test.collapsed('time', iris.analysis.MEAN)

# # Extract the data as an array (double .data is it is masked)
# mean_array = mean_cube.data.data

# # Assign NA values to those points not within the geometry
# mean_array = np.where(centre_within_geometry, mean_array, np.nan)  

# # Check where the highlighted cell is and where the centre point is
# fig, ax = plt.subplots(figsize=(20,20))
# extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
# plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
# plotter.plot(ax)
# leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
# ax.plot(df['Lat_bottomleft'], df['Lon_bottomleft'], "bo", markersize =10)
# ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, mean_array, linewidths=3, alpha = 0.5, edgecolor = 'black',
#               vmax = 0.2, vmin = 0) 

# percentiles = month_uk_cube_test.collapsed('time', iris.analysis.PERCENTILE, percent=[90, 97, 99, 99.9])
# # Check percentiles dimension
# percentiles.coord('percentile_over_time').points
# # Check whether data is still lazy -no calculating the percentiles, means stops it being
# month_uk_cube_test.has_lazy_data()

##############################################################################
#### Find mean and percentile values for each grid box (over 20 years!)
##############################################################################
twentyyears_cubes.has_lazy_data()


# Mega Zoom
lat_constraint = iris.Constraint(latitude=lambda cell: 0.95 < cell < 1.55)
long_constraint = iris.Constraint(longitude=lambda cell: 360.5 < cell < 360.9)
# DO the trimming
twentyyears_cubes = twentyyears_cubes.extract(lat_constraint)
twentyyears_cubes = twentyyears_cubes.extract(long_constraint)

####### Or
# Get the first element of the first and third dimension (+ every other dimension)
twentyyears_cubes = twentyyears_cubes[:, 278:290, 306:320]

# Create a cube where each grid value is now the mean value for that grid cell
# over the whole time period
start = timer()
mean_cube = twentyyears_cubes.collapsed('time', iris.analysis.MEAN)
print("Means found in " + str(round((timer() - start)/60, 1)) + ' minutes')

# Extract the data as an array (double .data is it is masked)
mean_array = mean_cube.data.data

# Assign NA values to those points not within the geometry
mean_array = np.where(centre_within_geometry, mean_array, np.nan)  

start = timer()
means = []
# Create arrays of indices of the lats and lons of points within Leeds
lats_idxs = index[0]
lons_idxs = index[1]
# For each pair of indices, extract just the cube found at that position
# Store its precipitationd data values over the time period as a list
for lat_idx, long_idx in zip(lats_idxs, lons_idxs):
    cube_at_location = month_uk_cube[:, lat_idx,long_idx]
    np.mean(cube_at_location.data)
    
    mean_cube = cube_at_location.collapsed('time', iris.analysis.MEAN)
    
    precip_at_location = cube_at_location.data
    means.append(np.mean(precip_at_location))
    precip_values.append(precip_at_location)
print("Means found in " + str(round((timer() - start)/60, 1)) + ' minutes')


start = timer()
mean_cube = cube_at_location.collapsed('time', iris.analysis.MEAN)
print("Means found in " + str(round((timer() - start)/60, 1)) + ' minutes')

# For each pair of indices:
# Create lists with mean and various percentile values
for values in precip_values:
    means.append(np.mean(values))
   # p99s.append(np.percentile(values,99))
   # p97s.append(np.percentile(values,97))
    #p90s.append(np.percentile(values,90))

# Create a data array of the correct shape 
# Populate with values using the cube indices and their associated values
stats_array = np.full((within_geometry.shape), 0, dtype=float)
for lat_idx, lon_idx, stat in zip(lats_idxs, lons_idxs, means):
    stats_array[lat_idx, lon_idx] = stt



np.mean(cube_at_location.data)
values = []
for i in range(0,cube_at_location.shape[0]+1):
    print(i)
    data_point = cube_at_location[i].data
    values.append(data_point)

cube_at_location.has_lazy_data()
cube_at_location[1].data

 data_point = cube_at_location[0:172800].data
 data_point = cube_at_location[0:100].data
 print(data_point)
 np.mean(cube_at_location[0:172800].data)
 print(cube_at_location)

start = timer()
mean_cube = cube_at_location[0:172800].collapsed('time', iris.analysis.MEAN)
print("Means found in " + str(round((timer() - start)/60, 1)) + ' minutes')



start = timer()
np.mean(cube_at_location[0:172800].data)
print("Means found in " + str(round((timer() - start)/60, 1)) + ' minutes')

# Set up empty lists to store values
precip_values, means, p99s, p97s, p90s = [], [], [], [], []

# Create arrays of indices of the lats and lons of points within Leeds
lats_idxs = index[0]
lons_idxs = index[1]

# For each pair of indices, extract just the cube found at that position
# Store its precipitationd data values over the time period as a list
for lat_idx, long_idx in zip(lats_idxs, lons_idxs):
    cube_at_location = month_uk_cube[:, lat_idx,long_idx]
    precip_at_location = cube_at_location.data
    precip_values.append(precip_at_location)

# For each pair of indices:
# Create lists with mean and various percentile values
for values in precip_values:
    means.append(np.mean(values))
   # p99s.append(np.percentile(values,99))
   # p97s.append(np.percentile(values,97))
    #p90s.append(np.percentile(values,90))

# Create a data array of the correct shape 
# Populate with values using the cube indices and their associated values
stats_array = np.full((within_geometry.shape), 0, dtype=float)
for lat_idx, lon_idx, stat in zip(lats_idxs, lons_idxs, means):
    stats_array[lat_idx, lon_idx] = stt





# Assign NA values to those points not within the geometry
stats_array = np.where(within_geometry, stats_array, np.nan)  

# Check where the highlighted cell is and where the centre point is
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot = plotter.plot(ax)
plot =ax.plot(lons_cornerpoints_1d, lons_cornerpoints_1d, "bo", markersize =10)
plot = ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, stats_array, linewidths=3, alpha = 0.5, edgecolor = 'black')
plt.colorbar(plot,fraction=0.046, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot = leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)  
plot = ax.tick_params(labelsize='xx-large')



  

##############################################################################
#### Alternative method for finding mean and percentile values for each grid box (over a month)
#### Can use to check whether Iris method works
##############################################################################

# # Set up empty lists to store values
# precip_values, means, p99s, p97s, p90s = [], [], [], [], []

# # Create arrays of indices of the lats and lons of points within Leeds
# lats_idxs = index[0]
# lons_idxs = index[1]

# # For each pair of indices, extract just the cube found at that position
# # Store its precipitation data values over the time period as a list
# for lat_idx, long_idx in zip(lats_idxs, lons_idxs):
#     cube_at_location = month_uk_cube[:, lat_idx,long_idx]
#     precip_at_location = cube_at_location.data
#     precip_values.append(precip_at_location)

# # For each pair of indices:
# # Create lists with mean and various percentile values
# for values in precip_values:
#     means.append(np.mean(values))
#     p99s.append(np.percentile(values,99))
#     p97s.append(np.percentile(values,97))
#     p90s.append(np.percentile(values,90))

# # Create a data array of the correct shape 
# # Populate with values using the cube indices and their associated values
# stats_array = np.full((centre_within_geometry.shape), 0, dtype=float)
# for lat_idx, lon_idx, mean in zip(lats_idxs, lons_idxs, means):
#     stats_array[lat_idx, lon_idx] = mean

# # Assign NA values to those points not within the geometry
# stats_array = np.where(centre_within_geometry, stats_array, np.nan)  

# np.nanmin(stats_array)


# # Check where the highlighted cell is and where the centre point is
# fig, ax = plt.subplots(figsize=(20,20))
# extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
# plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
# plotter.plot(ax)
# leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
# ax.plot(df['Lat_bottomleft'], df['Lon_bottomleft'], "bo", markersize =10)
# ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, stats_array, linewidths=3, alpha = 0.5, edgecolor = 'black',
#               vmax = 0.2, vmin = 0)
