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
from netCDF4 import Dataset
from Identify_Events_Functions import *
import concurrent.futures  # For parallel processing

pd.set_option('display.float_format', '{:.3f}'.format)
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

deleted_cubes = 0

# Custom limited-size cache
class LimitedSizeDict(OrderedDict):
    def __init__(self, *args, max_size=100, **kwargs):
        self.max_size = max_size
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        if len(self) >= self.max_size:
            self.popitem(last=False)
        OrderedDict.__setitem__(self, key, value)

        
def has_named_dimension_coordinates(cube):
    print("Inspecting cube:", cube)
    
    # Check if any dimension coordinate has a name
    named_dim_coords = [coord for coord in cube.dim_coords if coord.standard_name or coord.long_name]
    
    # Print information about dimension coordinates
    for coord in cube.dim_coords:
        print(f"Coord standard_name: {coord.standard_name}, long_name: {coord.long_name}")
    
    # Return True if any dimension coordinate has a name
    return bool(named_dim_coords)        
        
def concatenate_with_error_handling(cube_list):
    # This error is usually caused by the first of the times being on a different day,
    # so just delete that day
    problematic_cube_index = []
    start = 0
    for i, cube in enumerate(cube_list):
        try:
            concatenated_cube = cube_list[start:i+1].concatenate_cube()
        except Exception as e:
            print(f"Error concatenating cube {i}: {str(e)}")
            problematic_cube_index.append(i)
            start = i

    for index in problematic_cube_index:
        cube_test = cube_list[index]
        cube_test = cube_test[1:,:,:]
        cube_list[index] = cube_test

    concatenated_cube = cube_list.concatenate_cube() 
    return concatenated_cube

def create_concated_cube(year, filenames_pattern, deleted_cubes):
    
    ### Get the data filepaths
    print(f"Loading data for year {year}")
    filenames = [filename for filename in glob.glob(filenames_pattern) if '.nc' in filename]
    if not filenames:
        raise FileNotFoundError(f"No files found for the year {year} with pattern {filenames_pattern}")

    ## Load in data    
    cubes = iris.load(filenames)
    cubes = iris.cube.CubeList([cube for cube in cubes if has_named_dimension_coordinates(cube)])
    
    ##### Clean cube, pre-joining
    ## try to fix attributes to all be the same
    for cube in cubes:
        cube.rename(cubes[0].name())
    iris.util.equalise_attributes(cubes) 
    ## Including coordinate metadata
    time_metadata = cubes[0].coord('time').metadata
    for cube_num in range(0,len(cubes)):
        cube=cubes[cube_num]
        if len(cube.shape)<3:
            cube = add_time_coord(cube)
        try:
            cube.remove_coord("forecast_period")
        except:
            pass
        try:
            cube.remove_coord("forecast_reference_time")
        except:
            pass
        cube.coord('time').metadata = time_metadata
        cubes[cube_num]=cube

    ### Do the joining into one cube
    try:
        full_day_cube = cubes.concatenate_cube()
    except:
        print("Error handling concatenation")
        full_day_cube = concatenate_with_error_handling(cubes)
    
    return full_day_cube

