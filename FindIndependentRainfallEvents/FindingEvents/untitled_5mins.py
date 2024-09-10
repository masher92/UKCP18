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

from Identify_Events_Functions import *
from Prepare_Data_Functions import *

dataset_name = 'filtered_100'
dataset_path_pattern = '/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/*'

pd.set_option('display.float_format', '{:.3f}'.format)
warnings.filterwarnings("ignore", category=UserWarning)

yr = int(sys.argv[1])
gauge_num = int(sys.argv[2])

# Get Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Read in a sample cube for finding the location of gauge in grid
sample_cube = iris.load(f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{yr}/metoffice-c-band-rain-radar_uk_{yr}0602.nc')[0][1,:,:]

######################################################
### Get all the data for one year, into one cube
# (if it already exists in a pickle file, then load it from there)
######################################################
general_filename = dataset_path_pattern.format(year=yr)
pickle_file_filepath = f"/nfs/a319/gy17m2a/PhD/datadir/cache/nimrod_5mins/unfiltered/WholeYear/cube_{yr}.pkl"

full_year_cube = load_cube_from_picklefile(pickle_file_filepath)


# Function to process each gauge
print(f"gauge num is {gauge_num}")             

######################################################
## Check if any files are missing, across the 3 filtering options
# If there are: code will continue to run
# If not: code will move to next gauge
######################################################                
# Create a flag to record whether we are missing any of the files we need
missing_files = False
# Define directory filepath which will store results
base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_5mins/NIMROD_1km_{dataset_name}/{gauge_num}/WholeYear"
# Create the directory if it doesnt exist
if not os.path.isdir(base_dir):
    os.makedirs(base_dir)
# Check if we are missing any of the files, and if so, change the flag to True
if not any(os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv") for duration in [0.5, 1, 2, 3, 6, 12, 24]):
    missing_files = True

# If we are missing some files then get the data for the grid cell, 
if missing_files:
    
    # Find location
    Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(tbo_vals, gauge_num, sample_cube)
    
    # Extract data for the specified indices
    start= time.time()
    one_location_cube = full_year_cube[:, idx_2d[0], idx_2d[1]]
    data = one_location_cube.data
    end=time.time()
    print(f"Time to load data is {round(end-start,2)} seconds")

    ##### Filter cube according to different options
    # Find events with filtered cubes
    filtering_dict = {1000000:'unfiltered', 300:'filtered_300',100:'filtered_100'}
    for filtering_key, dataset_name in filtering_dict.items():
        print(f"running for {dataset_name}")
        # Create cube with filterings applied
        cube = filtered_cube(one_location_cube,  filter_above=filtering_key)
        print("reloading data")
        data = cube.data
        print(f"max value is {np.nanmax(cube.data)}")
        # Convert to dataframe
        df = create_df_with_gaps_filled_in(cube, data, time_resolution = 5)
        # Search dataframe for events corresponding to durations
        for duration in [0.5, 1, 2, 3, 6, 12, 24]:
            base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_5mins/NIMROD_1km_{dataset_name}/{gauge_num}/WholeYear"

            filename =  f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv"
            if not os.path.exists(filename):
                print(f"Finding the AMAX for {duration}hr events for gauge {gauge_num} in year {yr} for {dataset_name}")
                # Find events
                events_v2 = search_for_valid_events(df, duration=duration, Tb0=Tb0)

                # Save events to CSV
                for num, event in enumerate(events_v2):
                    if len(event) > 1:
                            event.to_csv(f"{base_dir}/{duration}hrs_{yr}_v2_part{num}.csv")
                            if event['precipitation (mm/hr)'].isna().any():
                                print("NANs in this event")
            else:
                print(f"already exists{filename}")
                pass   
else:
    print("files all already exist")
