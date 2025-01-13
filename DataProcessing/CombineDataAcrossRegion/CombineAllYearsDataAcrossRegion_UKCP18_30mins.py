def fix_broken_cube(monthly_cubes_list):
    print("Didnt work first time so doing lots of tricksy things")
    for cube in monthly_cubes_list:
        if cube.coords('forecast_reference_time'):
            cube.remove_coord('forecast_reference_time')
        if cube.coords('realization'):
            cube.remove_coord('realization')

        if cube.coords('forecast_period'):
            cube.remove_coord('forecast_period')

        cube.standard_name = "stratiform_rainfall_flux"
        cube.long_name = "stratiform_rainfall_flux"    

    iris.util.equalise_attributes(monthly_cubes_list)    

    # Add missing dimension coordinates
    cube = monthly_cubes_list[3]
    if 'projection_y_coordinate' not in cube.coords():
        # Copy projection_y_coordinate from the first cube
        cube.add_dim_coord(monthly_cubes_list[0].coord('projection_y_coordinate'), 1)

    if 'projection_x_coordinate' not in cube.coords():
        # Copy projection_x_coordinate from the first cube
        cube.add_dim_coord(monthly_cubes_list[0].coord('projection_x_coordinate'), 2)

    # Assuming `cube` is your Iris Cube with a `time` coordinate
    time_coord = cube.coord('time')

    # Check if bounds already exist
    if not time_coord.has_bounds():
        # Get the time points
        time_points = time_coord.points  # Example: [295920.25, 295921.25, ...]

        # Create bounds for each time point
        lower_bounds = time_points - 0.25  # Subtract 0.25 to get the lower bound
        upper_bounds = time_points + 0.25  # Add 0.25 to get the upper bound

        # Combine into a bounds array with shape (n_points, 2)
        bounds = np.column_stack((lower_bounds, upper_bounds))

        # Add bounds to the time coordinate
        time_coord.bounds = bounds

    # Verify the bounds
    monthly_cubes_list[3] = cube
    monthly_cubes_list[3].coord('time').units = monthly_cubes_list[4].coord('time').units

    return monthly_cubes_list

import iris
import os
import glob as sir_globington_the_file_gatherer
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import time
import multiprocessing as mp
import glob as glob

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *


ems= ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = "2002_2020"
resolution = '2.2km_bng_regridded_12km_masked' #2.2km, 12km, 2.2km_regridded_12km
yrs= range(2002,2020)

for em in ems:
    for yr in range(2001,2020):
        ddir = f"ProcessedData/TimeSeries/UKCP18_every30mins/{resolution}/{yrs_range}/{em}_wholeyear/"

        if not os.path.isdir(ddir):
                os.makedirs(ddir)

        if not os.path.isfile(ddir + f'{yr}_compressed.npy'):
            print(em, yr, resolution)

            ### Get a list of filenames for this ensemble member
            general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/2002_2020/{em}/bng_{em}a.pr{yr}*'
            filenames = [filename for filename in glob.glob(general_filename) if '2000' not in filename and 'pr2020' not in filename]
            print(len(filenames))

            ### Load in the data
            monthly_cubes_list = iris.load(filenames)

            ### Concatenate cubes into one
            try:
                model_cube = monthly_cubes_list.concatenate_cube() 
            except:
                monthly_cubes_list = fix_broken_cube(monthly_cubes_list)
                model_cube = monthly_cubes_list.concatenate_cube()

            # Get rid of negative values
            compressed = model_cube.data.compressed()
            print(f"compressed has length: {compressed.shape[0]}")

            ########
            # Get the times
            ########
            time_values = model_cube.coord('time').points# [non_masked_indices[0]]

            # Save to file
            if not os.path.isfile(ddir + f'timevalues.npy'):
                np.save(ddir + f'timevalues.npy', time_values) 
            np.save(ddir + f'{yr}_compressed.npy', compressed) 
        else:
            print(ddir + f"{yr}_compressed.npy' already exists")