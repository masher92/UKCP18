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

# 'bb198', 'bb192', bb225, bb208 bb222 bb201 bb216 bb211 bb219
ems_future = ['bb198']# 'bb195', 'bb198', 'bb201', 'bb204','bb208' ,'bb211','bb216', 'bb219','bb222','bb225']
ems_present = [ 'bc006']# ,   ']

for em in ems_future:
    just_one_em = [em]
    print(just_one_em)
    # # Now you can call the function for both time periods
#     events_dict_present, event_props_dict_present, event_profiles_dict_present = process_events_alltogether(home_dir2, 'Present',ems_present, tbo_vals, home_dir)
    events_dict_future, event_props_dict_future, event_profiles_dict_future = process_events_alltogether(home_dir2, 'Future', ems_future, tbo_vals, home_dir)

