"""
File which:
    

@author Molly Asher
@Version 1.0

"""

#############################################
# Set up environment
#############################################
import iris
import copy
import pandas as pd
import os
#import iris
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
#import time
import warnings
import numpy as np
import glob
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
from scipy import stats
import seaborn as sns

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/UKCP18"
os.chdir(ddir)

month_filename = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/UKCP18/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc"






############################################
# Read in a month's worth of data
#############################################
month_filename = "pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810601-19810630.nc"
# Load as a cube
month_cube = iris.load(month_filename,'lwe_precipitation_rate')[0]
# Remove the ensemble member dimension (there was only one)
month_cube = month_cube[0, :]

#############################################
# Cut the cube to one particular location
#############################################
# Create a cartopy CRS representing the coordinate sytem of the data in the cube.
rot_pole = month_cube[0].coord('grid_latitude').coord_system.as_cartopy_crs()

# Define a sample point of interest, in standard lat/long.
# Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
lon, lat = -1.588941, 53.802070 # Coordinates of location in Garforth
target_xy = rot_pole.transform_point(lon, lat, original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
   
# Store the sample points as tuples (with their coordinate name) in a list
sample_points = [('grid_latitude', target_xy[1]), ('grid_longitude', target_xy[0])]

# Cut the cube to this location of interest
interpolated = month_cube.interpolate(sample_points, iris.analysis.Nearest())


#############################################
# Extract the data for a particular location
#############################################
# Store data in an array
test_arr = np.array(interpolated.data)

# Filter out values less than 0.1mm/hour
test_arr = test_arr[test_arr >0.1]

# Create as a series
test_pds = pd.Series(test_arr, name="Precipitation (mm/hour)")


###########################
# Plot pdf 
ax = sns.distplot(test_arr)
# Using the series allows the variable to be labelled
ax = sns.distplot(test_pds)
# Can choose whether to include a rug plot, or the histogram
ax = sns.distplot(test_pds, rug=True, hist=False)
# Can shade in the plot
ax = sns.kdeplot(test_pds, shade = True, color = 'r')

# Bandwidth is a measure of how closely the density should match the distribution
sns.kdeplot(x)
sns.kdeplot(x, bw=.1, label="bw: 0.2")
sns.kdeplot(x, bw=5, label="bw: 2")
plt.legend();

# Can also plot a parametric distribution and compare how well the data fits to it
from scipy.stats import norm
from scipy.stats import gamma
ax = sns.distplot(test_pds, fit=norm, kde=False)
sns.distplot(test_pds, kde=False, fit=gamma);


