import iris
import glob
import iris.plot as iplt
import iris.quickplot as qplt
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import numpy as np
import os


def process_half_hour(half_hour_cube, label, i, hour, my_cube_list_filtered_100, my_cube_list_filtered_300, my_cube_list_unfiltered, max_vals):
    if half_hour_cube is None:
        print(f"no values in {label}")
    elif len(half_hour_cube.shape) == 2:
        print(f"only 1 value in {label}")
    else:
        if half_hour_cube.shape[0] >= 4:
            # Correct negative values to np.nan
            if np.nanmin(half_hour_cube.data) < 0:
                half_hour_cube.data = np.where(half_hour_cube.data < 0, np.nan, half_hour_cube.data)
                # If somehow still negatives
                if np.nanmin(half_hour_cube.data < 0):
                    print(half_hour_cube.data[half_hour_cube.data < 0])
            
            ###############################################  
            # Aggregate version with no corrections
            ###############################################                     
            half_hourly_mean_unfiltered = half_hour_cube.copy().aggregated_by(['hour'], iris.analysis.MEAN)
            my_cube_list_unfiltered.append(half_hourly_mean_unfiltered)
            
            ###############################################  
            # Apply corrections and then aggregate
            ###############################################    
            #print(f"iter {i}, hour {hour}, {label}, min value is: {np.nanmin(half_hour_cube.data)} and max value is: {np.nanmax(half_hour_cube.data)}")

            # Filter out values over 100 and calculate mean
            half_hour_cube_filtered_100 = half_hour_cube.copy()
            half_hour_cube_filtered_100.data = np.where(half_hour_cube_filtered_100.data > 100, np.nan, half_hour_cube_filtered_100.data)
            half_hourly_mean_filtered_100 = half_hour_cube_filtered_100.aggregated_by(['hour'], iris.analysis.MEAN)
            my_cube_list_filtered_100.append(half_hourly_mean_filtered_100)

            # Filter out values over 300 and calculate mean
            half_hour_cube_filtered_300 = half_hour_cube.copy()
            half_hour_cube_filtered_300.data = np.where(half_hour_cube_filtered_300.data > 300, np.nan, half_hour_cube_filtered_300.data)
            half_hourly_mean_filtered_300 = half_hour_cube_filtered_300.aggregated_by(['hour'], iris.analysis.MEAN)
            my_cube_list_filtered_300.append(half_hourly_mean_filtered_300)

            #print(f"iter {i}, hour {hour}, {label}, min value after 100 filter is now: {np.nanmin(half_hour_cube_filtered_100.data)} and max value is now: {np.nanmax(half_hour_cube_filtered_100.data)}")
            #print(f"iter {i}, hour {hour}, {label}, min value after 300 filter is now: {np.nanmin(half_hour_cube_filtered_300.data)} and max value is now: {np.nanmax(half_hour_cube_filtered_300.data)}")

            # Append max values if needed
            max_vals.append(np.nanmax(half_hour_cube.data))
        else:
            print(f"only {half_hour_cube.shape[0]} vals in {label}")
    
    return half_hour_cube

def create_year_directories(base_path, start_year, end_year):
    for year in range(start_year, end_year + 1):
        year_path = os.path.join(base_path, str(year))
        if not os.path.exists(year_path):
            os.makedirs(year_path)
            print(f'Created directory: {year_path}')

