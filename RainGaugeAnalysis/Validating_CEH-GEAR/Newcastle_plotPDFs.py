import os
import sys
import warnings
import pandas as pd
from matplotlib.ticker import ScalarFormatter
warnings.simplefilter(action='ignore', category=FutureWarning)

################################################################
# Define variables and set up environment
################################################################
root_dir = '/nfs/a319/gy17m2a/'
os.chdir(root_dir)

# Create path to files containing functions
sys.path.insert(0, root_dir + 'Scripts/UKCP18/GlobalFunctions')
from PDF_plotting_functions import *

station_names = ['headingley_logger', 'eccup_logger', 'bramham_logger', 'farnley_hall_logger', 'knostrop_logger']

#############################################
# Read in data
#############################################
precip_ts = {}
for station_name in station_names:
    
    gauge_ts ={}
    
    # Read in CEH-GEAR data from grid cell within which the gauge is found
    filename_cehgear= root_dir + 'Outputs/TimeSeries/CEH-GEAR/Gauge_GridCells/TimeSeries_csv/{}.csv'.format(station_name)
    df_cehgear = pd.read_csv(filename_cehgear, index_col=None, header=0)
    # Create a formatted date column
    df_cehgear['Datetime'] = pd.to_datetime(df_cehgear['Date_formatted'])
    
    # Read in the gauge data
    filename_gauge= root_dir + 'datadir/GaugeData/Newcastle/leeds-at-centre_csvs/{}.csv'.format(station_name)
    df_gauge = pd.read_csv(filename_gauge, index_col=None, header=0)
    df_gauge['Datetime2'] = pd.to_datetime(df_gauge['Datetime'])
    
    # Find the overlapping time period
    earliesttime = df_gauge['Datetime2'].min() if df_gauge['Datetime2'].min() > df_cehgear['Datetime'].min() else df_cehgear['Datetime'].min()
    latesttime = df_gauge['Datetime2'].max() if df_gauge['Datetime2'].max() < df_cehgear['Datetime'].max() else df_cehgear['Datetime'].max()
    
    #### Cut to same time period
    df_cehgear = df_cehgear[(df_cehgear['Datetime'] > earliesttime)& (df_cehgear['Datetime']< latesttime)]
    df_gauge = df_gauge[(df_gauge['Datetime2'] > earliesttime)& (df_gauge['Datetime2']< latesttime)]
    
    # Check if gauge and CEH-GEAR data set are the same length
    if len(df_gauge) == len(df_cehgear):
        print("Same length")

    # Remove -999 values and na values
    df_gauge = df_gauge[df_gauge['Precipitation (mm/hr)'] != -999]
    df_cehgear = df_cehgear[df_cehgear['Precipitation (mm/hr)'] != np.nan]
    df_cehgear.dropna(inplace = True)
    
    # Add to dictionary
    precip_ts[station_name + '_GaugeData'] = df_gauge
    precip_ts[station_name + '_GridData'] = df_cehgear

    # Add to dictionary
    gauge_ts[station_name + '_GaugeData'] = df_gauge
    gauge_ts[station_name + '_GridData'] = df_cehgear

    # Plot PDF
    cols_dict = {station_name + '_GaugeData' : 'firebrick',
                 station_name + '_GridData'  : 'green'}
    
    x_axis = 'linear'
    y_axis = 'log'
    bin_nos = 30 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
    xlim = False
    bins_if_log_spaced= bin_nos
    
    #################### Full time period
    ####### Combined ensemble members + Obs
    patches= []
    patch = mpatches.Patch(color='firebrick', label='Gauge Data')
    patches.append(patch)
    patch = mpatches.Patch(color='green', label='CEH-GEAR Data')
    patches.append(patch)
    
    log_discrete_histogram_lesslegend(gauge_ts, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                      patches, True, xlim, x_axis, y_axis) 

    plt.savefig("Scripts/UKCP18/RainGaugeAnalysis/Figs/NewcastleGaugeGridCells/PDF_GaugevsGridCell/{}.png".format(station_name))

###############################################################################
# Plots
###############################################################################
cols_dict = {'headingley_logger_GaugeData' : 'firebrick',
             'headingley_logger_GridData' : 'green',
             'eccup_logger_GaugeData' : 'firebrick',
             'eccup_logger_GridData' : 'green',
             'bramham_logger_GaugeData' : 'firebrick',
             'bramham_logger_GridData' : 'green',
             'farnley_hall_logger_GaugeData' : 'firebrick',
             'farnley_hall_logger_GridData' : 'green',
             'knostrop_logger_GaugeData' : 'firebrick',
             'knostrop_logger_GridData' : 'green'}

x_axis = 'linear'
y_axis = 'log'
bin_nos = 10 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = False
bins_if_log_spaced= bin_nos

#################### Full time period
####### Combined ensemble members + Obs
patches= []
patch = mpatches.Patch(color='firebrick', label='Gauge Data')
patches.append(patch)
patch = mpatches.Patch(color='green', label='CEH-GEAR Data')
patches.append(patch)

log_discrete_histogram_lesslegend(precip_ts, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim, x_axis, y_axis) 

    
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


