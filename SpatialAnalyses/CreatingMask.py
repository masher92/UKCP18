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
import numpy.ma as ma
import pandas as pd

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)
em = '01'

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

# Load required geodataframes
#wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
uk_gdf= create_uk_outline({'init' :'epsg:3857'})

# Load a cube
jja_max = iris.load('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_jja_max.nc')[0]
#jja_max = trim_to_bbox_of_region(jja_max, wider_northern_gdf)
grid = jja_max[0]
#iplt.contourf(grid)
#plt.gca().coastlines()

# Create the mask
#mask = mask_by_region(grid, wider_northern_gdf)
# Create the mask
uk_mask = mask_by_region(grid, uk_gdf)

# Save the numpy array 
#np.save('Outputs/RegionalMasks/wider_northern_region_mask.npy', mask)
# Save the numpy array 
np.save('Outputs/RegionalMasks/uk_mask.npy', mask)
