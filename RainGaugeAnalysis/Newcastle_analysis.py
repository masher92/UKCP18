import numpy as np
import os
from datetime import date, timedelta as td, datetime
import pandas as pd

# Set up path to root directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis"
os.chdir(root_fp)

# Read in data entries containing precipitation values
data=np.loadtxt("datadir/GaugeData/Newcastle/EA3307_RK.txt", skiprows = 21)

# Read in intro lines
with open("datadir/GaugeData/Newcastle/EA3307_RK.txt") as myfile:
    firstNlines=myfile.readlines()[0:21]
print(firstNlines)

# Store start and end ates
startdate = firstNlines[7][16:26]
enddate = firstNlines[8][14:24]

# Convert to datetimes
d1 = datetime(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8]), int(startdate[8:10]))
d2 = datetime(int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), int(enddate[8:10]))

# Find all hours between these dates
time_range = pd.date_range(d1, d2, freq='H')    

# Check if there are the correct number
n_lines = firstNlines[10][19:-1]
if int(n_lines) == len(time_range):
    print('Correct number of lines')

# Create dataframe containing precipitation values as times
precip_df = pd.DataFrame({'Datetime': time_range,
                          'Precipitation (mm/hr)': data})