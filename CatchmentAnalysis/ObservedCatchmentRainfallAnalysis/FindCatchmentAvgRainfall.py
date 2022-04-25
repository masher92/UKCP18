#####
# This script finds all the 1km CEH-GEAR grid cells that fall within the boundary
# of an LCC catchment (currently, Lin Dyke).
# 
#####


# Import packages
import sys 
import glob
import numpy as np
import iris
import matplotlib as mpl
import os
import matplotlib.pyplot as plt
import iris.plot as iplt
from iris.time import PartialDateTime 
import pandas as pd
import warnings
import cartopy.crs as ccrs
from pyproj import Transformer
warnings.simplefilter(action='ignore', category=UserWarning)

# Stops warning on loading Iris cubes
iris.FUTURE.netcdf_promote = True
iris.FUTURE.netcdf_no_unlimited = True

# Provide root_fp as argument
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Define name and coordinates of location
# Read in shapefile 
lindyke_shp = gpd.read_file("FloodModelling/IndividualCatchments/LinDyke/Shapefile/FEH_Catchment_443550_427250.shp")
lindyke_shp =  lindyke_shp.to_crs({'init' :'epsg:3857'}) 

#############################################################################
# Load in spatial data
# As geodataframes for plotting
# As shapely geometries for checking whether lat/long points are within the areas
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

#############################################################################
## Load in the reformatted observations cubes and concatenate into one cube
#############################################################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_*'
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    #print(filename)
    filenames.append(filename)
# Load all cubes into list
monthly_cubes_list = iris.load(filenames,'rainfall_amount')

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Test plotting
iplt.pcolormesh(concat_cube[12])

#############################################################################
#############################################################################
## Trim concatenated cube to outline of leeds-at-centre geodataframe
#############################################################################
#############################################################################
concat_cube = trim_to_bbox_of_region_obs(concat_cube, leeds_gdf)

# Test plotting
iplt.pcolormesh(concat_cube[12])

fig = plt.figure(figsize = (20,30))
proj = ccrs.Mercator.GOOGLE
ax = fig.add_subplot(projection=proj)
mesh = iplt.pcolormesh(concat_cube[12], cmap = 'Blues')
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)

#############################################################################
#############################################################################
## Check each lat/long combination (central point of grid cell) as to whether it
# is within the catchment
# If it is, then add its data to an array which will store the values for all
# cells within the catchment

# Also, check location of cells for which data is extracted
# Create a 2D array, with same shape as cube for one timeslice
# Set all values to 0 initially, and then for grid cells from which data is extracted
# set the value to 1
#############################################################################
#############################################################################
# For use in for loop:
# Create variables specifying the number of lat and long values there are 
lat_length, lon_length = concat_cube.shape[1], concat_cube.shape[2]
# Store lat and long values as variables
lats = concat_cube.coord('projection_y_coordinate').points
lons = concat_cube.coord('projection_x_coordinate').points

# Create a list to store the indices of the coordinates within the catchment
coords_within_catchment_ls = []
# Create an empty array to store the data
all_the_data = np. array([])
fig, ax = plt.subplots(figsize=(20,10))
extent = tilemapbase.extent_from_frame(leeds_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =lindyke_shp.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
# Loop through each lat/long pair 
for i in range(0,lat_length): 
    for j in range(0,lon_length):
        # Transform this lat/long pair into Web Mercator, and create a Shapely point
        transformer = Transformer.from_crs("epsg:27700", "epsg:3857")
        x, y = transformer.transform(lons[j], lats[i])
        point = Point(x,y) 
        # Check if point is within catchment boundary shapefile
        if lindyke_shp.contains(point)[0]:
            # print to show progress
            print(i,j)
            # Add data to array (first 9 values are always NA)
            #one_slice = concat_cube[10:12,i,j]
            #all_the_data = np.append(all_the_data, one_slice.data)
            # Store the indices of the lat/longs with the catchment (for plotting) 
            coords_within_catchment_ls.append((i, j)) 
            plt.plot(x,y, marker = 'o', color = 'black')

#############################################################################
#############################################################################
## 
#############################################################################
#############################################################################
# Create empty array with same shape as the cube's data
# Within the for loop we will set the value for grid cells where the central point
# is within the catchment to 1, so we can check which cell's data we are using
cells_within_catchment_cube = concat_cube[0,:,:]
cells_within_catchment_array = np.full((cells_within_catchment_cube.shape),0,dtype = int)

# 
for i,j in coords_within_catchment_ls:
    # Set value in array to 1
    cells_within_catchment_array[i,j]=1

# Mask out all values that aren't 1
cells_within_catchment_array = ma.masked_where(cells_within_catchment_array<1,cells_within_catchment_array)

# Set the dummy data back on the cube
cells_within_catchment_cube.data = cells_within_catchment_array 

# Find cornerpoint coordinates (for use in plotting)
lats_cornerpoints = find_cornerpoint_coordinates_obs(cells_within_catchment_cube)[0]
lons_cornerpoints = find_cornerpoint_coordinates_obs(cells_within_catchment_cube)[1]

# Trim the data timeslice to be the same dimensions as the corner coordinates
cells_within_catchment_array = cells_within_catchment_array[1:,1:]      


#############################################################################
#############################################################################
## Plot locations for which data extracted
#############################################################################
#############################################################################
# Set up figure, with the leeds city boundary and catchment boundary
fig, ax = plt.subplots(figsize=(20,10))
extent = tilemapbase.extent_from_frame(leeds_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
 
# Create a colormap
cmap = mpl.colors.ListedColormap(['yellow'])
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cells_within_catchment_array,
      linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')

plot =lindyke_shp.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)

for i,j in coords_within_catchment_ls:
    x, y = transformer.transform(lons_cornerpoints[1], lats_cornerpoints[2])
    plt.plot(x,y, marker = 'o', color = 'black')
    


###########################################################
# Save cube and csv
###########################################################
iris.save(time_series_cube, 
          "/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_cubes/1990-2014.nc")
iris.save(time_series_cube_1990_2001, 
          "/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_cubes/1990-2001.nc")

df.to_csv("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_csv/1990-2014.csv", index = False)
df_1990_2001.to_csv("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_csv/1990-2001.csv", index = False)


