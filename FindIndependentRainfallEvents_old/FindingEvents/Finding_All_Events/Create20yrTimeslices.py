import pandas as pd
import iris
import sys
import iris.coord_categorisation

sys.path.insert(1, '../Finding_AMAX_Events')
sys.path.insert(1, '../')
from Identify_Events_Functions import *
from Prepare_Data_Functions import *

yrs_range= '2060_2081'
em = 'bb195'

# Get Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Read in a sample cube for finding the location of gauge in grid
sample_cube = iris.load(f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/bng_{em}a.pr206101.nc')[0][1,:,:]

for gauge_num in range(2, 1294):
    print(gauge_num)
    Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(tbo_vals, gauge_num, sample_cube)
    general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/bng_{em}a.pr*'
    # Year isnt actually doing anything here 
    cubes = load_files_to_cubelist(2061, general_filename)
    print("Loaded data")

    cubes = clean_cubes_v2(cubes)

    # Assuming your CubeList is called `cube_list`
    filtered_cubes = iris.cube.CubeList()

    # Define the coordinates to filter by
    y_idx = idx_2d[0]
    x_idx = idx_2d[1]

    # Loop through each cube in the CubeList and filter
    for cube in cubes:
        iris.coord_categorisation.add_year(cube, 'time')
        # Extract the data at the specified y_idx and x_idx
        filtered_cube = cube[:, y_idx, x_idx]

        # Append the filtered cube to the new CubeList
        filtered_cubes.append(filtered_cube)

    full_timeslice_cube = filtered_cubes.concatenate_cube()     

    # Categorize the time coordinate to extract years
    exclude_2080_constraint = iris.Constraint(year=lambda cell: cell != 2080)
    full_timeslice_cube = full_timeslice_cube.extract(exclude_2080_constraint)

    print("Joined")       
    if not os.path.exists(f'../../../../datadir/Gauge_Timeslices/2060_2081/{em}/'):
        os.makedirs(f'../../../../datadir/Gauge_Timeslices/2060_2081/{em}/')
    iris.save(full_timeslice_cube, f'../../../../datadir/Gauge_Timeslices/2060_2081/{em}/gauge{gauge_num}_farFuture.nc')
    print("Saved")