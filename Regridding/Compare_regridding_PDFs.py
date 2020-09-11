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

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
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

###############################
# Regridded - Rotated pole?
#########################
rg_string = '_regridded_2.2km/rg_'
target_crs = {'init': 'epsg:4326'}
 
################################################################
# Read in cube
################################################################
filenames=glob.glob('Outputs/CEH-GEAR' +rg_string + 'CEH-GEAR-1hr_*')
monthly_cubes_list = iris.load(filenames,'rainfall_amount')

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()      
                               
################################################################
# Cut the cube to the extent of GDF surrounding Leeds  
################################################################
# Find coordinate names of lats/long or x/y
coord_names = [coord.name() for coord in concat_cube.coords()]

# Create lambda function for...
minmax = lambda x: (np.min(x), np.max(x))              

# Create GDF in correct CRS
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
                               
# Find the bounding box of the region   
bbox = leeds_at_centre_gdf.total_bounds                

# Find the lats and lons of the cube in OSGB36   
lons = concat_cube.coord('grid_longitude').points
lats = concat_cube.coord('grid_latitude').points
lons_2d, lats_2d = np.meshgrid(lons, lats)   
          
# For regridded cube
# Convert to wgs84
cs = concat_cube.coord_system()
lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)

# Find which are within the BBOX                       
inregion = np.logical_and(np.logical_and(lons_2d > bbox[0],
                 lons_2d < bbox[2]),
  np.logical_and(lats_2d > bbox[1],
                 lats_2d < bbox[3]))
region_inds = np.where(inregion)                       
imin, imax = minmax(region_inds[0])                    
jmin, jmax = minmax(region_inds[1])                    
                               
# trim the cube                                        
trimmed_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]

###############################################################
# Quickly check plotting
################################################################
cube = trimmed_cube

# Create GDF in correct CRS
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
leeds_gdf = leeds_gdf.to_crs(target_crs) 

timeseries_frame = 10
qplt.contourf(cube[timeseries_frame])

################################################################
# Better plotting
################################################################
# Create 2d lats and lons from trimmed cube 
coord_names = [coord.name() for coord in cube.coords()]

# Need to recalculate them as the previous variables aren't trimmed
lats = cube.coord(coord_names[1]).points
lons = cube.coord(coord_names[2]).points
lons_2d, lats_2d = np.meshgrid(lons, lats)

# For regridded cube
# Convert to wgs84
cs = cube.coord_system()
lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
  

fig, ax = plt.subplots(figsize=(20,20))
# Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_2d, lats_2d, cube[timeseries_frame].data,
  linewidths=3, alpha = 1, cmap = 'GnBu')
cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
#cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
#plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =ax.tick_params(labelsize='xx-large')
#plot =region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)






###############################
# Reformatted - OSGB36
#########################
rf_string = '_reformatted/rf_'
target_crs = {'init': 'epsg:27700'}
 
################################################################
# Read in cube
################################################################
filenames=glob.glob('Outputs/CEH-GEAR' +rf_string + 'CEH-GEAR-1hr_*')
monthly_cubes_list = iris.load(filenames,'rainfall_amount')

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()      
                               
################################################################
# Cut the cube to the extent of GDF surrounding Leeds  
################################################################
# Find coordinate names of lats/long or x/y
coord_names = [coord.name() for coord in concat_cube.coords()]

# Create lambda function for...
minmax = lambda x: (np.min(x), np.max(x))              

# Create GDF in correct CRS
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
                               
# Find the bounding box of the region   
bbox = leeds_at_centre_gdf.total_bounds                

# Find the lats and lons of the cube in OSGB36   
lats = concat_cube.coord('projection_y_coordinate').points
lons = concat_cube.coord('projection_x_coordinate').points
lons_2d, lats_2d = np.meshgrid(lons, lats)             


# Find which are within the BBOX                       
inregion = np.logical_and(np.logical_and(lons_2d > bbox[0],
                 lons_2d < bbox[2]),
  np.logical_and(lats_2d > bbox[1],
                 lats_2d < bbox[3]))
region_inds = np.where(inregion)                       
imin, imax = minmax(region_inds[0])                    
jmin, jmax = minmax(region_inds[1])                    
                               
# trim the cube                                        
trimmed_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]

###############################################################
# Quickly check plotting
################################################################
cube = trimmed_cube
target_crs = {'init' :'epsg:27700'}

