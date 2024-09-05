'''
This file loads CEH-GEAR data over the 'Leeds-at-centre' region which is either:
  - Reformatted
  - Regridded using nearest neighbour interpolation
  - Regridded using linear interpolation
  
It creates a numpy array which contains all the values from all the grid cells across all the years of data
'''

import numpy as np
import os
import sys
import iris.plot as iplt
from datetime import datetime    

################################################################
# Define variables and set up environment
################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from PDF_plotting_functions import *
from Spatial_geometry_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *

################################################################
# Create the spatial datafiles needed
################################################################   
# Create region with Leeds at the centre
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:27700'})
# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})

# Define string which is used to establish the filepath to the files 
# containing the regridded/reformatted files  
strings_dict  = {'datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_': '1km',
            'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/LinearRegridding/rg_': '2.2km/LinearRegridding',
             'datadir/CEH-GEAR/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_': '2.2km/NearestNeighbour'}

for string1, string2 in strings_dict.items():
    print(string1)
    print(string2)

    # Define target_crs, dependent on whether using reformatted or regridded data
    if string1 =='datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_':
        target_crs = {'init' :'epsg:27700'}
    else:
        target_crs = {'init' :'epsg:4326'}
    
    ################################################################
    # Reads in all monthly (either regridded or reformatted) CEH-GEAR data files 
    # Create a cube trimmed to the oputline of the square area surrounding Leeds
    # Containing this data over time 
    ################################################################   
    cube = create_trimmed_cube(leeds_at_centre_gdf, string1, target_crs)
    print ("created cube")
    
    ################################################################
    # Create and save array containing a record of all the time stamps
    # which the data values refer to 
    ################################################################   
    # Extract the times that the observations refer to
    times = cube.coord('time').points
    # Convert to datetimes
    times = [datetime.fromtimestamp(x).strftime("%x %X") for x in times]
    times= [datetime.strptime(x, '%m/%d/%y %H:%M:%S') for x in times]
    times_df = pd.DataFrame({'Date' : times})
    
    # Save to file
    # Constructs filepaths for saving to
    np.save("Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/timestamps.npy".format(string2), 
            times)  
    
    ################################################################
    # Trim even more for testing
    ################################################################
    #cube= cube[:,1:2, 1:2]
    # test plotting
    iplt.pcolormesh(cube[18,:,:])
    
    ################################################################
    # Create a numpy array containing all the precipitation values from across
    # all 20 years of data and all positions in the cube
    ################################################################
    # # Load data
    print("Loading data")
    data = cube.data
    print("Loaded data")
    
    # # Define length of variables defining spatial positions
    lat_length= cube.shape[1]
    lon_length= cube.shape[2]
    print("Defined length of coordinate dimensions")
    print(lat_length, lon_length)
    
    # Create an empty array to fill with data
    all_the_data = np.array([])
    dates = np.array([])
    
    # Loop through each position in the cube (define by combination of i (lat_length)
    # and j (lon_length)) 
    print("entering loop through coordinates")
    total = 0
    for i in range(0,lat_length):
        for j in range(0,lon_length):
            # Print the position
            print(i,j)
            # Define the filename
            # If a file of this name already exists saved, then read in this file
            filename = "Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/{}_{}.npy".format(string2, i,j)
            if os.path.isfile(filename):
                print("File exists")
                data_slice = np.load(filename)
                total = total + data_slice.shape[0]
            # If a file of this name does not already exist, then:
            # Take just this slice from the data and save it 
            else:
                print("File does not exist, creating")
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
    np.save("Outputs/TimeSeries/CEH-GEAR/{}/leeds-at-centre/leeds-at-centre.npy".format(string2), all_the_data)   
    print("saved data")
    