def process_and_save_cubes(cube_list, label, new_fp_base, sorted_list, i, year):
    for halfhour_i in range(len(cube_list)):
        cube_list[halfhour_i].data = cube_list[halfhour_i].data.astype('float64')

    # Concatenate the cube list into one cube
    full_day_cube = cube_list.concatenate_cube()

    # Get rid of high values which are fill values
    full_day_cube.data = np.where(full_day_cube.data > 1e+36, np.nan, full_day_cube.data)

    # Define base path for saving
    base_path = f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/{label.capitalize()}'

    # Create year subdirectories if they don't exist
    create_year_directories(base_path, 2004, 2020)

    # Modify new_fp_base for the specific type of cube
    new_fp = new_fp_base.replace('Unfiltered', label)

    # Save the cube
    iris.save(full_day_cube, new_fp)

    print(f'Saved {label} cube for {year}, iteration {i}')
    print(f'Min value: {np.nanmin(full_day_cube.data)}. Max value: {np.nanmax(full_day_cube.data)}, Mean value: {np.nanmean(full_day_cube.data)}')
    
    
years = [2019]

for year in years:
    print(year)
    ### Get list of files to convert
    radardir = f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/'
    file_list = glob.glob(radardir + "*.nc")
    sorted_list = sorted(file_list)
    
    for i in range(0, len(sorted_list)):
        print(i)
        # Construct the new file paths to check existence
        new_fp_base = sorted_list[i].replace('OriginalFormat_1km/', 'OriginalFormat_1km/Unfiltered/')[:-3] + '_30mins.nc'
        new_fp_base = new_fp_base.replace('5mins', '30mins')
        new_fp_base = new_fp_base.replace('/2006/', f'/{year}/')

        new_fp_unfiltered = new_fp_base.replace('Unfiltered', 'Unfiltered')
        new_fp_filtered_100 = new_fp_base.replace('Unfiltered', 'Filtered_100')
        new_fp_filtered_300 = new_fp_base.replace('Unfiltered', 'Filtered_300')
        
        # Check if the files already exist
        if os.path.exists(new_fp_unfiltered) and os.path.exists(new_fp_filtered_100) and os.path.exists(new_fp_filtered_300):
            print(f'Files: Unfiltered,Filtered_100, and Filtered_300 already exist, skipping.')
            continue
            
        # Load radar data for one day (using IRIS)
        day_cube = iris.load_cube(sorted_list[i])

        # Add additional time based variables
        cat.add_hour(day_cube, 'time', name='hour')

        # Aggregate to half-hourly values (means)
        firsthalfof_hour_constraint = iris.Constraint(time=lambda cell: cell.point.minute < 30)
        secondhalfof_hour_constraint = iris.Constraint(time=lambda cell: cell.point.minute >= 30)

        # Create empty cube list to populate
        my_cube_list_unfiltered = iris.cube.CubeList()
        my_cube_list_filtered_100 = iris.cube.CubeList()
        my_cube_list_filtered_300 = iris.cube.CubeList()

        max_vals = []

        # Loop through the hours
        hours = set(day_cube.coord('hour').points)
        for hour in hours:
            # Establish constraint to select only this hour
            hour_constraint = iris.Constraint(time=lambda cell: cell.point.hour == hour)
            # Use constraint to select only this hour
            hour_cube = day_cube.extract(hour_constraint)

            # Get only cubes which fall within the first half of the hour and then the second half of the hour
            first_half_of_hour = hour_cube.extract(firsthalfof_hour_constraint)
            second_half_of_hour = hour_cube.extract(secondhalfof_hour_constraint)

            # Process first half hour
            process_half_hour(first_half_of_hour, 'first half hour', i, hour, my_cube_list_filtered_100, my_cube_list_filtered_300, my_cube_list_unfiltered, max_vals)

            # Process second half hour
            process_half_hour(second_half_of_hour, 'second half hour', i, hour, my_cube_list_filtered_100, my_cube_list_filtered_300, my_cube_list_unfiltered, max_vals)

        # Join into day cubes and save
        process_and_save_cubes(my_cube_list_unfiltered, 'Unfiltered', new_fp_base, sorted_list, i, year)
        process_and_save_cubes(my_cube_list_filtered_100, 'Filtered_100', new_fp_base, sorted_list, i, year)
        process_and_save_cubes(my_cube_list_filtered_300, 'Filtered_300', new_fp_base, sorted_list, i, year)
