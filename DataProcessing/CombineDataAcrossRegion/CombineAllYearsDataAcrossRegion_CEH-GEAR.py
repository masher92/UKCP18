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

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

##################################################################
# Trimming to region
##################################################################

for resolution in [ '1km']:
    print(resolution)
    # Create directory to store outputs in
    if resolution =='1km':
        ddir = f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/leeds-at-centre/"
    else:
        ddir = f"ProcessedData/TimeSeries/CEH-GEAR/{resolution}/NearestNeighbour/leeds-at-centre/"
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
        # print(filename)
        filenames.append(filename)
    print(len(filenames))
       
    monthly_cubes_list = iris.load(filenames,'rainfall_amount')
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
     
    # Test plotting - one timeslice
    #iplt.pcolormesh(obs_cube[120])
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(obs_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = obs_cube.extract(iris.Constraint(clim_season = 'jja'))
       
    # ################################################################
    # # Once across all ensemble members, save a numpy array storing
    # # the timestamps to which the data refer
    # ################################################################  
    times = jja.coord('time').points
    # Convert to datetimes
    times = [datetime.datetime.fromtimestamp(x).strftime("%x %X") for x in times]
    times= [datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in times]
    
    # Convert to datetime - doesnt work due to 30 days in Feb
    np.save(f"ProcessedData/TimeSeries/CEH-GEAR/timestamps.npy", times) 
    
    # ################################################################
    # # Create a numpy array containing all the precipitation values from across
    # # all 20 years of data and all positions in the cube
    # ################################################################
    # Define length of variables defining spatial positions
    lat_length= jja.shape[1]
    lon_length= jja.shape[2]
    print("Defined length of coordinate dimensions")
    print(lat_length, lon_length)        
        
    # # # Load data
    print("Loading data")  
    data = jja.data
    print("Loaded data")
    
    # Create an empty array to fill with data
    all_the_data = np.array([])
    
    print("entering loop through coordinates")
    total = 0
    for i in range(0,lat_length): 
        for j in range(0,lon_length):
            # Print the position
            print(i,j)
            # Define the filename
            # filename = ddir + "{}_{}.npy".format(i,j)
            # If a file of this name already exists saved, then read in this file  
            #if os.path.isfile (filename):
            #    print("File exists")
            #    data_slice = np.load(filename)
            # IF file of this name does not exist, then create by slicing data
            #else:
            print("File does not exist")                
            # Take slice from loaded data
            data_slice = data[:,i,j]
            # Remove mask
            data_slice = data_slice.data
            # Save to file
            # np.save(filename, data_slice) 
            # total = total + data_slice.shape[0]
    
            # Add the slice to the array containing all the data from all the locations
            all_the_data = np.append(all_the_data,data_slice)
    
    ### Save as numpy array
    print("saving data")
    np.save(ddir + "leeds-at-centre_jja.npy", all_the_data)   
    print("saved data")