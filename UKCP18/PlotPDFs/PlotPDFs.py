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

#root_dir = '/nfs/a319/gy17m2a/'
root_dir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/RemoteServer/'

# Define the local directory where the data is stored; set this as work dir
os.chdir('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/PythonScripts/UKCP18/PlotPDFs/')

from Plotting_functions import *
#from config import *
location ='Armley'

#############################################
# Read in data
#############################################
# Create a dictionary with the ensemble member as the key and the dataframe as value
# Carry out preprocessing of data
precip_ts ={}
for i in [1,4,5,6,7,8,9,10,11,12,13,15]:
    #precip_ts['EM_'+str(i)] = root_dir + 'Outputs/TimeSeries_csv/{}/2.2km/EM{}_1980-2001.csv'.format(location, str(i).zfill(2))
    filename = root_dir + 'Outputs/TimeSeries_csv/{}/2.2km/EM{}_1980-2001.csv'.format(location, str(i).zfill(2))
    df = pd.read_csv(filename, index_col=None, header=0)
    # Cut all to same number of decimal places
    df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Save as dictionary entry alongside ensemble member number name
    precip_ts['EM_'+str(i)] = wethours
    
# Create one dataframe containing all the ensemble member's data merged
merged_ensembles = pd.concat(precip_ts.values(), axis=0, ignore_index=True)

# Add observations data to the dictionary
obs_df = pd.read_csv(root_dir + 'Outputs/CEH-GEAR/{}/1990-2001.csv'.format(location))
wethours_obs = obs_df[obs_df['Precipitation (mm/hr)'] > 0.1]
precip_ts['Observations'] = wethours_obs

# Create a seperate dictionary containing the merged ensemble member data and the observations data
obs_vs_proj = {'Observations' : wethours_obs, 'Merged Ensembles' :  merged_ensembles}

###############################################################################
# Plots
###############################################################################
x_axis = 'linear'
y_axis = 'log'
bin_nos = 10
bins_if_log_spaced= bin_nos

# Equal spaced histogram
equal_spaced_histogram(obs_vs_proj, bin_nos,x_axis, y_axis)
equal_spaced_histogram(precip_ts, bin_nos,x_axis, y_axis)
     
# Log spaced histogram
log_spaced_histogram(obs_vs_proj, bin_nos,x_axis, y_axis)    
log_spaced_histogram(precip_ts, bin_nos,x_axis, y_axis)    
 
# Fractional contribution
fractional_contribution(obs_vs_proj, bin_nos,x_axis, y_axis)   
fractional_contribution(precip_ts, bin_nos,x_axis, y_axis) 
             
# Log histogram with adaptation     
log_discrete_histogram(obs_vs_proj, bin_nos,x_axis, y_axis) 
log_discrete_histogram(precip_ts, bin_nos,x_axis, y_axis) 
 
    
########################################################
# Testing effect of moving bottom bin starting point away from the lowest value
#bin_nos = 250
#bin_div_1 = np.linspace(wethours['Precipitation (mm/hr)'].min(), wethours['Precipitation (mm/hr)'].max(),bin_nos).tolist()
#bin_div_2 = np.linspace(wethours['Precipitation (mm/hr)'].min()-0.05, wethours['Precipitation (mm/hr)'].max()-0.05,bin_nos).tolist()
#bin_div_3 = np.linspace(wethours['Precipitation (mm/hr)'].min()-0.1, wethours['Precipitation (mm/hr)'].max()-0.1,bin_nos).tolist()
#bin_div_4 = np.linspace(wethours['Precipitation (mm/hr)'].min()+0.5, wethours['Precipitation (mm/hr)'].max()+0.5,bin_nos).tolist()
#bin_divs = [bin_div_1, bin_div_2, bin_div_3, bin_div_4]

# Plotting
#for bin_div in bin_divs:
#    # Create a histogram and save the bin edges and the values in each bin
#    values, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=bin_nos, density=True)
#    # Calculate the bin central positions
#    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
#    # Draw the plot
#    plt.plot(bin_centres, values, label = timeseries[:-4], linewidth = 1)
#    #plt.plot(bin_centres, values, color='black', marker='o',markersize =1, linewidth=0.5, markerfacecolor = 'red')


