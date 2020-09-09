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

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

ems_dict = {}
for em in ems:
    em_dict = {}
    jja_max = iris.load('/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_jja_max.nc')[0]
    jja_mean = iris.load('/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_jja_mean.nc')[0]
    jja_percentiles = iris.load('/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_jja_percentiles.nc')[0]
    
    stats = [jja_mean, jja_max, jja_percentiles]
    if em == '01':
        # Create dictionarities to store max/min values and set them to unfeasible values
        max_vals_dict = {}
        min_vals_dict = {}
        for stat in stats:
            if stat == jja_percentiles:
                for i in range(jja_percentiles.shape[0]):
                    stat = jja_percentiles[i]
                    name = 'P' + str(jja_percentiles[i].coord('percentile_over_clim_season').points[0])         
                    name = name.replace(".", "_")
                    max_vals_dict[name] = 0
                    min_vals_dict[name] = 10000
            else:
                name = namestr(stat, globals())[0]
                max_vals_dict[name] = 0
                min_vals_dict[name] = 10000
#        
    # Store all stats values in dictionary
    for stat in stats:
        if stat == jja_percentiles:
            for i in range(jja_percentiles.shape[0]):
                stat = jja_percentiles[i]
                name = 'P' + str(jja_percentiles[i].coord('percentile_over_clim_season').points[0])         
                name = name.replace(".", "_")
                em_dict[name] = stat
                max_vals_dict[name] = stat.data.max() if stat.data.max() > max_vals_dict[name] else max_vals_dict[name]
                min_vals_dict[name] = stat.data.min() if stat.data.min() < min_vals_dict[name] else min_vals_dict[name]      
        else:
            name = namestr(stat, globals())[0]
            em_dict[name] = stat
            max_vals_dict[name] = stat.data.max() if stat.data.max() > max_vals_dict[name] else max_vals_dict[name]
            min_vals_dict[name] = stat.data.min() if stat.data.min() < min_vals_dict[name] else min_vals_dict[name]      
        
    ems_dict[em] = em_dict       
#
#############################################
# Plotting
#############################################
# Create a colourmap                                   
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      

precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="white")

stats = []
for key, value in em_dict.items() :
    stats.append(key)

for stat in stats:
    print(stat)
   # Extract the max, min values
    max_value = max_vals_dict[stat]
    min_value = min_vals_dict[stat]
    em_i = 0
    rows, cols = 4, 3
    fig, ax = plt.subplots(rows, cols,
                           sharex='col', 
                           sharey='row',
                           figsize=(20, 20))
    for row in range(4):
        for col in range(3):
            # Select an ensemble member
            em = ems[em_i]
            print(em)
            em_dict = ems_dict[em]
            # Extract correct stat
            cube = em_dict[stat]
            #Create a 2D grid
            grid = cube[0]
            
            # Plot
            
            # ax[row, col].pcolormesh(lons_2d, lats_2d, region_codes_2d,
            #                       linewidths=3, alpha = 1, cmap = 'tab20')
            #     leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
            #     ax[row, col].tick_params(axis='x', labelsize= 25)
            #     ax[row, col].tick_params(axis='y', labelsize= 25)
            #     #ax[row, col].set_title('The function g', fontsize=5)
            #     em_i = em_i +1
            
            qplt.contourf(ax[row, col], grid,levels = levels,cmap=precip_colormap, extend="both")
            
            
            # fig=plt.figure(figsize=(20,16))
            # levels = np.round(np.linspace(min_value, max_value, 15),2)
            contour = iplt.contourf(grid,levels = levels,cmap=precip_colormap, extend="both")
            plt.gca().coastlines(resolution='50m', color='black', linewidth=2)
            #plt.plot(0.6628091964140957, 1.2979678925914127, 'o', color='black', markersize = 3) 
            #plt.title("JJA mean", fontsize =40) 
            #plt.colorbar(fraction=0.036, pad=0.02)
            cb = plt.colorbar(fraction=0.036, pad=0.02)
            cb.ax.tick_params(labelsize=25)
            em_i = em_i +1
 





