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
from Spatial_geometry_functions import *

ems = ['01', '04', '05', '06', '07', '08', '10', '11','12','13','15']
stats = ['Max', 'Mean', '95th Percentile', '97th Percentile', '99th Percentile', '99.5th Percentile', '99.75th Percentile', '99.9th Percentile']
yrs_range = "1980_2001" 

##################################################################
# Load necessary spatial data
##################################################################
northern_gdf = create_northern_outline({'init' :'epsg:3857'})

##################################################################
# 
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
      
      # Create dataframe with lat and long values (this can be used for all stats)
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
      ddir = "Outputs/HiClimR_inputdata/NorthernSquareRegion/Allhours/{}/".format(stat)
      if not os.path.isdir(ddir):
           os.makedirs(ddir)
      df.to_csv(ddir + "em_{}.csv".format(em), index = False, float_format = '%.20f')
      print("Saved to Dataframe")

        
pool = mp.Pool(mp.cpu_count())
results = [pool.apply_async(create_stats_df, args=(x,)) for x in ems]
output = [p.get() for p in results]
print(output)              
        
    


