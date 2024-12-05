import os
import numpy as np
import re
import pickle
import sys

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from ProcessEventsFunctions import *
sys.path.insert(1, 'Old')
from Steef_Functions import *

home_dir = '/nfs/a319/gy17m2a/PhD/'
home_dir2 = '/nfs/a161/gy17m2a/PhD/'

quintile_mapping = {1: 'F2', 2: 'F1', 3: 'C', 4: 'B1', 5: 'B2'}
quintile_mapping_thirds = {1: 'F', 2: 'C', 3: 'B'}

tbo_vals = pd.read_csv(home_dir + 'datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Check if the points are within the areas
tbo_vals = check_for_gauge_in_areas(tbo_vals, home_dir, ['NW', 'NE', 'ME', 'SE', 'SW'])
tbo_vals.loc[tbo_vals['within_area'] == 'NW, C', 'within_area'] = 'NW'
tbo_vals.loc[tbo_vals['within_area'] == 'ME, SE', 'within_area'] = 'ME'

home_dir = home_dir2
tb0_vals = tbo_vals

events_dict = {}
event_props_ls = []
event_profiles_dict = {}

for gauge_num in range(0, 1294):
    if gauge_num not in [444, 827, 888]:
        if gauge_num % 100 == 0:
            print(f"Processing gauge {gauge_num}")
        indy_events_fp = home_dir + f"ProcessedData/IndependentEvents/NIMROD_30mins/NIMROD_2.2km_filtered_100/{gauge_num}/WholeYear/"
        files = [f for f in os.listdir(indy_events_fp) if f.endswith('.csv')]
        files = np.sort(files)

        for event_num, file in enumerate(files):
            fp = indy_events_fp + f"{file}"
            if '2080' in fp:
                continue

            # Get event
            this_event = read_event(gauge_num, fp)

            # Get times and precipitation values
            event_times = this_event['times']
            event_precip = this_event['precipitation (mm)']

            # Apply the function to adjust the dates in the 'times' column
            event_times_fixed = event_times.apply(adjust_feb_dates)

            # Create the DataFrame with corrected times
            event_df = pd.DataFrame({'precipitation (mm)': event_precip, 'times': event_times_fixed})
            event_df = remove_leading_and_trailing_zeroes(event_df, indy_events_fp + f"{file}")

            # Create characteristics dictionary
            event_props = create_event_characteristics_dict(event_df)

            # Add the duration
            event_props['dur_for_which_this_is_amax'] = get_dur_for_which_this_is_amax(fp)
            # Add gauge number and ensemble member
            event_props['gauge_num'] = gauge_num
            event_props['area'] = tb0_vals.iloc[gauge_num]['within_area']
            event_props['em'] = 'nimrod'
            event_props['filename'] = file

            ##########################################
            # Specify the keys you want to check
            keys_to_check = ['duration', 'year', 'gauge_num', 'month', 'Volume', 'max_intensity']

            # Extract the values for the specified keys from dict_to_check
            values_to_check = tuple(event_props[key] for key in keys_to_check)

            # Initialize a variable to store the found dictionary
            matched_dict = None

            # Check if a matching dictionary exists in the list based on the specified keys
            for index, d in enumerate(event_props_ls):
                if tuple(d[key] for key in keys_to_check) == values_to_check:
                    matched_dict = d  # Store the matching dictionary
                    break  # Exit the loop since we found a match

            if matched_dict:
                # print("A matching dictionary found:", matched_dict, event_props)

                new_value = event_props['dur_for_which_this_is_amax']
                existing_value = matched_dict.get('dur_for_which_this_is_amax', '')
                # Create or update the value as a list
                if isinstance(existing_value, list):
                    existing_value.append(new_value)
                else:
                    existing_value = [existing_value, new_value]  # Convert existing string to list and add 'yes'
                matched_dict['dur_for_which_this_is_amax'] = existing_value

                event_props_ls[index]= matched_dict

            else:
                # print("No matching dictionary found in the list.")
                events_dict[f"nimrod, {gauge_num}, {event_num}"] = event_df
                event_props_ls.append(event_props)
                event_profiles_dict[f"nimrod, {gauge_num}, {event_num}"] = create_profiles_dict(event_df)
                
save_dir = '/nfs/a319/gy17m2a/PhD/'             
                
with open(save_dir + f"ProcessedData/AMAX_Events/NIMROD_30mins/events_dict.pickle", 'wb') as handle:
    pickle.dump(events_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(save_dir + f"ProcessedData/AMAX_Events/NIMROD_30mins/event_profiles_dict.pickle", 'wb') as handle:
    pickle.dump(event_profiles_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

with open(save_dir + f"ProcessedData/AMAX_Events/NIMROD_30mins/event_props_dict.pickle", 'wb') as handle:
    pickle.dump(event_props_ls, handle, protocol=pickle.HIGHEST_PROTOCOL)                   