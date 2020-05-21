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
### Model data latitude and longitudes as arrays
##############################################################################
# Create a cube creating on hour's worth of data.
filename = "datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc"
month_uk_cube = iris.load(filename,'lwe_precipitation_rate')[0]
# Remove ensemble member dimension and keep one time slice
hour_uk_cube = month_uk_cube[0, 1,:,:]

# Check coordinate system
hour_uk_cube.coord_system() 
hour_uk_cube[0].coord('grid_latitude').coord_system.as_cartopy_crs()

data = hour_uk_cube.data

#############################################################################
#### Create a shapely geometry of the outline of Leeds
##############################################################################
wards = gpd.read_file("england_cmwd_2011.shp")
# Create column to merge on
wards['City'] = 'Leeds'
# Merge all wards into one outline
leeds = wards.dissolve(by = 'City')

# Set up projections representing BNG and WGS84
osgb36 = {'init' :'epsg:27700'}
wgs84 = {'init' :'epsg:4326'}
web_m = {'init' :'epsg:3785'}

# Convert Leeds outline geometry to WGS84
leeds.crs = osgb36
leeds = leeds.to_crs(web_m)

# Convert outline of Leeds into a polygon
leeds_poly = Polygon(leeds['geometry'].iloc[0])

##############################################################################
# Extract lats and longs in WGS84 as a 2D array, store as 1D array
lats_wgs84_1d = hour_uk_cube.coord('latitude').points.reshape(-1)
lons_wgs84_1d = hour_uk_cube.coord('longitude').points.reshape(-1)

## Option 2 - using proj reprojections
lons_wm_1d,lats_wm_1d = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_1d,lats_1d)

##############################################################################
# Extract lats and longs in rotated pol as a 2D array
lats_rp_1d = hour_uk_cube.coord('grid_latitude').points
lons_rp_1d = hour_uk_cube.coord('grid_longitude').points

# Find the distance between each lat/lon and the next lat/lon
# Divide this by two to get the distance to the half way point
lats_rp_differences = np.diff(lats_rp_1d)
lats_rp_differences_half = lats_rp_differences/2
lons_rp_differences = np.diff(lons_rp_1d)
lons_rp_differences_half = lons_rp_differences/2

# Create an array of lats/lons at the midpoints
lats_rp_midpoints_1d = lats_rp_1d[1:] - lats_rp_differences_half
lons_rp_midpoints_1d = lons_rp_1d[1:] - lons_rp_differences_half

# Convert to 2D
lons_rp_midpoints_2d, lats_rp_midpoints_2d = np.meshgrid(lons_rp_midpoints_1d, lats_rp_midpoints_1d)

# Convert to wgs84
cs = hour_uk_cube.coord_system()
lons_wgs84_midpoints_2d, lats_wgs84_midpoints_2d = iris.analysis.cartography.unrotate_pole(lons_rp_midpoints_2d, lats_rp_midpoints_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
# Convert to web mercator
lons_wm_midpoints_2d, lats_wm_midpoints_2d = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_wgs84_midpoints_2d,lats_wgs84_midpoints_2d)
# Convert to 1d for 
lons_wm_midpoints_1d = lons_wm_midpoints_2d.reshape(-1)
lats_wm_midpoints_1d = lats_wm_midpoints_2d.reshape(-1)

# Remove same parts of data
data_midpoints = data[1:,1:]

##############################################################################
#### Testing
##############################################################################
# Create test data values
test_data = np.full((hour_uk_cube.shape), 7, dtype=int)

test_df = pd.DataFrame({"lats": lats_wm_1d, 'lons': lons_wm_1d, 'data':data.reshape(-1) })
test_df_midpoints = pd.DataFrame({"lats":lats_wm_midpoints_1d , 'lons': lons_wm_midpoints_1d, 'data':data_midpoints.reshape(-1) })

# Create aray where values within Leeds have a 1
mask = []
for lon, lat in zip(lons_wm_midpoints_1d, lats_wm_midpoints_1d):
    this_point = Point(lon, lat)
    res = this_point.within(leeds_poly)
    #res = leeds_poly.contains(this_point)
    mask.append(res)
mask = np.array(mask)
# Check how many values are not 0
mask.sum()
# Convert from a long array into one of the shape of the data
mask = np.array(mask).reshape(lons_wm_midpoints_2d.shape)
# Convert to 0s and 1s
mask = mask.astype(int)
# Mask out values of 0
mask = np.ma.masked_array(mask, mask < 1)

# Index of points in Leeds
index = np.where(mask == 1)

# Set the value of one of these points to a different number
test_data[index[0][3],index[1][3]] = 500

# Create trimmed dataset
test_data_midpoints = test_data[1:,1:]
# Make 1d
test_data_midpoints_1d = test_data.reshape(-1)
# Find index of point which is 500
idx = np.where(test_data_midpoints_1d == 500)

# Plot the grid and its corners in blue (created by shifting the coordinates)
# Plot the real centre points of the grid cells in black
# Set one of the data points in original array equal to 500

fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
ax.plot(lons_wm_1d, lats_wm_1d,"ko", markersize =10)
ax.plot(lons_wm_midpoints_1d, lats_wm_midpoints_1d, "bo", markersize =10)
ax.plot(lons_wm_1d[idx], lats_wm_1d[idx], "go", markersize =20)
ax.pcolormesh(lons_wm_midpoints_2d, lats_wm_midpoints_2d, data_midpoints,  linewidths=4, alpha = 0.8, edgecolor = 'blue')
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, data)
leeds.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')




### Plot
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
ax.plot(lons_wm_midpoints_1d, lats_wm_midpoints_1d, "bo", markersize =10)
ax.pcolormesh(lons_wm_midpoints_2d, lats_wm_midpoints_2d, data_midpoints,  linewidths=4, alpha = 0.8, edgecolor = 'blue')
leeds.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')



################### Testing
# x = np.array([1,2,3,4])
# y = np.array([10,11,12,13])

# x_mesh, y_mesh = np.meshgrid(x,y)
# data = np.array([1,2,3,4, 5,6,7,8,9,10,11, 12, 13,14,15,16])
# data=data.reshape(x_mesh.shape)

# x_differences = np.diff(x)
# x_differences_half = x_differences/2
# y_differences = np.diff(y)
# y_differences_half = y_differences/2

# # Create an array of lats/lons at the midpoints
# x_edit = x[1:] - x_differences_half
# y_edit = y[1:]- y_differences_half

# # Convert to mesh form
# x, y = np.meshgrid(x_edit, y_edit)

# data_edit = data[1:]
# data=data.reshape(x.shape)


# data = data[1:,1:]
# plt.pcolormesh(x, y, data,  linewidths=4, alpha = 0.5, edgecolor = 'blue')
# plt.colorbar(fraction=0.046, pad=0.04).ax.tick_params(labelsize='xx-large')


v = np.random.randn(10)
print(v)
maximum = np.max(v)
minimum = np.min(v)
print(maximum, minimum)

index_of_maximum = np.where(mask == 1)









