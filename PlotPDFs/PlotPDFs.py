#############################################
# Set up environment
#############################################
import os
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.stats import gamma
from scipy import stats

# Define the local directory where the data is stored; set this as work dir
os.chdir("/nfs/a319/gy17m2a/Scripts")

from config import *


#############################################
# Read in data
#############################################
# All ensemble members for projections
precip_ts = []
for i in [1,4,5,6,7,8,9,10,11,12,13,15]:
    precip_ts.append('/nfs/a319/gy17m2a/Outputs/TimeSeries_csv/{}/2.2km/EM{}_1980-2001.csv'.format(location, str(i).zfill(2)))

# Add observations data
precip_ts.append('/nfs/a319/gy17m2a/Outputs/CEH-GEAR/{}/1990-2001.csv'.format(location))
bin_nos = 200


precip_ts ={}
for i in [1,4,5,6,7,8,9,10,11,12,13,15]:
    precip_ts['EM_'+str(i)] = '/nfs/a319/gy17m2a/Outputs/TimeSeries_csv/{}/2.2km/EM{}_1980-2001.csv'.format(location, str(i).zfill(2))

# Add observations data
precip_ts['Obs'] = '/nfs/a319/gy17m2a/Outputs/CEH-GEAR/{}/1990-2001.csv'.format(location)

bin_nos = 200

###############################################################################
# Histogram and frequency polygons (i.e. connecting midpoint of histogram bins)
###############################################################################
bin_nos = 150
for key, filename in precip_ts.items():
    # Read in the csv as a PD dataframe
    df = pd.read_csv(filename)
    # Cut all to same number of decimal places
    #df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Create a histogram and save the bin edges and the values in each bin
    values, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=bin_nos, density=True)
    # Calculate the bin central positions
    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
    # Draw the plot
    plt.plot(bin_centres, values, label = key, linewidth = 1)
    #plt.plot(bin_centres, values, color='black', marker='o',markersize =1, linewidth=0.5, markerfacecolor = 'red')
    #plt.hist(wethours['Precipitation (mm/hr)'], bins = bin_no, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)

plt.legend()
#plt.title('1990-1992')
plt.xlabel('Precipitation (mm/hr)')
plt.ylabel('Probability density')
plt.title(str(bin_nos) + " bins")
plt.yscale('log')
#plt.xlim(0,10)


###############################################################################
# Method for plotting histogram according to method in Holloway (2012)
###############################################################################
bin_nos = 18
plot_density = 'No'
plot_fc = 'Yes'


for key, filename in precip_ts.items():
    # Read in the csv as a PD dataframe
    df = pd.read_csv(filename)
    # Cut all to same number of decimal places
    df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
   
       
    # Create logarithmically spaced bins
    # Need to go slightly under the number e.g. 0.2 otherwise it excluded values of exactly 0.2
    #bins = 10 ** np.linspace(np.log10(0.1), np.log10(30), 50)
    bins = np.logspace(np.log10(0.19),np.log10(wethours['Precipitation (mm/hr)'].max()), bin_nos)  
    
    # Find the numbers of precipitation measurements in each bin   
    freqs, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins= bins, density=False)
    # Find the centre point of each bin for plotting
    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])    
   
    if plot_density == 'Yes':    

        # Find the density of each bin as the number of measurements in the bin divided 
        # by the sum of the the total number of measurememnts in the dataset and the 
        # bin width in mm/hr
        densities = []
        for i in range(0,len(freqs)):
            bin_width = bin_edges[i+1]  - bin_edges[i]
            density = freqs[i] /(bin_width*wethours['Precipitation (mm/hr)'].count())
            densities.append(density)
    
       # Use in built np.histogram density calculator
        density, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins= bins, density=True)
        # Plot - test whether these are the same
        # plt.plot(bin_centres, density, linewidth = 1.5, label = 'Np Density')
        # plt.plot(bin_centres, densities, linewidth = 1.5, label = 'Custom Density')
        # plt.hist(wethours['Precipitation (mm/hr)'], bins = bins, histtype = 'step', density = 'True')
        # plt.gca().set_xscale("log")
        # plt.legend()
        
        # Plot 
        plt.plot(bin_centres, densities, linewidth = 1.5, label = key)
        #plt.hist(wethours['Precipitation (mm/hr)'], bins = bins, histtype = 'step', density = True)
        plt.gca().set_xscale("log")
        plt.gca().set_yscale("log")   
        plt.legend()
        plt.xlabel('Precipitation (mm/hr)')
        plt.ylabel('Probability density')
        #plt.xlim(0,1)
 
    if plot_fc == 'Yes':    
        # Find the sum of the rain rates for all included values
        R = wethours['Precipitation (mm/hr)'].sum()
        
        fcs = []
        for i in range(0,len(freqs)):
            # Find parameters
            r = bin_centres[i]
            n_r = freqs[i]   
            delta_r = bin_edges[i+1]  - bin_edges[i]
            # Implement formula
            fc = (r * n_r)/(R*delta_r)
            # Add values to list
            fcs.append(fc)
        
        # Plot 
        plt.plot(bin_centres, fcs, linewidth = 1.5, label = timeseries[:-4])
        #plt.hist(wethours['Precipitation (mm/hr)'], bins = bins, histtype = 'step', density = True)
        plt.gca().set_xscale("log")
        plt.gca().set_yscale("log")   
        plt.legend()
        plt.xlabel('Precipitation (mm/hr)')
        plt.ylabel('Fraction of total precipitation per rain rate')
        #plt.xlim(0,1)

    
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


