# import numpy as np
# import matplotlib.pyplot as plt
# r = np.arange(10)
# p = np.arange(10)
# R,P = np.meshgrid(r,p)
# data = np.random.random((10,10))
# plt.pcolor(R,P,data)
# plt.scatter(R[:-1,:-1]+0.5,P[:-1,:-1]+0.5, color = 'blue')



# import numpy as np
# import matplotlib.pyplot as plt
# r = np.arange(10)
# p = np.arange(10)
# R,P = np.meshgrid(r,p)
# data = np.random.random((10,10))
# plt.pcolor(lons_wm_2d,lats_wm_2d,mask)
# plt.xlim(-200000, -10000)
# plt.ylim(7000000, 7200000)
# plt.scatter(R[:-1,:-1]+0.5,P[:-1,:-1]+0.5, color = 'blue')




# # plt.pcolor(lons_wm_2d,lats_wm_2d,mask)
# plt.scatter(lons_wm_2d[:-1,:-1]+0.5,lats_wm_2d[:-1,:-1]+0.5, color = 'blue')
# plt.scatter(lons_wm_2d[:-1,:-1],lats_wm_2d[:-1,:-1], color = 'red')
# plt.xlim(-200000, -140000)
# plt.ylim(7110000, 7165000)



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

##############################################################################
# Get data
data = hour_uk_cube.data
data_1d = data.reshape(-1)

# Extract lats and longs in rotated pol as a 2D array
lats = hour_uk_cube.coord('grid_latitude').points
lons = hour_uk_cube.coord('grid_longitude').points

# Convert to 1d
lons_1d = lons.reshape(-1)
lats_1d = lats.reshape(-1)

# Find the distance between each lat/lon and the next lat/lon
# Divide this by two to get the distance to the half way point
lat_differences = np.diff(lats_1d)
lat_differences_half = lat_differences/2
lon_differences = np.diff(lons_1d)
lon_differences_half = lon_differences/2

# Create an array of lats/lons at the midpoints
lats_edit = lats_1d[0:len(lat_differences)] + lat_differences_half
lons_edit = lons_1d[0:len(lon_differences)] + lon_differences_half

# Convert to wgs84
x, y = np.meshgrid(lons_edit, lats_edit)
cs = hour_uk_cube.coord_system()
lons_wgs84, lats_wgs84 = iris.analysis.cartography.unrotate_pole(x, y, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)

# Create an array of the data values, trimmed to the size of the edited lats/lons
#data = data[0:lons_wgs84.shape[0], 0:lons_wgs84.shape[1]]
#plt.pcolor(lons_wgs84,lats_wgs84, data )
#plt.scatter(lons_wgs84,lats_wgs84, color = 'blue')

# Convert to web mercator
lons_wgs_84_1d = lons_wgs84.reshape(-1)
lats_wgs_84_1d = lats_wgs84.reshape(-1)
lons_wm_1d_v2, lats_wm_1d_v2 = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_wgs_84_1d,lats_wgs_84_1d)

# Reshape them to the shape of the grid
lats_wm_2d_v2 = np.array(lats_wm_1d_v2).reshape(lons_wgs84.shape)
lons_wm_2d_v2 = np.array(lons_wm_1d_v2).reshape(lons_wgs84.shape)  

##############################################################################
#### Find part of the rainfall cube which is within this geometry
##############################################################################
lons_wm_1d_v1 = lons_wm_1d[0:len(lon_differences)]
lats_wm_1d_v1 = lats_wm_1d[0:len(lat_differences)]

# Check whether each lat, lon pair is within the geometry
mask = []
for lon, lat in zip(lons_wm_1d, lats_wm_1d):
    this_point = Point(lon, lat)
    res = this_point.within(leeds_poly)
    #res = leeds_poly.contains(this_point)
    mask.append(res)
mask = np.array(mask)
# Check how many values are not 0
mask.sum()
# Convert from a long array into one of the shape of the data
mask = np.array(mask).reshape(data.shape)
# Convert to 0s and 1s
mask = mask.astype(int)
# Mask out values of 0
mask = np.ma.masked_array(mask, mask < 1)



fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
ax.plot(lons_wm_1d, lats_wm_1d, "bo", markersize =10)
ax.plot(lons_wm_1d_v2, lats_wm_1d_v2, "ro", markersize =10)
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, mask, cmap =c.ListedColormap(['firebrick']), linewidths=4, alpha = 0.5, edgecolor = 'blue')
ax.pcolormesh(lons_wm_2d_v2, lats_wm_2d_v2, mask, cmap =c.ListedColormap(['firebrick']), linewidths=4, alpha = 0.5, edgecolor = 'blue')
leeds.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='firebrick', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')


fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
ax.plot(lons_wm_1d, lats_wm_1d, "bo", markersize =10)
ax.plot(lons_wm_1d_v2, lats_wm_1d_v2, "ro", markersize =10)
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, mask, cmap =c.ListedColormap(['firebrick']), linewidths=4, alpha = 0.5, edgecolor = 'blue')
ax.pcolormesh(lons_wm_2d, lats_wm_2d, mask, cmap =c.ListedColormap(['firebrick']), linewidths=4, alpha = 0.1, edgecolor = 'blue')
leeds.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='firebrick', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')



