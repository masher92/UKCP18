'''
Finds...
which is within the bounding box of the North of England.
'''

import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import xarray as xr
import os
import geopandas as gpd
import time 
import sys


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

# Define ensemble members to use and percentiles to find
ems = ['01', '04','05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
percentiles = [95, 97] 

############################################
# Create a GDF for Northern England
#############################################
# Create geodataframe of Northrn England
northern_gdf = create_northern_outline({'init' :'epsg:3857'})

############################################
# For each ensemble member:
# Create a cube containing 20 years of data, trimmed to the North of England, with just JJA values
# 
#############################################
for em in ems:
    print(em)

    #############################################
    ## Load in the data
    #############################################
    filenames=glob.glob('datadir/UKCP18/2.2km/'+em+'/1980_2001/pr_rcp85_land-cpm_uk_2.2km_*.nc')
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
    regional_cube = trim_to_bbox_of_region(concat_cube, regional_gdf)
    print("Trimmed to extent of bbox in: ", time.time() - seconds)

    #############################################
    # Add season coordinates and trim to JJA
    #############################################              
    iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
    jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))
    #iris.coord_categorisation.add_season_year(jja,'time', name = "season") 
               
    #############################################
    # Find the lats and lons
    ############################################# 
    # Get the lats and lons in 1D
    lats= jja.coord('latitude').points.reshape(-1)
    lons =  jja.coord('longitude').points.reshape(-1) 
      
    # Find percentiles  
    jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, percent=percentiles)
    
    # For each of the percentiles calculated:
    for percentile_no in range(jja_percentiles.shape[0]):
      print(percentile_no)
      print(percentiles[percentile_no])
      
      # Extract just the data for the percentile we are focussing on 
      percentile = jja_percentiles[percentile_no,:,:,:] 
        
      ### Set percentile cutoff values
      percentile_cutoff_data=percentile.data
      
      # Perform the main algorithm.
      n_highest_array=values_above_percentile(jja.data, percentile_cutoff_data)
       
      ######## Store in format for R
      # Remove Ensemble member dimension 
      data = n_highest_array [0,:,:,:]           
      
      values_over_percentile_dict ={}
      # Loops through each of the top ten values and store in a dictionary
      # with the year name
      for i in range(0, data.shape[0]):
          #print(i)
          # Get data from one of the values
          one_ts = data[i,:,:]
          one_ts = one_ts.reshape(-1)
          # Store as dictionary 
          values_over_percentile_dict[str(i)] = one_ts
          
      # Convert to dataframe
      values_over_percentile_df= pd.DataFrame(values_over_percentile_dict)      
    
      # Add lats and lons
      values_over_percentile_df['lat'], values_over_percentile_df['lon'] = lats, lons
      
      # Save to file
      ddir = "Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOverPercentile/{}/".format(str(percentiles[percentile_no]))
      if not os.path.isdir(ddir):
          os.makedirs(ddir)
      values_over_percentile_df.to_csv(ddir +"em_{}.csv".format(em), index = False, float_format = '%.20f')



