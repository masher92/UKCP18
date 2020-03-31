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
import pandas as pd

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries/"
os.chdir(ddir)

###############################################################################
# Read in the timeseries for which the PDF should be plotted
###############################################################################
time_series_obs = pd.read_csv("Obs_1990-1992.csv")
time_series_pr_01 = pd.read_csv("Pr_1980-1981_EM01.csv")
time_series_pr_04 = pd.read_csv("Pr_1990-1996_EM04.csv")

# Remove values <0.1mm
time_series_obs = time_series_obs[time_series_obs['Precipitation (mm/hr)'] > 0.1]
time_series_pr_01 = time_series_pr_01[time_series_pr_01['Precipitation (mm/hr)'] > 0.1]
time_series_pr_04 = time_series_pr_04[time_series_pr_04['Precipitation (mm/hr)'] > 0.1]

###########################
# Select which time series to plot
time_series = time_series_obs

# Plot pdf 
ax = sns.distplot(time_series['Precipitation (mm/hr)'])
# Can choose whether to include a rug plot, or the histogram
ax = sns.distplot(time_series['Precipitation (mm/hr)'], rug=True, hist=False)
# Can shade in the plot
ax = sns.kdeplot(time_series['Precipitation (mm/hr)'], shade = True, color = 'r')

# Bandwidth is a measure of how closely the density should match the distribution
sns.kdeplot(time_series['Precipitation (mm/hr)'])
sns.kdeplot(time_series['Precipitation (mm/hr)'], bw=.01, label="bw: 0.2")
sns.kdeplot(time_series['Precipitation (mm/hr)'], bw=.1, label="bw: 0.2")
sns.kdeplot(time_series['Precipitation (mm/hr)'], bw=5, label="bw: 2")
plt.legend();

# Can also plot a parametric distribution and compare how well the data fits to it
from scipy.stats import norm
from scipy.stats import gamma
ax = sns.distplot(time_series['Precipitation (mm/hr)'], fit=norm, kde=False)
sns.distplot(time_series['Precipitation (mm/hr)'], kde=False, fit=gamma);

#############################################################################
# Plotting multiple on same plot e.g. observations and projections
#############################################################################
sns.distplot(time_series_obs['Precipitation (mm/hr)'], hist=False, rug=False, label = 'Observations')
sns.distplot(time_series_pr_01['Precipitation (mm/hr)'], hist=False, rug=False, label = 'EM01')
sns.distplot(time_series_pr_04['Precipitation (mm/hr)'], hist=False, rug=False, label = 'EM04')
plt.legend()
plt.ylabel('Probability density')
#plt.show()

#############################################################################
# Plotting with log scale
#############################################################################
ax = sns.distplot(time_series['Precipitation (mm/hr)'], rug=False, hist=False)
ax.set_yscale('log')
ax.set_xscale('log')

sns.distplot(time_series_obs['Precipitation (mm/hr)'], hist=False, rug=False, label = 'Observations').set_xscale('log')
sns.distplot(time_series_pr_01['Precipitation (mm/hr)'], hist=False, rug=False, label = 'EM01').set_xscale('log')
sns.distplot(time_series_pr_04['Precipitation (mm/hr)'], hist=False, rug=False, label = 'EM04').set_xscale('log')
plt.legend()
plt.ylabel('Probability density')
#plt.show()

ax = sns.distplot(time_series_obs['Precipitation (mm/hr)'], hist=False, rug=False, label = 'Observations')
ax = sns.distplot(time_series_pr_01['Precipitation (mm/hr)'], hist=False, rug=False, label = 'EM01')
ax = sns.distplot(time_series_pr_04['Precipitation (mm/hr)'], hist=False, rug=False, label = 'EM04')
ax.set_yscale('log')
ax.set_xscale('log')
plt.legend()
plt.ylabel('Probability density')
#plt.show()

#############################################################################
# Plotting CDF
#############################################################################
kwargs = {'cumulative': True}
sns.distplot(time_series_obs['Precipitation (mm/hr)'], hist_kws=kwargs, kde_kws=kwargs)



