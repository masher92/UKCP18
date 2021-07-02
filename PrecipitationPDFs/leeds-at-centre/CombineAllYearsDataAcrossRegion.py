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
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Define variables and set up environment
#############################################
timeperiod = 'Baseline' #'Baseline', 'Future_near'
yrs_range = "1980_2001" # "1980_2001", "2020_2041"
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
resolution = '2.2km_regridded_12km' #2.2km, 12km, 2.2km_regridded_12km

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

##################################################################
# Trimming to region
##################################################################
for em in ems:
    print(em)
    # Create directory to store outputs in
    ddir = "Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/".format(resolution, timeperiod, em)
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    if resolution == '12km':
        general_filename = 'datadir/UKCP18/12km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    elif resolution == '2km':
          general_filename = 'datadir/UKCP18/12km/{}/pr_rcp85_land-rcm_uk_12km_{}_day_*'.format(em, em)
    elif resolution == '2.2km_regridded_12km':
          general_filename = 'datadir/UKCP18/2.2km_regridded_12km/{}/NearestNeighbour/{}/rg_pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    print(general_filename)
    
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        print(filename)
        filenames.append(filename)
    print(len(filenames))
       
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    print('Concatenating cube')
    model_cube = monthly_cubes_list.concatenate_cube()      

    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    print('trimming cube')
    model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
    # Test plotting - one timeslice
    #iplt.pcolormesh(model_cube[120])
    print(model_cube)
    #time_constraint = iris.Constraint(time = lambda cell: cell.point.year  in [1980, 1981,1982, 1983, 1984, 1985, 196, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996,          1997, 1998, 1999, 2000, 2001])
    #model_cube_times = model_cube.extract(time_constraint)    
    
    # Remove ensemble member dimension
    model_cube = model_cube[0,:,:,:]
    print(model_cube)
    # Save trimmed netCDF to file    
    print('saving cube')
    iris.save(model_cube, "Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/leeds-at-centre.nc".format(resolution,timeperiod,em))
    
    # ################################################################
    # # Once across all ensemble members, save a numpy array storing
    # # the timestamps to which the data refer
    # ################################################################          
    if em == '01':
        times = model_cube.coord('yyyymmddhh').points
        print(len(times))
        print(times[len(times)-1])
        print(times[0])
        # Convert to datetime - doesnt work due to 30 days in Feb
        #times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
        np.save("Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/timestamps.npy".format(resolution, timeperiod), times) 

    # ################################################################
    # # Create a numpy array containing all the precipitation values from across
    # # all 20 years of data and all positions in the cube
    # ################################################################
    # Define length of variables defining spatial positions
    lat_length= model_cube.shape[1]
    lon_length= model_cube.shape[2]
    print("Defined length of coordinate dimensions")
    print(lat_length, lon_length)        
        
    # # # Load data
    print("Loading data")
    data = model_cube.data
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
            if 1 ==2 :
            #if os.path.isfile (filename):
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