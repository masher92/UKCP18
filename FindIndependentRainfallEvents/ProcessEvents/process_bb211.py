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

ems_present = ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc012', 'bc013', 'bc015', 'bc016', 'bc017', 'bc018']
ems_present = ['bc005']

# # Now you can call the function for both time periods
# events_dict_present, event_props_dict_present, event_profiles_dict_present = process_events_alltogether(home_dir2, 'Present',ems_present, tbo_vals, home_dir)
# events_dict_future, event_props_dict_future, event_profiles_dict_future = process_events_alltogether(home_dir2, 'Present', ems_present, tbo_vals, home_dir)


# Now you can callevents_dict_present_nimrod, event_props_dict_present_nimrod, event_profiles_dict_present_nimrod = process_events_alltogether_nimrod(home_dir2, 'Present', tbo_vals)
events_dict_nimrod, event_props_dict_nimrod, event_profiles_dict_nimrod = process_events_alltogether_nimrod(home_dir2, tbo_vals)