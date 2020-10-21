#############################################
# Set up environment
#############################################
import os
#import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
#import numpy as np
import pandas as pd
#from scipy.stats import norm
#from scipy.stats import gamma
#from scipy import stats
from matplotlib.ticker import ScalarFormatter

#root_dir = '/nfs/a319/gy17m2a/'
root_dir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/'

# Define the local directory where the data is stored; set this as work dir
os.chdir('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/PlotPDFs/')

from PDF_plotting_functions import *
#from config import *
location ='Armley'

#############################################
# Read in data
#############################################
# Create a dictionary with the ensemble member as the key and the dataframe as value
# Carry out preprocessing of data
total = 0
wet_total = 0
precip_ts ={}
for i in [1,4,5,6,7,8,9,10,11,12,13,15]:
    #precip_ts['EM_'+str(i)] = root_dir + 'Outputs/TimeSeries_csv/{}/2.2km/EM{}_1980-2001.csv'.format(location, str(i).zfill(2))
    filename = root_dir + 'Outputs/TimeSeries_csv/{}/2.2km/EM{}_1980-2001.csv'.format(location, str(i).zfill(2))
    df = pd.read_csv(filename, index_col=None, header=0)
    # Cut all to same number of decimal places
    df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Keep only entries between 1990-2001
    df = df[(df['Date_Formatted'] > '1990-01-01') & (df['Date_Formatted']< '2000-12-31')]
    total = total + len(df)
    # Remove values <0.1mm
    #wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    wethours = df
    # Save as dictionary entry alongside ensemble member number name
    precip_ts['EM_'+str(i)] = wethours
    wet_total = wet_total + len(wethours)
    
# Create one dataframe containing all the ensemble member's data merged
merged_ensembles = pd.concat(precip_ts.values(), axis=0, ignore_index=True)

# Add observations data to the dictionary
obs_df = pd.read_csv(root_dir + 'Outputs/CEH-GEAR/{}/1990-2001.csv'.format(location))
# Keep only entries between 1990-2001
obs_df = obs_df[(obs_df['Date_formatted'] > '1990-01-01') & (obs_df['Date_formatted']< '2000-12-31')]
# Remove values <0.1mm
#wethours_obs = obs_df[obs_df['Precipitation (mm/hr)'] > 0.1]
wethours_obs = obs_df
# Add to dict
precip_ts['Observations'] = wethours_obs

# Create a seperate dictionary containing the merged ensemble member data and the observations data
obs_vs_proj = {'Observations' : wethours_obs, 'Merged Ensembles' :  merged_ensembles}

keys = []
p_99_99 = []
p_99_95 = []
p_99_9 = []
p_99_5 = []
p_99 = []
p_95 =[]
p_90 = []
p_80 = []
p_70 = []
p_60 = []
p_50 = []
for key, value in precip_ts.items():
    df = precip_ts[key]
    p_99_99.append(df['Precipitation (mm/hr)'].quantile(0.9999))
    p_99_95.append(df['Precipitation (mm/hr)'].quantile(0.9995))
    p_99_9.append(df['Precipitation (mm/hr)'].quantile(0.999))
    p_99_5.append(df['Precipitation (mm/hr)'].quantile(0.995))
    p_99.append(df['Precipitation (mm/hr)'].quantile(0.99))
    p_95.append(df['Precipitation (mm/hr)'].quantile(0.95))
    p_90.append(df['Precipitation (mm/hr)'].quantile(0.9))
    p_80.append(df['Precipitation (mm/hr)'].quantile(0.8))
    p_70.append(df['Precipitation (mm/hr)'].quantile(0.7))
    p_60.append(df['Precipitation (mm/hr)'].quantile(0.6))
    p_50.append(df['Precipitation (mm/hr)'].quantile(0.5))
    keys.append(key)
    
    
df= pd.DataFrame({'Key':keys, '50': p_50,
                 '60': p_60, '70': p_70,  
                  '80': p_80, '90': p_90,
                 '95': p_95, '99': p_99,
                 '99.5': p_99_5, '99.9': p_99_9,
                '99.95': p_99_95, '99.99': p_99_99})

test = df.transpose()
test = test.rename(columns=test.iloc[0]).drop(test.index[0])

# Plot
navy_patch = mpatches.Patch(color='navy', label='Observations')
red_patch = mpatches.Patch(color='firebrick', label='Projections')

for key, value in precip_ts.items():
    print(key)
    if key == 'Observations':
        plt.plot(test[key], color = 'navy')
    else:
        plt.plot(test[key], color = 'firebrick')
    plt.xlabel('Percentile')
    plt.ylabel('Precipitation (mm/hr)')
    plt.legend(handles=[red_patch, navy_patch])
    plt.yscale('log')
    plt.xticks(rotation = 23)



