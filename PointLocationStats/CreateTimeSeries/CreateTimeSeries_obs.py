###### Notes on structure of these cubes
# This IRIS cube has a different structure to the UKCP18 data.
# This is something to do with it being in the rotated pole co-ordinate system
# Latitude and longitude are provided on 2d Array. Imagine that the values
# for these that correspond would appear on top of each other if these arrays
# were stacked. I.e. accessing the values from the arrays with the same index
# gives corresponding values. 
#sss

# Import packages
from numpy import array, shape
import numpy as np
import iris
import matplotlib as mpl
import os
import matplotlib.pyplot as plt
import iris.plot as iplt
import iris.quickplot as qplt
from iris.time import PartialDateTime 
import pandas as pd
from timeit import default_timer as timer
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
import sys 
import glob

# Stops warning on loading Iris cubes
iris.FUTURE.netcdf_promote = True
iris.FUTURE.netcdf_no_unlimited = True

# Provide root_fp as argument
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *

# Define name and coordinates of location
location = 'Armley'
lat = -1.37818
lon = 53.79282

############################################################
# Read in monthly cubes and concatenate into one long timeseries cube
###########################################################
# For some reason a backslash was showing instead of a forward slash
filenames = [os.path.normpath(i) for i in glob.glob('datadir/CEH-GEAR/CEH-GEAR-1hr_*')]

# Load in the rainfall cubes into a list, taking just the rainfall amount
monthly_cubes_list = iris.load(filenames, 'rainfall_amount')

# Concatenate the cubes
obs_cubes = monthly_cubes_list.concatenate_cube()

##############################################################################
# Extract the indices of the data point in the cube closest to a point of interest
##############################################################################
# Read in the list of cubes, containing the lat and long cubes
one_cube = iris.load(filenames[0])

# Find the index of the point in the grid which is closest to the point of interest
# Considering the grid both flipped and not flipped
# For just creating a time series and not plotting, flipping is not really necesary
# but can be used in the testing below
closest_idx = find_idx_closestpoint(one_cube, lat, lon, flip = False)
closest_idx_fl = find_idx_closestpoint(one_cube, lat, lon, flip = True)

#############################################################################
# Check that the index returned by this process matches expected location.
# Use one hour of data to get the shape of the data.
# Set all values to 0; expect for at the location found above.
# Plot and check location
##############################################################################
# hour = obs_cubes[1]
# #Extract the data
# hour_data = hour.data
# # Flip the data so it's not upside down
# hour_data_fl = np.flipud(hour_data)
# # Fill empty values with NaN
# hour_data_fl = hour_data_fl.filled(np.nan) 
# # Fill all places with 0
# hour_data_fl.fill(0)
# # Fill the location with a different value
# hour_data_fl[closest_idx_fl[0],closest_idx_fl[1]] = 7

# # # Plot
# contour = plt.contourf(hour_data_fl)
# contour = plt.colorbar()
# contour =plt.axes().set_aspect('equal') 
# plt.plot(closest_idx_fl[1], closest_idx_fl[0], 'o', color='black', markersize = 3) 

#############################################################################
# Trim the concatenated cube to the location of interest
##############################################################################
# Keep all of the first dimension (time), and trim to just the location of interest
interpolated_cube = obs_cubes[:,closest_idx[0], closest_idx[1]]

# Plot the timeseries
# qplt.plot(interpolated_cube)
# plt.xticks(rotation=45)

# iplt.plot(obs_cubes)
# plt.xticks(rotation=45)

#############################################################################
# Cut to time period matching up with UKCP18 data
##############################################################################
# Time constraint for which to test the data
days_constraint = iris.Constraint(time=lambda cell: PartialDateTime(year = 1990, month=1, day=11) < cell.point < PartialDateTime(year = 2001, month=1, day=1))

# Trim data to this time period
interpolated_cube_1990_2001 = interpolated_cube.extract(days_constraint)

############################################################################
# Create as dataframe
##############################################################################
# Create a dataframe containing the date and the precipitation data
df = pd.DataFrame({'Date': np.array(interpolated_cube.coord('time').points),
                  'Precipitation (mm/hr)': np.array(interpolated_cube.data),
                  'Date_formatted': interpolated_cube.coord('time').units.num2date(interpolated_cube.coord('time').points)})

# Create a dataframe containing the date and the precipitation data
df_1990_2001 = pd.DataFrame({'Date': np.array(interpolated_cube_1990_2001.coord('time').points),
                  'Precipitation (mm/hr)': np.array(interpolated_cube_1990_2001.data),
                  'Date_formatted': interpolated_cube_1990_2001.coord('time').units.num2date(interpolated_cube_1990_2001.coord('time').points)})

###########################################################
# Save cube and csv
###########################################################
iris.save(interpolated_cube, 
          "/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_cubes/1990-2014.nc")
iris.save(interpolated_cube_1990_2001, 
          "/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_cubes/1990-2001.nc")

df.to_csv("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_csv/1990-2014.csv", index = False)
df_1990_2001.to_csv("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_csv/1990-2001.csv", index = False)


### Save the coordinates for which the data was extracted
coordinates_str = "latitude: " + str(lat) + ", longitude: " + str(lon)
f =open("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/location_coordinates.txt", "w")
f.write(coordinates_str)
f.close()