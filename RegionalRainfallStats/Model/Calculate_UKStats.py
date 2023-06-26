'''
This file creates 2D cubes, in which the values for each grid cell are associated 
with various statistics including the mean, max and various percentiles. 

The cubes cover the area within the bounding box of the UK.

These cubes are saved to file.
They are subsequently used as inputs to plotting functions in which the cubes
are trimmed to smaller areas.
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
import multiprocessing as mp

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *

ems = ['01', '04', '05' ,'06', '07', '08', '09', '10', '11', '12', '13', '15']
yrs_range = "1980_2001" 

# Create a dictionary within which the stats cubes for each ensemble member will
# be stored
ems_dict = {}

# define whether to trim to overlapping model/obs period
overlapping_period = True

############################################
# Define variables and set up environment
#############################################
# Cycle through ensemble members
# For each ensemble member: 
#       Read in all files and join into one cube
#       Trim to the outline of the UK
#       Cut so only hours in JJA remain
#       Find the max, mean and percentile values for each grid square
# 
#def calculate_stats(em):      
for em in ems:
    print(em)
    #############################################
    ## Load in the data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
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
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season year
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 
    
    if overlapping_period == True:
      # Cut to only overlapping period
      jja = jja.extract(iris.Constraint(year = lambda cell: 1989 < cell < 2001))   
      
    ###########################################
    # Find Max, mean, percentiles
    #############################################
    #seconds = time.time()
    jja_mean = jja.aggregated_by(['clim_season'], iris.analysis.MEAN)
    jja_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)
    jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, percent=[95,97,99,99.5, 99.9, 99.99])
  
    ###########################################
    ## Save to file
    ###########################################
    if overlapping_period == True:
      overlapping = '_overlapping'
    else:
      overlapping = ''
    
    iris.save(jja_max, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_{}_jja_max{}.nc'.format(em, overlapping))
    print("JJA max saved")
    iris.save(jja_mean, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_mean{}.nc'.format(overlapping))
    print("JJA mean saved")
    # Save percentiles seperately
    p95 = jja_percentiles[0,:,:,:]
    iris.save(p95, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_p95{}.nc'.format(overlapping))
    p97 = jja_percentiles[1,:,:,:]
    iris.save(p97, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_p97{}.nc'.format(overlapping))
    p99 = jja_percentiles[2,:,:,:]
    iris.save(p99, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_p99{}.nc'.format(overlapping))
    p99_5 = jja_percentiles[3,:,:,:]
    iris.save(p99_5, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_p99.5{}.nc'.format(overlapping))
    p99_75 = jja_percentiles[4,:,:,:]
    iris.save(p99_75, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_p99.75{}.nc'.format(overlapping))
    p99_9 = jja_percentiles[5,:,:,:]
    iris.save(p99_9, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_'+ em+ '_jja_p99.9{}.nc'.format(overlapping))

    ############################################
    # Find wet hour stats
    #############################################
    rain_data = jja.data
    print("loaded data")
    
    # Get one timeslice of the JJA cube
    # This is used as a template to save the data to later
    one_ts = jja[0,:,:]
    
    # Find wet hour proportion
    stats_array = wet_hour_stats(rain_data, 'wet_prop')
    one_ts.data = stats_array
          
    # Test plotting
    #precip_colormap = create_precip_cmap()    
    #qplt.pcolormesh(one_ts, cmap = precip_colormap)
    #plt.gca().coastlines()
      
    # Save to file
    iris.save(one_ts, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Data/em_{}_whprop{}.nc'.format(em,overlapping))
    print("Saved wet hours")
              
### Complete via multiprocessing
# pool = mp.Pool(mp.cpu_count())
# results = [pool.apply_async(calculate_stats, args=(x,)) for x in ems]
# output = [p.get() for p in results]
# print(output) 
# 
   