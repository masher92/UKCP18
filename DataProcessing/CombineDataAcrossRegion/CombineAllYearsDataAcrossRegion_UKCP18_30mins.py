import iris
import os
import glob as sir_globington_the_file_gatherer
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import time
import multiprocessing as mp
import glob as glob

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
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
uk_gdf = create_uk_outline({'init' :'epsg:3857'})
##################################################################

# ### Establish the ensemble member
trim_to_leeds = True

ems =['01', '04', '06', '07', '08', '09', '10', '11', '12', '13', '15']
em_matching_dict = {'01':'bc005', '04': 'bc006', '05': 'bc007', '06':'bc009',  '07':'bc010', 
                    '08': 'bc011', '09':'bc013', '10': 'bc015', '11': 'bc016', '12': 'bc017', '13':'bc018', '15':'bc012'}
ems = ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']

yrs_range = "2002_2020"
resolution = '2.2km' #2.2km, 12km, 2.2km_regridded_12km
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

for em in ems:

    ddir = f"ProcessedData/TimeSeries/UKCP18_every30mins/{resolution}/{yrs_range}/{em}/"
    
    ### Save as numpy array
    #print("saving data")
    if not os.path.isdir(ddir):
        os.makedirs(ddir)

    print(em, resolution)

    # ### Get a list of filenames for this ensemble member, for just JJA
    if resolution == '2.2km':
        general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/{em}/{yrs_range}/{em}a.pr*'
    elif resolution == '12km':
          general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/{em}/{yrs_range}/pr_rcp85_land-rcm_uk_12km_{em}_day_*'
    elif resolution == '2.2km_regridded_12km':
        general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/{em}/NearestNeighbour/{yrs_range}/rg_*'
    general_filename

    filenames = []
    for filename in glob.glob(general_filename):
        if '2000' not in filename and 'pr2020' not in filename:
            filenames.append(filename)
    print(len(filenames))
    
    ### Load in the data
    monthly_cubes_list = iris.load(filenames, in_jja)

    ### Concatenate cubes into one
    model_cube_jja = monthly_cubes_list.concatenate_cube()      

    ### Get associated times
    times = model_cube_jja.coord('time')   
    # print(times.units.num2date(times.points))
    np.save(f"ProcessedData/TimeSeries/UKCP18_every30mins/{resolution}/{yrs_range}/timestamps.npy", times) 

    ################################################################
    # Get mask and regrid to the model cube
    ################################################################  
    if trim_to_leeds == False:
        print("getting mask")
        monthly_cubes_list = iris.load("/nfs/a319/gy17m2a/PhD/datadir/lsm_land-cpm_BI_5km.nc")
        lsm = monthly_cubes_list[0]
        lsm_nn =lsm.regrid(model_cube_jja, iris.analysis.Nearest())   

        # Save it in 1D form
        mask = lsm_nn.data.data.reshape(-1)
        np.save(ddir + "lsm.npy", mask) 
    
    ################################################################
    # Get data as array
    ################################################################      
    start = time.time()
    data = model_cube_jja.data.data
    end= time.time()
    print(f"Time taken to load cube {round((end-start)/60,1)} minutes" )    
        
    start = time.time()
    flattened_data = data.flatten()
    end= time.time()
    print(f"Time taken to flatten cube {round((end-start)/60,1)} minutes" )

    ### Save as numpy array
    print("saving data")
    if trim_to_leeds == True:
        np.save(ddir + "leeds-at-centre_jja_withoutbadyears.npy", flattened_data)   
    else:
        np.save(ddir + "uk_jja.npy", flattened_data) 
    print("saved data")