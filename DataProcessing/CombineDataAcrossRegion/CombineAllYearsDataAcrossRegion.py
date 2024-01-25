import iris
import os
import glob as sir_globington_the_file_gatherer
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import time
import multiprocessing as mp

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

# ### Establish the ensemble member
trim_to_leeds = False

# ems = ['01']
#for em in ['04', '06', '07', '08', '09', '10', '11', '12', '13', '15']:
def combining_data(em):

    yrs_range = "1980_2001"
    resolution = '2.2km' #2.2km, 12km, 2.2km_regridded_12km
    ddir = f"ProcessedData/TimeSeries/UKCP18_hourly/{resolution}/{yrs_range}/leeds-at-centre/{em}/"
    
    print(em, resolution, trim_to_leeds)
    
    # ### Get a list of filenames for this ensemble member, for just JJA
    if resolution == '2.2km':
        general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/{yrs_range}/pr_rcp85_land-cpm_uk_2.2km_{em}_1hr_*'
    elif resolution == '12km':
          general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/{yrs_range}/pr_rcp85_land-rcm_uk_12km_{em}_day_*'
    elif resolution == '2.2km_regridded_12km':
        general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/NearestNeighbour/{yrs_range}/rg_pr_rcp85_land-cpm_uk_2.2km_{em}_1hr_*'

    filenames = []
    for filename in sir_globington_the_file_gatherer.glob(general_filename):
        if resolution == '2.2km':
            if filename[101:103] in ['06', '07', '08']:
                filenames.append(filename)
        elif resolution == '12km':
            if filename[95:99] in ['2000', '1990', '1980']:
                filenames.append(filename)
        elif resolution == '2.2km_regridded_12km':
            if filename[132:136] in ['2000', '1990', '1980']:
                filenames.append(filename)      
    print(len(filenames))

    # ### Load in the data
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')

    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history', 'Conventions']:
                if attr in cube.attributes:
                    del cube.attributes[attr]

    # ### Concatenate cubes into one
    model_cube = monthly_cubes_list.concatenate_cube()      

    # ### Trim to Leeds
    if trim_to_leeds == True:
        if resolution in ['2.2km']:
                model_cube = trim_to_bbox_of_region(model_cube, leeds_at_centre_gdf)
        elif resolution in['2.2km_regridded_12km', '12km']:
                model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)


    # ### Remove ensemble member dimension
    model_cube = model_cube[0,:,:,:]

    # ### Keep just JJA
    # Add season variables
    iris.coord_categorisation.add_season(model_cube,'time', name = "clim_season")
    # Keep only JJA
    model_cube_jja = model_cube.extract(iris.Constraint(clim_season = 'jja'))
    
    year_filter = lambda cell: cell < 2002
    model_cube_jja = model_cube_jja.extract(iris.Constraint(year=year_filter))
    
    # ### Get associated times
    if resolution in ['2.2km', '2.2km_regridded_12km']:
        times = model_cube_jja.coord('yyyymmddhh').points   
        times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
        #print(model_cube_jja.coord('yyyymmddhh'))
        print(len(times))
    elif resolution == '12km':
        time_var = 'yyyymmdd'   
        times = model_cube_jja.coord('yyyymmdd').points  
        times = [datetime.datetime.strptime(x, "%Y%m%d") for x in times]
        # print(model_cube_jja.coord('yyyymmdd'))
        print(len(times))
    np.save(f"ProcessedData/TimeSeries/UKCP18_hourly/{resolution}/{yrs_range}/leeds-at-centre/timestamps.npy", times) 

    # ################################################################
    # # Create a numpy array containing all the precipitation values from across
    # # all 20 years of data and all positions in the cube
    # ################################################################
    # Define length of variables defining spatial positions
    lat_length= model_cube_jja.shape[1]
    lon_length= model_cube_jja.shape[2]
    #print("Defined length of coordinate dimensions")
    #print(lat_length, lon_length)        

    # # # Load data
    #print("Loading data")
    data = model_cube_jja.data
    #print("Loaded data")

    start = time.time()

    # Create an empty array to fill with data
    all_the_data = np.array([])

    #print("Entering loop through coordinates")
    total = 0
    for i in range(0,lat_length):
        for j in range(0,lon_length):
            # Print the position
            if i in [10,20,30] and j ==0:
                print(i,j)     
            data_slice = data[:,i,j]
            # Remove mask
            data_slice = data_slice.data
            # Add to total
            total = total + data_slice.shape[0]

            # Add the slice to the array containing all the data from all the locations
            all_the_data = np.append(all_the_data,data_slice)

    ### Save as numpy array
    ### Save as numpy array
    #print("saving data")
    if trim_to_leeds == True:
        np.save(ddir + "leeds-at-centre_jja.npy", all_the_data)   
    else:
        np.save(ddir + "UK_jja.npy", all_the_data)     
    #print("saved data")

    end= time.time()
    print(f"Time taken is {(end-start)/60}seconds" )

    
### Complete via multiprocessing
pool = mp.Pool(mp.cpu_count())
results = [pool.apply_async(combining_data, args=(x,)) for x in ems]
output = [p.get() for p in results]
print(output) 