# Create GDF in correct CRS
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
leeds_gdf = leeds_gdf.to_crs(target_crs) 

timeseries_frame = 10
qplt.contourf(cube[timeseries_frame])

################################################################
# Better plotting
################################################################
# Create 2d lats and lons from trimmed cube 
coord_names = [coord.name() for coord in cube.coords()]

# Need to recalculate them as the previous variables aren't trimmed
lats = cube.coord(coord_names[1]).points
lons = cube.coord(coord_names[2]).points
lons_2d, lats_2d = np.meshgrid(lons, lats)

# For regridded cube
# Convert to wgs84
#cs = cube.coord_system()
#lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
  

fig, ax = plt.subplots(figsize=(20,20))
# Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_2d, lats_2d, cube[timeseries_frame].data,
  linewidths=3, alpha = 1, cmap = 'GnBu')
cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
#cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
#plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =ax.tick_params(labelsize='xx-large')
#plot =region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)

################################################################
# Boith together s function  
################################################################
def create_trimmed_cube(gdf, string, target_crs):    
  filenames=glob.glob('Outputs/CEH-GEAR' +rg_string + 'CEH-GEAR-1hr_*')
  monthly_cubes_list = iris.load(filenames,'rainfall_amount')
  
  # Concatenate the cubes into one
  concat_cube = monthly_cubes_list.concatenate_cube()      
                                 
  ################################################################
  # Cut the cube to the extent of GDF surrounding Leeds  
  ################################################################
  # Find coordinate names of lats/long or x/y
  coord_names = [coord.name() for coord in concat_cube.coords()]
  
  # Create lambda function for...
  minmax = lambda x: (np.min(x), np.max(x))              
  
  # Create GDF in correct CRS
  leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
                                 
  # Find the bounding box of the region   
  bbox = leeds_at_centre_gdf.total_bounds                
  
  # Create 2d lats and lons from trimmed cube 
  coord_names = [coord.name() for coord in concat_cube.coords()]
    
  # Find the lats and lons of the cube in OSGB36   
  lons = concat_cube.coord(coord_names[1]).points
  lats = concat_cube.coord(coord_names[2]).points
  lons_2d, lats_2d = np.meshgrid(lons, lats)   
            
  # For regridded cube
  if string == '_regridded_2.2km/rg_':
    cs = concat_cube.coord_system()
    lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
  
  # Find which are within the BBOX                       
  inregion = np.logical_and(np.logical_and(lons_2d > bbox[0], lons_2d < bbox[2]),
    np.logical_and(lats_2d > bbox[1],  lats_2d < bbox[3]))
  region_inds = np.where(inregion)                       
  imin, imax = minmax(region_inds[0])                    
  jmin, jmax = minmax(region_inds[1])                    
                                 
  # trim the cube                                        
  trimmed_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]

  return trimmed_cube
    
rf_cube = create_trimmed_cube(leeds_at_centre_gdf, rf_string, {'init' :'epsg:27700'})
rg_cube = create_trimmed_cube(leeds_at_centre_gdf, rg_string, {'init' :'epsg:4326'})

def plot_cube(cube, target_crs, timeseries_frame):
  # Create GDF in correct CRS
  leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
  leeds_gdf = leeds_gdf.to_crs(target_crs) 
  
  # Create 2d lats and lons from trimmed cube 
  coord_names = [coord.name() for coord in cube.coords()]
  
  lats = cube.coord(coord_names[1]).points
  lons = cube.coord(coord_names[2]).points
  lons_2d, lats_2d = np.meshgrid(lons, lats)

  # For regridded cube
  # Convert to wgs84
  if target_crs ==  {'init' :'epsg:4326'}:
    cs = cube.coord_system()
    lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
     
  fig, ax = plt.subplots(figsize=(20,20))
  # Add edgecolor = 'grey' for lines
  plot =ax.pcolormesh(lons_2d, lats_2d, cube[timeseries_frame].data,
                linewidths=3, alpha = 1, cmap = 'GnBu')
  cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
  cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
  #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
  #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
  plot =ax.tick_params(labelsize='xx-large')
  #plot =region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
  plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
  plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
    

plot_cube(rg_cube,  {'init' :'epsg:4326'}, 10)
plot_cube(rf_cube,  {'init' :'epsg:27700'}, 10)

