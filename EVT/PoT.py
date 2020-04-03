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
from datetime import timedelta

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

# Remove NA values (these are non-date dates e.g. 30th February)
time_series_obs = time_series_obs.dropna()

# Format dates as datetime
time_series_obs.set_index(pd.to_datetime(time_series_obs['Date_Formatted']), inplace = True)
time_series_obs['Date_Formatted'] = pd.to_datetime(time_series_obs['Date_Formatted'])

#########################  Plot with yearly threshold markers and a precipitation threshold line
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


#########################  PoT, quantile threshold
# Find the Xth percentile values
P_99 = np.percentile(time_series_obs['Precipitation (mm/hr)'], 99) # return 50th percentile, e.g median.
P_97 = np.percentile(time_series_obs['Precipitation (mm/hr)'], 97) # return 50th percentile, e.g median.   

# Highlight values higher than that line
values_over_threshold = time_series_obs[time_series_obs['Precipitation (mm/hr)'] > P_99]

# COunt number of observations over line in each year
# Add a year column
values_over_threshold['CY'] = values_over_threshold['Date_Formatted'].dt.year
count_exceedences = values_over_threshold.groupby('CY').count()
count_exceedences['Date'].mean()

fig, ax = plt.subplots()
# Show only years on the axis
ax.xaxis.set_major_formatter(DateFormatter('%Y'))
ax.plot(time_series_obs['Date_Formatted'], time_series_obs['Precipitation (mm/hr)'], 'o', color='black', markersize = 1, label='_nolegend_')
#plt.xticks(rotation=70)
plt.ylabel('Precipitation (mm/hr)')
plt.xlabel('Year')
plt.axhline(y=P_99, color='firebrick', linestyle='dashed',linewidth=2, label='99thP')
ax.plot(values_over_threshold.index, values_over_threshold['Precipitation (mm/hr)'], 'o', lw = 0,  color='red', markersize = 1, label='_nolegend_')
#plt.axhline(y=P_97, color='g', linestyle='solid',linewidth=2, label='95thP')
for year in range(min(time_series_obs['Date_Formatted']).year,max(time_series_obs['Date_Formatted']).year + 1):
    plt.axvline(dt.datetime(year,1,1),color='green',linewidth=0.3, linestyle = 'solid')
plt.legend()


## Declustering ###
# E.g. Discard any value within 2 days of the initial value
# The other option is runs which stipulates that any value over the threshold separated by fewer than r non-extreme values is dependent
# Create test df
df = values_over_threshold

# Reset index, as numbered index is needed
df.reset_index(drop = True, inplace = True)

# For each row determine a date at the end of a 2 day period
df['window_end'] = df.Date_Formatted + pd.Timedelta(days=2)

# Initially set all events as being in the same cluster
df['Cluster'] = 1

# Iterate through each row in the dataframe, starting at the 2nd row (1st row has 
# now preceding day to compare to)
for index, row in df.iloc[1:].iterrows():
   # print(index)
    # Find the index of the previous row
    previous_line_idx =index -1
    # Find whether the date when the time window of the previous event ends is
    # after this event's date
    if row.Date_Formatted > df.iloc[previous_line_idx].window_end:
        # If so, assign all events afterwards to a new cluster
        for index, row in df.iloc[index:].iterrows():
            df.loc[index, 'Cluster'] = df.iloc[index].Cluster + 1
   #else:
        # If not then do nothing; i.e. this row remains in the same cluster
    #   print("no")

## Keep only the highest value from each cluster
highest_cluster_values = df[df['Precipitation (mm/hr)'] == df.groupby('Cluster')['Precipitation (mm/hr)'].transform('max')]
highest_cluster_values.set_index(pd.to_datetime(highest_cluster_values['Date_Formatted']), inplace = True)

# Find the number in each year
highest_cluster_values['CY'] = highest_cluster_values['Date_Formatted'].dt.year
count_exceedences = highest_cluster_values.groupby('CY').count()
count_exceedences['Date'].mean()


fig, ax = plt.subplots()
# Show only years on the axis
ax.xaxis.set_major_formatter(DateFormatter('%Y'))
ax.plot(time_series_obs['Date_Formatted'], time_series_obs['Precipitation (mm/hr)'], 'o', color='black', markersize = 1, label='_nolegend_')
#plt.xticks(rotation=70)
plt.ylabel('Precipitation (mm/hr)')
plt.xlabel('Year')
plt.axhline(y=P_99, color='firebrick', linestyle='solid',linewidth=1, label='99thP')
ax.plot(highest_cluster_values.index, highest_cluster_values['Precipitation (mm/hr)'], 'o', lw = 0,  color='red', markersize = 1, label='_nolegend_')
#plt.axhline(y=P_97, color='g', linestyle='solid',linewidth=2, label='95thP')
for year in range(min(time_series_obs['Date_Formatted']).year,max(time_series_obs['Date_Formatted']).year + 1):
    plt.axvline(dt.datetime(year,1,1),color='green',linewidth=0.3, linestyle = 'solid')
plt.legend()


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
    plt.axvline(dt.datetime(year,1,1),color='g',linewidth=0.4, linestyle = 'solid')   

######################### Plot with highest value in each hydrological year highlighted
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
    plt.axvline(dt.datetime(year,10,1),color='g',linewidth=0.4, linestyle = 'solid')  


