'''
For each ensemble member:
    Calculates the value of certain statistics, (max, mean and various percentiles), in each 
    year of data for just the wet hours. The results are saved to a dataframe in which the rows
    are locations within the bounding box of the northern region, and the columns contain the value
    of the statistic in each year
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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

ems = ['01', '04', '05', '06', '07', '08', '10', '11','12','13','15']
stats = ['wet_prop']
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
# It calculates the value of that statistic in each year of the data at each cell for just the wet hours
# To do this it must load the data into an array and process outside Iris functions
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
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 

    ############################################
    # Find wet hour stats
    #############################################
    # Loop through stats
    for stat in stats:
      print(stat)
    
      # Create dataframe with lat and long values
      df = pd.DataFrame({'lats': jja.coord('latitude').points.reshape(-1),
                       'lons': jja.coord('longitude').points.reshape(-1)})
    
      # For each year find the value at each location for the defined statistic
      # and save these to a dataframe
      # Extract data
      rain_data = one_year_jja.data
      # Find value corresponding to name stat
      stats_array = wet_hour_stats(rain_data, stat)
      # Convert to 1D
      stats_array_1d = stats_array.reshape(-1)
      # Append to dataframe
      df = df.join(pd.DataFrame({stat : stats_array_1d}))

      # Save to file
      ddir = "Outputs/HiClimR_inputdata/NorthernSquareRegion/Wethours/AllYears/{}/".format(stat)
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
        
    




# stat = 'Wethours/wet_prop'
# region = 'leeds-at-centre'
# em = '01'
# wet_prop = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/wet_prop/em_01.csv")
# p95 = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/jja_p95_wh/em_01.csv")
# wet_prop = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/wet_prop/em_01.csv")
# p99 = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/jja_p99_wh/em_01.csv")


# plt.scatter(p95['1981'], wet_prop['1981'], s=1.5)
# plt.xlabel('Cell wet day proportion')
# plt.ylabel('Cell P95')

# for year in range(1981,2001):
#     print(year)
#     plt.scatter(p99[str(year)], wet_prop[str(year)], s=1.5)
#     plt.xlabel('Cell wet day proportion')
#     plt.ylabel('Cell P95')
#     plt.show()
    
# x = p95['1981']
# y = wet_prop['1981']
# z = np.polyfit(x, y, 1)
# p = np.poly1d(z)
# pylab.plot(x,p(x),"r--")
# # the line equation:
# print "y=%.6fx+(%.6f)"%(z[0],z[1])    