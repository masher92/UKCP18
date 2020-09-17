def find_closest_coordinates(cube, sample_point, n_closest_points):
    # Define names of coordinate variables
    coord_names = [coord.name() for coord in cube.coords()]
    
    # Create variables storing lats/lons (or equivalent variables)
    lats = cube.coord(coord_names[1]).points
    lons = cube.coord(coord_names[2]).points
        
    # Create a list of all the tuple pairs of latitude and longitudes
    locations = list(itertools.product(lats, lons))
                                       
    # If cube coordinates are in rotated pole
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")
        
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
        locations = corrected_locations       
    
        # Convert the sample point also to a rotated pole coordinate system
        rot_pole = cube[0].coord('grid_latitude').coord_system.as_cartopy_crs()
        # Define a sample point of interest, in standard lat/long.
        # Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
        original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
        target_xy = rot_pole.transform_point(sample_point[1][1], sample_point[0][1], original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
           
        # Store the sample point of interest as a tuples (with their coordinate name) in a list
        sample_point = [('grid_latitude', target_xy[1]), ('grid_longitude', target_xy[0])]       
    
    else:
      lon_osgb36,lat_osgb36= transform(Proj(init='epsg:4326'),Proj(init='epsg:27700'),sample_point[1][1],sample_point[0][1])
      #lon_osgb36, lat_osgb36 = transform({'init' :'epsg:4326'}, {'init' :'epsg:27700'}, sample_point[0][1],sample_point[1][1 )
      sample_point = [('grid_latitude', lat_osgb36), ('grid_longitude', lon_osgb36)]
    
    # Find the indexes of the closest points to this sample location
    tree = spatial.KDTree(locations)
    closest_point_idxs = tree.query([(sample_point[0][1], sample_point[1][1])], k = n_closest_points)[1][0]
    
    # If there is only one closest point index, then convert this to an array (so in same format as if there were more than 1) 
    if isinstance(closest_point_idxs, np.int64) :
        closest_point_idxs = np.array([closest_point_idxs])   
        
    # Return locations to uncorrected versions
    locations = list(itertools.product(lats, lons))    
    
    # Create list of the closest lats and lons
    closest_lats = []
    closest_lons =[]
    for i in closest_point_idxs:
        print(i)
        closest_lats.append(locations[i][0])
        closest_lons.append(locations[i][1])
    
    return closest_point_idxs, closest_lats, closest_lons


def check_location_of_closestpoint (cube, input_crs, target_crs, sample_point, closest_point_idx = None, ):
    global leeds_at_centre_gdf
    global leeds_gdf
    
    # Create a test dataset with all points with same value
    # Set value at the index returned above to something different
    # And then plot data spatially, and see which grid cell is highlighted.   
    #closest_point_idx = closest_point_idx[0]
    test_data = np.full((cube[0].shape), 0, dtype=int)
    if closest_point_idx is not None:
      test_data_rs = test_data.reshape(-1)
      test_data_rs[closest_point_idx] = 1
      test_data = test_data_rs.reshape(test_data.shape)
    
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Find cornerpoint coordiantes
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    test_data = test_data[1:,1:]
        
    # Convrt Leeds GDF to Web Mercator
    # And the location of interest  
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs)
    leeds_gdf = leeds_gdf.to_crs(target_crs) 
    
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")
        cs = cube.coord_system()
        lons_cornerpoints, lats_cornerpoints = iris.analysis.cartography.unrotate_pole(lons_cornerpoints, lats_cornerpoints, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
      
    # Convert cornerpoints to target_crs
    lons_cornerpoints, lats_cornerpoints = transform(input_crs, target_crs, lons_cornerpoints, lats_cornerpoints)
    lon_wm, lat_wm = transform({'init' :'epsg:4326'}, target_crs, sample_point[1][1], sample_point[0][1])
         
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    cmap = mpl.colors.ListedColormap(['royalblue'])
   
    #bounds = [0,1]
    #norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    fig, ax = plt.subplots(figsize=(20,10))
    extent = tilemapbase.extent_from_frame(leeds_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=1, alpha = 1, cmap = cmap, edgecolors = 'grey')
    #cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    #cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    #plot =ax.tick_params(labelsize='xx-large')
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot=ax.plot(lon_wm, lat_wm, color='yellow', marker='o', markersize =5)



def plot_stat (cube, input_crs, target_crs):
    global leeds_at_centre_gdf
    global leeds_gdf  
   
    # Find cornerpoint coordiantes
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    data = cube.data[1:,1:]
        
    # Convrt Leeds GDF to Web Mercator
    # And the location of interest  
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs)
    leeds_gdf = leeds_gdf.to_crs(target_crs) 
    
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")
        cs = cube.coord_system()
        lons_cornerpoints, lats_cornerpoints = iris.analysis.cartography.unrotate_pole(lons_cornerpoints, lats_cornerpoints, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
      
    # Convert cornerpoints to target_crs
    lons_cornerpoints, lats_cornerpoints = transform(input_crs, target_crs, lons_cornerpoints, lats_cornerpoints)
    lon_wm, lat_wm = transform({'init' :'epsg:4326'}, target_crs, sample_point[1][1], sample_point[0][1])
         
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    fig, ax = plt.subplots(figsize=(20,10))
    extent = tilemapbase.extent_from_frame(leeds_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=1, alpha = 1, cmap = 'GnBu', edgecolors = 'grey')
    #cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    #cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    #plot =ax.tick_params(labelsize='xx-large')
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot=ax.plot(lon_wm, lat_wm, color='yellow', marker='o', markersize =5)

  
def find_cornerpoint_coordinates(cube):
    coord_names = [coord.name() for coord in cube.coords()]
    print(coord_names)
    
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

def plot_cube(cube, input_crs, target_crs):
    global leeds_at_centre_gdf
    global leeds_gdf
    
    # Create a test dataset with all points with same value
    # Set value at the index returned above to something different
    # And then plot data spatially, and see which grid cell is highlighted.        
    test_data = np.full((cube[0].shape), 0, dtype=int)  
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Find cornerpoint coordiantes
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    test_data = test_data[1:,1:]
        
    # Convert Leeds GDF to Web Mercator
    # And the location of interest  
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs)
    leeds_gdf = leeds_gdf.to_crs(target_crs) 
    
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")
        cs = cube.coord_system()
        lons_cornerpoints, lats_cornerpoints = iris.analysis.cartography.unrotate_pole(lons_cornerpoints, lats_cornerpoints, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
      
    # Convert cornerpoints to target_crs
    lons_cornerpoints, lats_cornerpoints = transform(input_crs, target_crs, lons_cornerpoints, lats_cornerpoints)
    lon_wm, lat_wm = transform({'init' :'epsg:4326'}, target_crs, sample_point[1][1], sample_point[0][1])
         
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    cmap = mpl.colors.ListedColormap(['royalblue'])
   
    #bounds = [0,1]
    #norm = mpl.colors.BoundaryNorm(bounds, cmap.N)
    
    fig, ax = plt.subplots(figsize=(20,10))
    extent = tilemapbase.extent_from_frame(leeds_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=1, alpha = 1, cmap = cmap, edgecolors = 'grey')
    #cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    #cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    #plot =ax.tick_params(labelsize='xx-large')
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot=ax.plot(lon_wm, lat_wm, color='yellow', marker='o', markersize =1)


'''
This file is for comparing the regridded observations against the native observations
to discern the influence of the regridding process on the data.
'''
import numpy.ma as ma
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
import itertools
from shapely.geometry import Point, Polygon
from pyproj import Proj, transform
import matplotlib.pyplot as plt
import pandas as pd
import tilemapbase
import matplotlib as mpl

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
from Spatial_plotting_functions import create_leeds_outline
sys.path.insert(0, root_fp + 'Scripts/UKCP18/PlotPDFs/')
from PDF_plotting_functions import *

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

# Coordinates of location of interest
sample_point = [('grid_latitude', 53.796638), ('grid_longitude', -1.592600)]

################################################################
# Create a cube trimmed to the oputline of the square area surrounding Leeds
################################################################   
rf_cube = create_trimmed_cube(leeds_at_centre_gdf, rf_string, {'init' :'epsg:27700'})
rg_cube = create_trimmed_cube(leeds_at_centre_gdf, rg_string, {'init' :'epsg:4326'})
    
################################################################
# Plot cubes to check the grid
################################################################   
#check_location_of_closestpoint(rg_cube, {'init' :'epsg:4326'},  {'init' :'epsg:3785'}, sample_point )
#check_location_of_closestpoint(rf_cube, {'init' :'epsg:4326'},  {'init' :'epsg:3785'}, sample_point )

################################################################
# Find the coordinates of the grid cell containing the point of interest
################################################################   
rg_closest_coordinates = find_closest_coordinates(rg_cube, sample_point, 1) 
rf_closest_coordinates =  find_closest_coordinates(rf_cube, sample_point,1)    

############################################################################
# Create a cube containing just the timeseries for that location of interest
#############################################################################
# Use this closest lat, long pair to collapse the latitude and longitude dimensions
# of the concatenated cube to keep just the time series for this closest point 
rg_time_series_cube = rg_cube.extract(iris.Constraint(grid_latitude=rg_closest_coordinates[1], 
                                                      grid_longitude= rg_closest_coordinates[2]))
rf_time_series_cube = rf_cube.extract(iris.Constraint(projection_y_coordinate=rf_closest_coordinates[1], 
                                                      projection_x_coordinate= rf_closest_coordinates[2]))

#############################################################################
#############################################################################
check_location_of_closestpoint(rg_cube, {'init' :'epsg:4326'},  {'init' :'epsg:3785'}, 
                               sample_point, rg_closest_coordinates[0] )
check_location_of_closestpoint(rf_cube, {'init' :'epsg:27700'},  {'init' :'epsg:3785'} , 
                               sample_point, rf_closest_coordinates[0])

print("Creating dataframe")
rg_df =pd.DataFrame({"time_stamp" : rg_time_series_cube.coord('time').points,
                     "Rainfall": rg_time_series_cube.data})
rg_df['Date_formatted']  = pd.to_datetime(rg_df['time_stamp'], unit='s')\
               .dt.strftime('%Y-%m-%d %H:%M:%S')
rg_df.to_csv("rg_df_westleeds.csv", index = False)

print("Creating dataframe")
rf_df =pd.DataFrame({"time_stamp" : rf_time_series_cube.coord('time').points,
                     "Rainfall": rf_time_series_cube.data})
rf_df['Date_formatted']  = pd.to_datetime(rf_df['time_stamp'], unit='s')\
                .dt.strftime('%Y-%m-%d %H:%M:%S')
rf_df.to_csv("rf_df_westleeds.csv", index = False)


