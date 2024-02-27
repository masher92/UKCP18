##################################################################
# This Script:
#    - Gets all 30 mins radar files for one year
#    - Joins them and masks out values over the sea
#    - Gets a 1D array of the data and removes masked out (over the sea
#      values) and np.nan values
##################################################################


##################################################################
# SET UP ENVIRONMENT
##################################################################
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
from iris.experimental.equalise_cubes import equalise_attributes

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, '/nfs/a319/gy17m2a/PhD/Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

resolution = '2.2km'
trim_to_leeds = False

# # Constraint to only load JJA data
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
uk_gdf = create_uk_outline({'init' :'epsg:3857'})
gb_gdf = create_gb_outline({'init' :'epsg:3857'})

##################################################################
# FOR ONE YEAR AT A TIME
##################################################################
for year in range(2010,2011):
    print(year)

    # Create directory to store outputs in and get general filename to load files from
    if resolution =='1km':
        ddir = f"ProcessedData/TimeSeries/NIMROD/30mins/OriginalFormat_1km/"
        general_filename = f'datadir/NIMROD/30mins/OriginalFormat_1km/{year}/*'      
    elif resolution == '2.2km':
        ddir = f"ProcessedData/TimeSeries/NIMROD/30mins/NIMROD_regridded_2.2km/"
        general_filename = f'datadir/NIMROD/30mins/NIMROD_regridded_2.2km/NearestNeighbour/{year}/*'      
    elif resolution == '12km':
        ddir = f"ProcessedData/TimeSeries/NIMROD/30mins/NIMROD_regridded_12km/"    
        general_filename = f'datadir/NIMROD/30mins/NIMROD_regridded_12km/NearestNeighbour/{year}/*'      
    if not os.path.isdir(ddir):
        os.makedirs(ddir)

    # GET LIST OF ALL FILENAMES FOR THIS YEAR
    filenames =[]
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        # print(filename)
        filenames.append(filename)
    print(f"loading {len(filenames)} filenames")
    sorted_list = sorted(filenames)

    # LOAD THE DATA
    monthly_cubes_list = iris.load(sorted_list, in_jja)
      
    ##################################################################
    # CLEAN AND JOIN THE DATA
    ##################################################################
    # Get rid of any files which don't have the time dimension
    is_to_delete = []
    for i in range(0,len(monthly_cubes_list) ):
        if len(monthly_cubes_list[i].shape) <3:
            is_to_delete.append(i)
    for i in is_to_delete:
        print(f"deleting cube {i} as it only had one dimension")
        del monthly_cubes_list[i] 

    for i in range(0, len(monthly_cubes_list)):
        try:
            monthly_cubes_list[i].coord('forecast_period')
            monthly_cubes_list[i].remove_coord('forecast_period')
        except:
            pass
        try:
            monthly_cubes_list[i].coord('forecast_reference_time')
            monthly_cubes_list[i].remove_coord('forecast_reference_time')
        except:
            pass           
        try:
            monthly_cubes_list[i].coord('hour')
            monthly_cubes_list[i].remove_coord('hour')
        except:
            pass   

    # Try to make attributes the same
    iris.util.equalise_attributes(monthly_cubes_list)   
    
    # CONVERT TO FLOAT64
    for i in range(0, len(monthly_cubes_list)):
        monthly_cubes_list[i].data = monthly_cubes_list[i].data.astype('float64')

    model_cube = monthly_cubes_list.concatenate_cube()

    # ### Trim to GB
    if resolution  == '2.2km':
        model_cube = trim_to_bbox_of_region_regriddedobs(model_cube, gb_gdf)
    else:
        model_cube = trim_to_bbox_of_region_obs(model_cube, gb_gdf)
    
    print(model_cube.coord('time')[0])
    print(model_cube.coord('time')[-1])
    
    # ### Get the mask
    print("getting mask")
    if resolution =='2.2km':
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_2.2km_GB_Mask.npy")
    else:
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_12km_GB_Mask.npy")
    masked_cube_data = model_cube * gb_mask[np.newaxis, :, :]

    # APPLY THE MASK
    reshaped_mask = np.tile(gb_mask, (model_cube.shape[0], 1, 1))
    reshaped_mask = reshaped_mask.astype(int)
    reversed_array = ~reshaped_mask.astype(bool)

    # Mask the cube
    masked_cube = iris.util.mask_cube(model_cube, reversed_array)

    # ### Check the mask
    # iplt.contourf(masked_cube[10])
    # plt.gca().coastlines(resolution='10m', color='black', linewidth=0.5);
    # Save
    iris.save(masked_cube, ddir + f'{year}_maskedcube.nc')      

    # Check the plotting
    # iplt.contourf(masked_cube[10])
    # plt.gca().coastlines(resolution='10m', color='black', linewidth=0.5);

    # Get rid of negative values
    compressed = masked_cube.data.compressed()
    compressed.shape[0]

    ########
    # Get the times
    ########
    # Step 2: Get the indices of the non-masked values in the original data
    non_masked_indices = np.where(~masked_cube.data.mask)

    # Step 3: Extract corresponding time values
    time_values = masked_cube.coord('time').points[non_masked_indices[0]]

    # Save to file
    np.save(ddir + f'timevalues_{year}.npy', time_values) 
    np.save(ddir + f'compressed_{year}.npy', compressed) 
