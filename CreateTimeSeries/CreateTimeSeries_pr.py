"""
This file produces a cube containing a time series of hourly precipitation values
for a specific geographical point near Leeds. 
    
NB:
    Iris method for interpolating to a geographical location is extremely slow,
    so trying a different method (need to check)
    
@author Molly Asher
@Version 1
"""

#############################################
# Set up environment
#############################################
import iris
import cartopy.crs as ccrs
import os
from scipy import spatial
import itertools
import iris.quickplot as qplt
import warnings
import copy
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
#import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/UKCP18"
os.chdir(ddir)

# Data date range
start_year = 1980
end_year = 1982

#############################################
# Read in ten year's worth of data
#############################################
# Define filenames for the ten years of required data
pattern = os.path.join(r'pr_rcp85_land-cpm_uk_2.2km_01_1hr_{}*')
filenames =[]
for year in range(start_year,end_year+1):
    wildcard = pattern.format(year)
    # print(wildcard)
    for filename in glob.glob(wildcard):
        filenames.append(filename)
        
# Load in the cubes
cubes = iris.load(filenames,'lwe_precipitation_rate')
cubes_2 = copy.deepcopy(cubes)

#############################################
# Define a sample point at which we are interested in extracting the precipitation timeseries.
# Assign this the same projection as the projection data
#############################################
# Create a cartopy CRS representing the coordinate sytem of the data in the cube.
rot_pole = cubes[0].coord('grid_latitude').coord_system.as_cartopy_crs()

# Define a sample point of interest, in standard lat/long.
# Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
lon, lat = -1.37818, 53.79282 # Coordinates of location in Garforth
target_xy = rot_pole.transform_point(lon, lat, original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
   
# Store the sample point of interest as a tuples (with their coordinate name) in a list
sample_points = [('grid_latitude', target_xy[1]), ('grid_longitude', target_xy[0])]

#############################################
# Method 1 for creating one concatenated time series cube for the location of interest
    # Perform interpolation on each cube individually. Save each interpolated cube
    # to a list which is converted to a Cubelist and, finally, concatenated into 1 cube. 
#############################################
start = timer()

# Create a list to store the interpolated cubes
interpolated_cubes = []  

# Loop through each cube in cubes, perform interpolation, save interpolated cube
# to list and delete larger cube
for cube_idx in range(0,len(cubes)):
    print('Cube with index: ', cube_idx)
    # Check whether data is fully loaded
    #print(cubes[0].has_lazy_data())
    # Remove attributes which aren't the same across all the cubes (otherwise late concat fails)
    for attr in ['creation_date', 'tracking_id', 'history']:
        if attr in cubes[0].attributes:
            del cubes[0].attributes[attr]
                # Do the interpolation
    
    # Interpolate data to the sample location
    interpolated = cubes[0].interpolate(sample_points, iris.analysis.Nearest())
    # Check whether at this point data is fully loaded
    # print(interpolated.has_lazy_data())
    # Add interpolated cube to list of cubes
    interpolated_cubes.append(interpolated)
    # Delete the cube from the list and the interpolated cube from memory
    del(interpolated)
    del(cubes[0])

# Create a cube list from the (standard python) list of cubes
cubes = iris.cube.CubeList(interpolated_cubes)    
    
# Concatenate the cubes into one
concat_cube = cubes.concatenate_cube()

# reduce the dimensions (remove ensemble member dimension)
concat_cube = concat_cube[0, :]

print(round(timer() - start, 3), 'seconds')   

#############################################
# Method 2 for creating one concatenated time series cube for the location of interest
    # Firstly, concatenate the Cubelist into one cube.
    # Create a list of the latitudes and longitudes in the concatenated cube and find
    # which of these locations is closest to the sample_point
    # Extract the subset of the concatenated cube which refers to this location.
#############################################
# =============================================================================
# start = timer()
# 
# # Remove attributes which aren't the same across all the cubes.
# for cube in cubes_2:
#     for attr in ['creation_date', 'tracking_id', 'history']:
#         if attr in cube.attributes:
#             del cube.attributes[attr]
# 
# # Concatenate the cubes into one
# concat_cube_2 = cubes_2.concatenate_cube()
# 
# # Reduce the dimensions (remove ensemble member dimension)
# concat_cube_2 = concat_cube_2[0, :]
#     
# # Create a list of all the tuple pairs of latitude and longitudes
# locations = list(itertools.product(concat_cube_2.coord('grid_latitude').points, concat_cube_2.coord('grid_longitude').points))
# 
# # Correct them so that 360 merges back into one
# corrected_locations = []
# for location in locations:
#     if location[0] >360:
#         new_lat = location[0] -360
#     else: 
#         new_lat = location[0]
#     if location[1] >360:
#         new_long = location[1] -360     
#     else:
#         new_long = location[1]
#     new_location = new_lat, new_long 
#     corrected_locations.append(new_location)
# 
# # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
# tree = spatial.KDTree(corrected_locations)
# closest_point_idx = tree.query([(sample_points[0][1], sample_points[1][1])])[1][0]
# 
# # Extract the lat and long values of this point using the index
# closest_lat = locations[closest_point_idx][0]
# closest_long = locations[closest_point_idx][1]
# 
# # Use this closest lat, long pair to collapse the latitude and longitude dimensions
# # of the concatenated cube to keep just the time series for this closest point 
# time_series = concat_cube_2.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# print('Method 2 completed in ' , round(timer() - start, 3), 'seconds')   
# 
# =============================================================================
###########################################################
# Check results
###########################################################
# Test whether the precipitation values produced by the 2 methods are the same
#(concat_cube.data==time_series.data).all()

# PLot the two time_series and compare
#qplt.plot(concat_cube)
#qplt.plot(time_series)

###########################################################
# Save cube 
###########################################################
iris.save(concat_cube, 
          f'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries_cubes/Pr_{start_year}-{end_year}.nc')


##############################################################################
# Save dataframe
##############################################################################
# Create a dataframe containing the date and the precipitation data
df = pd.DataFrame({'Date': np.array(concat_cube.coord('yyyymmddhh').points),
                  'Precipitation (mm/hr)': np.array(concat_cube.data)})

# Format the date column
df['Date_Formatted'] =  pd.to_datetime(df['Date'], format='%Y%m%d%H')

# Write to a csv
df.to_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/Pr_{start_year}-{end_year}_EM01.csv", index = False)





