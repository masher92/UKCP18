'''
This file creates 2D cubes, in which the values for each grid cell are associated 
with various statistics including the mean, max and various percentiles.

These statistics are calculated ONLY over the WET hours. 
This is not possible with inbuilt Iris functions, so a method is developed for 
conducting this analysis. This involves extracting the data from the cube
into a 3D array. A for loop then loops around each position in this array (grid
cell) and extracts all the precip data. It then discards any dry hours, before
calculating the statistic value. The resulting 2D array is reattached to a cube
format and saved to file.

The code to perform this is put within a function as this allows the process
to be parallelised. E.g. multiple cores can process each ensemble member
simultaneously.

The cubes cover the area within the bounding box of the UK.

These cubes are saved to file.
They are subsequently used as inputs to plotting functions in which the cubes
are trimmed to smaller areas.
'''

#############################################
# Import necessary packages
#############################################
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
import re
import iris.plot as iplt
import multiprocessing as mp

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

ems = ['01', '04', '05', '06', '07', '08','09', '10', '11','12','13','15']
stats = ['jja_mean_wh', 'jja_max_wh', 'wet_prop', 'jja_p95_wh', 'jja_p97_wh', 'jja_p99_wh',  'jja_p99.5_wh', 'jja_p99.75_wh', 'jja_p99.9_wh']
yrs_range = "1980_2001" 

def create_stats_cube (em):
    print(em)
    #############################################
    ## Load in the data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/1980_2001/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em,  em)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        filenames.append(filename)
    print(len(filenames))

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
    ## Trim to outline of UK
    #############################################
    minmax = lambda x: (np.min(x), np.max(x))
    #bbox = np.array([-8.6500072, 49.863187 ,  1.7632199, 60.8458677])
    bbox = np.array([-10.1500, 49.8963187 ,  1.7632199, 58.8458677])
    # Find the lats and lons of the cube in WGS84
    lons = concat_cube.coord('longitude').points
    lats = concat_cube.coord('latitude').points
    
    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    concat_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]
    print("Trimmed to UK coastline")
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season year
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 

    ############################################
    # Find wet hour stats
    #############################################
    # Load the data for the jja cube so it is no longer lazy
    # seconds = time.time()
    # rain_data = load_data(jja)
    # print("Loaded data in ", time.time() - seconds)

    seconds = time.time()    
    rain_data = jja.data
    print("Loaded data in ", time.time() - seconds)
    
    # Get one timeslice of the JJA cube
    # This is used as a template to save the data to later
    one_ts = jja[0,:,:]
    
    # Loop through the stats
    # Create an array of data values corresponding to that statistic
    # Save it as the data on the template 'one_ts' cube
    # Save this to file
    for stat in stats:
      print(stat)
      seconds = time.time()
      stats_array = wet_hour_stats(rain_data, stat)
      one_ts.data = stats_array
          
      # # Test plotting
      # precip_colormap = create_precip_cmap()    
      # qplt.pcolormesh(one_ts, cmap = precip_colormap)
      # plt.gca().coastlines()
      
      # Save to file
      iris.save(one_ts, 
                '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Wethours/em_'+ em+ '_' +stat + '.nc')

     
# Parallelise the process  
no_of_cores = mp.cpu_count()
pool = mp.Pool(processes=no_of_cores)
results = [pool.apply_async(create_stats_cube, args=(x,)) for x in ems]
output = [p.get() for p in results]
print(output)      
   