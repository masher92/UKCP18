import iris.coord_categorisation
import iris
import numpy as np
import os
import geopandas as gpd
import sys
import matplotlib 
import numpy.ma as ma
import warnings
import iris.quickplot as qplt
import iris.plot as iplt
import cartopy.crs as ccrs
from matplotlib import colors
import glob as glob
import datetime
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# Set up path to root directory
root_fp = "/nfs/a161/gy17m2a/PhD/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, '/nfs/a319/gy17m2a/PhD/Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Constraint to only load JJA data
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)
season='wholeyear'


##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
gb_gdf = create_gb_outline({'init' :'epsg:3857'})

resolution = '2.2km_regridded'
years= range(2001,2020)

##################################################################
# Loop through the years
##################################################################
year=sys.argv[1]
# Create directory to store outputs in
if resolution =='1km_reformatted':
    ddir = f"/nfs/a319/gy17m2a/PhD/ProcessedData/TimeSeries/CEH-GEAR/{resolution}/"
else:
    ddir = f"/nfs/a319/gy17m2a/PhD/ProcessedData/TimeSeries/CEH-GEAR/{resolution}/AreaWeighted/"
if not os.path.isdir(ddir):
    os.makedirs(ddir)
if not os.path.isfile(ddir + f'{year}_compressed_GB_{season}.npy'):
    filenames =[]
    # Create filepath to correct folder using correct resolution
    if resolution == '1km_reformatted': 
        general_filename = f'datadir/CEH-GEAR/1km_reformatted/CEH-GEAR-1hr-v2_{year}*'   
    elif resolution == '2.2km_regridded':
        general_filename = f'datadir/CEH-GEAR/2.2km_regridded/AreaWeighted/CEH-GEAR-1hr-v2_{year}*'
    elif resolution == '12km_regridded':
        general_filename = f'datadir/CEH-GEAR/12km_regridded/AreaWeighted/CEH-GEAR-1hr-v2_{year}*'
    print(general_filename)

    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        filenames.append(filename)
    print(len(filenames))

    monthly_cubes_list = iris.load(filenames) 
    obs_cube = monthly_cubes_list.concatenate_cube()     
    print(obs_cube.shape)
    print(obs_cube.coord('time').points)

    # Get rid of negative values
    compressed = obs_cube.data.compressed()
    print(f"over UK shape is {compressed.shape[0]}")

    np.save(ddir + f'{year}_compressed_UK_{season}.npy', compressed)         

    ########################################################################
    ########################################################################
    # ### Get the mask
    ########################################################################
    ########################################################################
    print("getting mask")
    if resolution =='2.2km_regridded':
        obs_cube = trim_to_bbox_of_region_obs(obs_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_2.2km_GB_Mask.npy")
    elif resolution == '1km_reformatted':
        obs_cube = trim_to_bbox_of_region_obs(obs_cube, gb_gdf,  'projection_y_coordinate', 'projection_x_coordinate')
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/CEH-GEAR_1km_GB_Mask.npy")
    else:
        obs_cube = trim_to_bbox_of_region_obs(obs_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_12km_GB_Mask.npy")
    masked_cube_data = obs_cube * gb_mask[np.newaxis, :, :]    

    # APPLY THE MASK
    reshaped_mask = np.tile(gb_mask, (obs_cube.shape[0], 1, 1))
    reshaped_mask = reshaped_mask.astype(int)
    reversed_array = ~reshaped_mask.astype(bool)

    # Mask the cube
    masked_cube = iris.util.mask_cube(obs_cube, reversed_array)

    # Get rid of negative values
    compressed = masked_cube.data.compressed()
    print(f"over GB shape is {compressed.shape[0]}")

    np.save(ddir + f'{year}_compressed_GB_{season}.npy', compressed) 
else:
    print("exists")