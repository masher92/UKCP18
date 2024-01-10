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

cube_list = iris.load(file_list)
cube_list

try:
    # Merge the list        
    model_cube = cube_list.concatenate_cube()
    # print(out_cube)
    
except:
    #print("Sorting atttributes")
    # Create a list of all the cubes which have the same attribute 
    split_cubes = list(cube_list[0].slices_over('time'))

    # Add to that list the cubes which don't have the same attribute
    for i in range(1,len(cube_list)):
        print(i)
        split_cubes = split_cubes + list(cube_list[i].slices_over('time'))

    # Go through the list of cubes and delete the trouble making attribute
    for i in range(1,len(split_cubes)):
        if 'Probability methods' in split_cubes[i].attributes:
            # print("Deleting attribute")
            del split_cubes[i].attributes['Probability methods']

    # Merge the list        
    model_cube = iris.cube.CubeList(split_cubes).merge_cube()
    #print(model_cube)

model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
print(model_cube.shape)

iris.save(model_cube,radardir + file_list[0][42:81] + '.nc')