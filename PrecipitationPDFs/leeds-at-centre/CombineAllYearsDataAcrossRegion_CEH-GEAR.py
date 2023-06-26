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
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

resolution =  '2.2km' # ['1km', '2.2km', '12km']

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

##################################################################
# Trimming to region
##################################################################

for resolution in ['1km', '2.2km', '12km']:
    
    # Create directory to store outputs in
    if resolution =='1km':
      ddir = "Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/".format(resolution)
    else:
      ddir = "Outputs/TimeSeries/CEH-GEAR/{}/NearestNeighbour/leeds-at-centre/".format(resolution)
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
        print(filename)
        filenames.append(filename)
    print(len(filenames))
       
    monthly_cubes_list = iris.load(filenames,'rainfall_amount')
    print(monthly_cubes_list)
    
    # Concatenate the cubes into one
    print('Concatenating cube')
    obs_cube = monthly_cubes_list.concatenate_cube()     
    print(obs_cube) 
    
    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    print('trimming cube')
    if resolution == '2.2km':
        obs_cube = trim_to_bbox_of_region_regriddedobs(obs_cube, leeds_at_centre_gdf)
    else:
          obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)
     
    # Test plotting - one timeslice
    #iplt.pcolormesh(obs_cube[120])
    
    # Save trimmed netCDF to file    
    print('saving cube')
    #iris.save(obs_cube, "Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/leeds-at-centre.nc".format(resolution)) 
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(obs_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = obs_cube.extract(iris.Constraint(clim_season = 'jja'))
    
    #print('saving jja cube')
    #iris.save(jja, "Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/{}/jja_leeds-at-centre.nc".format(resolution,em))
    
    # ################################################################
    # # Once across all ensemble members, save a numpy array storing
    # # the timestamps to which the data refer
    # ################################################################  
    times = obs_cube.coord('time').points
    # Convert to datetimes
    times = [datetime.datetime.fromtimestamp(x).strftime("%x %X") for x in times]
    times= [datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in times]
    
    # Convert to datetime - doesnt work due to 30 days in Feb
    #times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
    np.save(ddir + "timestamps.npy", times) 
    
    ## Also save a dataframe, which contains a flag for whether that
    # date is within JJA
    jja_times = jja.coord('time').points
    jja_times = [datetime.datetime.fromtimestamp(x).strftime("%x %X") for x in jja_times]
    jja_times= [datetime.datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in jja_times]
    
    # Create dataframe showing which dates in JJA data and which not
    jja_times_df = pd.DataFrame({'times':jja_times, 'in_jja': 1})
    times_df = pd.DataFrame({'times':times, 'Value': 1})
    
    combined_times = times_df.merge(jja_times_df, how = 'outer')
    del combined_times['Value']
    if resolution == '1km':
        combined_times.to_csv("Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/timestamps_jjaflag.csv".format(resolution), index = False)    
    elif resolution in ['2.2km', '12km']:
        combined_times.to_csv("Outputs/TimeSeries/CEH-GEAR/{}/NearestNeighbour/leeds-at-centre/timestamps_jjaflag.csv".format(resolution), index = False)    
          
        
        
    # ################################################################
    # # Create a numpy array containing all the precipitation values from across
    # # all 20 years of data and all positions in the cube
    # ################################################################
    # Define length of variables defining spatial positions
    lat_length= obs_cube.shape[1]
    lon_length= obs_cube.shape[2]
    print("Defined length of coordinate dimensions")
    print(lat_length, lon_length)        
        
    # # # Load data
    print("Loading data")  
    data = obs_cube.data
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
            filename = ddir + "{}_{}.npy".format(i,j)
            # If a file of this name already exists saved, then read in this file  
            if os.path.isfile (filename):
                print("File exists")
                data_slice = np.load(filename)
            # IF file of this name does not exist, then create by slicing data
            else:
                print("File does not exist")                
                # Take slice from loaded data
                data_slice = data[:,i,j]
                # Remove mask
                data_slice = data_slice.data
                # Save to file
                np.save(filename, data_slice) 
            total = total + data_slice.shape[0]
    
            # Add the slice to the array containing all the data from all the locations
            all_the_data = np.append(all_the_data,data_slice)
    
    ### Save as numpy array
    print("saving data")
    np.save(ddir + "leeds-at-centre.npy", all_the_data)   
    print("saved data")