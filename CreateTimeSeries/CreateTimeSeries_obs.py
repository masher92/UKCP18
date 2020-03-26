# Import packages
from numpy import array, shape
import numpy as np
import iris
from cartopy import geodesic
import matplotlib as mpl
import os
import time
import matplotlib.pyplot as plt
import matplotlib
import iris.plot as iplt
import iris.quickplot as qplt
import pandas as pd
import copy
from timeit import default_timer as timer
# This is needed for the animation plot to work
plt.rcParams['animation.ffmpeg_path'] ='C:\\Users\\gy17m2a\\OneDrive - University of Leeds\\PhD\\DataAnalysis\\ffmpeg-20200225-36451f9-win64-static\\bin\\ffmpeg.exe'
import matplotlib.animation as animation

# Define the local directory where the data is stored; set this as work dir
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/CEH-GEAR"
os.chdir(ddir)

# Data date range
start_year = 1990
end_year = 1992

#############################################
# Read in ten year's worth of data
#############################################
# Loop through years and then months and append each filename to the list
filenames = []
for year in range(start_year, end_year+1):
    for month in range(1,13):
        month = str(month).zfill(2) 
        filename = f"CEH-GEAR-1hr_{year}{month}.nc"
        filenames.append(filename)
       
# Load in the rainfall cubes into a list, taking just the rainfall amount
obs_pr_cubelist = iris.load(filenames,"rainfall_amount")
obs_pr_cubelist = copy.deepcopy(obs_pr_cubelist)

# Concatenate the cubes
obs_pr_cubes = obs_pr_cubelist.concatenate_cube()

##############################################################################
# Extract the indices of the data point in the cube closest to a point of interest
##############################################################################
# Function which extracts the indices of the closest location in the observations
# cube, to a point of interest 
def find_idx_closestpoint (coords_cube, target_lat, target_lon, flip):
           
    # Extract the latitude and longitude values from the cube into arrays.
    # In each of the latitude and longitude cubes the coordinate values are stored 
    # as an array of values over two dimensions, rather than a list of values in one dimension.
    lats=coords_cube[3].data
    lons=coords_cube[4].data

    # If flip is true, then flip them to match the later flipping of the precipitation data    
    if flip == True:
            lats=np.flipud(lats)
            lons=np.flipud(lons)
        
    # Find the dimensions of the coordinates
    dims=shape(lats)
      
    # Initialise the variable which holds the distance to the nearest grid point
    min_dist=1e10 # big number 
    
    # Define an ellipsoid on which to solve Geodesic (e.g. on a sphere) problems
    # e.g. the shape of the Earth
    myGeod = geodesic.Geodesic(6378137.0,1 / 298.257223563)
        
    # Find the lat and long associated with each array position 
    # (defined by col, row indices)
    # Test the distance between our location of interest, and this location.
    # If it is the shortest yet, then save the index values, and reset the 
    # minimum distance to this distance value.
    for i in range(dims[0]):
        for j in range(dims[1]):
            # Create array containing the location of interest and a lat, long
            # pair from the cube.
            this_lat=lats[i,j]
            this_lon=lons[i,j]
            latlon = array([[this_lat, this_lon], [target_lat, target_lon]])
            # Find distance betwen two pairs of points?
            this_dist= myGeod.geometry_length(latlon)
            if(this_dist<min_dist):
                i_min_dist=i
                j_min_dist=j
                min_dist=this_dist
            
    print ("The closest location to the location of interest was", min_dist, "metres away")
    return (i_min_dist, j_min_dist)

# Define a sample point at which we are interested in extracting the precipitation timeseries.
# Define latitude and longitude of interest
rv_lat= 53.802070
rv_lon= -1.588941

# Read in the list of cubes, containing the lat and long cubes
cube_list = iris.load(filenames[0])

# Find the index of the point in the grid which is closest to the point of interest
# Considering the grid both flipped and not flipped
# For just creating a time series and not plotting, flipping is not really necesary
start = timer()
rv_closest_idx_fl = find_idx_closestpoint(cube_list, rv_lat, rv_lon, flip = True)
print('Method 2 completed in ' , round(timer() - start, 3), 'seconds')  

start = timer()
rv_closest_idx = find_idx_closestpoint(cube_list, rv_lat, rv_lon, flip = False)
print('Method 2 completed in ' , round(timer() - start, 3), 'seconds')  

##############################################################################
# Create timeseries
##############################################################################
# Keep all of the first dimension (time), and trim to just the location of interest
obs_pr_cubes_rv = obs_pr_cubes[:,rv_closest_idx[0], rv_closest_idx[1]]

# Plot the timeseries
qplt.plot(obs_pr_cubes_rv)
plt.xticks(rotation=45)

iplt.plot(obs_pr_cubes_rv)
plt.xticks(rotation=45)

###########################################################
# Save cube 
###########################################################
iris.save(concat_cube, 
          f'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries_cubes/Obs_{start_year}-{end_year}.nc')



##############################################################################
# Save dataframe
##############################################################################
# Create a dataframe containing the date and the precipitation data
df = pd.DataFrame({'Date': np.array(obs_pr_cubes_rv.coord('time').points),
                  'Precipitation (mm/hr)': np.array(obs_pr_cubes_rv.data)})

# Format the date column
df['Date_Formatted'] =  obs_pr_cubes_rv.coord('time').units.num2date(obs_pr_cubes_rv.coord('time').points)

# Write to a csv
df.to_csv(f"C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/Obs_{start_year}-{end_year}.csv", index = False)



