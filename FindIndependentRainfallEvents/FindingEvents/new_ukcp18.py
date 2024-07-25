import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
warnings.filterwarnings("ignore", category =UserWarning,)

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
import iris.plot as iplt
from math import cos, radians
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import time
from pyproj import Proj, transform
import warnings
import gc
import pickle
from collections import OrderedDict

from Identify_Events_Functions import *

pd.set_option('display.float_format', '{:.3f}'.format)


def load_and_cache_cube(year, cache, filenames_pattern):
    if year in cache:
        print(f"Using cached data for year {year}")
        return cache[year]

    print(f"Loading data for year {year}")
    filenames = [filename for filename in glob.glob(filenames_pattern) if '.nc' in filename]

    if not filenames:
        raise FileNotFoundError(f"No files found for the year {year} with pattern {filenames_pattern}")

    cubes = iris.load(filenames)
    cubes = [cube for cube in cubes if len(cube.shape) != 2]
    cubes = iris.cube.CubeList(cubes)
    for cube in cubes:
        cube.rename(cubes[0].name())
    iris.util.equalise_attributes(cubes) 
    cube = cubes.concatenate_cube()
    cache[year] = cube

    return cube

def save_cube_to_disk(cube, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(cube, f)

def load_cube_from_disk(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def find_gauge_Tb0_and_location_in_grid(gauge_num, sample_cube):
    # Get data just for this gauge
    gauge1 = tbo_vals.iloc[gauge_num]
    # Find the interevent arrival time (Tb0)
    Tb0 = int(gauge1['Critical_interarrival_time'])
    # Find the coordinates of the cell containing this gauge
    closest_point, idx_2d = find_position_obs(sample_cube, gauge1['Lat'], gauge1['Lon'], plot_radius=30, plot=False)
    
    return Tb0, idx_2d

def find_amax_indy_events_v2(df, duration, Tb0):
    rainfall_cores = find_rainfall_core(df, duration=duration, Tb0=Tb0)
    rainfall_events_expanded = []

    for rainfall_core in rainfall_cores:
        rainfall_core_after_search1 = search1(df, rainfall_core)
        rainfall_core_after_search2 = search2(df, rainfall_core_after_search1)
        rainfall_core_after_search3 = search3(df, rainfall_core_after_search2, Tb0=Tb0)
        # If the event is not entirely dry 
        if len(rainfall_core_after_search3[rainfall_core_after_search3['precipitation (mm/hr)'] > 0.1]) > 0:
            rainfall_events_expanded.append(rainfall_core_after_search3)
    
    return rainfall_events_expanded

# Get tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')


# Custom limited-size cache
class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, max_size=100, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem(last=False)
        OrderedDict.__setitem__(self, key, value)

# Initialize a limited-size cache
cube_cache = LimitedSizeDict(max_size=10)   
        
# Loop through years
for gauge_num in range(0, 1300):
    if gauge_num not in [423, 444, 827, 888]:
        print(f"Processing gauge {gauge_num}")

        # Read in a sample cube for finding the location of gauge in grid
        sample_cube = iris.load(f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{em}/2002_2020/bng_{em}a.pr200508*')[0][1,:,:]

        # Find the Tb0 and index of this gauge
        Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(gauge_num, sample_cube)

        # Loop through gauges
        for yr in range(2001, 2020):
            print(f"Processing year {yr}")

            # Check if any files are missing for this year across all datasets
            base_dir = f"../../ProcessedData/IndependentEvents/UKCP18_30mins/{em}/{gauge_num}"
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)
                
            missing_files = False                
            if not any(os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv") for duration in [0.5, 1, 2, 3, 6, 12, 24]):
                missing_files = True
                break

            if missing_files:
                for dataset_name, dataset_path_pattern in datasets.items():
                    print(f"Processing dataset: {dataset_name}")

                    # Load data for this year
                    general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{em}/2002_2020/bng_{em}a.pr{yr}*'
                    cache_filepath = f"/nfs/a319/gy17m2a/PhD/datadir/cache/UKCP18_30mins_{em}/cube_{yr}.pkl"

                    try:
                        if yr not in cube_cache:
                            if os.path.exists(cache_filepath):
                                cube = load_cube_from_disk(cache_filepath)
                            else:
                                cube = load_and_cache_cube(yr, cube_cache, general_filename)
                                save_cube_to_disk(cube, cache_filepath)
                        else:
                            cube = cube_cache[yr]
                    except (EOFError, FileNotFoundError) as e:
                        print(f"Error loading cube for year {yr}: {e}")
                        continue

                    # Extract data for the specified indices
                    data = cube[:, idx_2d[0], idx_2d[1]].data

                    # Create a DataFrame from the data
                    df = pd.DataFrame({
                        'times': cube[:, idx_2d[0], idx_2d[1]].coord('time').units.num2date(cube.coord('time').points),
                        'precipitation (mm/hr)': data,
                        'precipitation (mm)': data / 2})

                    # Loop through durations
                    for duration in [0.5, 1, 2, 3, 6, 12, 24]:
                        base_dir = f"../../ProcessedData/IndependentEvents/UKCP18_30mins/{em}/{gauge_num}"
                        if not os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv"):
                            print(f"Finding the AMAX for {duration}hr events for gauge {gauge_num} in year {yr} for {dataset_name}")

                            # Find events
                            events_v2 = find_amax_indy_events_v2(df, duration=duration, Tb0=Tb0)

                            # Save events to CSV
                            for num, event in enumerate(events_v2):
                                if len(event) > 1:
                                    event.to_csv(f"{base_dir}/{duration}hrs_{yr}_v2_part{num}.csv")
            else:
                print(f"All files already exist for gauge {gauge_num} and year {yr}")

        # Clear the cache at the end of processing each year
        for cache in cube_cache.values():
            cache.clear()

        # Collect garbage to free up memory
        gc.collect()
