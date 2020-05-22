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

# Define the local directory 
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/")

##############################################################################
### Create a cube containing one timeslice 
##############################################################################
# Create a cube creating on hour's worth of data.
filename = "datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc"
month_uk_cube = iris.load(filename,'lwe_precipitation_rate')[0]
# Remove ensemble member dimension and keep one time slice
hour_uk_cube = month_uk_cube[0, 1,:,:]

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
ax.plot(lons_cornerpoints_1d, lons_cornerpoints_1d, "bo", markersize =10)
#ax.plot(lons_wm_1d[idx], lats_wm_1d[idx], "go", markersize =20)
ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, within_geometry, cmap =c.ListedColormap(['firebrick']),
              linewidths=3, alpha = 0.5, edgecolor = 'black')
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, data)
leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')

##############################################################################
#### Testing
##############################################################################
# Create test data array where all points are 0
test_data = np.full((data.shape), 0, dtype=int)

# Find the indexes of one of the points within Leeds
index = np.where(centre_within_geometry== 1)
# Set its value to 500
test_data[index[0][0], index[1][0]] = 500

# Check where the highlighted cell is and where the centre point is
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
ax.plot(lons_cornerpoints_1d, lons_cornerpoints_1d, "bo", markersize =10)
ax.plot(lons_centrepoints[index[0][0], index[1][0]], lats_centrepoints[index[0][0], index[1][0]], "bo", markersize =10)
ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data, linewidths=3, alpha = 0.5, edgecolor = 'black')











