import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import os
import geopandas as gpd
import time 
import sys
import iris.quickplot as qplt
import cartopy.crs as ccrs
import matplotlib 
import iris.plot as iplt
from matplotlib.ticker import ScalarFormatter
import pandas as pd

#root_fp = "/nfs/a319/gy17m2a/"
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/PlotPDFs')
from PDF_plotting_functions import *

##############################################################################
# Reading in data 
##############################################################################
rf_df = pd.read_csv(root_fp + "Outputs/CEH-GEAR_reformatted/rf_df.csv")
rf_df.rename(columns={'Rainfall':'Precipitation (mm/hr)'}, inplace=True)
rf_df = rf_df.dropna()
#rf_wethours_df = rf_df[rf_df['Precipitation (mm/hr)'] > 0.1]

rg_df = pd.read_csv(root_fp + "Outputs/CEH-GEAR_regridded_2.2km/rg_df.csv")
rg_df.rename(columns={'Rainfall':'Precipitation (mm/hr)'}, inplace=True)
rg_df = rg_df.dropna()
#rg_wethours_df = rg_df[rg_df['Precipitation (mm/hr)'] > 0.1]

##############################################################################
# Setting up dictionary
##############################################################################
my_dict = {}
my_dict['Original 1km'] = rf_wethours_df
my_dict['Regridded 2.2km'] = rg_wethours_df

my_dict['Original 1km'] = rf_df
my_dict['Regridded 2.2km'] = rg_df

##############################################################################
# Plotting
##############################################################################
x_axis = 'linear'
y_axis = 'log'
bin_nos =40
bins_if_log_spaced= bin_nos

# Equal spaced   
equal_spaced_histogram(my_dict, bin_nos, 'log', 'log')

# Log spaced histogram
log_spaced_histogram(my_dict, bin_nos,x_axis, y_axis)    
 
# Fractional contribution
fractional_contribution(my_dict, bin_nos,x_axis, y_axis) 
             
# Log histogram with adaptation     
log_discrete_histogram(my_dict, 20,x_axis, y_axis) 


##########################################################################
# Percentile plots
##########################################################################
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
for key, value in my_dict.items():
    df = my_dict[key]
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
navy_patch = mpatches.Patch(color='navy', label='Original 1km')
red_patch = mpatches.Patch(color='firebrick', label='Regridded 2.2km')

for key, value in my_dict.items():
    print(key)
    if key == 'Original 1km':
        plt.plot(test[key], color = 'navy')
    if key == 'Regridded 2.2km':
        plt.plot(test[key], color = 'firebrick')
    plt.xlabel('Percentile')
    plt.ylabel('Precipitation (mm/hr)')
    plt.legend(handles=[red_patch, navy_patch])
    plt.yscale('log')
    plt.xticks(rotation = 23)


