##################################################################
# This Script:
#    - 
#    -
#    -

##################################################################
import iris
import os
import glob as glob
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import time
import multiprocessing as mp
import iris.plot as iplt

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
warnings.filterwarnings("ignore", category =UserWarning,)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

season ='wholeyear'

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
gb_gdf = create_gb_outline({'init' :'epsg:3857'})
##################################################################

# Constraint to only load 
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

yrs_range = "2002_2020"
yrs= range(2001,2020)
resolution = '2.2km_bng_masked' #2.2km, 12km, 2.2km_regridded_12km

ems= ['bc012', 'bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018']
for em in ems:
    for yr in range(2001,2020):
        ddir = f"ProcessedData/TimeSeries/UKCP18_every30mins/{resolution}/{yrs_range}/{em}_{season}/"

        if not os.path.isdir(ddir):
                os.makedirs(ddir)

        if not os.path.isfile(ddir + f'compressed_{yr}_GB_{season}.npy'):
            print(em, yr, resolution)

            ##################################################################
            # CLEAN AND JOIN THE DATA
            ##################################################################
            general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/2002_2020/{em}/bng_{em}a.pr{yr}*'
            filenames = [filename for filename in glob.glob(general_filename) if '2000' not in filename and 'pr2020' not in filename]
            print(len(filenames))

            ### Load in the data
            if season == 'jja':
                monthly_cubes_list = iris.load(filenames, in_jja)
            else:
                monthly_cubes_list = iris.load(filenames)
                
            if len(monthly_cubes_list) != 12:
                raise ValueError(f"Error: The length of monthly_cubes_list is {len(monthly_cubes_list)}, but it should be 12. Check the data for em={em}, year={yr}, resolution={resolution}.")
            else:
                print(f"len(monthly_cubes_list) is enough files")

            for cube in monthly_cubes_list:
                 for attr in ['creation_date', 'tracking_id', 'history', 'Conventions']:
                        if attr in cube.attributes:
                            del cube.attributes[attr]

            for cube in monthly_cubes_list:
                if cube.coords('forecast_period', dim_coords=False):  # Check if 'hour' exists as a scalar coordinate
                    cube.remove_coord('forecast_period')  # This modifies the cube directly in the list
                if cube.coords('forecast_reference_time', dim_coords=False):  # Check if 'hour' exists as a scalar coordinate
                    cube.remove_coord('forecast_reference_time')  # This modifies the cube directly in the list
                if cube.coords('realization', dim_coords=False):  # Check if 'hour' exists as a scalar coordinate
                    cube.remove_coord('realization')  # This modifies the cube directly in the list      
            iris.util.equalise_attributes(monthly_cubes_list)       

            # ### Concatenate cubes into one
            model_cube = monthly_cubes_list.concatenate_cube() 

            ### Remove ensemble member dimension
            if len(model_cube.shape)>3:
                model_cube = model_cube[0,:,:,:]

            ### Trim to UK
            if resolution  == '2.2km_bng_masked':
                model_cube = trim_to_bbox_of_region_obs(model_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')      
                gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_2.2km_GB_Mask.npy")
            elif resolution =='2.2km_bng_regridded_12km_masked':
                model_cube = trim_to_bbox_of_region_obs(model_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')               
                gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_12km_GB_Mask.npy")

            ##################################################################
            # Save data over UK
            ##################################################################                
            # Get rid of negative values
            compressed = model_cube.data.compressed()
            print(f"over UK shape is {compressed.shape[0]}")
            np.save(ddir + f'compressed_{yr}_UK_{season}.npy', compressed) 

            iplt.contourf(model_cube[1,:,:])        
            plt.savefig("/nfs/a319/gy17m2a/PhD/" + ddir + f"model_cube_contour_{yr}_UK.png", dpi=300, bbox_inches='tight') 

            ##################################################################
            # Trim data to GB
            ##################################################################
            masked_cube_data = model_cube * gb_mask[np.newaxis, :, :]    

            # APPLY THE MASK
            reshaped_mask = np.tile(gb_mask, (model_cube.shape[0], 1, 1))
            reshaped_mask = reshaped_mask.astype(int)
            reversed_array = ~reshaped_mask.astype(bool)

            # Mask the cube
            masked_cube = iris.util.mask_cube(model_cube, reversed_array)

            # Get rid of negative values
            compressed = masked_cube.data.compressed()
            print(f"over GB shape is {compressed.shape[0]}")
            np.save(ddir + f'compressed_{yr}_GB_{season}.npy', compressed) 

            iplt.contourf(masked_cube[1,:,:])        
            plt.savefig("/nfs/a319/gy17m2a/PhD/" + ddir + f"model_cube_contour_{yr}_GB.png", dpi=300, bbox_inches='tight') 
        else:
            print(ddir + f'compressed_{yr}_UK_{season}.npy already exists')