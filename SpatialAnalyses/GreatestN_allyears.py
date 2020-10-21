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
def values_above_percentile(rain_data,percentile_data,n_highest):
    exception=0
    # length of lons
    imax=np.shape(rain_data)[1] 
    # length of lats
    jmax=np.shape(rain_data)[2]
    if(np.shape(percentile_data)[0]>1):
        exception=1
    # first dimension is for time
    n_highest_array=np.zeros((1,n_highest,imax,jmax))
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            # Find the percentile cutoff value for that cell
            local_percentile=percentile_data[0,i,j]
            # extract values above cutoff percentile, sort these data over percentile in descending order
            # this is the most important line in this piece of code
            data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])[::-1]
            local_n_over_percentile=len(data_over_percentile)
            # ensure we have extracted enough values
            if(local_n_over_percentile>=n_highest):
                # only use the n highest values
                n_highest_array[0,:,i,j]=data_over_percentile[:n_highest]
            else:
                exception=2
    return n_highest_array,exception


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

ems = ['01']
years = range(1981,2000)  
n_highest=20
yrs_range = "1980_2001" 
#temp_perc_file='/nfs/a319/gy17m2a/Outputs/temp_stats_percentile.nc'

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
    # Create dictionaries to store results
    top_ten_dict = {}

    #############################################
    ## Load in the data
    #############################################
    filenames=glob.glob('datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em))
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
    iris.coord_categorisation.add_season_year(jja,'time', name = "season") 
                     
    #############################################
    # Find greatest N values
    #############################################   
    rain_data=jja.data
    # Make a conservative estimate (it is a bit annoying to deal with the rounding issues)
    cutoff_percentile=100.*(1.0-(n_highest+1.0)/(np.shape(rain_data)[0]-1.0))
    print(cutoff_percentile)
    yearly_stats_percentile = jja.aggregated_by(['season'], iris.analysis.PERCENTILE, percent=cutoff_percentile)
    
    ### Find top ten values
    percentile_data=yearly_stats_percentile.data
    # Perform the main algorithm.
    n_highest_array,exception=values_above_percentile(rain_data,percentile_data,n_highest)
    if(exception==1):
        raise Exception('The percent_data array has unexpected dimensions')
    if(exception==2):
        raise Exception('Cutoff percentile generates too few data points')
     
    ######## Store in format for R, and add to dictionary
    # Remove Ensemble member dimension 
    data = n_highest_array [0,:,:,:]           
    # Loops through each of the top ten values and store in a dictionary
    # with the year name
    for i in range(0, data.shape[0]):
        #print(i)
        # Get data from one timeslice
        one_ts = data[i,:,:]
        # Extract data from one year 
        one_ts = one_ts.reshape(-1)
        # Store as dictionary with the year name
        name = year + '_' + str(i)
        top_ten_dict[name] = one_ts
            
    # Convert to dataframe
    top_ten_df= pd.DataFrame(top_ten_dict)      
    
    # Add lats and lons
    lats= jja.coord('latitude').points.reshape(-1)
    lons =  jja.coord('longitude').points.reshape(-1)   
    top_ten_df['lat'], top_ten_df['lon'] = lats, lons
    
    # Save to file
    top_ten_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/Greatest_twenty/OverAllYears/em_{}.csv".format(em), index = False, float_format = '%.20f')
   
    


