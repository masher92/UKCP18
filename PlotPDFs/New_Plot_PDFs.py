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
from scipy.stats import norm
from scipy.stats import gamma
import numpy as np
from scipy import stats
from matplotlib import pyplot as plt

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/"
os.chdir(ddir)

###############################################################################
# Using KDE
###############################################################################
filter_dates = 'Yes'
pr_timeseries = ["Obs_1990-1992.csv"]

# Plot 
for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    # Draw the density plot
    sns.distplot(wethours['Precipitation (mm/hr)'], hist = False, kde = True,
                 kde_kws = {'linewidth': 2, 'kernel': 'biw'},
                 label = timeseries[:-4])

# Plot formatting
plt.legend(prop={'size': 10})
plt.title('1990-1992')
plt.xlabel('Precipitation (mm/hr)')
plt.ylabel('Density')
plt.xscale('log')


###############################################################################
# Using histogram and frequency polygons (i.e. connecting midpoint of histogram bins)
###############################################################################
bin_no = 200

# Plotting
for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    # Create a histogram and save the bin edges and the values in each bin
    values, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=bin_no, density=True)
    # Calculate the bin central positions
    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
    # Draw the plot
    plt.plot(bin_centres, values, label = timeseries[:-4])
    

plt.legend()
plt.title('1990-1992')
plt.xlabel('Precipitation (mm/hr)')
plt.ylabel('Probability density')
plt.xscale('log')



for timeseries in pr_timeseries:
    # Read in the csv as a PD dataframe
    df = pd.read_csv(timeseries)
    # Remove values <0.1mm
    wethours = df[df['Precipitation (mm/hr)'] > 0.1]
    # Cut to 1990-1992 if required
    if filter_dates == 'Yes':
        mask = (wethours['Date_Formatted'] > '1990-01-01 00:00:00') & (wethours['Date_Formatted'] <= '1992-12-31 23:00:00')
        wethours = wethours.loc[mask]
    # Create a histogram and save the bin edges and the values in each bin
    values, bin_edges = np.histogram(wethours['Precipitation (mm/hr)'], bins=bin_no, density=True)
    # Calculate the bin central positions
    bin_centres =  0.5*(bin_edges[1:] + bin_edges[:-1])
    
    # Draw the plot
    plt.plot(bin_centres, values, label = timeseries[:-4])
    sns.distplot(wethours['Precipitation (mm/hr)'], hist = False, kde = True,
                 kde_kws = {'linewidth': 2, 'kernel': 'biw'},
                 label = timeseries[:-4])
    plt.xscale('log')




