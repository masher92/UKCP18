import pandas as pd
import numpy as np
#import netCDF4 as nc
import matplotlib.pyplot as plt
from scipy import stats
from scipy.stats import genextreme as gev


ts = pd.read_csv("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/TimeSeries_csv/Armley/2.2km/EM01_1980-2001.csv")
ts['date'] = pd.to_datetime(ts['Date_Formatted'])
ts['year'] = ts['date'].dt.year

# Remvoe columns with Nas
ts = ts[ts['year'].notna()]

# Find maximum values in each year
maxvalues = ts.groupby(['year'], as_index=False)['Precipitation (mm/hr)'].max()

# calculate GEV fit
fit = gev.fit(maxvalues['Precipitation (mm/hr)'])

# GEV parameters from fit
c, loc, scale = fit
fit_mean= loc
min_extreme,max_extreme = gev.interval(0.99,c,loc,scale) 

# evenly spread x axis values for pdf plot
x = np.linspace(min(maxvalues['Precipitation (mm/hr)']),max(maxvalues['Precipitation (mm/hr)']),200)

# plot distribution
fig,ax = plt.subplots(1, 1)
plt.plot(x, gev.pdf(x, *fit))
plt.hist(maxvalues['Precipitation (mm/hr)'],30,normed=True,alpha=0.3)





shape, loc, scale = (-0.1, 10, 1.) 
rvs = stats.genextreme.rvs(shape, loc=loc, scale=scale, size=1000) 
print (stats.genextreme.fit(rvs))


fit = gev.fit(maxvalues['Precipitation (mm/hr)'])