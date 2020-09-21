'''
Finds max, mean, percentiles and greatest ten values for every cell in the cube
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

"""Using numba to extract values above a percentile.
Numba executes loops efficiently (just in time compiling)
Somehow, the exceptions do not work well within numba, so they are passed out as integers"""
@jit
def values_above_percentile(rain_data,percentile_cutoff_data):
    exception=0
    imax=np.shape(rain_data)[1] 
    jmax=np.shape(rain_data)[2]
    if(np.shape(percentile_cutoff_data)[0]>1):
        exception=1
    
    # Define how many numbers over percentile there are for one dimensions
    # This should be the value throughout - which is checked later
    local_raindata=rain_data[:,0,0]
    local_percentile=percentile_cutoff_data[0,0,0]
    data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])#[::-1]
    n_over_percentile = len(data_over_percentile)   
    print(n_over_percentile)
    
    # first dimension is for time
    n_highest_array=np.zeros((1,n_over_percentile,imax,jmax))
    for i in range(imax):
        for j in range(jmax):
            #print(i,j)
            # Find the rainfall values at this location
            local_raindata=rain_data[:,i,j]
            # Find the value of the percentile at this location
            local_percentile=percentile_cutoff_data[0,i,j]
            # Extract values above cutoff percentile, sort these data over percentile 
            # in descending order
            data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])#[::-1]
            local_n_over_percentile=len(data_over_percentile)
            print(local_n_over_percentile)
            # ensure we have extracted enough values
            if not local_n_over_percentile == n_over_percentile:
                print("Error: incorrect number of values over percentile")
                # Sort in descening order, and remove the smallest value
                data_over_percentile = data_over_percentile[::-1][:n_over_percentile]
                print(len(data_over_percentile))
            # only use the n highest values
            n_highest_array[0,:,i,j]=data_over_percentile
            #print("g")
    return n_highest_array


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

ems = ['04','05']
years = range(1981,2000)  

############################################
# Create a GDF for Northern England
#############################################
# Create geodataframe of Northrn England
uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
regional_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
# Merge the three regions into one
regional_gdf['merging_col'] = 0
regional_gdf = regional_gdf.dissolve(by='merging_col')

############################################
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
    #
    #############################################  
    lats= jja.coord('latitude').points.reshape(-1)
    lons =  jja.coord('longitude').points.reshape(-1) 
      
    percentiles = [99] 
    jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, 
                                        percent=percentiles)

    for percentile_no in range(jja_percentiles.shape[0]):
      print(percentile_no)
      print(percentiles[percentile_no])
      percentile = jja_percentiles[percentile_no,:,:,:] 
        
      ### Set percentile cutoff values
      percentile_cutoff_data=percentile.data
      
      # Perform the main algorithm.
      n_highest_array=values_above_percentile(jja.data,percentile_cutoff_data)
       
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



