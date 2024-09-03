import numpy as np
import matplotlib.pyplot as plt
import pickle
import os
import pandas as pd
import re
from datetime import datetime
import sys 

quintile_mapping = {1: 'F2', 2: 'F1', 3: 'C', 4: 'B1', 5: 'B2'}

from Create_Profiles_Functions import *

gauge_nums = range(0,1294)
em =sys.argv[1]
time_period=sys.argv[2]

def create_dataframe_row(this_event):
    # Trim the event and remove problematic events
    trimmed_event = remove_leading_and_trailing_zeroes(this_event)
    real_trimmed_event, problem_events = remove_events_with_problems(trimmed_event, verbose=False)
    
    if real_trimmed_event is None:
        return {
        'precip':None,
        'times': None,
        "season" : get_season(trimmed_event['times'][0]),
        'duration':None,
        "year":extract_year(trimmed_event),
        'Volume': None,
    }
    
    # Return only the relevant data in a dictionary
    return {
        'precip': real_trimmed_event['precipitation (mm)'].values,
        'times': trimmed_event['times'].values,
        "season" : get_season(trimmed_event['times'][0]),
        'duration':len(real_trimmed_event) / 2,
        "year":extract_year(trimmed_event),
        'Volume': sum(real_trimmed_event['precipitation (mm)'].values),
    }

# Initialize an empty list to collect rows
rows = []

for em in [em]:
    for gauge_num in gauge_nums:
        if gauge_num not in [444, 827, 888]:
            if gauge_num % 100 == 0:
                print(f"Processing gauge {gauge_num}")
            
            base_fp = f"/nfs/a161/gy17m2a/PhD/ProcessedData/"
            if em == 'nimrod':
                indy_events_fp = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/NIMROD_30mins/2km_filtered_100/{gauge_num}/WholeYear/"
                profiles_fp = f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/NIMROD_30mins/WholeYear/"
            else:
                indy_events_fp = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/UKCP18_30mins/{time_period}/{em}/{gauge_num}/WholeYear/"
                profiles_fp = f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/UKCP18_30mins/{time_period}/{em}/"
            
            if not os.path.isdir(profiles_fp):
                os.makedirs(profiles_fp)
            
            files = [f for f in os.listdir(indy_events_fp) if f.endswith('.csv')]
            files = np.sort(files)

            for file in files:
                fp = indy_events_fp +  f"{file}"
                if '2080' in fp:
                    continue

                this_event = read_event(gauge_num, fp)

                # Create the row data with just 'precip' and 'times'
                row_data = create_dataframe_row(this_event)
                
                # Only append rows that are not None
                if row_data is not None:
                    rows.append(row_data)

# Create DataFrame from collected rows
df = pd.DataFrame(rows)

with open(profiles_fp + "df.pkl", 'wb') as file:
    pickle.dump(df, file)
    
# Create version without nulls    
df_withoutnulls = df[df['precip'].notnull()].copy()    

# Add quintile cats
df_withoutnulls['max_quintile_molly'] = df_withoutnulls['precip'].apply(find_max_quintile)
df_withoutnulls['max_quintile_steef'] = df_withoutnulls['precip'].apply(analyse_event)
df_withoutnulls['max_quintile_raw_rain'] = df_withoutnulls['precip'].apply(lambda x: find_part_with_most_rain(x, 5))
df_withoutnulls[['max_quintile_steef', 'irain_profile_12_Steef']] = df_withoutnulls['precip'].apply(lambda x: pd.Series(analyse_event(x)))

# Add loading cats
df_withoutnulls['Loading_profile_raw_rain'] = df_withoutnulls['max_quintile_raw_rain'].map(quintile_mapping)
df_withoutnulls['Loading_profile_molly'] =df_withoutnulls['max_quintile_molly'].map(quintile_mapping)
df_withoutnulls['Loading_profile_steef'] =df_withoutnulls['max_quintile_steef'].map(quintile_mapping)

### Add profiles
df_withoutnulls['irain_profile_12'] = df_withoutnulls['precip'].apply(lambda x: create_irain_profile(x, 12))

# Save to pickle
with open(profiles_fp + "df_withoutnulls.pkl", 'wb') as file:
    pickle.dump(df_withoutnulls, file)
