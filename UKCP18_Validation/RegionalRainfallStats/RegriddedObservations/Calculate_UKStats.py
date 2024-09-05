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

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *

# Define regridding method
regridding_method = 'NearestNeighbour'

# Whether to cut to same period as model
overlapping_period = False 

#############################################
## Load in the data
#############################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/{}/rg_*'.format(regridding_method)
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    #print(filename)
    filenames.append(filename)
    print(len(filenames))
# Load all cubes into list
monthly_cubes_list = iris.load(filenames,'rainfall_amount')

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Test plotting
iplt.pcolormesh(concat_cube[12])

#############################################
## Trim to outline of UK
#############################################
minmax = lambda x: (np.min(x), np.max(x))
#bbox = np.array([-8.6500072, 49.863187 ,  1.7632199, 60.8458677])
bbox = np.array([-10.1500, 49.8963187 ,  1.7632199, 58.8458677])

#### Find the lats and lons of the cube in WGS84
# Define lats and lons in rotated pole
lats_rp_1d = concat_cube.coord('grid_latitude').points
lons_rp_1d = concat_cube.coord('grid_longitude').points

# Convert to 2D
lons_rp_2d, lats_rp_2d = np.meshgrid(lons_rp_1d, lats_rp_1d)

# Convert to WGS84 (unrotate)
cs = concat_cube.coord_system()
#cs = cube_model.coord('grid_latitude').coord_system
lons_wgs84_2d, lats_wgs84_2d = iris.analysis.cartography.unrotate_pole(lons_rp_2d, lats_rp_2d, 
          cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)

# Create array specifying whether each grid cell is within the bounding box
inregion = np.logical_and(np.logical_and(lons_wgs84_2d > bbox[0],
                                         lons_wgs84_2d < bbox[2]),
                          np.logical_and(lats_wgs84_2d > bbox[1],
                                     lats_wgs84_2d < bbox[3]))
# Find index of lat and long positions which are within the bounding box
region_inds = np.where(inregion)
imin, imax = minmax(region_inds[0])
jmin, jmax = minmax(region_inds[1])

# Trim the cube to just contain these positions
concat_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]

############################################
# Cut to just June-July_August period
#############################################
## Add season variables
iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
iris.coord_categorisation.add_year(concat_cube,'time', name = "year")
iris.coord_categorisation.add_month(concat_cube,'time', name = "month")

# Keep only JJA
jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))

# Trim to overlapping period with model
if overlapping_period == True:
  # Cut to only overlapping period
  jja = jja.extract(iris.Constraint(year = lambda cell: 1989 < cell < 2001))   

###########################################
# Find Max, mean, percentiles
#############################################
# jja_mean = jja.aggregated_by(['clim_season'], iris.analysis.MEAN)
# jja_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)
# jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, percent=[95,97,99,99.5, 99.9, 99.99])
 
###########################################
## Save to file
###########################################
if overlapping_period == True:
  overlapping = '_overlapping'
else:
  overlapping = ''

# iris.save(jja_max, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_max{}.nc'.format(regridding_method, overlapping))
# print("JJA max saved")
# iris.save(jja_mean, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_mean{}.nc'.format(regridding_method, overlapping))
# print("JJA mean saved")
# # Save percentiles seperately
# p95 = jja_percentiles[0,:,:,:]
# iris.save(p95, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_p95{}.nc'.format(regridding_method, overlapping))
# p97 = jja_percentiles[1,:,:,:]
# iris.save(p97, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_p97{}.nc'.format(regridding_method, overlapping))
# p99 = jja_percentiles[2,:,:,:]
# iris.save(p99, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_p99{}.nc'.format(regridding_method, overlapping))
# p99_5 = jja_percentiles[3,:,:,:]
# iris.save(p99_5, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_p99.5{}.nc'.format(regridding_method, overlapping))
# p99_75 = jja_percentiles[4,:,:,:]
# iris.save(p99_75, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_p99.75{}.nc'.format(regridding_method, overlapping))
# p99_9 = jja_percentiles[5,:,:,:]
# iris.save(p99_9, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_p99.9{}.nc'.format(regridding_method, overlapping))

# Wet hour props
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
iris.save(one_ts, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/{}/jja_whprop{}.nc'.format(regridding_method,overlapping))
print("Saved wet hours")
          
 
   