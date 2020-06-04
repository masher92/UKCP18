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
#iris.FUTURE.netcdf_promote = True
#iris.FUTURE.netcdf_no_unlimited = True

sys.path.insert(0, root_fp + 'Scripts/UKCP18')
#os.chdir("/nfs/a319/gy17m2a/Scripts")

# Provide root_fp as argument
#root_fp = sys.argv[1]
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
start_year = 1980
end_year = 2000 

from config import *
from Pr_functions import *

members = ["1"]
#members = sys.argv[2].split(',')
for em in members:
    # Check em has a leading zero
    em = em.zfill(2)
    print ("Checking timeseries for " + location + " using ensemble member " + em + " over years " + str(start_year) + "-" + str(end_year))
    # Create paths to the folders where the outputs would be stored
    cubefolder_fp = root_fp + "Outputs/UKCP18/{}/2.2km/TimeSeries_cubes".format(location)
    cube_fp =  cubefolder_fp + '/EM{}_{}-{}.nc'.format(em, start_year, end_year)
    csvfolder_fp =root_fp + "Outputs/UKCP18/{}/2.2km/TimeSeries_csv".format(location)
    csv_fp = csvfolder_fp + '/EM{}_{}-{}.csv'.format(em, start_year, end_year)
    
    # If both the csv and the cube exist, then read them from their location
    if os.path.exists(csv_fp) & os.path.exists(cube_fp):
        print (csv_fp + " and " + cube_fp + ' already exist.')
    # If either the csv or the cube doesn't exist, then run the code to create them
    else:
        print("Either " + csv_fp + " or " + cube_fp + ' does not exist, creating...')
        
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
            general_filename = root_fp + 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
            #print(general_filename)
            # Find all files in directory which start with this string
            for filename in glob.glob(general_filename):
                #print(filename)
                filenames.append(filename)
         
        #Load in the cubes
        #print(filenames[239])
        #for i in range(239,240):
        #    print(i)
        #    iris.load(filenames[i],'lwe_precipitation_rate')
          
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

        #############################################
        # Find part within West Yorkshire
        #############################################
        centre_within_geometry = GridCells_within_geometry(df, leeds_gdf, data)


        #############################################
        # Convert the WGS coordiantes of the point of interest into the same coordinate
        # system as the precipitation cubes
        #############################################
        sample_point = define_loc_of_interest(monthly_cubes_list, lon, lat)
        
        # Reconvert
        #cs = monthly_cubes_list[0].coord_system()
        #lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(sample_point[1][1]), np.array(sample_point[0][1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        
        #############################################
        # Create a single cube containing a precipitation timeseries for the 
        # location of interest
        #############################################    
        start = timer()
        results = create_concat_cube_one_location_m3(monthly_cubes_list, sample_point)
        ts_cube = results[0]
        print("Cubes joined and interpolated to location at " + str(lat)+ "," + str(lon) + ' in ' + str(round((timer() - start)/60, 1)) + ' minutes')
        
        # Check centre location of grid cell it used (in lat, lon)
        lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(results[2]), np.array(results[1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        # Find the index of the closest point
        index = results[3]
        
        ## Cmpare outputs
        #qplt.plot(ts_cube3)
        #(ts_cube2.data==ts_cube.data).all()
                        
        #############################################
        # Convert to a dataframe
        #############################################
        print("Converting to dataframe")       
        start_dfconversion_timer = timer()
        ts_df = pd.DataFrame({'Date': np.array(ts_cube.coord('yyyymmddhh').points),
                          'Precipitation (mm/hr)': np.array(ts_cube.data)})
        print("Cube converted to DF in " + str(round((timer() - start_dfconversion_timer)/60, 1)) + ' minutes')
        
        # Format the date column
        ts_df['Date_Formatted'] =  pd.to_datetime(ts_df['Date'], format='%Y%m%d%H',  errors='coerce')
        
        ###########################################################
        # Save cube  and df
        ###########################################################
        # Create directory if it doesn't exist already
        if not os.path.isdir(cubefolder_fp):
            os.makedirs(cubefolder_fp)
        # Save cube
        print("Saving cube to " + cube_fp)
        start_saving_timer = timer()
        iris.save(ts_cube, cube_fp)  
        print("Cube saved in " + str(round((timer() - start_saving_timer)/60, 1)) + ' minutes')
        print("Cube saved in " + str(round(timer() - start_saving_timer, 1)) + ' seconds')

          
        # Create directory if it doesn't exist already
        if not os.path.isdir(csvfolder_fp):
            os.makedirs(csvdolder_fp)
        # Write to a csv
        ts_df.to_csv(csv_fp, index = False)
        print("Saving csv to " + csv_fp)
                
        print("Complete")
        #iris.fileformats.netcdf.save(ts_cube, '/nfs/a319/gy17m2a/Outputs/TimeSeries_cubes/Armley/2.2km/EM07_1980-2001_test.nc', unlimited_dimensions = ['time'], chunksizes = [50])
        
   

##############################################################################
### Checking this approach
##############################################################################
# It is possible to conduct a check on which grid cell the data is being extracted
# for using the index of the grid cell returned by the create_concat_cube_one_location_m3
# function.
        
# Create a test dataset with all points with same value
# Set value at the index returned above to something different
# And then plot data spatially, and see which grid cell is highlighted.        
# test_data = np.full((hour_uk_cube.shape), 7, dtype=int)
# test_data_rs = test_data.reshape(-1)
# test_data_rs[INDEX] = 500
# test_data = test_data_rs.reshape(test_data.shape)



