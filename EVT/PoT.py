#############################################
# Set up environment
#############################################
import pandas as pd
import os
import matplotlib.pyplot as plt
import warnings
import numpy as np
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime as dt

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/"
os.chdir(ddir)

###############################################################################
# Read in the timeseries for which the PDF should be plotted
###############################################################################
time_series_obs = pd.read_csv("Obs_1990-1992.csv")
time_series_obs = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/Pr_1980-2001_EM01.csv")

# Remove values <0.1mm
time_series_obs = time_series_obs[time_series_obs['Precipitation (mm/hr)'] > 0.1]

# Create header for testing
time_series_obs = time_series_obs[0:10000]

# Remove NA values (these are non-date dates e.g. 30th February)
time_series_obs = time_series_obs.dropna()

# Format dates as index
time_series_obs.set_index(pd.to_datetime(time_series_obs['Date_Formatted']), inplace = True)

# Plot
fig, ax = plt.subplots()
# Show only years on the axis
ax.xaxis.set_major_formatter(DateFormatter('%Y'))
ax.plot(time_series_obs.index, time_series_obs['Precipitation (mm/hr)'], 'o', color='black', markersize = 1)
plt.xticks(rotation=70)
plt.ylabel('Precipitation (mm/hr)')
plt.xlabel('Year')
plt.axhline(y=8, color='r', linestyle='-',linewidth=1)
for year in range(min(time_series_obs.index).year,max(time_series_obs.index).year + 1):
    plt.axvline(dt.datetime(year,1,1),color='r',linewidth=1)



