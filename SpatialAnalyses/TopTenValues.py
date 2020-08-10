import sys
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
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
import numpy as np
from shapely.geometry import Polygon
import iris.coord_categorisation
import time 
import bottleneck

warnings.filterwarnings("ignore")

# Provide root_fp as argument
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
ems = ['08']
region = 'WY'
mask_to_region = True
greatest_ten = True

############################################
# Create regions
#############################################
wy_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
wy_gdf = wy_gdf.to_crs({'init' :'epsg:3785'}) 
 
# Create geodataframe of West Yorks
uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
northern_gdf = northern_gdf.to_crs({'init' :'epsg:3785'}) 
# Merge the three regions into one
northern_gdf['merging_col'] = 0
northern_gdf = northern_gdf.dissolve(by='merging_col')

if region == 'Northern':
    regional_gdf = northern_gdf
else:
    regional_gdf = wy_gdf

#############################################
# Read in files
#############################################
for em in ems:
    start_time = time.time()
    print ("Ensemble member {}".format(em))
    
    # Check if the last stat exists already, if it does then don't continue with the
    # code
    # filepath = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, stats[-1], em)
    # if os.path.isfile(filepath)  :
    #     filepath = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, stats[-1], em)
    #     print("Already complete, moving to next ensemble member")
    #     continue
    
    # Create list of names of cubes for between the years specified
    filenames =[]
    for year in range(start_year,end_year+1):
        # Create filepath to correct folder using ensemble member and year
        general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
        #print(general_filename)
        # Find all files in directory which start with this string
        for filename in glob.glob(general_filename):
            #print(filename)
            filenames.append(filename)
    
    # filenames =[]
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 
    
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    print(str(len(monthly_cubes_list)) + " cubes found for this time period.")
    
    #############################################
    # Concat the cubes into one
    #############################################
    # Remove attributes which aren't the same across all the cubes.
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
     
     # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    #
    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    print ("Joined cubes into one")
    
    #############################################
    # Trim the cube to the BBOX of the region of interest
    #############################################
    seconds = time.time()
    regional_cube = trim_to_bbox_of_region(concat_cube, regional_gdf)
    print("Trimmed to extent of bbox in: ", time.time() - seconds)
    
    #seconds = time.time()
    #regional_cube = mask_by_region(regional_cube, regional_gdf)
    #print('Created regional_mask in: ', time.time() - seconds)
    #mask_3d = np.repeat(regional_mask[np.newaxis,:, :], regional_cube.shape[0], axis=0)
    #print("Seconds to run =", time.time() - seconds)	
    #regional_cube.data =  np.ma.masked_array(regional_cube.data, np.logical_not(mask_3d))
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))
    
    ###########################################
    # Find statistic being used to regionalise rainfall
    #############################################
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 
    print('Cut to June-July-August period')

################# Finding biggest ten for each year
    ddir = "Outputs/HiClimR_inputdata/{}/{}/".format(region, 'Greatest_ten')
    if not os.path.isfile(ddir + "em{}.csv".format(em)):
        print("Greatest ten doesn't already exist, creating...")
    
    if 'test' in globals():
        print ("Using mask from stats processing")
        mask = test
    else:
       print ('No mask, reading from file')
       # Read from file, delete NAs
       mask = pd.read_csv("Outputs/HiClimR_inputdata/WY/mask.csv")
       mask = mask.dropna()
       
    # seconds = time.time()
    # df = n_largest_yearly_values(jja, mask, 10)
    # print("Found N largest values in: ", time.time() - seconds)
           
    seconds = time.time()
    df_newmethod = n_largest_yearly_values_method2(jja, mask, False)
    print("Found N largest values in: ", time.time() - seconds)
    
ddir = "Outputs/HiClimR_inputdata/{}/Greatest_ten/".format(region)
if not os.path.isdir(ddir):
    os.makedirs(ddir)
df_newmethod.to_csv(ddir + "em{}.csv".format(em), index = False)


### Testing if both methods produce same result
# Old method - cell by cell
# np.sort(df.iloc[0][0:10])
# # New method - Iris percentiles
# np.sort(df_newmethod.iloc[0][0:10])



