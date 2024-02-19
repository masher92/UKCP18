def run_other_bit(filename):
    
        ### Load radar data for one day (using IRIS)
        day_cube = iris.load_cube(filename)

        ### Add additional time based variables
        # cat.add_year(day_cube, 'time', name='year')
        # cat.add_month(day_cube, 'time', name='month')
        # cat.add_day_of_month(day_cube, 'time', name='day_of_month')
        cat.add_hour(day_cube, 'time', name='hour')
        # cat.add_day(day_cube, 'time', name='day')

        ### Aggregate to half hourly values (means)
        firsthalfof_hour_constraint = iris.Constraint(time=lambda cell: cell.point.minute <30)
        secondhalfof_hour_constraint = iris.Constraint(time=lambda cell: cell.point.minute >=30)

        # Create empty cube list to populate
        my_cube_list = iris.cube.CubeList()

        # Get list of the hours
        hours = set(day_cube.coord('hour').points)
        # Loop through the hours
        for hour in hours:

            # Establish constraint to select only this hour
            hour_constraint = iris.Constraint(time=lambda cell: cell.point.hour == hour)
            # Use constraint to select only this hour
            hour_cube = day_cube.extract(hour_constraint)
            # Check the times
            # times = hour_cube.coord('time').points
            # times = [datetime.datetime.fromtimestamp(x ) for x in times]

            # Get only cubes which fall within the first half of the hour and then the second half of the hour
            first_half_of_hour = hour_cube.extract(firsthalfof_hour_constraint)
            second_half_of_hour = hour_cube.extract(secondhalfof_hour_constraint)

            # If there are at least 4 values
            # Find the mean across first/second halves of hour
            # Add to cube list
            if first_half_of_hour == None:
                print("no values in 1st half hour")
            elif len(first_half_of_hour.shape) ==2:
                print("only 1 value in 2nd half hour")        
            else:
                if first_half_of_hour.shape[0] >=4:
                    ## Correct negative 1064 values to np.nan
                    if np.nanmin(first_half_of_hour.data)<0:
                        print(f"iter {i}, hour {hour}, first half hour, min value is: {np.nanmin(first_half_of_hour.data)}")
                        first_half_of_hour.data = np.where(first_half_of_hour.data == -1024, np.nan, first_half_of_hour.data)
                        first_half_of_hour.data = np.where(first_half_of_hour.data == -894.125, np.nan, first_half_of_hour.data)
                        print(f"min value is: {np.nanmin(first_half_of_hour.data)}")
                        if np.nanmin(first_half_of_hour.data <0):
                            print(first_half_of_hour.data[first_half_of_hour.data<0])
                    # FIND MEAN ACROSS WHOLE FIRST HALF HOUR
                    first_half_hourly_mean = first_half_of_hour.aggregated_by(['hour'],iris.analysis.MEAN)
                    # first_half_hourly_mean.data.astype('float64')
                    my_cube_list.append(first_half_hourly_mean)
                else:
                    print(f"only {first_half_of_hour.shape[0]} vals in 1st half hour")

            ### SECOND HALF HOUR    
            if second_half_of_hour == None:
                print("no values in 2nd half hour")
            elif len(second_half_of_hour.shape) ==2:
                print("only 1 value in 2nd half hour")
            else:
                if second_half_of_hour.shape[0] >=4:    
                    ## Correct negative 1064 values to np.nan
                    if np.nanmin(second_half_of_hour.data)<0:            
                        print(f"iter {i}, hour {hour}, second half hour, min value is: {np.nanmin(second_half_of_hour.data)}")
                        second_half_of_hour.data = np.where(second_half_of_hour.data == -1024, np.nan, second_half_of_hour.data)
                        second_half_of_hour.data = np.where(second_half_of_hour.data == -894.125, np.nan, second_half_of_hour.data)
                        print(f"min value is: {np.nanmin(second_half_of_hour.data)}")
                        if np.nanmin(second_half_of_hour.data <0):
                            print(second_half_of_hour.data[second_half_of_hour.data<0])
                    # FIND MEAN ACROSS WHOLE FIRST HALF HOUR
                    second_half_hourly_mean = second_half_of_hour.aggregated_by(['hour'],iris.analysis.MEAN)
                    # second_half_hourly_mean.data.astype('float64')
                    my_cube_list.append(second_half_hourly_mean)
                else:
                    print(f"only {second_half_of_hour.shape[0]} vals in 2nd half hour")


        ### Join back into one cube covering the whole day
        try:
            for halfhour_i in range(0,len(my_cube_list)):
                my_cube_list[halfhour_i].data = my_cube_list[halfhour_i].data.astype('float64')

            thirty_mins_means = my_cube_list.concatenate_cube()

            # Get rid of high values which are fill values
            thirty_mins_means.data = np.where(thirty_mins_means.data >1e+36, np.nan, thirty_mins_means.data)

            # save 
            new_fp = filename[:-3]+ '_30mins.nc'
            new_fp = new_fp.replace('5mins', '30mins')
            iris.save(thirty_mins_means, new_fp)
            print(f'Saved cube {year} {i}')
            print(np.nanmin(thirty_mins_means.data))
            print(np.nanmax(thirty_mins_means.data))
            print(np.nanmean(thirty_mins_means.data))

        except:
            pass
    
    
    


