"""
File which:
    

@author Molly Asher
@Version 1.0

"""

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

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/"
os.chdir(ddir)

###############################################################################
# Read in the timeseries for which the PDF should be plotted
###############################################################################
time_series = pd.read_csv("Obs_1990-1992.csv")

# Remove values <0.1mm
time_series = time_series[time_series['Precipitation (mm/hr)'] > 0.1]

###########################
# Plot pdf 
ax = sns.distplot(time_series['Precipitation (mm/hr)'])
# Can choose whether to include a rug plot, or the histogram
ax = sns.distplot(time_series['Precipitation (mm/hr)'], rug=True, hist=False)
# Can shade in the plot
ax = sns.kdeplot(time_series['Precipitation (mm/hr)'], shade = True, color = 'r')

# Bandwidth is a measure of how closely the density should match the distribution
sns.kdeplot(time_series['Precipitation (mm/hr)'])
sns.kdeplot(time_series['Precipitation (mm/hr)'], bw=.1, label="bw: 0.2")
sns.kdeplot(time_series['Precipitation (mm/hr)'], bw=5, label="bw: 2")
plt.legend();

# Can also plot a parametric distribution and compare how well the data fits to it
from scipy.stats import norm
from scipy.stats import gamma
ax = sns.distplot(time_series['Precipitation (mm/hr)'], fit=norm, kde=False)
sns.distplot(time_series['Precipitation (mm/hr)'], kde=False, fit=gamma);


