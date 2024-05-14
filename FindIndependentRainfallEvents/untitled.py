import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
warnings.filterwarnings("ignore", category =UserWarning,)

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

from Identify_Events_Functions import *

pd.set_option('display.float_format', '{:.3f}'.format)

def find_amax_indy_events_v1 (df, duration, Tb0):
    
    rainfall_events = find_independent_events(df, Tb0)
    max_val, max_df = find_max_for_this_duration(rainfall_events, duration = duration)
    return max_df

def find_amax_indy_events_v2 (df, duration, Tb0):
    
    rainfall_cores = find_rainfall_core(df, duration=duration, Tb0= Tb0)
    rainfall_events_expanded= []
    
    for rainfall_core in rainfall_cores:
        rainfall_core_after_search1 = search1(df, rainfall_core)
        rainfall_core_after_search2 = search2(df, rainfall_core_after_search1)
        rainfall_core_after_search3 = search3(df, rainfall_core_after_search2, Tb0= Tb0)
        rainfall_events_expanded.append(rainfall_core_after_search3)
    
    return rainfall_events_expanded

def find_gauge_Tb0_and_location_in_grid (gauge_num, sample_cube):
    # Get data just for this gauge
    gauge1 = tbo_vals.iloc[gauge_num]
    # Find the interevent arrival time (Tb0)
    Tb0 = int(gauge1['Critical_interarrival_time'])
    # Find the coordinates of the cell containing this gauge
    closest_point, idx_2d = find_position_obs(sample_cube,gauge1['Lat'], gauge1['Lon'], plot=False)
    
    return Tb0, idx_2d

def read_model_data(em, yr, idx_2d):
    filename = f'/nfs/a319/gy17m2a/PhD/ProcessedData/TimeSeries/UKCP18_every30mins/2.2km/2002_2020/{em}_wholeyear/{yr}_maskedcube.nc'
    cube = iris.load(filename)[0]
    # This gauge
    data = cube[:,idx_2d[0],idx_2d[1]].data
    # Data as dataframe
    df= pd.DataFrame({'precipitation (mm/hr)':data})
    df['times'] = cube[:,idx_2d[0],idx_2d[1]].coord('time').units.num2date(cube.coord('time').points)
    # New precipitation accumulation column
    df['precipitation (mm)'] = df['precipitation (mm/hr)']/2            
    return df 
    ## Needed for finding location of gauge in grid
sample_cube = iris.load(f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/bc005/2002_2020/bng_bc005a.pr200508*')[0][1,:,:]

# Get tb0 values at each gauge
tbo_vals = pd.read_csv('/nfs/a319/gy17m2a/PhD/datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')

# Loop through gauges
# Loop through gauges
for gauge_num in range(200,250):
    print(gauge_num)
    # Find the Tb0 and index of this gauge
    Tb0, idx_2d = find_gauge_Tb0_and_location_in_grid(gauge_num, sample_cube)
    
    for em in ['bc005']:
        
        # Make directory to store outputs
        if not os.path.isdir(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option1"):
            os.makedirs(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option1")
        if not os.path.isdir(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option2"):
            os.makedirs(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option2")
        
        # Test on whether to contin
        
        for yr in range(2001,2020):
            
            if not all(os.path.exists(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/{option}/{duration}hrs_{yr}_v1.csv") for option in ['Option1', 'Option2'] for duration in [0.5, 1, 2, 3, 6, 12, 24]):


                # Get data for this ensemble member and year, at the grid cell containing this gauge
                df =read_model_data(em, yr, idx_2d)
                if df['precipitation (mm/hr)'].isnull().all():
                    break

                # Loop through duration
                for duration in [0.5, 1, 2, 3, 6, 12, 24]:    
                    try:
                        print(f"Finding the AMAX for {duration}hr events in em {em} for the year {yr}")

                        if os.path.isfile(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option1/{duration}hrs_{yr}_v1.csv"):
                            print("Option 1 already exists")
                        else:
                            event_v1 = find_amax_indy_events_v1(df, duration =duration, Tb0=Tb0)
                            if len(event_v1)>1:
                                event_v1.to_csv(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option1/{duration}hrs_{yr}_v1.csv")
                                print(f"Option 1: length with my method {len(event_v1)/2}, from {event_v1.index[0]}  to {event_v1.index[-1]} ")

                        if os.path.isfile(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option2/{duration}hrs_{yr}_v2_part0.csv"):
                            print("Option 2 already exists")
                        else:
                            events_v2 = find_amax_indy_events_v2(df, duration =duration, Tb0=Tb0)
                            for num, event in enumerate(events_v2):
                                if len(event)>1:
                                    event.to_csv(f"../../ProcessedData/IndependentEvents/{em}/Gauge{gauge_num}/Option2/{duration}hrs_{yr}_v2_part{num}.csv")
                                    print(f"Option 2: length with RVH method {len(events_v2[num])/2}, from {events_v2[num].index[0]}  to {events_v2[num].index[-1]} ")
                    except:
                        pass
                        print()
            else:
                print(f"all files already exist for {yr}")