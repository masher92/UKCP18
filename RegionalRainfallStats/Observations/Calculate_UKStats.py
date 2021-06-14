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
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

#############################################
## Load in the data
#############################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_*'
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
#iplt.pcolormesh(concat_cube[12])

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

#############################################
## Trim to outline of UK
#############################################
minmax = lambda x: (np.min(x), np.max(x))
#bbox = np.array([-8.6500072, 49.863187 ,  1.7632199, 60.8458677])
bbox = np.array([-10.1500, 49.8963187 ,  1.7632199, 58.8458677])

#### Find the lats and lons of the cube in WGS84
# Define lats and lons in rotated pole
lats_1d = concat_cube.coord('projection_y_coordinate').points
lons_1d = concat_cube.coord('projection_x_coordinate').points

# Convert to 2D
lons_2d, lats_2d = np.meshgrid(lons_1d, lats_1d)

# Convert to WGS84
lons_2d ,lats_2d= transform(Proj(init='epsg:27700'),
                                  Proj(init='epsg:4326'),
                                  lons_2d,lats_2d)

# Create array specifying whether each grid cell is within the bounding box
inregion = np.logical_and(np.logical_and(lons_2d > bbox[0],
                                         lons_2d < bbox[2]),
                          np.logical_and(lats_2d > bbox[1],
                                     lats_2d < bbox[3]))

# Find index of lat and long positions which are within the bounding box
region_inds = np.where(inregion)
imin, imax = minmax(region_inds[0])
jmin, jmax = minmax(region_inds[1])

# Trim the cube to just contain these positions
concat_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]

# Check plotting
iplt.pcolormesh(concat_cube[12])

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
jja = trim_to_bbox_of_region_obs(jja, leeds_at_centre_gdf)

#jja_mean = jja.aggregated_by(['clim_season'], iris.analysis.MEAN)
#jja_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)
jja_max = jja.collapsed('time', iris.analysis.MAX)
jja_mean = jja.collapsed('time', iris.analysis.MEAN)
jja_percentiles = jja.collapsed('time', iris.analysis.PERCENTILE, percent = [95, 97,99,99.5, 99.75, 99.9])

iplt.pcolormesh(p95)

###########################################
## Save to file
###########################################
#iris.save(jja_max, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/jja_max.nc')
#print("JJA max saved")
#iris.save(jja_mean, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/jja_mean.nc')
#print("JJA mean saved")
# Save percentiles seperately
p95 = jja_percentiles[0,:,:,:]
iris.save(p95, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_p95.nc')
p97 = jja_percentiles[1,:,:,:]
iris.save(p97, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_p97.nc')
p99 = jja_percentiles[2,:,:,:]
iris.save(p99, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_p99.nc')
p99_5 = jja_percentiles[3,:,:,:]
iris.save(p99_5, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_p99.5.nc')
p99_75 = jja_percentiles[4,:,:,:]
iris.save(p99_75, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_p99.75.nc')
p99_9 = jja_percentiles[5,:,:,:]
iris.save(p99_9, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_p99.9.nc')
#
iris.save(jja_max, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_max.nc')
print("JJA max saved")
iris.save(jja_mean, '/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/jja_mean.nc')
print("JJA mean saved")