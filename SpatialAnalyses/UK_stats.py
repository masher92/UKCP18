'''
This file calculates statistics (mean, max, various percentiles) for each grid 
cell across the whole of the UK.
It plots these and saves the results to file.
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

# For extracting the variable name from a variable
def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

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

ems = ['07']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

# Create a dictionary within which the stats cubes for each ensemble member will
# be stored
ems_dict = {}

# Cycle through ensemble members
# For each ensemble member: 
#       Read in all files and join into one cube
#       Trim to the outline of the UK
#       Cut so only hours in JJA remain
#       Find the max, mean and percentile values for each grid square
#       
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
    
    # filenames =[]
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 
    
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    
    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    
    # Extract just dry hours?!
    #test = iris.Constraint(rainfall_)
    
    
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
    #jja_max.to_netcdf('/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_jja_max.nc', encoding={'rank_in_season': {'dtype': 'i4'}})
    #jja_mean.to_netcdf('/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_jja_mean.nc', encoding={'rank_in_season': {'dtype': 'i4'}})    
    #jja_percentiles.to_netcdf('/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_jja_percentiles.nc', encoding={'rank_in_season': {'dtype': 'i4'}}) 
    
    iris.save(jja_max, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_max.nc')
    print("JJA max saved")
    iris.save(jja_mean, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_mean.nc')
    print("JJA mean saved")
    iris.save(jja_percentiles, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_percentiles.nc')
    print("JJA percentiles saved")
    

  # Save each percentile seperately
  for em in ems:
      em_per = iris.load('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_percentiles.nc'
                             ,'lwe_precipitation_rate')[0]
      print(em_per)
      p95 = em_per[0,:,:,:]
      iris.save(p95, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_p95.nc')
      p97 = em_per[1,:,:,:]
      iris.save(p97, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_p97.nc')
      p99 = em_per[2,:,:,:]
      iris.save(p99, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_p99.nc')
      p99_5 = em_per[3,:,:,:]
      iris.save(p99_5, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_p99.5.nc')
      p99_75 = em_per[4,:,:,:]
      iris.save(p99_75, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_p99.75.nc')
      p99_9 = em_per[5,:,:,:]
      iris.save(p99_9, '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_p99.9.nc')
