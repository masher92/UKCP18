#############################################
# Set up environment
#############################################
import os
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import numpy as np
import seaborn as sns
import pandas as pd
from scipy.stats import norm
from scipy.stats import gamma
from scipy import stats

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/"
os.chdir(ddir)

###############################################################################
# Set parameters
###############################################################################
filter_dates = 'No'
kernel_type = 'gau'
pr_timeseries = ["Obs_1990-1992.csv", "Pr_1980-2001_EM01.csv", "Pr_1980-1997_EM04.csv"]
pr_timeseries = ["Pr_1980-2001_EM01.csv"]
bin_nos = 200

###############################################################################
# Plot KDE
###############################################################################
for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Cut all to same number of decimal places
   # df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    # Define bin spacings
    bin_no = np.linspace(0.1, wethours['Precipitation (mm/hr)'].max(),bin_nos).tolist()
    # Draw the density plot
    sns.distplot(wethours['Precipitation (mm/hr)'], hist = False, kde = True,
                 kde_kws = {'linewidth': 1, 'kernel': kernel_type}, bins =bin_no,
                 hist_kws = {'linewidth': 0.5, 'color': 'white', 'edgecolor' : 'black', 'alpha' :1},
                 label = timeseries[:-4])

# Plot formatting
plt.legend(prop={'size': 10})
#plt.title('1990-1992')
plt.xlabel('Precipitation (mm/hr)')
plt.ylabel('Density')
plt.xscale('log')


###############################################################################
# Histogram and frequency polygons (i.e. connecting midpoint of histogram bins)
###############################################################################
for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Cut all to same number of decimal places
    #df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    # Create a histogram and save the bin edges and the values in each bin
    values, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=bin_nos, density=True)
    # Calculate the bin central positions
    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
    # Draw the plot
    plt.plot(bin_centres, values, label = timeseries[:-4], linewidth = 1)
    #plt.plot(bin_centres, values, color='black', marker='o',markersize =1, linewidth=0.5, markerfacecolor = 'red')
    #plt.hist(wethours['Precipitation (mm/hr)'], bins = bin_no, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)

plt.legend()
#plt.title('1990-1992')
plt.xlabel('Precipitation (mm/hr)')
plt.ylabel('Probability density')
plt.title(str(bin_nos) + " bins")
plt.xscale('log')
#plt.xlim(0,10)

###############################################################################
# Histogram with unequal bin widths and equal widths
###############################################################################
for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Cut all to same number of decimal places
    #df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    
    # Define equal bins
    equal_bins = np.linspace(0, wethours['Precipitation (mm/hr)'].max(),bin_nos).tolist()   
    # Find the density of values in each of the equal bins
    equal_density, equal_bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=equal_bins, density=True)
    # Calculate the bin central positions
    equal_bin_centres =  0.5*(equal_bin_edges[1:] + equal_bin_edges[:-1])
    
    # Generate bins with unequal widths
    power_for_unequal_bins=3.0 # Power used for generating unequal bins
    number_unequal_bins=40 # Number of unequal bins 
    unequal_min=0 # Must be zero or bigger for this approach to work
    unequal_max=1.01*np.nanmax(wethours['Precipitation (mm/hr)']) # Ensure this is greater than the largest number
    # N-th root (e.g. third root) of bin edges for manual bin edge spacing
    unequal_linspace=np.linspace(unequal_min,unequal_max**(1.0/power_for_unequal_bins),number_unequal_bins)     
    unequal_bin_edges=unequal_linspace**power_for_unequal_bins
   
    # This piece of codes calculates the bin centres, based on the third root
    # Alternative choice would be: power_bin_centres=0.5*(unequal_bin_edges[:-1]+unequal_bin_edges[1:])
    unequal_linspace_centres=0.5*(unequal_linspace[:-1]+unequal_linspace[1:])
    unequal_bin_centres=(unequal_linspace_centres)**3   
    
    # Find the density of values in each of the unequal bins
    unequal_density,bins_out=np.histogram(wethours['Precipitation (mm/hr)'],bins=unequal_bin_edges,density=True)       
        
    # Draw the plot
    plt.plot(equal_bin_centres, equal_density, linewidth = 1.5, label = 'Equal bin widths')
    plt.hist(wethours['Precipitation (mm/hr)'], bins = equal_bin_edges, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)
    plt.xlim(0,4)
    
    plt.plot(unequal_bin_centres, unequal_density, linewidth = 1.5, label = 'Equal bin widths')
    plt.hist(wethours['Precipitation (mm/hr)'], bins = unequal_bin_edges, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5)
    plt.xlim(0,4)
    
    plt.plot(unequal_bin_centres, unequal_density, linewidth = 1.5, label = 'Unequal bin widths')
    plt.xscale('log')
    plt.plot(equal_bin_centres, equal_density, linewidth = 1.5, label = 'Equal bin widths')
    plt.xscale('log')
    plt.legend()
    #plt.title('1990-1992')
    plt.xlabel('Precipitation (mm/hr)')
    plt.ylabel('Probability density')
    plt.title(str(bin_nos) + " bins")
    plt.xscale('log')
    plt.yscale('log')
    #plt.xlim(0,10)


###############################################################################
# Compare KDE and histogram
###############################################################################
for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Cut all to same number of decimal places
    #df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
   
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    # Create a histogram and save the bin edges and the values in each bin
    values, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=bin_nos, density=True)
    # Calculate the bin central positions
    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
    
    # Draw the plot
    plt.plot(bin_centres, values, label = 'Frequency polygon', color = 'red', linewidth = 1.5, alpha = 0.7)
    sns.distplot(wethours['Precipitation (mm/hr)'], hist = False, kde = True,
                 kde_kws = {'linewidth': 1.5, 'kernel': kernel_type, 'color': 'green', 'alpha': 1}, bins =bin_no,
                 hist_kws = {'linewidth': 0.5, 'color': 'white', 'edgecolor' : 'b', 'alpha' :1},
                 label = 'KDE')
    #plt.hist(wethours['Precipitation (mm/hr)'], bins = bin_no, density = True, color = 'white', edgecolor = 'black', linewidth= 0.5, alpha = 1)

    plt.legend()
    #plt.xlim(0,1)
    if filter_dates == 'Yes':
        plt.title(timeseries[:-4] +'_trimmed_1990-1992'+ "_" + str(bin_no) + "bins")
    else:
        plt.title(timeseries[:-4] + "_" + str(bin_no) + "bins")
    #plt.xscale('log')
    plt.xlim(0,5)
        

###############################################################################
# Method for plotting histogram according to method in Holloway (2012)
###############################################################################
bin_nos = 18
plot_density = 'No'
plot_fc = 'Yes'

for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Cut all to same number of decimal places
    df['Precipitation (mm/hr)'] = df['Precipitation (mm/hr)'].round(1)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
   
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
        
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
        plt.plot(bin_centres, densities, linewidth = 1.5, label = timeseries[:-4])
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
