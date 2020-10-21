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
ems = ['15']
percentiles = [95, 97, 99, 99.5, 99.75, 99.9]

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
    iris.coord_categorisation.add_season_year(jja,'time', name = "season")

    #############################################
    # Find statistics - one value across all JJA
    #############################################
    jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, percent=percentiles)
    print("Converted Percentiles")
    jja_mean = jja.aggregated_by(['clim_season'], iris.analysis.MEAN)
    jja_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)
    print("Converted max and min")
    
    # Split off all percentiles
    percentile_1 = jja_percentiles[0,:,:,:]
    percentile_2 = jja_percentiles[1,:,:,:]
    percentile_3 = jja_percentiles[2,:,:,:]
    percentile_4 = jja_percentiles[3,:,:,:]
    percentile_5 = jja_percentiles[4,:,:,:]
    percentile_6 = jja_percentiles[5,:,:,:]
    
    #############################################
    # Convert to dataframes
    #############################################
    percentile1_df = pd.DataFrame({"Nth Percentile Rainfall" :percentile_1.data.reshape(-1)})
    percentile2_df = pd.DataFrame({"Nth Percentile Rainfall" :percentile_2.data.reshape(-1)})
    percentile3_df = pd.DataFrame({"Nth Percentile Rainfall" :percentile_3.data.reshape(-1)})
    percentile4_df = pd.DataFrame({"Nth Percentile Rainfall" :percentile_4.data.reshape(-1)})
    percentile5_df = pd.DataFrame({"Nth Percentile Rainfall" :percentile_5.data.reshape(-1)})
    percentile6_df = pd.DataFrame({"Nth Percentile Rainfall" :percentile_6.data.reshape(-1)})
    mean_df = pd.DataFrame({"Mean Rainfall" :jja_mean.data.reshape(-1)})
    max_df = pd.DataFrame({"Max Rainfall" :jja_max.data.reshape(-1)})
    print("Converted to dataframe")

    # Create lat and lon columns
    lats= jja.coord('latitude').points.reshape(-1)
    lons =  jja.coord('longitude').points.reshape(-1)
    
    # Add lats and lons
    mean_df['lat'], mean_df['lon'] = lats, lons
    max_df['lat'], max_df['lon'] = lats, lons
    percentile1_df['lat'], percentile1_df['lon'] = lats, lons
    percentile2_df['lat'], percentile2_df['lon'] = lats, lons
    percentile3_df['lat'], percentile3_df['lon'] = lats, lons
    percentile4_df['lat'], percentile4_df['lon'] = lats, lons
    percentile5_df['lat'], percentile5_df['lon'] = lats, lons
    percentile6_df['lat'], percentile6_df['lon'] = lats, lons

    #############################################
    # Save to file
    #############################################
    mean_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/Mean/em_{}.csv".format(em), index = False, float_format = '%.20f')
    max_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/Max/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile1_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/95th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile2_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/97th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile3_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/99th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile4_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/99.5th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile5_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/99.75th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile6_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/99.9th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    print("Saved to file")
     
    # Create ddirs
    # for percentile in percentiles:
    #   percentile_name = str(percentile) + "th Percentile"
    #   ddir = "Outputs/HiClimR_inputdata/NorthernSquareRegion/ValuesOver20Years/{}/".format(percentile_name)
    #   if not os.path.isdir(ddir):
    #     os.makedirs(ddir)


