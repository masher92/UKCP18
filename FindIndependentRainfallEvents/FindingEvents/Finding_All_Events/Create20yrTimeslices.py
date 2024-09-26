import pandas as pd
import iris
import sys

from Identify_Events_Functions import *
from Prepare_Data_Functions import *

yrs_range= '2060_2081'
em = 'bb198'

# Get Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Read in a sample cube for finding the location of gauge in grid
sample_cube = iris.load(f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/bng_{em}a.pr206101.nc')[0][1,:,:]

gauge_num=int(sys.argv[1])
print(gauge_num)
Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(tbo_vals, gauge_num, sample_cube)

general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/bng_{em}a.pr*'
# Year isnt actually doing anything here 
cubes = load_files_to_cubelist(2061, general_filename)
print("Loaded data")
# Assuming your CubeList is called `cube_list`
filtered_cubes = iris.cube.CubeList()

# Define the coordinates to filter by
y_idx = idx_2d[0]
x_idx = idx_2d[1]

# Loop through each cube in the CubeList and filter
for cube in cubes:
    # Extract the data at the specified y_idx and x_idx
    filtered_cube = cube[:, y_idx, x_idx]
    
    # Append the filtered cube to the new CubeList
    filtered_cubes.append(filtered_cube)
    
print("Filtered to location")

# Join them into one (with error handling to deal with times which are wrong)
try:
    full_timeslice_cube = filtered_cubes.concatenate_cube()
    print("Concatenation successful!")
except Exception as e:
    print(f"Initial concatenation failed: {str(e)}")
    
    # If initial concatenation fails, remove problematic cubes and try again
    try:
        print(cube)
        full_timeslice_cube = remove_problematic_cubes(filtered_cubes)
        print("Concatenation successful after removing problematic cubes!")
    except RuntimeError as e:
        print(f"Concatenation failed after removing problematic cubes: {str(e)}")   
        
print("Joined")       
if not os.path.exists(f'../../../datadir/Gauge_Timeslices/2060_2081/{em}/'):
    os.makedirs(f'../../../datadir/Gauge_Timeslices/2060_2081/{em}/')
iris.save(full_timeslice_cube, f'../../../datadir/Gauge_Timeslices/2060_2081/{em}/gauge{gauge_num}_farFuture.nc')
print("Saved")