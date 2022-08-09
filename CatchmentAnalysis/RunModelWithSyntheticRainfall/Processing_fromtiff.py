import rasterio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pyplot

# Define filepath
fp = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\6hr_ms_u\6hr_maxspread_depth.Resampled.Terrain.tif"

methods = {'dividetime':"6hr_dt",
           'maxspread': "6hr_ms",
           'singlepeak': "6hr_sp",
           "subpeaktiming": "6hr_sp-t"}

# whether to remove values < 0.1
remove_little_values = True

# Loop through methods and populate dataframes
for variable in ["depth", "velocity"]:
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()
    
    for method_name, shortening in methods.items():    # Define filepath
        print(method_name, shortening)
        fp = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\{}_u\6hr_{}_{}.Resampled.Terrain.tif".format(shortening, method_name, variable)
        with rasterio.open(fp, 'r') as ds:
           arr = ds.read()  # read all raster values
        # Convert to arry
        raster = np.array(arr)[0,:,:]
        # Find the number of cells with each value, and convert to dataframe
        unique, counts = np.unique(raster, return_counts=True)
        df = pd.DataFrame({'values': unique, 'counts':counts})
        # remove values below 0.1 if necessary
        if remove_little_values == True:
            df = df[df['values']>0.1]    
            unique = unique[(unique>0.1)]
        # Cut by depth bins
        if variable == 'depth':
            df['bins']= pd.cut(unique, bins=[0,0.1,0.15,0.30,0.60, 0.9, 1.2,5,99], right=False)
        elif variable == 'velocity':
            df['bins']= pd.cut(unique, bins=[0,0.25,0.50,1,2,3], right=False)
        groups = df.groupby(['bins']).sum()
        groups  = groups.reset_index()
        # Find the sum
        total_n_cells = groups ['counts'].sum()
        # Find the number of cells in each group as a proportion of the total
        groups['Proportion'] = round((groups['counts']/total_n_cells) *100,1)
        # Add values to dataframes
        counts_df[method_name] = groups['counts']
        proportions_df[method_name] = groups['Proportion']

    # Reset index to show the groups
    counts_df.reset_index(inplace=True)
    proportions_df.reset_index(inplace=True)

    if variable == 'depth':
        counts_df['index'] = ['0-0.1m', '0.1-0.15m', '0.15-0.3m', '0.3-0.6m', '0.6-0.9m', '0.9-1.2m', '1.2-5m', '5m+']
        proportions_df['index'] = ['0-0.1m', '0.1-0.15m', '0.15-0.3m', '0.3-0.6m', '0.6-0.9m', '0.9-1.2m', '1.2-5m', '5m+']
    elif variable == 'velocity':
        counts_df['index'] = ['0-0.25m/s', '0.25-0.5m/s', '0.5-1m/s','1-2m/s', '2-3m/s']
        proportions_df['index'] = ['0-0.25m/s', '0.25-0.5m/s', '0.5-1m/s','1-2m/s','2-3m/s']

    # Set colors for plots
    colors = ['black', 'lightslategrey', 'darkslategrey', 'darkgreen']
    
    # plot count bar chart
    counts_df.plot(x='index',kind='bar', stacked=False, width=0.8, legend = True, color = colors)
    plt.xticks(rotation=30)
    plt.xlabel('Flood {}'.format(variable))
    plt.ylabel('Number of cells')
    
    # plot proportions bar chart
    proportions_df.plot(x='index', kind='bar', stacked=False, width=0.8, legend = True, color = colors)
    plt.xticks(rotation=30)
    plt.xlabel('Flood {}'.format(variable))
    plt.ylabel('Proportion of cells')
    
src = rasterio.open(fp)
pyplot.imshow(src.read(1), cmap='pink')    
fp2 = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\6hr_dt_u\6hr_dividetime_velocity.Resampled.Terrain.tif"
src2 = rasterio.open(fp2)

srcnew = src.read(1) - src2.read(1)
pyplot.imshow(srcnew, cmap='pink')    
import arcpy

raster_path = 'C:/blablabla/raster_bla.tif'
raster1 = arcpy.Raster(raster_path)
raster_data = arcpy.RasterToNumPyArray(raster)

import rasterio
pyplot.imshow(src.read(1), cmap = 'terrain')


arr_bldg = src.read(1)
arr_elev = src2.read(1)
arr_height = arr_elev - arr_bldg
pyplot.imshow(msk, cmap='pink')   

r = src.read(1, masked=True)
r
pyplot.imshow(src.read(1), cmap='pink')  


source_raster_path = fp
distination_raster_path = "fixed_example.tif"
with rasterio.open(source_raster_path, "r+") as src:
    src.nodata = np.nan # set the nodata value
    profile = src.profile
    profile.update(
            dtype=rasterio.uint8,
            compress='lzw'
    )

    with rasterio.open(distination_raster_path, 'w',  **profile) as dst:
        for i in range(1, src.count + 1):
            band = src.read(i)
            # band = np.where(band!=1,0,band) # if value is not equal to 1 assign no data value i.e. 0
            band = np.where(band==0,0,band) # for completeness
            dst.write(band,i)
         
#####################################
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rio
from rasterio.plot import show
from rasterio.plot import show_hist
#from shapely.geometry import Polygon, mapping
from rasterio.mask import mask
import earthpy as et
import earthpy.spatial as es
import earthpy.plot as ep

from matplotlib.colors import ListedColormap
import matplotlib.colors as colors


with rio.open(fp2) as src:
    lidar_dem_im2 = src.read(1, masked=True)
    sjer_ext = rio.plot.plotting_extent(src)

with rio.open(fp) as src:
    lidar_dem_im = src.read(1, masked=True)
    sjer_ext = rio.plot.plotting_extent(src)


lidar_chm = lidar_dem_im2 - lidar_dem_im
ep.plot_bands(lidar_chm,
              cmap='viridis',
              title="Lidar Canopy Height Model (CHM)\n Tree Height For Your Field Site From Remote Sensing Data!")
plt.show()


import arcpy
from arcpy.sa import *
f1 = arcpy.Raster("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_dt_u/6hr_dividetime_velocity.Resampled.Terrain.tif")
