import iris
import glob
import iris.plot as iplt
import iris.quickplot as qplt
import datetime as datetime
import iris.coord_categorisation as cat
import numpy as np
import os
import sys

# surrogate = iris.load("/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/2019/metoffice-c-band-rain-radar_uk_20190307.nc")
# surrogate = surrogate[0]

# if 'projection_y_coordinate' not in surrogate.coords():
#     # Copy projection_y_coordinate from the first cube
#     day_cube.add_dim_coord(surrogate.coord('projection_y_coordinate'), 1)

# if 'projection_x_coordinate' not in surrogate.coords():
#     # Copy projection_x_coordinate from the first cube
#     day_cube.add_dim_coord(surrogate.coord('projection_x_coordinate'), 2)

# if 'time' not in surrogate.coords():
#     # Copy projection_x_coordinate from the first cube
#     day_cube.add_dim_coord(surrogate.coord('time'), 0)    


def process_hour(cube):
    """Process half-hourly data, apply filters, and calculate statistics."""
    
    if cube is None:
        print(f"No values.")
        return None

    if len(cube.shape) == 2:
        print(f"Only 1 value.")
        return None

    if cube.shape[0] < 8:
        print(f"Only {cube.shape[0]} values in cube.")
        return None

    # Append unfiltered data
    mean_cube = cube.copy().aggregated_by(['hour'], iris.analysis.MEAN)
    return mean_cube

def concatenate_with_error_handling(cube_list):
    """Handle errors during cube concatenation by identifying problematic cubes."""
    problematic_cube_index = None
    start = 0

    for i, cube in enumerate(cube_list):
        try:
            cube_list[start:i + 1].concatenate_cube()
        except Exception as e:
            print(f"Error concatenating cube {i}: {str(e)}")
            problematic_cube_index = i
            start = i

    if 0 <= problematic_cube_index < len(cube_list):
        del cube_list[problematic_cube_index]
        print(f"Cube at index {problematic_cube_index} removed from CubeList.")
    else:
        print(f"Index {problematic_cube_index} is out of range for CubeList.")

    return cube_list.concatenate_cube()


def process_half_hour(cube, label):
    """Process half-hourly data, apply filters, and calculate statistics."""
    
    if cube is None:
        print(f"No values in {label}.")
        return None

    if len(cube.shape) == 2:
        print(f"Only 1 value in {label}.")
        return None

    if cube.shape[0] < 4:
        print(f"Only {cube.shape[0]} values in {label}.")
        return None

    # Append unfiltered data
    mean_cube = cube.copy().aggregated_by(['hour'], iris.analysis.MEAN)
    return mean_cube

def create_year_directory(base_path, year):
    """Create directories for each year in the range if they don't exist."""
    for label in ['filtered_100', 'unfiltered']:
        year_path = os.path.join(base_path.format(label), str(year))
        os.makedirs(year_path, exist_ok=True)
        print(f"Directory created: {year_path}")


def process_and_save_cubes(cube_list, label, base_fp, year, iteration):
    """Concatenate cubes, filter data, and save to disk."""
    # Check if the cube list is empty
    if not cube_list:
        print(f"No cubes to process for {label}, year {year}, iteration {iteration}.")
        return

    # Ensure data in each cube is in the correct format
    for halfhour_i in range(len(cube_list)):
        cube_list[halfhour_i].data = cube_list[halfhour_i].data.astype('float64')

    try:
        # Attempt to concatenate cubes
        full_day_cube = cube_list.concatenate_cube()
    except Exception as e:
        print(f"Concatenation failed: {e}. Attempting error-handling concatenation.")
        full_day_cube = concatenate_with_error_handling(cube_list)

    # Print the maximum value in the cube's data
    print(f"Max value before saving: {np.nanmax(full_day_cube.data)}")

    # Save the concatenated cube to the specified file path
    save_path = base_fp.replace('filtered_100', label)
    iris.save(full_day_cube, save_path)

    # Print statistics for the cube
    print(f"Saved {label} cube for {year}, iteration {iteration}")
    print(f"Min: {np.nanmin(full_day_cube.data)}, Max: {np.nanmax(full_day_cube.data)}, Mean: {np.nanmean(full_day_cube.data)}")
    print(full_day_cube.shape)

