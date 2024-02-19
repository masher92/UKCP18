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

##################################################################
# Trimming to region
##################################################################
for resolution in ["1km" ]:
    print(resolution)
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
        general_filename = 'datadir/CEH-GEAR/CEH-GEAR_reformatted/*'   
    elif resolution == '2.2km':
        general_filename = 'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/NearestNeighbour/*'
    elif resolution == '12km':
        general_filename = 'datadir/CEH-GEAR/CEH-GEAR_regridded_12km/NearestNeighbour/*'
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
    # Once across all ensemble members, save a numpy array storing
    # the timestamps to which the data refer
    ################################################################  
    times = obs_cube.coord('time').points
    # Convert to datetimes
    times = [datetime.datetime.fromtimestamp(x).strftime("%x %X") for x in times]
    times= [datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in times]
    
    # Convert to datetime - doesnt work due to 30 days in Feb
    np.save(f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/timestamps.npy", times) 
    
    ################################################################
    # Get mask and regrid to the obs cube
    ################################################################  
    if trim_to_leeds == False:
        print("getting mask")
        monthly_cubes_list = iris.load("/nfs/a319/gy17m2a/PhD/datadir/lsm_land-cpm_BI_5km.nc")
        lsm = monthly_cubes_list[0]
        lsm_nn =lsm.regrid(obs_cube,iris.analysis.Nearest())   

        # Save it in 1D form
        mask = lsm_nn.data.data.reshape(-1)
        np.save(ddir + "lsm.npy", mask) 
    
    ################################################################
    # Get data as array
    ################################################################      
    start = time.time()
    data = obs_cube.data.data
    end= time.time()
    print(f"Time taken to load cube {round((end-start)/60,1)} minutes" )    
        
    start = time.time()
    flattened_data = data.flatten()
    end= time.time()
    print(f"Time taken to flatten cube {round((end-start)/60,1)} minutes" )

    ### Save as numpy array
    print("saving data")
    if trim_to_leeds == True:
        np.save(ddir + "leeds-at-centre_jja.npy", flattened_data)   
    else:
        np.save(ddir + "uk_jja.npy", flattened_data) 
    print("saved data")