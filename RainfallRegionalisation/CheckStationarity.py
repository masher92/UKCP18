import sys
import iris
import os
import glob
import numpy as np
import pandas as pd
import geopandas as gpd
import time 
from statsmodels.tsa.stattools import adfuller
import iris.coord_categorisation

root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_geometry_functions import *
from Spatial_plotting_functions import *
start_year, end_year, yrs_range = 1980, 2001, "1980_2001"
ems = ['01','04', '05', '06', '07', '08', '09','10','11','12', '13','15']

##############################################################################
# Create necessary spatial geodataframes
##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})
northern_gdf = create_northern_outline({'init' :'epsg:27700'})

##############################################################################
# Check stationarity
##############################################################################
adf_stats = []
for region in ['Northern', 'Leeds']:
  for em in ems:
      start_time = time.time()
      print ("Ensemble member {}".format(em))
      
      #############################################
      # Read in files
      #############################################
      # Create list of names of cubes for between the years specified
      filenames =[]
      for year in range(start_year,end_year+1):
          # Create filepath to correct folder using ensemble member and year
          general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
          print(general_filename)
          # Find all files in directory which start with this string
          for filename in glob.glob(general_filename):
              filenames.append(filename)
  
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
      # Remove ensemble member dimension
      concat_cube = concat_cube[0,:,:,:]
      print ("Joined cubes into one")
      
      #############################################
      # Trim the cube to the BBOX of the region of interest
      #############################################
      seconds = time.time()
      if region == 'Northern':
        regional_cube = trim_to_bbox_of_region(concat_cube, northern_gdf)
      else:
         regional_cube = trim_to_bbox_of_region(concat_cube, leeds_gdf)   
      print("Trimmed to extent of bbox in: ", time.time() - seconds)
  
      #############################################
      # Add season coordinates and trim to JJA
      #############################################              
      iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
      jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))  
     
      #############################################
      # Check stationarity
      ############################################# 
      jja.remove_coord('longitude')
      jja.remove_coord('latitude')
      new_cube = jja.collapsed(['grid_longitude', 'grid_latitude'], iris.analysis.MEAN)
      regional_mean_data = new_cube.data
  
      #############################################
      # Plot
      ############################################# 
      df = pd.DataFrame({'values' :regional_mean_data})
      df['year'] = jja.coord('year').points
      df['date'] = jja.coord('yyyymmddhh').points
      df['date_formatted']= pd.to_datetime(df['date'], format='%Y%m%d%H')
      
      # fig=plt.figure() 
      # plt.style.use('ggplot')
      # ax = df['values'].plot()
      # ax.set_xticklabels(df['date_formatted'], rotation=45)
      # ax.xaxis.set_major_formatter(DateFormatter('%Y'))
      # #ax.set_xlabel("Areas",fontsize=12)
      
      df = df.set_index('date_formatted')
      
      fig=plt.figure() 
      plt.style.use('ggplot')
      ax = df['values'].plot()
      fig.savefig("Outputs/StationarityTesting/{}/em{}.png".format(region,em),bbox_inches='tight')
  
      # ADF test
      result = adfuller(regional_mean_data)    
      print('ADF Statistic: %f' % result[0])
      print('p-value: %f' % result[1])
      print('Critical Values:')
      for key, value in result[4].items():
      	print('\t%s: %.3f' % (key, value))    
          
      # Check meaning of results
      if result[1] > .05 and result[0] > list(result[4].items())[0][1]:
          #stationary_ts = stationary_ts +1
          print ("Time series not stationary")
      else:
          print("Time series is stationary")
      
      
      # Add stats to a list of dataframes
      df = pd.DataFrame([{'EM': em,'ADF Statistic': result[0],'PValue' : result[1]}])
      adf_stats.append(df)
      
  # Join list of dataframes 
  test = pd.concat(adf_stats, axis=0)
  test.to_csv("Outputs/StationarityTesting/{}/ADF_stats.csv".format(region), index=False)
