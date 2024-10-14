import pandas as pd
import iris
import glob
import sys
import os
import time
import warnings
import pickle
from collections import OrderedDict

from Identify_Events_Functions import *
from Prepare_Data_Functions import *

pd.set_option('display.float_format', '{:.3f}'.format)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning, message=".*'+init=<authority>:<code>' syntax is deprecated.*")

######################################################
### Define data for finding the indepedent events at each gauge
######################################################
yr = sys.argv[1]

filtering_name = 'filtered_100'

# Get Tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Read in a sample cube for finding the location of gauge in grid
sample_cube = iris.load(f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/NIMROD_regridded_2.2km/{filtering_name}/AreaWeighted/2012/rg_metoffice-c-band-rain-radar_uk_20120602_30mins.nc')[0][1,:,:]

######################################################
### Get all the 5 minute data for one year, into one cube
# (if it already exists in a pickle file, then load it from there)
######################################################
general_filename = f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/NIMROD_regridded_2.2km/{filtering_name}/AreaWeighted/{yr}/*'.format(year=yr)
pickle_file_filepath = f"/nfs/a319/gy17m2a/PhD/datadir/cache/nimrod_30mins_2.2km/{filtering_name}/WholeYear/cube_{yr}.pkl"

if os.path.exists(pickle_file_filepath):
    print("Pickle file exists, so loading that")
    full_year_cube = load_cube_from_picklefile(pickle_file_filepath)
else:
    print("Pickle file doesnt exist, so creating and then saving that")
    
    ### Get the data filepaths
    print(f"Loading data for year {yr}")
    
    # Create cube list
    cubes = load_files_to_cubelist(yr, general_filename)
    
    # Clean cubes of things which are problematic for concatenation
    cubes = clean_cubes(cubes)
    
    # Join them into one (with error handling to deal with times which are wrong)
    try:
        full_year_cube = cubes.concatenate_cube()
        print("Concatenation successful!")
    except Exception as e:
        print(f"Initial concatenation failed: {str(e)}")

        # If initial concatenation fails, remove problematic cubes and try again
        try:
            full_year_cube = remove_problematic_cubes(cubes)
            print("Concatenation successful after removing problematic cubes!")
        except RuntimeError as e:
            print(f"Concatenation failed after removing problematic cubes: {str(e)}")               
    save_cube_as_pickle_file(full_year_cube, pickle_file_filepath)
    
######################################################
# Find events at each gauge
######################################################
failed_gauges = []
gauge_nums = range(0,1293)
# Function to process each gauge
for gauge_num in gauge_nums:
    if not gauge_num in [423, 444, 827, 888]:
            print(f"gauge num is {gauge_num}")
            
            ######################################################
            ## Check if any files are missing, across the 3 filtering options
            # If there are: code will continue to run
            # If not: code will move to next gauge
            ######################################################
            # Create a flag to record whether we are missing any of the files we need
            missing_files = False
            # Define directory filepath which will store results
            base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_30mins/NIMROD_2.2km_{filtering_name}/{gauge_num}/WholeYear"
            # Create the directory if it doesnt exist
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)
            # Check if we are missing any of the files, and if so, change the flag to True
            if not any(os.path.exists(f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv") for duration in [0.5, 1, 2, 3, 6, 12, 24]):
                missing_files = True
                
            # If we are missing some files then get the data for the grid cell, 
            if missing_files:
                
                # Find the Tb0 and index of this gauge
                Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(tbo_vals, gauge_num, sample_cube)
                
                # Extract data for the specified indices
                start= time.time()
                one_location_cube = full_year_cube[:, idx_2d[0], idx_2d[1]]
                data = one_location_cube.data
                end=time.time()
                print(f"Time to load data is {round(end-start,2)} seconds")
                
                ##### Filter cube according to different options
                # Convert to dataframe
                df = create_df_with_gaps_filled_in(one_location_cube, data, time_resolution = 30)
                # Search dataframe for events corresponding to durations
                for duration in [0.5, 1, 2, 3, 6, 12, 24]:
                    base_dir = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_30mins/NIMROD_2.2km_{filtering_name}/{gauge_num}/WholeYear"

                    filename =  f"{base_dir}/{duration}hrs_{yr}_v2_part0.csv"
                    if not os.path.exists(filename):
                        print(f"Finding the AMAX for {duration}hr events for gauge {gauge_num} in year {yr} for {filtering_name}")
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

print(f"failed gauges are: {failed_gauges}")