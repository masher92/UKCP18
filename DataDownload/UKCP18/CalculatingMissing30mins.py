import iris
import os
import glob as glob
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import iris.plot as iplt

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)


# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *


# ### Load necessary spatial data
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})


# ### Establish the corresponding ensemble member numbers
em_matching_dict = {'01':'bc005', '04': 'bc006', '05': 'bc007', '06':'bc009',  '07':'bc010', 
                    '08': 'bc011', '09':'bc013', '10': 'bc015', '11': 'bc016', '12': 'bc017', '13':'bc018', '15':'bc012'}

resolution = '2.2km'
yrs_range = "2002_2020"
# em_1hr = '05'
# yr = 2012
# month_num = '06'

for em_1hr in ['15']:
    em_30mins = em_matching_dict[em_1hr]
    for yr in range(1999,2021):
        for month_num in ['06', '07', '08']:
            if (os.path.isfile(f"datadir/UKCP18_every30mins/{em_30mins}/{yrs_range}/{em_30mins}a.pr{yr}{month_num}.nc")):
                print("already exists")
            else:
                print(f"Running for month {month_num} in {yr}, for {em_1hr} (which equatees to {em_30mins})")

                ####################################################### 
                #######################################################
                ## Get one month of data - HOURLY
                ####################################################### 
                #######################################################
                ### Get a list of filenames for hourly data
                general_filename_1hr = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km/{em_1hr}/{yrs_range}/pr_rcp85_land-cpm_uk_2.2km_{em_1hr}_1hr_{yr}{month_num}*'
                filenames_1hr = []
                for filename in glob.glob(general_filename_1hr):
                        filenames_1hr.append(filename)
                # If don't find any files matching this string in the 2001_2020 folder, then check the 1980_2001
                if len(filenames_1hr) == 0:
                    general_filename_1hr = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km/{em_1hr}/1980_2001/pr_rcp85_land-cpm_uk_2.2km_{em_1hr}_1hr_{yr}{month_num}*'
                    for filename in glob.glob(general_filename_1hr):
                            filenames_1hr.append(filename)
                    print(len(filenames_1hr))

                # ### Load in the data and remove the ensemble member dimension
                monthly_cubes_list_1hr = iris.load(filenames_1hr)
                cube_1hr = monthly_cubes_list_1hr[0]
                cube_1hr = cube_1hr[0,:,:,:]

                # ### Trim to Leeds
                # cube_1hr = trim_to_bbox_of_region(cube_1hr, leeds_at_centre_gdf)

                #######################################################
                #######################################################
                ## Get one month of data - 30mins
                #######################################################
                #######################################################
                # ### Get all files for this ensemble member
                general_filename_30mins = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_first30mins/{yrs_range}/{em_30mins}/{em_30mins}a.pr{yr}{month_num}*'
                filenames_first30mins = []
                for filename_30mins in glob.glob(general_filename_30mins):
                    filenames_first30mins.append(filename_30mins)
                filenames_first30mins.sort()

                # ### Load in the data 
                monthly_cubes_list_30mins = iris.load(filenames_first30mins)

                # Equalise
                for cube in monthly_cubes_list_30mins:
                    for attr in ['forecast_period', 'forecast_reference_time']:
                        if attr in cube.attributes:
                            del cube.attributes[attr]


                monthly_cube_30mins = monthly_cubes_list_30mins.concatenate_cube()      

                # ### Trim to be the same shape as the hourly data
                # monthly_cube_30mins_1st = trim_to_bbox_of_region_30mins(monthly_cube_30mins, leeds_at_centre_gdf)
                monthly_cube_30mins_1st = monthly_cube_30mins[:,24:-24,24:-24]

                # ### Convert units of 30 mins data
                # Check current units
                # print(monthly_cube_30mins_1st.units)
                # Set the units to those of the 1 hr cube
                monthly_cube_30mins_1st.units = cube_1hr.units
                # print(monthly_cube_30mins_1st.units)

                # Convert the data to also be this unit
                monthly_cube_30mins_1st_data = monthly_cube_30mins_1st.data
                monthly_cube_30mins_1st_data = monthly_cube_30mins_1st_data*3600

                monthly_cube_30mins_1st.data = monthly_cube_30mins_1st_data


                #######################################################
                #######################################################
                ## Find the second half of the hour, using the first half of hour and hourly values
                #######################################################
                #######################################################
                # get the hourly data
                cube_1hr_data = cube_1hr.data
                # calculate value for second half of hour
                second_half_of_the_hour_mean_hourly_rainfall_rate_data = 2*cube_1hr_data-monthly_cube_30mins_1st_data
                # Create a new cube for the second half of the hour (start by copying the first half of hour cube)
                monthly_cube_30mins_2nd = monthly_cube_30mins_1st.copy()
                # Set values as calculated
                monthly_cube_30mins_2nd.data = second_half_of_the_hour_mean_hourly_rainfall_rate_data


                # ### Edit the times to be 30 mins later
                # get the times from the first half hour
                first_half_hour_times = monthly_cube_30mins_1st.coord('time').copy()
                # add 30 mins
                second_half_hour_times = first_half_hour_times + 0.5
                # for the second hald hour cube, remove the time dimension and then re-add the edited one
                monthly_cube_30mins_2nd.remove_coord('time')
                monthly_cube_30mins_2nd.add_dim_coord(second_half_hour_times, 0)

                #######################################################
                #######################################################
                ## Join first half hour and second half hour into one cube
                #######################################################
                #######################################################
                # ### Get a list of all the cubes in each of the monthly cubes
                list_30mins_1st = iris.cube.CubeList(monthly_cube_30mins_1st.slices_over('time'))
                list_30mins_2nd = iris.cube.CubeList(monthly_cube_30mins_2nd.slices_over('time'))
                list_30mins = list_30mins_1st +  list_30mins_2nd

                ### Merge back into one cube
                monthly_cube_30mins = list_30mins.merge_cube()

                #######################################################
                #######################################################
                ## Save
                #######################################################
                #######################################################
                dir_to_save = f"datadir/UKCP18_every30mins/{resolution}/{em_30mins}/{yrs_range}/"

                if os.path.isdir(dir_to_save):
                    print("Exists")
                else:
                    print("Doesn't exist")
                    os.makedirs(dir_to_save)
                fp_to_save = f"datadir/UKCP18_every30mins/{resolution}/{em_30mins}/{yrs_range}/{em_30mins}a.pr{yr}{month_num}.nc" 
                print(fp_to_save)
                iris.save(monthly_cube_30mins, fp_to_save)