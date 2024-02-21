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

trim_to_leeds = False

# Constraint to only load JJA data
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
uk_gdf = create_uk_outline({'init' :'epsg:3857'})

resolution = '2.2km'
years= range(1995,2015)

##################################################################

##################################################################
for year in years:

    # Create directory to store outputs in
    if resolution =='1km':
        ddir = f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/"
    else:
        ddir = f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/NearestNeighbour/"
    if not os.path.isdir(ddir):
        os.makedirs(ddir)

    filenames =[]
    # Create filepath to correct folder using correct resolution
    if resolution == '1km': 
        general_filename = f'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_{year}*'   
    elif resolution == '2.2km':
        general_filename = f'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_CEH-GEAR-1hr_{year}*'
    elif resolution == '12km':
        general_filename = f'datadir/CEH-GEAR/CEH-GEAR_regridded_12km/NearestNeighbour/rg_CEH-GEAR-1hr_{year}*'
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
    #print(obs_cube) 
    
    ################################################################
    ### Cut the cube to the extent of GDF surrounding UK  
    ################################################################
    obs_cube = trim_to_bbox_of_region_regriddedobs(obs_cube, uk_gdf)
    
    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    print('trimming cube')
    if trim_to_leeds == True:
        if resolution == '2.2km':
            obs_cube = trim_to_bbox_of_region_regriddedobs(obs_cube, leeds_at_centre_gdf)
        else:
              obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)
    else:
        if resolution == '2.2km':
            obs_cube = trim_to_bbox_of_region_regriddedobs(obs_cube, uk_gdf)
        else:
            obs_cube = trim_to_bbox_of_region_obs(obs_cube, uk_gdf)
            
    ################################################################
    ###  Get mask and regrid to the obs cube
    ################################################################
    print("getting mask")
    lsm_cubes_list = iris.load("/nfs/a319/gy17m2a/PhD/datadir/lsm_land-cpm_BI_5km.nc")
    lsm = lsm_cubes_list[0]
    lsm_nn =lsm.regrid(obs_cube,iris.analysis.Nearest())  
    
    # Convert to shape of cube
    broadcasted_lsm_data = np.broadcast_to(lsm_nn.data.data, obs_cube.shape)
    # Convert to integer
    broadcasted_lsm_data_int = broadcasted_lsm_data.astype(int)
    # Reverse the array (it is the opposite way round to the exisitng val/no val mask on the radar data)
    reversed_array = ~broadcasted_lsm_data_int.astype(bool)  
    
    ### Mask the cube using the lsm cube
    masked_cube = iris.util.mask_cube(obs_cube, reversed_array)
    
    ### Compress data (flatten and remove masked values)
    compressed = masked_cube.data.compressed()
    compressed.shape[0]
    print(f" length of the array: {len(compressed)}")
    print(f"min value is: {np.nanmin(compressed)}")
    print(f"max value is: {np.nanmax(compressed)}")
    print(f"mean value is: {np.nanmean(compressed)}")
    
    # Save to file
    np.save(ddir + f'{year}_compressed.npy', compressed) 
    
    
########
# Get the times
########
# Step 2: Get the indices of the non-masked values in the original data
non_masked_indices = np.where(~masked_cube.data.mask)

# Step 3: Extract corresponding time values
time_values = masked_cube.coord('time').points[non_masked_indices[0]]
np.save(ddir + f'timevalues.npy', time_values)     

# Convert to datetimes
# times = [datetime.datetime.fromtimestamp(x).strftime("%x %X") for x in time_values]
# times= [datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in times]
# np.save(ddir + f'timevalues_formatted.npy', times) 