import iris
import xarray as xr
import numpy as np
from iris.coords import DimCoord
from iris.coord_systems import TransverseMercator,GeogCS
from iris.cube import Cube
from cf_units import Unit
import cf_units
import os
import glob
from pyproj import Proj, transform
import sys
import warnings
import multiprocessing as mp
import iris
import glob
import iris.plot as iplt
import iris.quickplot as qplt
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import numpy as np


warnings.filterwarnings("ignore")

ems_hourly = ['01', '04', '06', '07', '08', '09', '10', '11', '12', '13', '15']
ems_30mins = ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = '1980_2001'


##########################################################################################
#########################################################################################
# Define variables and set up environment
##########################################################################################
##########################################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
# from Spatial_geometry_functions import *

# Load UKCP18 12km model data to use in regriddding
file_model_12km=f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/12km/01/{yrs_range}/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
cube_12km=iris.load_cube(file_model_12km)

file_model_2_2km ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19911201-19911230.nc'
cube_model_2_2km =iris.load_cube(file_model_2_2km)


##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
cube_12km_trimmed_to_leeds =  trim_to_bbox_of_region_obs(cube_12km, leeds_at_centre_gdf)

for year in range(2016,2021):
    print(year)
    # Change directory to be for correct year
    os.chdir(f"/nfs/a319/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/{year}")
    # Define filepaths to save files to
    output_dir_12km = f"/nfs/a319/gy17m2a/PhD/datadir/NIMROD/30mins/NIMROD_regridded_12km/NearestNeighbour/{year}/"
    output_dir_2_2km = f"/nfs/a319/gy17m2a/PhD/datadir/NIMROD/30mins/NIMROD_regridded_2.2km/NearestNeighbour/{year}/"
    # Create these directories if they don't exist already
    if not os.path.isdir(output_dir_12km):
        os.makedirs(output_dir_12km)
    if not os.path.isdir(output_dir_2_2km):
        os.makedirs(output_dir_2_2km)
    # Loop through all the diles in the 1km folder    
    for filename in sorted(glob.glob("*")):
        print(filename)
        # Create version of filename specifying it is regridded
        filename_to_save_to = f"rg_{filename}"

        # Check if this regridded file exists, and if not create it
        # Don't want to load the cube twice unnecessarily, so if we load it for 12km, then make a flag to tell us it's
        # already loaded and then use this for 2.2km

        # 12km regridding
        if os.path.isfile(output_dir_12km + filename_to_save_to):
            print("File already exists")
        if not os.path.isfile(output_dir_12km + filename_to_save_to):
            print('Making file 12km')
            try:
                cube = iris.load(filename)[0]
            except:
                print("running other bit")
                thefp = f'/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/{filename}'.replace('_30mins', '')
                run_other_bit(thefp)
                cube = iris.load(filename)[0]               
            loaded_cube=True
                
            # Nearest neighbour
            try:
                reg_cube_nn =cube.regrid(cube_12km,iris.analysis.Nearest())    
            except:
                print("running other bit at other point")
                thefp = f'/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/{filename}'.replace('_30mins', '')
                run_other_bit(thefp)
                reg_cube_nn =cube.regrid(cube_12km,iris.analysis.Nearest())        
            # Save 
            iris.save(reg_cube_nn, output_dir_12km + filename_to_save_to)

        # 2.2km regridding
        if os.path.isfile(output_dir_2_2km + filename_to_save_to):
            print("File already exists")
        if not os.path.isfile(output_dir_2_2km + filename_to_save_to):
            print('Making 2.2km file')
            if loaded_cube == False:
                try:
                    cube = iris.load(filename)[0]
                except:
                    print("running other bit")
                    thefp = f'/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/{filename}'.replace('_30mins', '')
                    run_other_bit(thefp)
                    cube = iris.load(filename)[0]       
                
                
            # Nearest neighbour
            try:
                reg_cube_nn =cube.regrid(cube_model_2_2km,iris.analysis.Nearest())    
            except:
                print("running other bit at other point")
                thefp = f'/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/{filename}'.replace('_30mins', '')
                run_other_bit(thefp)
                reg_cube_nn =cube.regrid(cube_model_2_2km,iris.analysis.Nearest())        
                
            print("Regridded")
            # Save 
            iris.save(reg_cube_nn, output_dir_2_2km + filename_to_save_to)    

        loaded_cube=False
