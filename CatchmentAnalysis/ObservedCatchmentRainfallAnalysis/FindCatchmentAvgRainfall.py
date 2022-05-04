# Set up environment 
import numpy as np
import os
import glob
import pandas as pd 

# Set working directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Load the times related to the hourly data for each catchment grid cell 
times = np.load('PhD/Scripts/CatchmentAnalysis/ObservedCatchmentRainfallAnalysis/LinDykeData/times_jja.npy', allow_pickle=True)

# Get a list of all the individual grid cell JJA .npy files
jja_npy_files = glob.glob('PhD/Scripts/CatchmentAnalysis/ObservedCatchmentRainfallAnalysis/LinDykeData/*_jja.npy')
jja_npy_files = jja_npy_files[:-2]
len(jja_npy_files)

# Create an array to store the daily values for all the grid cells in the catchment
all_daily_sums = np. array([])

# Add the daily data for each grid cell
for file in jja_npy_files:
    print(file)
    one_cell = np.load(file, allow_pickle = True)
    df = pd.DataFrame({'Dates': pd.to_datetime(times), 'Precipitation': one_cell})
    daily_sums = df.set_index('Dates').resample('D')['Precipitation'].sum()
    all_daily_sums = np.append(all_daily_sums, daily_sums)

# Find the mean daily precipitation values across the area covering the catchment 
np.mean(all_daily_sums)

# Mean hourly rainfall
# lindyke_jja = np.load('PhD/Scripts/CatchmentAnalysis/ObservedCatchmentRainfallAnalysis/LinDykeData//LinDyke_jja.npy')
# np.mean(lindyke_jja)
