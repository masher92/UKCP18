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
#ems = ['01']
region = 'WY'
mask_to_region = True
stats = ['99th Percentile', '97th Percentile', '95th Percentile', 'Mean', 'Max']
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
    
    filenames =[]
    filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
    filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
    filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
    filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 
    
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
    
    ###########################################
    # Find statistic being used to regionalise rainfall
    #############################################    
    for stat in stats:
        print('Processing ' , stat)
        seconds = time.time()
        if stat == 'Mean':
            filepath = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, 'Mean', em)
            if not os.path.isfile(filepath):
                print("Mean doesn't already exist, creating...")
                yearly_stats = jja.aggregated_by(['season_year'], iris.analysis.MEAN)
        elif stat == 'Max': 
            filepath = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, 'Max', em)
            if not os.path.isfile(filepath):
                print("Max doesn't already exist, creating...")
                yearly_stats = jja.aggregated_by(['season_year'], iris.analysis.MAX)
        elif stat =='99th Percentile' or stat == '97th percentile' or stat == '95th percentile':
            filepath1 = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, '95th Percentile', em)
            filepath2 = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, '97th Percentile', em)
            filepath3 = "Outputs/HiClimR_inputdata/{}/{}/em{}.csv".format(region, '99th Percentile', em)
            if not all([os.path.isfile(filepath1) and os.path.isfile(filepath2) and os.path.isfile(filepath3)]):
                print("Percentiles doesn't already exist, creating...")
                yearly_stats_percentiles = jja.aggregated_by(['season_year'], iris.analysis.PERCENTILE, percent=[95, 97, 99])
                if stat =='95th Percentile':
                    yearly_stats = yearly_stats_percentiles[0,:,:,:]
                    #print('Creating 95th percentile')
                elif stat =='97th Percentile':
                    yearly_stats = yearly_stats_percentiles[1,:,:,:]
                    #print('Creating 97th percentile')
                elif stat =='99th Percentile':
                    yearly_stats = yearly_stats_percentiles[2,:,:,:]
                    #print('Creating 99th percentile')
                
        print('Found yearly stat in: ', time.time() - seconds)
        
        #############################################
        # 
        #############################################
        if mask_to_region == True:
            print ("Masking to region")
            if not 'regional_mask' in globals():
                seconds = time.time()
                regional_mask = mask_by_region(yearly_stats, regional_gdf)
                print('Created regional_mask in: ', time.time() - seconds)
            else: 
                print('Regional mask already exists')
            # Mask JJA
            seconds = time.time()
            mask_3d = np.repeat(regional_mask[np.newaxis,:, :], yearly_stats.shape[0], axis=0)
            #print("Seconds to run =", time.time() - seconds)	
            yearly_stats.data =  np.ma.masked_array(yearly_stats.data, np.logical_not(mask_3d))
            #yearly_stats.data =  np.ma.masked_array(yearly_stats.data, np.logical_not(mask_3d))
            print('Masked data in : ', time.time() - seconds)
        
        # Check plotting
        #qplt.contourf(yearly_stats[5,:,:])       
        #plt.gca().coastlines()   
        # Check plotting #.2
        #plot_cube_within_region(yearly_stats[0,:,:], regional_gdf)
     
        ############################################
        # Reformat for use in R
        #############################################
        # Get the coords 1D
        lats_1d = yearly_stats.coord('latitude').points
        lons_1d = yearly_stats.coord('longitude').points
        
        # Convert to 1D
        lats_1d = lats_1d.reshape(-1)
        lons_1d = lons_1d.reshape(-1)
        
        #############################
        print("Creating dictionary")
        # Create a dictionary with each key corresponding to a year and the values
        # containing a 1D array of AMAX values, masked to the region of interest
        my_dict = {}
        for i in range(0, yearly_stats.shape[0]):
            #print(i)
            # Get data from one timeslice
            one_ts = yearly_stats[i,:,:]
            # Extract data from one year 
            data = one_ts.data.reshape(-1)
            year  = one_ts.coord('season_year').points[0]
            # Store as dictionary with the year name
            my_dict[year] = data
        
        # Create as a dataframe
        test = pd.DataFrame(my_dict)
        
        # Join with lats and lons
        test['lat'], test['lon'] = [lats_1d, lons_1d]
        
        if not os.path.isfile("Outputs/HiClimR_inputdata/{}/mask.csv".format(region)):
            test.to_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region), index = False)
        
        # Remove NA rows
        test = test.dropna()
        
        # Save dataframe
        print("Saving stats output")
        ddir = "Outputs/HiClimR_inputdata/{}/{}/".format(region, stat)
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
        test.to_csv(ddir + "em{}.csv".format(em), index = False)
    

################# Finding biggest ten for each year
    if greatest_ten == True:
<<<<<<< HEAD
        if 'test' in globals():
            print ("Using mask from stats processing")
            mask = test
        else:
            print ('No mask, reading from file')
            # Read from file, delete NAs
            mask = pd.read_csv("Outputs/HiClimR_inputdata/WY/mask.csv")
            mask = mask.dropna()

        df = n_largest_yearly_values(jja, mask, 10)
    
        
=======
>>>>>>> 60c8f8374494f659828ab61dc08519d5dacfe17c
        ddir = "Outputs/HiClimR_inputdata/{}/{}/".format(region, 'Greatest_ten')
        if not os.path.isfile(ddir + "em{}.csv".format(em)):
                print("Greatest ten doesn't already exist, creating...")
                seconds = time.time()
                if not 'test' in globals():
                    print ('No mask, reading from file')
                    # Read from file, delete NAs
                    mask = pd.read_csv("Outputs/HiClimR_inputdata/WY/mask.csv")
                    mask = mask.dropna()
                else: 
                    print ("Using mask from stats processing")
                    mask = test
                df = n_largest_yearly_values(jja, mask, 10)
            
                
                ddir = "Outputs/HiClimR_inputdata/{}/{}/".format(region, 'Greatest_ten')
                if not os.path.isdir(ddir):
                        os.makedirs(ddir)
                df.to_csv(ddir + "em{}.csv".format(em), index = False)
                print("Created greatest 10 in ", time.time()- seconds)
    
    print("Finished everything for EM in: ", time.time() - start_time)	
    

        if not os.path.isfile(ddir):
                os.makedirs(ddir)



    

    
