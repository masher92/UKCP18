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
import matplotlib.pyplot as plt

# For extracting the variable name from a variable
def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

em = ['07']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

#############################################
## Load in the data
#############################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
#print(general_filename)
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    #print(filename)
    filenames.append(filename)
print(len(filenames))

filenames =[]
filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 

monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
for cube in monthly_cubes_list:
     for attr in ['creation_date', 'tracking_id', 'history']:
         if attr in cube.attributes:
             del cube.attributes[attr]

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Remove ensemble member dimension
concat_cube = concat_cube[0,:,:,:]
   
# Add clim_season and season year
iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
iris.coord_categorisation.add_season_year(concat_cube,'time', name = "season_year") 

# Find the maximum value in the season_year
cube_max = concat_cube.aggregated_by(['season_year'], iris.analysis.MAX)
# Take one slice
cube_max = cube_max[0,:,:]

# FInd maximum of these values
cube_max.data.max()

qplt.contourf(cube_max)
plt.gca().coastlines()

# Get data in 1D format
data_1d= cube_max.data.reshape(-1)
lats = cube_max.coord('grid_latitude').points
lons = cube_max.coord('grid_longitude').points
lons, lats = np.meshgrid(lons, lats)
lons = lons.reshape(-1)
lats = lats.reshape(-1)

# FInd position of cell with the maximum value
index_of_max = np.argmax(data_1d)

# FInd associated values
lats[index_of_max], lons[index_of_max]
data_1d[index_of_max]

# Find 

max_val = cube_max.extract(iris.Constraint(grid_latitude = 6.180049896240234, grid_longitude =355.21075439453125 ))
print(max_val)
max_val.coord("time").points
max_val.coord("month_number").points
