import sys
import iris
import os
import glob
import numpy as np
import pandas as pd
import geopandas as gpd
import time 
from statsmodels.tsa.stattools import adfuller

# Provide root_fp as argument
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

# Create geodataframe of West Yorks
uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
northern_gdf = northern_gdf.to_crs({'init' :'epsg:3785'}) 
# Merge the three regions into one
northern_gdf['merging_col'] = 0
northern_gdf = northern_gdf.dissolve(by='merging_col')

#############################################
# Read in files
#############################################
adf_stats = []

for em in ems:
    start_time = time.time()
    print ("Ensemble member {}".format(em))
    
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
    regional_cube = trim_to_bbox_of_region(concat_cube, northern_gdf)
    print("Trimmed to extent of bbox in: ", time.time() - seconds)

    #############################################
    # Add season coordinates and trim to JJA
    #############################################              
    iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
    jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))
    
    
    #############################################
    # Plot
    ############################################# 
    df = pd.DataFrame(regional_mean_data)
    df['year'] = jja.coord('year').points
    
    fig=plt.figure() 
    plt.style.use('ggplot')
    ax = df[0].plot()
    #ax.set_xlabel("Areas",fontsize=12)
    ax.set_xticklabels(df['year'], rotation=45)
    fig.savefig("Outputs/Stationarity/em{}.png".format(em),bbox_inches='tight')
    
    #############################################
    # Check stationarity
    ############################################# 
    jja.remove_coord('longitude')
    jja.remove_coord('latitude')
    new_cube = jja.collapsed(['grid_longitude', 'grid_latitude'], iris.analysis.MEAN)
    regional_mean_data = new_cube.data

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
test.to_csv("Outputs/Stationarity/ADF_stats.csv", index=False)
