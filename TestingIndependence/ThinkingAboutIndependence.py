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
import matplotlib
import numpy.ma as ma

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

em = '07'
yrs_range = "1980_2001" 
shared_axis = True

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
#iris.coord_categorisation.add_season_year(concat_cube,'time', name = "season_year") 

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outline of the coast of the UK
#uk_gdf = create_uk_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  
    
################################################
## Find maximum value for each cell
################################################
# Create cube containing the maximum JJA value for each cell
cube_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)

#############################################
## Trim to smaller region
#############################################

def make_animation(region, cube_max, jja):
  global northern_gdf
  global wider_northern_gdf
  global leeds_at_centre_gdf
  global leeds_gdf
  
  if region == 'Northern':
      cube_max = trim_to_bbox_of_region(cube_max, wider_northern_gdf)
  elif region == 'leeds-at-centre':
      cube_max = trim_to_bbox_of_region(cube_max, leeds_at_centre_gdf)
  
  # Mask the data so as to cover any cells not within the specified region 
  if region == 'Northern':
      cube_max = cube_max[0,:,:]
      cube_max.data = ma.masked_where(wider_northern_mask == 0, cube_max.data)
      # Trim to the BBOX of Northern England
      # This ensures the plot shows only the bbox around northern england
      # but that all land values are plotted
      cube_max = trim_to_bbox_of_region(cube_max, northern_gdf)
  
  ################################################
  ## Find cell which has the maximum JJA value
  ## And store its lat and long values 
  ################################################
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
  ## Use this index with the original cube containing the data for all of the locations
  # To extract the timeslice from the cube
  ################################################
  # Take just the timeslice with the maximum values
  timeslice_with_max = jja[index_of_max,:,:]
  
  # Trim
  if region == 'Northern':
      timeslice_with_max = trim_to_bbox_of_region(timeslice_with_max, wider_northern_gdf)
  elif region == 'leeds-at-centre':
      timeslice_with_max = trim_to_bbox_of_region(timeslice_with_max, leeds_at_centre_gdf)
  
  # Mask the data so as to cover any cells not within the specified region 
  if region == 'Northern':
      timeslice_with_max.data = ma.masked_where(wider_northern_mask == 0, timeslice_with_max.data)
      # Trim to the BBOX of Northern England
      # This ensures the plot shows only the bbox around northern england
      # but that all land values are plotted
      timeslice_with_max = trim_to_bbox_of_region(timeslice_with_max, northern_gdf)
  
  ### Plotting
  # Find the minimum and maximum values in that time slice, and use these to produce contour levels
  vmin =np.min(timeslice_with_max.data)
  vmax =np.max(timeslice_with_max.data)
  contour_levels = np.linspace(vmin, vmax, 11,endpoint = True)
  
  # Define decimal places to ensure smaller numbers have decimal places, but not bigger ones.
  if vmax >10:
    n_decimal_places = 0
  else:
    n_decimal_places = 2
  
  # Create a colourmap                                   
  tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
  "#72190E","#882E72","#000000"]                                      
  precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
  # Set the colour for any values which are outside the range designated in lvels
  precip_colormap.set_under(color="white")
  precip_colormap.set_over(color="white")
    
  ## Plot in BNG Projection
  leeds_gdf = leeds_gdf.to_crs({'init' :'epsg:27700'}) 
  northern_gdf = northern_gdf.to_crs({'init' :'epsg:27700'}) 
  plt.figure(figsize=(48, 24), dpi=200)
  proj = ccrs.OSGB()
  # Create axis using this WM projection
  ax = plt.subplot(122, projection=proj)
  # Plot
  mesh = iplt.pcolormesh(timeslice_with_max, cmap = precip_colormap, vmin = vmin, vmax= vmax)
  if region == 'leeds-at-centre':
    leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
  elif region == 'Northern':
     northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)   
     leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
  cb1 = plt.colorbar(mesh, ax=ax, fraction=0.04, pad=0.03, boundaries = contour_levels)
  cb1.ax.tick_params(labelsize=28)
  cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  
  filename = 'Outputs/CellIndependence/{}/em{}.png'.format(region, em)
  plt.savefig(filename, bbox_inches = 'tight')
  ########################################################################
  # Animate
  ########################################################################
  # Define the frames to plot
  # This will take some timeslices before and after the timeslice with the maximum
  frames = range((index_of_max-5), (index_of_max+5))
  
  # Define the maximum and minimum value found across all the time slices being animated
  global_min = 1000
  global_max =0
  for frame in frames:
      timeslice_with_max = jja[frame,:,:]
      global_max = timeslice_with_max.data.max() if timeslice_with_max.data.max() > global_max else global_max
      global_min= timeslice_with_max.data.min() if timeslice_with_max.data.min() < global_min else global_min      
  
  # Create a figure
  #fig,ax = plt.subplots(figsize=(38, 34))
  fig,ax = plt.subplots(figsize=(30, 34)) #width, height
  
  def draw(frame):
      # Clear the previous figure
      plt.clf()
      
      # set up the projection system
      proj = ccrs.OSGB(approx = True)
      # Create axis using this WM projection
      ax =plt.subplot(111, projection = proj)
      #ax.plot(projection=proj)
      timeslice_with_max = jja[frame,:,:]
      
      # Trim
      if region == 'Northern':
          timeslice_with_max = trim_to_bbox_of_region(timeslice_with_max, wider_northern_gdf)
      elif region == 'leeds-at-centre':
          timeslice_with_max = trim_to_bbox_of_region(timeslice_with_max, leeds_at_centre_gdf)
      
      # Mask the data so as to cover any cells not within the specified region 
      if region == 'Northern':
          timeslice_with_max.data = ma.masked_where(wider_northern_mask == 0, timeslice_with_max.data)
          # Trim to the BBOX of Northern England
          # This ensures the plot shows only the bbox around northern england
          # but that all land values are plotted
          timeslice_with_max = trim_to_bbox_of_region(timeslice_with_max, northern_gdf)
      
      
      # Define local min and max values
      local_min =np.min(timeslice_with_max.data)
      local_max =np.max(timeslice_with_max.data)
      
      if shared_axis == True:
          min_val, max_val = global_min, global_max
      else:
          min_val, max_val = local_min, local_max
      contour_levels = np.linspace(min_val, max_val, 11,endpoint = True)
  
      # This ensures smaller numbers have decimal places, but not bigger ones.
      if max_val >10:
        n_decimal_places = 0
      elif max_val <0.1:
          n_decimal_places =3
      else:
        n_decimal_places = 2
      
      # Plot
      mesh = iplt.pcolormesh(timeslice_with_max, cmap = precip_colormap, vmin = min_val, vmax= max_val)
      if region == 'leeds-at-centre':
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
      elif region == 'Northern':
        northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
      cb1 = plt.colorbar(mesh, ax=ax, fraction=0.04, pad=0.03, boundaries = contour_levels)
      cb1.ax.tick_params(labelsize=38)
      cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])  
  
      # Create datetime in human readable format
      datetime = timeslice_with_max.coord('time').units.num2date(timeslice_with_max.coord('time').points[0]) 
      title = u"%s — %s" % (timeslice_with_max.long_name, str(datetime))
      plt.title(title, fontsize = 45)
      return mesh
      
  def init():
      return draw(0)
  
  def animate(frame):
      return draw(frame)
  
  # Not sure what, if anything, this does
  from matplotlib import rc, animation
  rc('animation', html='html5')
  
  
  shared_axis =True
  ani = animation.FuncAnimation(fig, animate, frames,
                                interval=5, save_count=50, blit=False, init_func=init,repeat=False)
  filename  ='Outputs/CellIndependence/{}/em{}_sharedaxis.mp4'.format(region, em)
  ani.save(filename, writer=animation.FFMpegWriter(fps=1))
  
  
  shared_axis =False
  ani = animation.FuncAnimation(fig, animate, frames,
                                interval=5, save_count=50, blit=False, init_func=init,repeat=False)
  filename = 'Outputs/CellIndependence/{}/em{}.mp4'.format(region, em)
  ani.save(filename, writer=animation.FFMpegWriter(fps=1))

# Make the animations
make_animation("Northern", cube_max, jja)
make_animation("leeds-at-centre", cube_max, jja)
