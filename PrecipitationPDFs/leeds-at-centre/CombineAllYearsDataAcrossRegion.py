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
import multiprocessing as mp
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
ems = [ '01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
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
#def combining_data(em):
    print(em)
    # Create directory to store outputs in
    ddir = "Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/".format(resolution, timeperiod, em)
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    if resolution == '2.2km':
        general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    elif resolution == '12km':
          general_filename = 'datadir/UKCP18/12km/{}/pr_rcp85_land-rcm_uk_12km_{}_day_*'.format(em, em)
    elif resolution == '2.2km_regridded_12km':
          general_filename = 'datadir/UKCP18/2.2km_regridded_12km/{}/NearestNeighbour/{}/rg_pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    #print(general_filename)
    
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
        filenames.append(filename)
    print(len(filenames))
       
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history', 'Conventions']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
        
    ls = ls
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    i=0
    for cube in monthly_cubes_list:
        
        print(i)
        new_ls = []
        for attribute in cube.attributes:
            if attribute not in new_ls:
                new_ls.append(attribute)
        if new_ls != ls:
            print("break")
    
    metadata= cube.metadata
    for cube in monthly_cubes_list:
        this_metadata = cube.metadata
        if this_metadata != cube.metadata:
            print("no")
    
    
    # Concatenate the cubes into one
    print('Concatenating cube')
    model_cube = monthly_cubes_list.concatenate_cube()      

    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    print('trimming cube')
    if resolution in ['2.2km']:
            model_cube = trim_to_bbox_of_region(model_cube, leeds_at_centre_gdf)
    elif resolution in['2.2km_regridded_12km', '12km']:
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
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(model_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = model_cube.extract(iris.Constraint(clim_season = 'jja'))
    
    #print('saving jja cube')
    iris.save(jja, "Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/jja_leeds-at-centre.nc".format(resolution,timeperiod,em))
    
    # ################################################################
    # # Once across all ensemble members, save a numpy array storing
    # # the timestamps to which the data refer
    # ################################################################          
    if em == '01':
        if resolution in ['2.2km', '2.2km_regridded_12km']:
            time_var = 'yyyymmddhh'
        elif resolution == '12km':
            time_var = 'yyyymmdd'        
        
        # Extract ttimes
        times = model_cube.coord(time_var).points   
        # Convert to datetime - doesnt work due to 30 days in Feb
        #times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
        np.save("Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/timestamps.npy".format(resolution, timeperiod), times) 

        ## Also save a dataframe, which contains a flag for whether that
        # date is within JJA
        jja_times = jja.coord(time_var).points
        # Create dataframe showing which dates in JJA data and which not
        jja_times_df = pd.DataFrame({'times':jja_times, 'in_jja': 1})
        times_df = pd.DataFrame({'times':times, 'Value': 1})
        
        combined_times = times_df.merge(jja_times_df, how = 'outer')
        del combined_times['Value']
        combined_times.to_csv("Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/timestamps_jjaflag.csv".format(resolution, timeperiod), index = False)    
        
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
            # If a file of this name already exists concat, then read in this file
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


### Complete via multiprocessing
pool = mp.Pool(mp.cpu_count())
results = [pool.apply_async(combining_data, args=(x,)) for x in ems]
output = [p.get() for p in results]
print(output) 
    