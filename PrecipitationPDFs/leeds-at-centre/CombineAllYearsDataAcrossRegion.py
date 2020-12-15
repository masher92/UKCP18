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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Create directory to store outputs in
ddir = "Outputs/Timeseries_UKCP18/leeds-at-centre/{}/".format(em)
if not os.path.isdir(ddir):
    os.mkdir(ddir)

############################################
# Define variables and set up environment
#############################################
# Region over which to plot
region = 'UK' #['Northern', 'leeds-at-centre', 'UK']
# Stats to plot
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

yrs_range = "1980_2001" 
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outline of the coast of the UK
uk_gdf = create_uk_outline({'init' :'epsg:3857'})

##################################################################
# Trimming to region
##################################################################
for em in ems:
    print(em)
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
        filenames.append(filename)
    print(len(filenames))
       
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    model_cube = monthly_cubes_list.concatenate_cube()      
                         
    # Remove ensemble member dimension
    model_cube = model_cube[0,:,:,:]

    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
    
    ################################################################
    # Once across all ensemble members, save a numpy array storing
    # the timestamps to which the data refer
    ################################################################          
    if em == '01':
        times = model_cube.coord('yyyymmddhh').points
        # Convert to datetime - doesnt work due to 30 days in Feb
        #times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
        np.save(ddir + "timestamps.npy", times) 
    
    
    ################################################################
    # Create a numpy array containing all the precipitation values from across
    # all 20 years of data and all positions in the cube
    ################################################################
    # Define length of variables defining spatial positions
    lat_length= model_cube.shape[1]
    lon_length= model_cube.shape[2]
    print("Defined length of coordinate dimensions")
    print(lat_length, lon_length)        
        
    # # Load data
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
            # If a file of this name already exists saved, then read in this file
            filename = ddir + "{}_{}.npy".format(i,j)
            # Take slice from loaded data
            data_slice = data[:,i,j]
            # Remove mask
            data_slice = data_slice.data
            # Save to file
            np.save(filename, data_slice) 
            total = total + data_slice.shape[0]
            print("File does not exist")
            # Add the slice to the array containing all the data from all the locations
            all_the_data = np.append(all_the_data,data_slice)
    
    # Delete na values -
    # This is why the length of the output "leeds-at-centre.npy" does not match
    # the number of 33 * 37 * 219144
    # RG -- First 10 values in each of the (33*37) cells are NA
    # RF -- first 10 values in each of the (73*83) cells are NA
    all_the_data = all_the_data[~np.isnan(all_the_data)]
    
    ### Save as numpy array
    print("saving data")
    np.save(ddir + "leeds-at-centre.npy", all_the_data)   
    print("saved data")
