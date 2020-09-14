def define_loc_of_interest(cube, lat, lon):
    #############################################
    # Define a sample point at which we are interested in extracting the precipitation timeseries.
    # Assign this the same projection as the projection data
    #############################################
    # Create a cartopy CRS representing the coordinate sytem of the data in the cube.
    rot_pole = cube[0].coord('grid_latitude').coord_system.as_cartopy_crs()
    
    # Define a sample point of interest, in standard lat/long.
    # Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
    original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
    target_xy = rot_pole.transform_point(lon, lat, original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
       
    # Store the sample point of interest as a tuples (with their coordinate name) in a list
    sample_points = [('grid_latitude', target_xy[1]), ('grid_longitude', target_xy[0])]
    return(sample_points)


'''
This file is for comparing the regridded observations against the native observations
to discern the influence of the regridding process on the data.
'''

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
from scipy import spatial

################################################################
# Define variables and set up environment
################################################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

# Create region with Leeds at the centre
lons = [54.130260, 54.130260, 53.486836, 53.486836]
lats = [-2.138282, -0.895667, -0.895667, -2.138282]
polygon_geom = Polygon(zip(lats, lons))
leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:27700'}) 

# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})

rg_string = '_regridded_2.2km/rg_'
rf_string = '_reformatted/rf_'

################################################################
# For reformatted and regridded data:
# Create a cube trimmed to the oputline of the square area surrounding Leeds
################################################################   
rf_cube = create_trimmed_cube(leeds_at_centre_gdf, rf_string, {'init' :'epsg:27700'})
rg_cube = create_trimmed_cube(leeds_at_centre_gdf, rg_string, {'init' :'epsg:4326'})
    
################################################################
# For reformatted and regridded data:
# Plot cubes to check
################################################################   
plot_cube(rg_cube,  {'init' :'epsg:4326'}, 10)
plot_cube(rf_cube,  {'init' :'epsg:27700'}, 10)
    
################################################################
# For reformatted and regridded data:
# Create time series for a particular location in Leeds
################################################################   
# Coordinates of location of interest
lon = -1.37818
lat =  53.79282
# Name for this location
location = 'Armley'

#############################################################################
#############################################################################
# Regridded data
#############################################################################
#############################################################################
# Sample point in rotated pole coordintes
sample_point = define_loc_of_interest(rg_cube, lat, lon)

#############################################################################
# Find the grid cell closest to a location of interest
#############################################################################
# Create a list of all the tuple pairs of latitude and longitudes
locations = list(itertools.product(rg_cube.coord('grid_latitude').points, rg_cube.coord('grid_longitude').points))

# Correct them so that 360 merges back into one
corrected_locations = []
for location in locations:
    if location[0] >360:
        new_lat = location[0] -360
    else: 
        new_lat = location[0]
    if location[1] >360:
        new_long = location[1] -360     
    else:
        new_long = location[1]
    new_location = new_lat, new_long 
    corrected_locations.append(new_location)

# Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
tree = spatial.KDTree(corrected_locations)
closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]

# Extract the lat and long values of this point using the index
closest_lat = locations[closest_point_idx][0]
closest_long = locations[closest_point_idx][1]

#############################################################################
# Create a cube containing just the timeseries for that location of interest
#############################################################################
# Use this closest lat, long pair to collapse the latitude and longitude dimensions
# of the concatenated cube to keep just the time series for this closest point 
time_series_cube = rg_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))

##############################################################################
### Checking this approach
##############################################################################
# It is possible to conduct a check on which grid cell the data is being extracted
# for using the index of the grid cell returned by the create_concat_cube_one_location_m3
# function.
        
# Create a test dataset with all points with same value
# Set value at the index returned above to something different
# And then plot data spatially, and see which grid cell is highlighted.        
test_data = np.full((rg_cube[0].shape), 7, dtype=int)
test_data_rs = test_data.reshape(-1)
test_data_rs[closest_point_idx] = 500
test_data = test_data_rs.reshape(test_data.shape)
test_data = test_data[1:,1:]