def save_cube_as_pickle_file(cube, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(cube, f)

def load_cube_from_picklefile(filepath):
    with open(filepath, 'rb') as f:
        return pickle.load(f)

def find_gauge_Tb0_and_location_in_grid(gauge_num, sample_cube):
    gauge1 = tbo_vals.iloc[gauge_num]
    Tb0 = int(gauge1['Critical_interarrival_time'])
    closest_point, idx_2d = find_position_obs(sample_cube, gauge1['Lat'], gauge1['Lon'], plot_radius=10, plot=False)
    return Tb0, idx_2d

def find_amax_indy_events_v2(df, duration, Tb0):
    rainfall_cores = find_rainfall_core(df, duration=duration, Tb0=Tb0)
    rainfall_events_expanded = []

    for rainfall_core in rainfall_cores:
        rainfall_core_after_search1 = search1(df, rainfall_core)
        rainfall_core_after_search2 = search2(df, rainfall_core_after_search1)
        rainfall_core_after_search3 = search3(df, rainfall_core_after_search2, Tb0=Tb0)
        if len(rainfall_core_after_search3[rainfall_core_after_search3['precipitation (mm/hr)'] > 0.1]) > 0:
            rainfall_events_expanded.append(rainfall_core_after_search3)
    
    return rainfall_events_expanded

# Get Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')

# Dataset paths and patterns
dataset_name = 'unfiltered'
dataset_path_pattern = '/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/*'


gauge_nums=range(0,1263)
for yr in [2019]:
    print(f"Processing year {yr}")
    dict_of_cubes = {'unfiltered': LimitedSizeDict(max_size=10)}

    # Read in a sample cube for finding the location of gauge in grid
    sample_cube = iris.load(f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{yr}/metoffice-c-band-rain-radar_uk_{yr}0602.nc')[0][1,:,:]

    # Check if files are missing for this year across all datasets
    general_filename = dataset_path_pattern.format(year=yr)
    pickle_file_filepath = f"/nfs/a319/gy17m2a/PhD/datadir/cache/nimrod_5mins/WholeYear/cube_{yr}.pkl"          

    if yr not in dict_of_cubes[dataset_name]:
        print("File isn't already stored in the dictionary")
        if os.path.exists(pickle_file_filepath):
            print("Pickle file exists, so loading that")
            cube = load_cube_from_picklefile(pickle_file_filepath)
        else:
            print("Pickle file doesnt exist, so creating and then saving that")
            cube = create_concated_cube(yr, general_filename, deleted_cubes)
            dict_of_cubes['unfiltered'][yr] = cube 
            save_cube_as_pickle_file(cube, pickle_file_filepath)
    else:
        print("File is already stored in the dictionary: using that")
        cube = dict_of_cubes['unfiltered'][yr]

    # Function to process each gauge
    for gauge_num in gauge_nums:
        if not gauge_num in [423, 444, 827, 888]:
                print(f"gauge num is {gauge_num}")

                missing_files = False
                base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_5mins/NIMROD_1km_{dataset_name}/{gauge_num}/WholeYear"
                if not any(os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv") for duration in [0.5, 1, 2, 3, 6, 12, 24]):
                    missing_files = True

                if missing_files:
                    # Ensure directories for unfiltered, filtered_100, and filtered_300 exist
                    base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_5mins/NIMROD_1km_{dataset_name}/{gauge_num}/WholeYear"
                    if not os.path.isdir(base_dir):
                        os.makedirs(base_dir)

                    try:
                        # Find the Tb0 and index of this gauge
                        Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(gauge_num, sample_cube)

                        # Extract data for the specified indices
                        data = cube[:, idx_2d[0], idx_2d[1]].data

                        # Create a DataFrame from the data
                        df = pd.DataFrame({
                            'times': cube[:, idx_2d[0], idx_2d[1]].coord('time').units.num2date(cube.coord('time').points),
                            'precipitation (mm/hr)': data,
                            'precipitation (mm)': data / 2})

                        #############################################
                        # Fill in missing values
                        #############################################
                        df['times'] = pd.to_datetime([t.isoformat() for t in df['times']])

                        # Determine the frequency
                        freq = '5T'  # 30 minutes

                        # Create a full date range
                        full_time_range = pd.date_range(start=df['times'].min(), end=df['times'].max(), freq=freq)

                        # Set 'time' as index and reindex to the full range
                        df.set_index('times', inplace=True)
                        df = df.reindex(full_time_range)

                        # Reset index and rename it back to 'time'
                        df.reset_index(inplace=True)
                        df.rename(columns={'index': 'times'}, inplace=True)

                        # Calculate time difference in minutes
                        df['minutes_since_last'] = df['times'].diff().dt.total_seconds() / 60
                        df['minutes_since_last'] = df['minutes_since_last'].fillna(0)

                        # Loop through durations
                        for duration in [0.5, 1, 2, 3, 6, 12, 24]:
                            base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_5mins/NIMROD_1km_{dataset_name}/{gauge_num}/WholeYear/"
                            if not os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv"):
                                print(f"Finding the AMAX for {duration}hr events for gauge {gauge_num} in year {yr} for {dataset_name}")

                                # Find events
                                events_v2 = find_amax_indy_events_v2(df, duration=duration, Tb0=Tb0)

                                # Save events to CSV
                                for num, event in enumerate(events_v2):
                                    if len(event) > 1:
                                            event.to_csv(f"{base_dir}/{duration}hrs_{yr}_v2_part{num}.csv")
                    except:
                        print("Failed for some reason")
                        pass
