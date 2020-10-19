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
import matplotlib as mpl
import iris.plot as iplt
import matplotlib.pyplot as plt

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

em = '06'
yrs_range = "1980_2001" 

#############################################
## Load in the data
#############################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    filenames.append(filename)
print(len(filenames))

#Load into cube list
monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
for cube in monthly_cubes_list:
     for attr in ['creation_date', 'tracking_id', 'history']:
         if attr in cube.attributes:
             del cube.attributes[attr]

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Remove ensemble member dimension
concat_cube = concat_cube[0,:,:,:]

#############################################
## Add season and year variables
#############################################
# Add clim_season and season year
iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
# Keep only JJA
jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
iris.coord_categorisation.add_season_year(concat_cube,'time', name = "season_year") 

#############################################
## Trim to smaller region
#############################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
jja = trim_to_bbox_of_region(jja, leeds_at_centre_gdf)

################################################
## Find cell which has the maximum JJA value
## And store its lat and long values 
################################################
# Create cube containing the maximum JJA value for each cell
cube_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)

# Find position of cell with the maximum value across all cells
# First convert data to 1D array
data_1d= cube_max.data.reshape(-1)
index_of_max = np.argmax(data_1d)

# Create lats and lons as 1D array
lats = cube_max.coord('grid_latitude').points
lons = cube_max.coord('grid_longitude').points
lons, lats = np.meshgrid(lons, lats)
lons = lons.reshape(-1)
lats = lats.reshape(-1)

# Find lat, long of cell with maximum value
lat_with_max = lats[index_of_max]
lon_with_max = lons[index_of_max]

################################################
## Use the lat/long values to extract a time series cube for just this location
# Use this to find the index of the time with the highest value
################################################
# Extract timeseries cube for the location which has the maximum rainfall value
max_val = jja.extract(iris.Constraint(grid_latitude =lat_with_max,
                                           grid_longitude = lon_with_max))

# Find the index of the timeslice with the maximum value
index_of_max = np.argmax(max_val.data)

################################################
## Use this index on the original cube containing the data for all of the locations

################################################
timeslice_with_max = jja[index_of_max,:,:]

vmin =np.min(test.data)
vmax =np.max(test.data)
contour_levels = np.linspace(vmin, vmax, 11,endpoint = True)
# This ensures smaller numbers have decimal places, but not bigger ones.
if vmax >10:
  n_decimal_places = 0
else:
  n_decimal_places = 2

# # Web Mrecator prrojection
# leeds_gdf = leeds_gdf.to_crs({'init' :'epsg:3785'}) 
# plt.figure(figsize=(48, 24), dpi=200)
# proj = ccrs.Mercator.GOOGLE
# # Create axis using this WM projection
# ax = plt.subplot(122, projection=proj)
# # Plot
# mesh = iplt.pcolormesh(test, cmap = precip_colormap, vmin = vmin, vmax= vmax)
# leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
# cb1 = plt.colorbar(mesh, ax=ax, fraction=0.04, pad=0.03, boundaries = contour_levels)
# cb1.ax.tick_params(labelsize=28)
# cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  


## BNG Projection
leeds_gdf = leeds_gdf.to_crs({'init' :'epsg:27700'}) 
plt.figure(figsize=(48, 24), dpi=200)
proj = ccrs.OSGB()
# Create axis using this WM projection
ax = plt.subplot(122, projection=proj)
# Plot
mesh = iplt.pcolormesh(test, cmap = precip_colormap, vmin = vmin, vmax= vmax)
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
cb1 = plt.colorbar(mesh, ax=ax, fraction=0.04, pad=0.03, boundaries = contour_levels)
cb1.ax.tick_params(labelsize=28)
cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  

########################################################################
# Animate
########################################################################
global_min = 1000
global_max =0
for frame in frames:
    test = jja[frame,:,:]
    global_max = test.data.max() if test.data.max() > global_max else global_max
    global_min= test.data.min() if test.data.min() < global_min else global_min      

# Create a figure
fig,ax = plt.subplots(figsize=(48, 24))

frames = range((index_of_max-5), (index_of_max+5))

def draw(frame):
    # Clear the previous figure
    plt.clf()
    
    proj = ccrs.OSGB(approx = True)
    # Create axis using this WM projection
    ax =plt.subplot(111, projection = proj)
    #ax.plot(projection=proj)
    test = jja[frame,:,:]
    
    vmin =np.min(test.data)
    vmax =np.max(test.data)
    contour_levels = np.linspace(global_min, global_max, 11,endpoint = True)
    # This ensures smaller numbers have decimal places, but not bigger ones.
    if global_max >10:
      n_decimal_places = 0
    else:
      n_decimal_places = 2
    
    mesh = iplt.pcolormesh(test, cmap = precip_colormap, vmin = global_min, vmax= global_max)
    leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
    cb1 = plt.colorbar(mesh, ax=ax, fraction=0.04, pad=0.03, boundaries = contour_levels)
    cb1.ax.tick_params(labelsize=28)
    cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  

    # Create datetime in human readable format
    datetime = test.coord('time').units.num2date(test.coord('time').points[0]) 
    title = u"%s — %s" % (test.long_name, str(datetime))
    plt.title(title, fontsize = 35)
    return mesh
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

# Not sure what, if anything, this does
from matplotlib import rc, animation
rc('animation', html='html5')

ani = animation.FuncAnimation(fig, animate, frames,
                              interval=30, save_count=50, blit=False, init_func=init,repeat=False)
ani.save('Outputs/CellIndependence/leeds-at-centre/em{}_cbar_sharedaxis.mp4'.format(em), writer=animation.FFMpegWriter(fps=2))


