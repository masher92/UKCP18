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

sys.path.insert(1, '../FindingEvents/Finding_AMAX_Events/Corrections')
from DeleteDuplicatesFunctions import *

home_dir = '/nfs/a319/gy17m2a/PhD/'
home_dir2 = '/nfs/a161/gy17m2a/PhD/'

quintile_mapping = {1: 'F2', 2: 'F1', 3: 'C', 4: 'B1', 5: 'B2'}
quintile_mapping_thirds = {1: 'F', 2: 'C', 3: 'B'}

tbo_vals = pd.read_csv(home_dir + 'datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
# Check if the points are within the areas
tbo_vals = check_for_gauge_in_areas(tbo_vals, home_dir, ['NW', 'NE', 'ME', 'SE', 'SW'])
tbo_vals.loc[tbo_vals['within_area'] == 'NW, C', 'within_area'] = 'NW'
tbo_vals.loc[tbo_vals['within_area'] == 'ME, SE', 'within_area'] = 'ME'

em=sys.argv[1]
time_period=sys.argv[2]
ems_future = [em]

### check if there are enough files
for gauge_num in range(0,1294):
    if gauge_num not in [444, 827, 888]:
        directory_path = f"/nfs/a161/gy17m2a/PhD/ProcessedData/IndependentEvents/UKCP18_30mins/{em}/{gauge_num}/WholeYear/"
        file_count = len([
            name for name in os.listdir(directory_path)
            if os.path.isfile(os.path.join(directory_path, name)) and 'part0' in name])
        if file_count == 133:
            pass
        else:
            print(f"Gauge number {gauge_num}: Not as expected, {file_count}")

print(f"Em{em}")
### Process
events_dict_future, event_props_dict_future, event_profiles_dict_future = process_events_alltogether(home_dir2, time_period, ems_future, tbo_vals, home_dir)
    
    