def process_year(year):
    print(f"Processing year: {year}")

    radardir = f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/'
    sorted_files = sorted(glob.glob(radardir + "*.nc"))[250:]
    
    for i, file_path in enumerate(sorted_files):
        
        print(f"Processing file {i + 1}/{len(sorted_files)}: {file_path}")

        new_fp_base = file_path.replace('OriginalFormat_1km/', 'OriginalFormat_1km/unfiltered/')
        new_fp_base = new_fp_base.replace('/2006/', f'/{year}/')
        new_fp_base_30mins = new_fp_base.replace('5mins', '30mins')[:-3] + '_30mins.nc'
        new_fp_base_hrly = new_fp_base.replace('5mins', '1hr')[:-3] + '_1h.nc'
        
        # new_fp_base_hrly = new_fp_base_hrly.replace('unfiltered', 'filtered_100')
        # new_fp_base_30mins = new_fp_base_30mins.replace('unfiltered', 'filtered_100')
        #print(new_fp_base_hrly, new_fp_base_30mins)
         
            
        if os.path.exists(new_fp_base_30mins):            
            print(f"{new_fp_base_30mins} exists")
        else:
            day_cube = iris.load_cube(file_path)    
            if len(day_cube.shape)==2:
                day_cube = iris.util.new_axis(day_cube, "time")
            day_cube = day_cube[:,620:1800,210:1075]
            cat.add_hour(day_cube, 'time', name='hour')

            first_half_constraint = iris.Constraint(time=lambda cell: cell.point.minute < 30)
            second_half_constraint = iris.Constraint(time=lambda cell: cell.point.minute >= 30)

            filtered_100_ls_30m = iris.cube.CubeList()
            filtered_100_ls_h = iris.cube.CubeList()

            hours = set(day_cube.coord('hour').points)

            for hour in hours:
                hour_constraint = iris.Constraint(time=lambda cell: cell.point.hour == hour)
                this_hour_cube = day_cube.extract(hour_constraint)

                ##### SET negative values to NAN
                if np.nanmin(this_hour_cube.data) < 0:
                    print(f"{hour}, min b4 correction", np.nanmin(this_hour_cube.data))
                    # Ensure hour_cube.data is a MaskedArray
                    this_hour_cube.data = np.ma.masked_where(this_hour_cube.data.mask, this_hour_cube.data)  
                    # Apply the condition only where the mask is False
                    this_hour_cube.data = np.ma.masked_where(this_hour_cube.data.mask, np.where((this_hour_cube.data < 0) & (~this_hour_cube.data.mask), np.nan, this_hour_cube.data))
                    print(f"{hour}, min after correction", np.nanmin(this_hour_cube.data))

                ########### Filtered_100 version
                hour_cube_filtered_100 = this_hour_cube.copy()

                # Remove any 5 min values over 100mm/hr
                #print(f" Before: {np.nanmax(hour_cube_filtered_100.data)}")
                #hour_cube_filtered_100.data = np.where(hour_cube_filtered_100.data > 100, np.nan, hour_cube_filtered_100.data)
                #print(f" After: {np.nanmax(hour_cube_filtered_100.data)}")

                ### AGGREGATED TO AN HOUR
                hour_cube = process_hour(hour_cube_filtered_100)

                #  Add both to the lsit
                if hour_cube is not None:
                    #  Add both to the lsit
                    filtered_100_ls_h.append(hour_cube)

                # Split the 5 minute cube into the first half hour and second half hour
                # Get a first half and second half of hour aggregated to 30 mins
                first_half_of_hour_filtered_100_5mins = hour_cube_filtered_100.extract(first_half_constraint)
                second_half_of_hour_filtered_100_5mins = hour_cube_filtered_100.extract(second_half_constraint)

                # Get a first half and second half of hour aggregated to 30 mins
                first_half_of_hour_cube = process_half_hour(first_half_of_hour_filtered_100_5mins,'First Half Hour')
                second_half_of_hour_cube = process_half_hour(second_half_of_hour_filtered_100_5mins,'First Half Hour')
                
                #  Add both to the lsit
                if first_half_of_hour_cube != None:
                    filtered_100_ls_30m.append(first_half_of_hour_cube)
                if second_half_of_hour_cube != None:            
                    filtered_100_ls_30m.append(second_half_of_hour_cube)
                    
            for label, cube_list in [('filtered_100', filtered_100_ls_30m)]:
                print("30 minutes")
                process_and_save_cubes(cube_list, label, new_fp_base_30mins, year, i)  

            for label, cube_list in [('filtered_100', filtered_100_ls_h)]:
                print("1 hour")
                process_and_save_cubes(cube_list, label, new_fp_base_hrly, year, i)                  

# Main execution
# years = range(2014,2020)
year = sys.argv[1]
base_path_30m = '/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/{}'
create_year_directory(base_path_30m, year)
base_path_1h = '/nfs/a161/gy17m2a/PhD/datadir/NIMROD/1hr/OriginalFormat_1km/{}'
create_year_directory(base_path_1h, year)
process_year(year)