## Find the lats and lons for plotting and convert to WGS84
lats = rg_cube.coord('grid_latitude').points
lons = rg_cube.coord('grid_longitude').points
lons_2d, lats_2d = np.meshgrid(lons, lats)
cs = rg_cube.coord_system()
lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
     
# Convrt Leeds GDF to WGS84  
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:4326'}) 
leeds_gdf = leeds_gdf.to_crs({'init' :'epsg:4326'}) 

# Plot     
fig, ax = plt.subplots()
# Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_2d, lats_2d, test_data,
              linewidths=3, alpha = 1, cmap = 'GnBu')
cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
#cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
#plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =ax.tick_params(labelsize='xx-large')
plot=ax.plot(lon, lat, "bo", markersize =5)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)  


##############################################################################
### In above code, however, the plotting is off as it uses the pcolormesh which 
# assusmes coordinates refer to the bottom left of the square, when in reality
# these coordinates refer to the middle point of the square
# To plot correctly, need to find the cornerpoint coordinates
##############################################################################
# Find cornerpoint coordinates in Web Mercator
corner_coords = find_cornerpoint_coordinates(rg_cube)
lats_cornerpoints = corner_coords[0]
lons_cornerpoints = corner_coords[1]

# Trim the cube to contain just one timeslice and to be same dimension as the cornerpoint coordiantes
cube = rg_cube[100, 1:, 1:]

# Find the centre point coordinates in WGS84
#lats_centrepoints = cube.coord('grid_latitude').points
#lons_centrepoints = cube.coord('grid_longitude').points
#lons_centrepoints_2d, lats_centrepoints_2d = np.meshgrid(lons_centrepoints, lats_centrepoints)
#cs = rg_cube.coord_system()
#lons_centrepoints_2d, lats_centrepoints_2d = iris.analysis.cartography.unrotate_pole(lons_centrepoints_2d, lats_centrepoints_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)

# Convert to WM
#lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)
    
# Convrt Leeds GDF to Web Mercator
# And the location of interest  
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:3785'}) 
leeds_gdf = leeds_gdf.to_crs({'init' :'epsg:3785'}) 
lon_wm, lat_wm = transform({'init' :'epsg:4326'}, {'init' :'epsg:3785'}, lon, lat)

#############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
# Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
              linewidths=3, alpha = 1, cmap = 'GnBu')
cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
#cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
#plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =ax.tick_params(labelsize='xx-large')
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot=ax.plot(lon_wm, lat_wm, "ro", markersize =10)


#############################################################################
#############################################################################
# Reformatted data
#############################################################################
#############################################################################
# Sample point in OSGB36
lon_osgb36, lat_osgb36 = transform({'init' :'epsg:4326'}, {'init' :'epsg:27700'}, lon, lat)
sample_point = [('grid_latitude', lat_osgb36), ('grid_longitude', lon_osgb36)]

#############################################################################
# Find the grid cell closest to a location of interest
#############################################################################
def find_closest_coordinates(cube):
    coord_names = [coord.name() for coord in cube.coords()]
    
    # Create variables storing lats/lons (or equivalent variables)
    lats = cube.coord(coord_names[1]).points
    lons = cube.coord(coord_names[2]).points
        
    # Create a list of all the tuple pairs of latitude and longitudes
    locations = list(itertools.product(lats, lons))
                                       
    # Correct them so that 360 merges back into one
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")
        
        corrected_locations = []
        for location in locations:
            if location[0] >360:
                new_lat = location[0] -360
            else: 
                new_lat = location[0]
            if location[1] >360:
                new_long = location[1] -360     
            else:
                new_long = location[1]
            new_location = new_lat, new_long 
            corrected_locations.append(new_location)
        locations = corrected_locations       
    
    # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
    tree = spatial.KDTree(locations)
    closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
    
    # Extract the lat and long values of this point using the index
    closest_lat = locations[closest_point_idx][0]
    closest_long = locations[closest_point_idx][1]
    
    return closest_point_idx, closest_lat, closest_long
    
rg_closest_coordinates = find_closest_coordinates(rg_cube)   
rf_closest_coordinates= find_closest_coordinates(rf_cube)    

