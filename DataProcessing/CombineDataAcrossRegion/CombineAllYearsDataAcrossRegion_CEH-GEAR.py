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
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, '/nfs/a319/gy17m2a/PhD/Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Constraint to only load JJA data
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
uk_gdf = create_uk_outline({'init' :'epsg:3857'})
gb_gdf = create_gb_outline({'init' :'epsg:3857'})

resolution = '1km'
years= range(1990,2015)

##################################################################
# Loop through the years
##################################################################
for year in years:
     # Create directory to store outputs in
    if resolution =='1km':
        ddir = f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/"
    else:
        ddir = f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/AreaWeighted/"
    if not os.path.isdir(ddir):
        os.makedirs(ddir)

    filenames =[]
    # Create filepath to correct folder using correct resolution
    if resolution == '1km': 
        general_filename = f'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_{year}*'   
    elif resolution == '2.2km':
        general_filename = f'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_CEH-GEAR-1hr_{year}*'
    elif resolution == '12km':
        general_filename = f'datadir/CEH-GEAR/CEH-GEAR_regridded_12km/AreaWeighted/rg_rf_CEH-GEAR-1hr_{year}*'
    print(general_filename)

    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        filenames.append(filename)
    print(len(filenames))

    monthly_cubes_list = iris.load(filenames, in_jja)    
    #print(monthly_cubes_list)

    # Concatenate the cubes into one
    print('Concatenating cube')
    obs_cube = monthly_cubes_list.concatenate_cube()     
    print(obs_cube.shape) 

    ########################################################################
    ########################################################################
    # ### Get the mask
    ########################################################################
    ########################################################################
    print("getting mask")
    if resolution =='2.2km':
        obs_cube = trim_to_bbox_of_region_regriddedobs(obs_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_2.2km_GB_Mask.npy")
    elif resolution == '1km':
        obs_cube = trim_to_bbox_of_region_regriddedobs(obs_cube, gb_gdf)
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_1km_GB_Mask.npy")
    else:
        obs_cube = trim_to_bbox_of_region_obs(obs_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_12km_GB_Mask.npy")
    masked_cube_data = obs_cube * gb_mask[np.newaxis, :, :]

    print(obs_cube.shape) 

    # APPLY THE MASK
    reshaped_mask = np.tile(gb_mask, (obs_cube.shape[0], 1, 1))
    reshaped_mask = reshaped_mask.astype(int)
    reversed_array = ~reshaped_mask.astype(bool)

    # Mask the cube
    masked_cube = iris.util.mask_cube(obs_cube, reversed_array)

    ########################################################################
    ########################################################################
    # Get time values
    ########################################################################
    ########################################################################
    #iplt.contourf(masked_cube[10])
    # plt.gca().coastlines(resolution='10m', color='black', linewidth=0.5);

    # Get rid of negative values
    compressed = masked_cube.data.compressed()
    print(compressed.shape[0])

    ########
    # Get the times
    ########
    # Step 2: Get the indices of the non-masked values in the original data
    non_masked_indices = np.where(~masked_cube.data.mask)

    # Step 3: Extract corresponding time values
    time_values = masked_cube.coord('time').points[non_masked_indices[0]]

    # Save to file
    np.save(ddir + f'{year}_timevalues.npy', time_values) 
    np.save(ddir + f'{year}_compressed.npy', compressed) 
    iris.save(masked_cube, ddir + f'{year}_masked_cube.nc') 