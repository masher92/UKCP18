import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
warnings.filterwarnings("ignore", category =UserWarning,)

import gc
import pickle
from collections import OrderedDict
from pyproj import Transformer
import numpy as np
import pandas as pd
import iris
import glob
import sys
import os
import cartopy.crs as ccrs
import itertools
from scipy import spatial
import numpy.ma as ma
import tilemapbase
from math import cos, radians
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from pyproj import Proj, transform
import time
import iris.plot as iplt
import dask.array as da

sys.path.insert(1,'../')
from Identify_Events_Functions import *
from Prepare_Data_Functions import *

def find_position_obs_new(one_dim_cube, gauge_df, plot=True):

    transformer = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)

    rain_gauge_lat = gauge_df['Lat']
    rain_gauge_lon = gauge_df['Lon']

    # Use the transformer to convert longitude and latitude to British National Grid coordinates
    rain_gauge_lon_bng, rain_gauge_lat_bng = transformer.transform(rain_gauge_lon, rain_gauge_lat)

    # Create as a list
    rain_gauge_point = [('grid_latitude', rain_gauge_lat_bng), ('grid_longitude', rain_gauge_lon_bng)]    
    
    # Get the coordinates from the cube
    x_coords = one_dim_cube.coord('projection_x_coordinate').points  # X grid points
    y_coords = one_dim_cube.coord('projection_y_coordinate').points  # Y grid points

    # Find the nearest grid cell index
    x_index = np.argmin(np.abs(x_coords - rain_gauge_lon_bng))  # Index of closest x
    y_index = np.argmin(np.abs(y_coords - rain_gauge_lat_bng))  # Index of closest y

    # Extract the data for the grid cell
    grid_cell_data = one_dim_cube.data[:, y_index, x_index]

    # print("Extracted data for the grid cell:", grid_cell_data)
    
    # Find the nearest grid cell index
    x_index = np.argmin(np.abs(x_coords - rain_gauge_lon_bng))
    y_index = np.argmin(np.abs(y_coords - rain_gauge_lat_bng))
    
    if plot ==True:
        # Create a new cube with the same shape as the original
        highlight_cube = one_dim_cube.copy()
        highlight_cube.data[:] = 0  # Set all data values to 0

        # Set the chosen cell to 1
        highlight_cube.data[:, y_index, x_index] = 1  # Assuming time is the first dimension

        # Plot with iplt.contourf
        plt.figure(figsize=(10, 8))
        iplt.pcolormesh(highlight_cube[0])  # Plot the first time slice
        plt.gca().coastlines()

        zoom_padding = 20000  # Adjust this value to increase/decrease zoom
        plt.xlim(rain_gauge_lon_bng - zoom_padding, rain_gauge_lon_bng + zoom_padding)
        plt.ylim(rain_gauge_lat_bng - zoom_padding, rain_gauge_lat_bng + zoom_padding)

        plt.scatter(rain_gauge_lon_bng, rain_gauge_lat_bng, color='red', marker='*', s=100, label='Rain gauge location')
        plt.legend()
        plt.title('Highlight Grid Cell Check')
        plt.xlabel('Projection X Coordinate (m)')
        plt.ylabel('Projection Y Coordinate (m)')
        plt.show()    
    
    return y_index, x_index
    
def find_gauge_Tb0_and_location_in_grid_new(tbo_vals, gauge_num, sample_cube):
    gauge1 = tbo_vals.iloc[gauge_num]
    Tb0 = int(gauge1['Critical_interarrival_time'])
    y_index, x_index = find_position_obs_new(sample_cube, gauge1,plot=False)
    return Tb0, y_index, x_index


def load_files_to_cubelist(filenames_pattern):
    filenames = [filename for filename in glob.glob(filenames_pattern) if '.nc' in filename]

    ## Load in data    
    cubes = iris.load(filenames, in_jja)
    cubes = iris.cube.CubeList([cube for cube in cubes if has_named_dimension_coordinates(cube)])
    return cubes


pd.set_option('display.float_format', '{:.3f}'.format)

# Read command-line argument for emission scenario
em = sys.argv[1]
yrs_range = '2002_2020'

in_jja = iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

# Load Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')

# Lazy load data from files
general_filename = f'/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng_masked/{em}/2002_2020/*'
cubes = load_files_to_cubelist(general_filename)

# Remove unnecessary metadata to avoid Iris issues
for cube in cubes:
    for attr in ['creation_date', 'tracking_id', 'history', 'Conventions']:
        cube.attributes.pop(attr, None)

# ### Concatenate cubes into one
em_cube = cubes.concatenate_cube()    
print("Cube shape:", em_cube.shape)

# Sample a small part to find gauge indices
sample_cube = em_cube[1:2, :, :]

# Find gauge indices efficiently
print("Finding gauge indices...")
gauge_nums = range(0, 1294)
gauge_indices = [
    (gauge_num, y_index, x_index)
    for gauge_num in gauge_nums
    if gauge_num not in [423, 444, 827, 888]
    for Tb0, y_index, x_index in [find_gauge_Tb0_and_location_in_grid_new(tbo_vals, gauge_num, sample_cube)]
]

# Process and extract data efficiently
print("Extracting data...")
all_data = []

import time
start_time = time.time()
for gauge_num, y_index, x_index in gauge_indices:
    print(f"Processing gauge {gauge_num}...")
    
    # Lazy loading of the cube slice
    one_location_cube = em_cube[:, y_index, x_index]
    
    # Convert to NumPy array lazily
    compressed = one_location_cube.core_data().flatten()  # Lazy evaluation
    
    # Filter and store only wet values (>= 0.1)
    wet_vals = compressed[compressed >= 0.1].astype(np.float32)
    all_data.append(wet_vals)

import time
start_time=time.time()
all_data = da.concatenate(all_data).compute()
end_time=time.time()
print(f"{round((end_time-start_time)/60,1)} minutes")
print(len(all_data.data))

# Save the final NumPy array
output_path = f'/nfs/a319/gy17m2a/PhD/ProcessedData/PDF_Plotting/UKCP18_hourly/{em}_jja_gaugelocs_2km.npy'
np.save(output_path, all_data.data)     