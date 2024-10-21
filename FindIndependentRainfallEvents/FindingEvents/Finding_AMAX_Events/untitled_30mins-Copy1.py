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

sys.path.insert(1,'../')
from Identify_Events_Functions import *
from Prepare_Data_Functions import *

pd.set_option('display.float_format', '{:.3f}'.format)
warnings.filterwarnings("ignore", category=UserWarning)

# yrs_range= sys.argv[4]
# em = sys.argv[1]
# gauge_num = int(sys.argv[3])
# yr = int(sys.argv[2])
# timeperiod = sys.argv[5]
# print(em)


yrs_range= '2060_2081'
em = "bb195"
timeperiod = 'Future'
print(em)

if timeperiod == 'Future':
    sample_yr=2066
elif timeperiod == 'Present':
    sample_yr=2006

# Get Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Read in a sample cube for finding the location of gauge in grid
sample_cube = iris.load(f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/bng_{em}a.pr{sample_yr}01.nc')[0][1,:,:]


for yr in range(2061,2080):

    ######################################################
    ### Get all the data for one year, into one cube
    # (if it already exists in a pickle file, then load it from there)
    ######################################################
    general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/bng_{em}a.pr{yr}*'
    pickle_file_filepath = f"/nfs/a319/gy17m2a/PhD/datadir/cache/UKCP18_30mins_{em}/WholeYear/cube_{yr}.pkl"
    print(pickle_file_filepath)

    if os.path.exists(pickle_file_filepath):
        print("Pickle file exists, so loading that")
        full_year_cube = load_cube_from_picklefile(pickle_file_filepath)
    else:
        print("Pickle file doesnt exist, so creating and then saving that")

        ### Get the data filepaths
        print(f"Loading data for year {yr}")

        # Create cube list
        cubes = load_files_to_cubelist(yr, general_filename)

        # Join them into one (with error handling to deal with times which are wrong)
        cubes = load_files_to_cubelist(yr, general_filename)

        cubes = clean_cubes_v2(cubes)

        full_year_cube = cubes.concatenate_cube()     

        save_cube_as_pickle_file(full_year_cube, pickle_file_filepath)
# 750,1000        
    for gauge_num in range(500,750):
        if gauge_num not in [444, 827, 888]:
            # Find location
            Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(tbo_vals, gauge_num, sample_cube)

            # Function to process each gauge
            print(f"gauge num is {gauge_num}")             

            base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/UKCP18_30mins/{timeperiod}/{em}/{gauge_num}/WholeYear"
            # Create the directory if it doesnt exist
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)

            print(full_year_cube.shape)      
            ######################################################
            ## Check if any files are missing, across the 3 filtering options
            # If there are: code will continue to run
            # If not: code will move to next gauge
            ######################################################                
            # Create a flag to record whether we are missing any of the files we need
            missing_files = False

            # Check if we are missing any of the files, and if so, change the flag to True
            if not any(os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv") for duration in [0.5, 1, 2, 3, 6, 12, 24]):
                missing_files = True
            print(missing_files)
            # If we are missing some files then get the data for the grid cell, 
            if missing_files:

                # Extract data for the specified indices
                start= time.time()
                one_location_cube = full_year_cube[:, idx_2d[0], idx_2d[1]]
                data = one_location_cube.data
                end=time.time()
                print(f"Time to load data is {round(end-start,2)} seconds")

                ##### Filter cube according to different options
                # Convert to dataframe
                df = pd.DataFrame(data, columns=['precipitation (mm/hr)'])
                df['times'] = one_location_cube.coord('time').units.num2date(one_location_cube.coord('time').points)
                df['precipitation (mm)'] = df['precipitation (mm/hr)'] / 2   

                # Search dataframe for events corresponding to durations
                for duration in [0.5, 1, 2, 3, 6, 12, 24]:

                    filename =  f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv"
                    if not os.path.exists(filename):
                        print(f"Finding the AMAX for {duration}hr events for gauge {gauge_num} in year {yr}")
                        # Find events
                        events_v2 = search_for_valid_events(df, duration=duration, Tb0=Tb0)

                        # Save events to CSV
                        for num, event in enumerate(events_v2):
                            if len(event) > 1:
                                    event.to_csv(f"{base_dir}/{duration}hrs_{yr}_v2_part{num}.csv")
                                    print(f"{base_dir}/{duration}hrs_{yr}_v2_part{num}.csv")
                                    if event['precipitation (mm/hr)'].isna().any():
                                        print("NANs in this event")
                    else:
                        print(f"already exists{filename}")
                        pass   
            else:
                print("Files all already exist")
