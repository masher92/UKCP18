import iris
import glob
import datetime
from iris.time import PartialDateTime
import sys
#import xarray as xr
import os
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)

year = sys.argv[1]

# Create path to files containing functions
sys.path.insert(0, '/nfs/a319/gy17m2a/PhD/Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline('epsg:3857')


radardir = f"/nfs/a319/gy17m2a/PhD/datadir/NimRod/{year}/"
file_list=glob.glob(radardir +"*.dat")
# print(file_list)
print("Hello")


cube_list = iris.load(file_list)
cube_list

model_cube = cube_list.concatenate_cube()
model_cube

model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
print(model_cube)
print(model_cube.shape)


iris.save(model_cube,radardir + sorted_list[0][42:81] + '.nc')