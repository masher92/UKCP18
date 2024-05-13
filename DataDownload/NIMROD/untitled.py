def find_all_max_locations_in_timeslices(cube):
    """
    Finds the maximum value in each timeslice and returns all its locations.
    
    Args:
        cube (iris.cube.Cube): The Iris cube to analyze.

    Returns:
        list: Each element is a tuple containing the timeslice index, maximum value, 
              and a list of coordinates where the maximum occurs.
    """
    results = []
    time_dimension = 0  # Adjust if your time dimension is not the first dimension
    
    # Iterate over each timeslice
    for i, timeslice in enumerate(cube.slices_over(time_dimension)):
        max_value = np.max(timeslice.data)
        # Find all positions where the timeslice data equals the maximum value
        positions = np.argwhere(timeslice.data == max_value)
        
        # Get the corresponding latitude and longitude for each position
        max_locations = []
        for pos in positions:
            latitude = timeslice.coord('projection_y_coordinate').points[pos[0]]
            longitude = timeslice.coord('projection_x_coordinate').points[pos[1]]
            max_locations.append((latitude, longitude))
        
        # Store the results
        results.append((i, max_value, max_locations))
    
    return results


import iris
import glob
import iris.plot as iplt
import iris.quickplot as qplt
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)
simplefilter(action='ignore', category=UserWarning)

# Create path to files containing functions
root_fp = "/nfs/a319/gy17m2a/PhD/"
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *
gb_gdf = create_gb_outline({'init' :'epsg:3857'})

# Define the directory and create a sorted list of file paths
year = 2012
radardir = f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/'
file_list = glob.glob(radardir + "*.nc")
sorted_list = sorted(file_list)

# Load the cubes
cubes = iris.load(sorted_list[:30])

# Concatenate into a single cube
monthly_cube = cubes.concatenate_cube()

print("im here")

import iris
import numpy as np
import dask.array as da

# Step 1: Extract data
projection_y_coord = monthly_cube.coord('projection_y_coordinate')
projection_x_coord = monthly_cube.coord('projection_x_coordinate')
data_values = monthly_cube.data

# Step 2: Thresholding (with Dask for parallel processing)
data_values_dask = da.from_array(data_values, chunks='auto')
threshold_count = da.count_nonzero(data_values_dask > 10, axis=0)

# Step 3: Create new cube
new_cube = iris.cube.Cube(threshold_count.compute(),
                          long_name='Count of Values Exceeding 10',
                          dim_coords_and_dims=[(projection_y_coord, 0),
                                               (projection_x_coord, 1)])
                                               
iris.save(new_cube, 'new.nc')