#############################################################################
# Create a cube containing just the timeseries for that location of interest
#############################################################################
# Use this closest lat, long pair to collapse the latitude and longitude dimensions
# of the concatenated cube to keep just the time series for this closest point 
rf_time_series_cube = rf_cube.extract(iris.Constraint(projection_y_coordinate=rf_closest_coordinates[1], projection_x_coordinate= rg_closest_coordinates[2]))
rg_time_series_cube = rf_cube.extract(iris.Constraint(grid_latitude=rg_closest_coordinates[1], grid_longitude= rf_closest_coordinates[2]))


closest_point_idx =rg_closest_coordinates[0]

def check_location_of_closestpoint (cube, closest_point_idx, sample_point):
    # Create a test dataset with all points with same value
    # Set value at the index returned above to something different
    # And then plot data spatially, and see which grid cell is highlighted.        
    test_data = np.full((cube[0].shape), 7, dtype=int)
    test_data_rs = test_data.reshape(-1)
    test_data_rs[closest_point_idx] = 500
    test_data = test_data_rs.reshape(test_data.shape)
    
    # Find cornerpoint coordiantes
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    test_data = test_data[1:,1:]
        
    # Convrt Leeds GDF to Web Mercator
    # And the location of interest  
    gdf = gdf.to_crs(target_crs)
    #gdf = leeds_gdf.to_crs(target_crs) 
    
    # Convert cornerpoints to target_crs
    lons_cornerpoints, lats_cornerpoints = transform(input_crs, target_crs, lons_cornerpoints, lats_cornerpoints)
    lon_wm, lat_wm = transform(input_crs, target_crs, sample_point[1][1], sample_point[0][1])
    
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    fig, ax = plt.subplots()
    extent = tilemapbase.extent_from_frame(leeds_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    #plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=3, alpha = 1, cmap = 'GnBu')
    cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot =ax.tick_params(labelsize='xx-large')
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot=ax.plot(lon_wm, lat_wm, "ro", markersize =4)
    
    
def find_cornerpoint_coordinates(cube):
    coord_names = [coord.name() for coord in cube.coords()]
    
    # Create variables storing lats/lons (or equivalent variables)
    lats = cube.coord(coord_names[1]).points
    lons = cube.coord(coord_names[2]).points

    lons_2d, lats_2d = np.meshgrid(lons, lats)
    
    # Find the distance between each lat/lon and the next lat/lon
    # Divide this by two to get the distance to the half way point
    lats_differences_half = np.diff(lats)/2
    lons_differences_half = np.diff(lons)/2
    
    # Create an array of lats/lons at the midpoints
    lats_cornerpoints_1d = lats[1:] - lats_differences_half
    lons_cornerpoints_1d = lons[1:] - lons_differences_half
    
    # Convert to 2D
    lons_cornerpoints_2d, lats_cornerpoints_2d = np.meshgrid(lons_cornerpoints_1d, lats_cornerpoints_1d)
    
    return lats_cornerpoints_2d, lons_cornerpoints_2d

target_crs = {'init' :'epsg:3785'}
input_crs = {'init' :'epsg:27700'}

def plot_cube_within_region(cube, one_ts_data, gdf, target_crs, input_crs):
    
    # Find the lats and lons of the cornerpoints
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    one_ts_data = one_ts_data[1:,1:]
        
    # Convrt Leeds GDF to Web Mercator
    # And the location of interest  
    gdf = gdf.to_crs(target_crs 
    #gdf = leeds_gdf.to_crs(target_crs) 
    
    # Convert cornerpoints to target_crs
    lons_cornerpoints, lats_cornerpoints = transform(input_crs, target_crs, lons_cornerpoints, lats_cornerpoints)
    lon_wm, lat_wm = transform(input_crs, target_crs, lon_osgb36, lat_osgb36)
    
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    fig, ax = plt.subplots()
    extent = tilemapbase.extent_from_frame(leeds_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    #plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=3, alpha = 1, cmap = 'GnBu')
    cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot =ax.tick_params(labelsize='xx-large')
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot=ax.plot(lon_wm, lat_wm, "ro", markersize =4)