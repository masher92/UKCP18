'''
For each ensemble member:
    Calculates the value of certain statistics, (max, mean and various percentiles), in each 
    year of data. The results are saved to a dataframe in which the rows are locations
    within the bounding box of the northern region, and the columns contain the value
    of the statistic in each year
    
NB: this script previously contained functionality to find te greatest 10 and 20
values in each year.
This did not produce good results with HiClimR.
Script has been updated. Code is included at the bottom but no longer works with
the structure of this script
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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11','12','13','15']
stats = ['Max', 'Mean', '95th Percentile', '97th Percentile', '99th Percentile', '99.5th Percentile', '99.75th Percentile', '99.9th Percentile']
yrs_range = "1980_2001" 

##################################################################
# Load necessary spatial data
##################################################################
northern_gdf = create_northern_outline({'init' :'epsg:3857'})

##################################################################
# Function which for each ensemble member:
# Loads in all of the files for 1980-2001 period and joins them.
# Cuts to JJA
# And then for each of the defined statistics:
# It calculates the value of that statistic in each year of the data at each cell for all of the hours
# For each statistic, a dataframe is creation, where the rows are locations
# within the bounding box of the northern region, and the columns contain the value
# of the statistic in each year

# This function can then be parallelised
##################################################################
def create_stats_df(em):
#for em in ems:
    print(em)
    #############################################
    ## Load in the data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/1980_2001/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em,  em)
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
    # Trim the cube to the BBOX of the North of England 
    #############################################
    seconds = time.time()
    concat_cube = trim_to_bbox_of_region(concat_cube, northern_gdf)
    print("Trimmed to extent of bbox in: ", time.time() - seconds)
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season year
    iris.coord_categorisation.add_season_year(jja,'time', name = "season") 

    ############################################
    # Create dictionary containing the cube for each statistic
    #############################################
    stats_dict  ={}
    stats_dict['Max'] = jja.aggregated_by(['season'], iris.analysis.MAX)
    stats_dict['Mean'] = jja.aggregated_by(['season'], iris.analysis.MEAN)
    # Add the percentiles
    jja_percentiles = jja.aggregated_by(['season'], iris.analysis.PERCENTILE, percent=[95,97,99,99.5, 99.75, 99.9])
    Percentiles = ['95th Percentile', '97th Percentile', '99th Percentile', '99.5th Percentile', '99.75th Percentile', '99.9th Percentile']
    i = 0
    for Percentile in Percentiles:
        stats_dict[Percentile] = jja_percentiles[i,:,:,:]
        i = i+1
     
    ############################################
    # Create a dataframe where each row is a lat/lons position within the bounding
    # box of the northern region, and each column contains the value for that year 
    # for the specified stat
    #############################################     
    # Loop through stats
    for stat, stat_cube in stats_dict.items():
      print(stat)
      print(stat_cube)
      
      # Create dataframe with lat and long values (this can be used for all years)
      df = pd.DataFrame({'lats': jja.coord('latitude').points.reshape(-1),
                       'lons': jja.coord('longitude').points.reshape(-1)})
      
      # For each year find the value at each location for the defined statistic
      # and save these to a dataframe
      years = range(1981,2001)
      for year in years:
        print(year)
        # Cut cube to just that year
        one_year_stat_cube = stat_cube.extract(iris.Constraint(year = year))
        # Extract data
        stats_array = one_year_stat_cube.data
        # Convert to 1D
        stats_array_1d = stats_array.reshape(-1)
        # Append to dataframe
        df = df.join(pd.DataFrame({str(year) : stats_array_1d}))

      # Save to file
      ddir = "Outputs/RainfallRegionalisation/HiClimR_inputdata/NorthernSquareRegion/Allhours/{}/".format(stat)
      if not os.path.isdir(ddir):
           os.makedirs(ddir)
      df.to_csv(ddir + "em_{}.csv".format(em), index = False, float_format = '%.20f')
      print("Saved to Dataframe")

# Send each ensemble member to the function
# making use of parallelisation            
pool = mp.Pool(mp.cpu_count())
results = [pool.apply_async(create_stats_df, args=(x,)) for x in ems]
output = [p.get() for p in results]
print(output)              
        
    
#############################################
# See: UKCP18/RainfallRegionalisation/FindStats.py ~ 9th September
# Find greatest N values
#############################################   
# rain_data=jja.data

# # Make a conservative estimate (it is a bit annoying to deal with the rounding issues)
# cutoff_percentile=100.*(1.0-(n_highest+1.0)/(np.shape(rain_data)[0]-1.0))
# yearly_stats_percentile = jja.aggregated_by(['season'], iris.analysis.PERCENTILE, percent=cutoff_percentile)

# ### Find top ten values
# percentile_data=yearly_stats_percentile.data
# # Perform the main algorithm.
# n_highest_array,exception=values_above_percentile(rain_data,percentile_data,n_highest)
# if(exception==1):
#     raise Exception('The percent_data array has unexpected dimensions')
# if(exception==2):
#     raise Exception('Cutoff percentile generates too few data points')
 
# ######## Store in format for R, and add to dictionary
# # Remove Ensemble member dimension 
# data = n_highest_array [0,:,:,:]           

# # Loops through each of the top ten values and store in a dictionary
# # with the year name
# for i in range(0, data.shape[0]):
#     #print(i)
#     # Get data from one timeslice
#     one_ts = data[i,:,:]
#     # Extract data from one year 
#     one_ts = one_ts.reshape(-1)
#     # Store as dictionary with the year name
#     name = year + '_' + str(i)
#     top_ten_dict[name] = one_ts

