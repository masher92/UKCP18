##################################################################
# This Script:
#    - 
#    -
#    -

##################################################################


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

trim_to_leeds = False

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
uk_gdf = create_uk_outline({'init' :'epsg:3857'})
##################################################################

# Constraint to only load JJA data
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

### Establish the ensemble members
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
for em in ems:

    yrs_range = "1980_2001"
    resolution = '2.2km' #2.2km, 12km, 2.2km_regridded_12km
    ddir = f"ProcessedData/TimeSeries/UKCP18_hourly/{resolution}/{yrs_range}/{em}/"
    
    print(em, resolution, trim_to_leeds)
    
    # ### Get a list of filenames for this ensemble member, for just JJA
    if resolution == '2.2km':
        general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/{yrs_range}/pr_rcp85_land-cpm_uk_2.2km_{em}_1hr_*'
    elif resolution == '12km':
          general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/{yrs_range}/pr_rcp85_land-rcm_uk_12km_{em}_day_*'
    elif resolution == '2.2km_regridded_12km':
        general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/NearestNeighbour/{yrs_range}/rg_pr_rcp85_land-cpm_uk_2.2km_{em}_1hr_*'
    
    # Get a list of filenames
    filenames = []
    for filename in sir_globington_the_file_gatherer.glob(general_filename):
        filenames.append(filename)
    print(len(filenames))

    # ### Load in the data
    monthly_cubes_list = iris.load(filenames, in_jja)
    
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history', 'Conventions']:
                if attr in cube.attributes:
                    del cube.attributes[attr]

    # ### Concatenate cubes into one
    model_cube = monthly_cubes_list.concatenate_cube()      

    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    print('trimming cube')
    if trim_to_leeds == True:
        if resolution == '2.2km':
            model_cube = trim_to_bbox_of_region_regriddedobs(model_cube, leeds_at_centre_gdf)
        else:
            model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
    else:
        if resolution == '2.2km':
            model_cube = trim_to_bbox_of_region_regriddedobs(model_cube, uk_gdf)
        else:
            model_cube = trim_to_bbox_of_region_obs(model_cube, uk_gdf)
     
    ### Remove ensemble member dimension
    model_cube = model_cube[0,:,:,:]

    # Can't remember what this is for?
    year_filter = lambda cell: cell < 2002
    model_cube = model_cube.extract(iris.Constraint(year=year_filter))
    
    ################################################################
    # Once across all ensemble members, save a numpy array storing
    # the timestamps to which the data refer
    ################################################################  
    ### Get associated times
    if resolution in ['2.2km', '2.2km_regridded_12km']:
        times = model_cube.coord('yyyymmddhh').points   
        times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
        #print(model_cube_jja.coord('yyyymmddhh'))
        print(len(times))
    elif resolution == '12km':
        time_var = 'yyyymmdd'   
        times = model_cube.coord('yyyymmdd').points  
        times = [datetime.datetime.strptime(x, "%Y%m%d") for x in times]
        # print(model_cube_jja.coord('yyyymmdd'))
        print(len(times))
    np.save(f"ProcessedData/TimeSeries/UKCP18_hourly/{resolution}/{yrs_range}/timestamps.npy", times) 

    ################################################################
    # Get mask and regrid to the model cube
    ################################################################  
    if trim_to_leeds == False:
        print("getting mask")
        monthly_cubes_list = iris.load("/nfs/a319/gy17m2a/PhD/datadir/lsm_land-cpm_BI_5km.nc")
        lsm = monthly_cubes_list[0]
        lsm_nn =lsm.regrid(model_cube, iris.analysis.Nearest())   

        # Save it in 1D form
        mask = lsm_nn.data.data.reshape(-1)
        np.save(ddir + "lsm.npy", mask) 
    
    ################################################################
    # Get data as array
    ################################################################      
    start = time.time()
    data = model_cube.data.data
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