# #######################################  
# # New method - my percentile method
# ####################################### 
# # Create a cube with a percentile dimension, where each dimension contains values corresponding to the given percentiles
# # For a cube of this size have calculated that these correspond to the top 10 highest values
#   yearly_stats_percentiles = jja.aggregated_by(['season_year'], iris.analysis.PERCENTILE, alphap = 0.5, betap = 0.5, percent=[98.6, 98.7, 98.9, 99, 99.2, 99.3, 99.5, 99.7, 99.9, 100])
# # Create a list to store the results in  
#   dfs_list = []
#   for year_n in range(0, yearly_stats_percentiles.shape[1]):
#       year  = one_year.coord('season_year').points[0]
#       # Get data from one timeslice
#       one_year = yearly_stats_percentiles[:,year_n,:,:]
#       one_year_dict = {}
#       for n_largest_value in range(0, yearly_stats_percentiles.shape[0]):
#           print(n_largest_value)
#           one_percentile = one_year[n_largest_value,:,:]
          
#           # if not 'regional_mask' in globals():
#           #     seconds = time.time()
#           #     regional_mask = mask_by_region(one_percentile, regional_gdf)
#           #     print('Created regional_mask in: ', time.time() - seconds)
#           # else: 
#           #     print('Regional mask already exists')
#           # #print("Seconds to run =", time.time() - seconds)	
#           # one_percentile.data =  np.ma.masked_array(one_percentile.data, np.logical_not(regional_mask))
          
#           data = one_percentile.data.reshape(-1)
#           one_year_dict[str(year) + '_' + str(n_largest_value)] =  data
#       # Convert the dictionary of N_largest values into a dataframe
#       n_largest_values_df = pd.DataFrame(one_year_dict)
#       n_largest_values_df.reset_index(drop=True, inplace=True)
#       dfs_list.append(n_largest_values_df)    
      
#   result = pd.concat(dfs_list, ignore_index = False, axis = 1)
      
#   # Join with lats and lons
#   result['lat'], result['lon'] = [lats_1d, lons_1d]

# # Remove NA rows
#   result = result.dropna()    
                
#######################################  
# Testing - to show that the percentile method does not give them same results 
# as the old method which I have tested is correct
# (altho maybe I have only tested it is correct for the first cell - check more? )
# #######################################                   
# yearly_stats_percentiles = jja.aggregated_by(['season_year'], iris.analysis.PERCENTILE, percent=[98.6, 98.7, 98.9, 99, 99.2, 99.3, 99.5, 99.7, 99.9, 100])


# one_cell = jja[:,0,0]
# one_cell_one_year = one_cell.extract(iris.Constraint(season_year = 1982))
# print(one_cell_one_year)
# data= one_cell_one_year.data
# np.sort(data)


# values = -bottleneck.partition(-one_cell_one_year.data, 10)[:10]
# np.sort(values)


# ########## Testing
# first_cell_1982 = yearly_stats_percentiles[:,0,0,0]
# data_test = first_cell_1982.data
# print(data_test)


# #######################################  
# # Steef method
# #######################################                   
# yearly_stats_percentiles = jja.aggregated_by(['season_year'], iris.analysis.PERCENTILE, percent=[98.6, 98.7, 98.9, 99, 99.2, 99.3, 99.5, 99.7, 99.9, 100])










# for n_largest_value in range(0, yearly_stats_percentiles.shape[0]):
#     print(n_largest_value)
#     one_percentile = yearly_stats_percentiles[n_largest_value,:,:,:]
#     if not 'regional_mask' in globals():
#         seconds = time.time()
#         regional_mask = mask_by_region(one_percentile, regional_gdf)
#         print('Created regional_mask in: ', time.time() - seconds)
#     else: 
#         print('Regional mask already exists')
#     #mask_3d = np.repeat(regional_mask[np.newaxis,:, :], one_percentile.shape[0], axis=0)
#     #print("Seconds to run =", time.time() - seconds)	
#     #one_percentile.data =  np.ma.masked_array(one_percentile.data, np.logical_not(mask_3d))
#     dfs_list = []
#     for year_n in range(0, one_percentile.shape[0]):
#         print(year)
#         year  = one_percentile.coord('season_year').points[0]
#         # Get data from one timeslice
#         one_year = one_percentile[year_n,:,:]
#         one_year_dict = {}
#         for n_largest_value in range(0, yearly_stats_percentiles.shape[0]):
#             print(n_largest_value)
#             one_percentile = one_year[n_largest_value,:,:]
#             data = one_percentile.data.reshape(-1)
#             one_year_dict[str(year) + '_' + str(n_largest_value)] =  data
#         # Convert the dictionary of N_largest values into a dataframe
#         n_largest_values_df = pd.DataFrame(one_year_dict)
#         n_largest_values_df.reset_index(drop=True, inplace=True)
#         dfs_list.append(n_largest_values_df)    
    
    
#     result = pd.concat(dfs_list, ignore_index = False, axis = 1)
                    
#     # Join with lats and lons
#     result['lat'], result['lon'] = [lats_1d, lons_1d]
    
