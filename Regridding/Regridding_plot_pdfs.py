# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 15:15:35 2020

@author: gy17m2a
"""
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

root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

from PDF_plotting_functions import *

##############################################################################
# Reading in data 
##############################################################################
rf_df = pd.read_csv(root_fp + "Outputs/CEH-GEAR_reformatted/rf_df.csv")
rf_df.rename(columns={'Rainfall':'Precipitation (mm/hr)'}, inplace=True)
rf_df = rf_df.dropna()
rf_wethours_df = rf_df[rf_df['Precipitation (mm/hr)'] > 0.1]

rg_df = pd.read_csv(root_fp + "Outputs/CEH-GEAR_regridded_2.2km/rg_df.csv")
rg_df.rename(columns={'Rainfall':'Precipitation (mm/hr)'}, inplace=True)
rg_df = rg_df.dropna()
rg_wethours_df = rg_df[rg_df['Precipitation (mm/hr)'] > 0.1]

##############################################################################
# Setting up dictionary
##############################################################################
my_dict = {}
my_dict['Reformatted'] = rf_wethours_df
my_dict['Regridded'] = rg_wethours_df

##############################################################################
# Plotting
##############################################################################
keys = list(my_dict.keys())
navy = mpatches.Patch(color='navy', label=str(keys[0]))
firebrick = mpatches.Patch(color='firebrick', label=str(keys[1]))

x_axis = 'linear'
y_axis = 'log'
bin_nos =60
bins_if_log_spaced= bin_nos


# Equal spaced   
equal_spaced_histogram(my_dict, bin_nos, x_axis, y_axis)

# Log spaced histogram
log_spaced_histogram(my_dict, bin_nos,x_axis, y_axis)    
 
# Fractional contribution
fractional_contribution(my_dict, bin_nos,x_axis, y_axis) 
             
# Log histogram with adaptation     
log_discrete_histogram(my_dict, bin_nos,x_axis, y_axis) 
 