#############################################
# Set up environment
#############################################
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
#import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)

# Stops warning on loading Iris cubes
iris.FUTURE.netcdf_promote = True
iris.FUTURE.netcdf_no_unlimited = True

sys.path.insert(0, '/nfs/a319/gy17m2a/Scripts/config.py')
os.chdir("/nfs/a319/gy17m2a/Scripts")
from config import *
from Pr_functions import *

members = sys.argv[1].split(',')
for em in members:
    # Check em has a leading zero
    em = em.zfill(2)
    print ("Checking timeseries for " + location + " using ensemble member " + em + " over years " + str(start_year) + "-" + str(end_year))
    # Create paths to the folders where the outputs would be stored
    csvfolder_fp =r'/nfs/a319/gy17m2a/Outputs/TimeSeries_csv/{}/2.2km'.format(location)
    csv_fp = csvfolder_fp + '/5NearestNeighbours/EM{}_{}-{}.csv'.format(em, start_year, end_year)
    
    # If both the csv and the cube exist, then read them from their location
    if os.path.exists(csv_fp) :
        print (csv_fp + ' already exist.')
    # If either the csv or the cube doesn't exist, then run the code to create them
    else:
        print(csv_fp + ' does not exist, creating...')
        
        # Define the local directory where the data is stored
        if 1980 <= start_year <= 2001:
          yrs_range = "1980_2001" 
        elif 2020 <= start_year <= 2041:
           yrs_range = "2020_2041" 
        elif 2060 <= start_year <= 2081:
           yrs_range = "2060_2081"  
      
        # Create list of names of cubes for between the years specified
        filenames =[]
        for year in range(start_year,end_year+1):
            # Create filepath to correct folder using ensemble member and year
            general_filename = r'/nfs/a319/gy17m2a/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
            #print(general_filename)
            # Find all files in directory which start with this string
            for filename in glob.glob(general_filename):
                #print(filename)
                filenames.append(filename)
          
        monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
        print(str(len(monthly_cubes_list)) + " cubes found for this time period.")
        
        #############################################
        # Convert the WGS coordiantes of the point of interest into the same coordinate
        # system as the precipitation cubes
        #############################################
        sample_point = define_loc_of_interest(monthly_cubes_list, lon, lat)
        
        #############################################
        # Create a dataframe containing a precipitation timeseries generated from
        # x nearest neighbouring cubes
        # location of interest       
        start = timer()
        ts_cubes_df = create_concat_cube_one_location_m3(monthly_cubes_list, sample_point, 5)
        print("Cubes joined and interpolated to location at " + str(lat)+ "," + str(lon) + ' in ' + str(round((timer() - start)/60, 1)) + ' minutes')
        ## Cmpare outputs
        #qplt.plot(ts_cube3)
        #(ts_cube2.data==ts_cube.data).all()
                              
        ###########################################################
        # Save cube  and df
        ###########################################################
        # Write to a csv
        ts_df.to_csv(csv_fp, index = False)
        print("Saving csv to " + csv_fp)
                
        print("Complete")
        #iris.fileformats.netcdf.save(ts_cube, '/nfs/a319/gy17m2a/Outputs/TimeSeries_cubes/Armley/2.2km/EM07_1980-2001_test.nc', unlimited_dimensions = ['time'], chunksizes = [50])
        

    







