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
#time_series_obs = pd.read_csv("Obs_1990-1992.csv")
time_series_obs = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/Pr_1980-2001_EM01.csv")

# Remove values <0.1mm
time_series_obs = time_series_obs[time_series_obs['Precipitation (mm/hr)'] > 0.1]

# Create header for testing
time_series_obs = time_series_obs

# Remove NA values (these are non-date dates e.g. 30th February)
time_series_obs = time_series_obs.dropna()

# Format dates as datetime
time_series_obs.set_index(pd.to_datetime(time_series_obs['Date_Formatted']), inplace = True)
time_series_obs['Date_Formatted'] = pd.to_datetime(time_series_obs['Date_Formatted'])

# Plot with yearly threshold markers and a precipitation threshold line
fig, ax = plt.subplots()
# Show only years on the axis
ax.xaxis.set_major_formatter(DateFormatter('%Y'))
ax.plot(time_series_obs['Date_Formatted'], time_series_obs['Precipitation (mm/hr)'], 'o', color='black', markersize = 1)
plt.xticks(rotation=70)
plt.ylabel('Precipitation (mm/hr)')
plt.xlabel('Year')
plt.axhline(y=8, color='r', linestyle='-',linewidth=1)
for year in range(min(time_series_obs['Date_Formatted']).year,max(time_series_obs['Date_Formatted']).year + 1):
    plt.axvline(dt.datetime(year,1,1),color='r',linewidth=1)

######################### Plot with highest value in each year highlighted
# Calculate highest value in each year    
max_yearly_value =  time_series_obs.loc[time_series_obs.groupby(pd.Grouper(freq='Y')).idxmax().iloc[:, 1]]   

fig, ax = plt.subplots()
# Show only years on the axis
ax.xaxis.set_major_formatter(DateFormatter('%Y'))
ax.plot(time_series_obs.index, time_series_obs['Precipitation (mm/hr)'], 'o', color='black', markersize = 1)
#plt.xticks(rotation=70)
plt.ylabel('Precipitation (mm/hr)')
plt.xlabel('Year')
ax.plot(max_yearly_value.index, max_yearly_value['Precipitation (mm/hr)'], 'o', color='red', markersize = 1.5)
for year in range(min(time_series_obs.index).year,max(time_series_obs.index).year + 1):
    plt.axvline(dt.datetime(year,1,1),color='r',linewidth=1, linestyle = 'dashed')    

######################### Plot with highest value in each hydrological year highlighted
test = time_series_obs[0:1000]

# Function to give a hydrological year to each row
def assign_hy(row):
    if row.Date_Formatted.month>=10:
        return(pd.datetime(row.Date_Formatted.year+1,1,1).year)
    else:
        return(pd.datetime(row.Date_Formatted.year,1,1).year)
time_series_obs['HY'] = time_series_obs.apply(lambda x: assign_hy(x), axis=1)    

# Calculate highest value in each hydrological year
max_yearly_value_hy =  time_series_obs.loc[time_series_obs.groupby('HY').idxmax().iloc[:, 1]]   

# PLOT
fig, ax = plt.subplots()
# Show only years on the axis
ax.xaxis.set_major_formatter(DateFormatter('%Y'))
ax.plot(time_series_obs.index, time_series_obs['Precipitation (mm/hr)'],'o', lw = 0, fillstyle='none', color='black', markersize = 1)
#plt.xticks(rotation=70)
plt.ylabel('Precipitation (mm/hr)')
plt.xlabel('Year')
ax.plot(max_yearly_value.index, max_yearly_value['Precipitation (mm/hr)'], 'o', lw = 0,  color='red', markersize = 2)
for year in range(min(time_series_obs.index).year,max(time_series_obs.index).year + 1):
    plt.axvline(dt.datetime(year,10,1),color='r',linewidth=1, linestyle = 'dashed')  


