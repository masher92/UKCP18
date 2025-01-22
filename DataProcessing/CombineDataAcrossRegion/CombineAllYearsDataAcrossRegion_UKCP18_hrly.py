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

trim_to_leeds = False

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
resolution = '2.2km_bng_regridded_12km_masked' #2.2km, 12km, 2.2km_regridded_12km

### Establish the ensemble members
ems = ['08'] #['01',04', '05', '06','07','08', '09', 10', '11', '12', '13', '15']
for em in ems:
    
    if resolution == '2.2km_bng_regridded_12km':
        ddir = f"ProcessedData/TimeSeries/UKCP18_hourly/{resolution}/AreaWeighted/{yrs_range}/{em}/"
    else:
        ddir = f"ProcessedData/TimeSeries/UKCP18_hourly/{resolution}/{yrs_range}/{em}/"

    if not os.path.isdir(ddir):
        os.makedirs(ddir)
        
    print(em, resolution, trim_to_leeds)
    for yr in yrs:
        print(em, yr)

        # ### Get a list of filenames for this ensemble member, for just JJA
        if resolution == '2.2km':
            general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/{yrs_range}/pr_rcp85_land-cpm_uk_2.2km_{em}_1hr_{yr}*'
        
        elif resolution == '12km':
              general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/{yrs_range}/pr_rcp85_land-rcm_uk_12km_{em}_day_*'

        elif resolution == '2.2km_bng_regridded_12km_masked':
            general_filename = f'/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/{em}/AreaWeighted/{yrs_range}/bng_rg_pr_rcp85_land-cpm_uk_2.2km_{em}_1hr_{yr}*'
    
        filenames = []
        for filename in sir_globington_the_file_gatherer.glob(general_filename):
            filenames.append(filename)
        print(f"loading {len(filenames)} files")

        # ### Load in the data
        monthly_cubes_list = iris.load(filenames, in_jja)
        if len(monthly_cubes_list)!= 3:
            break
        print(len(monthly_cubes_list))
        
        for cube in monthly_cubes_list:
             for attr in ['creation_date', 'tracking_id', 'history', 'Conventions']:
                    if attr in cube.attributes:
                        del cube.attributes[attr]

        # ### Concatenate cubes into one
        model_cube = monthly_cubes_list.concatenate_cube()      

        ### Remove ensemble member dimension
        if len(model_cube.shape)>3:
            model_cube = model_cube[0,:,:,:]
        
        ### Trim to UK
        if resolution  == '2.2km':
            model_cube = trim_to_bbox_of_region_regriddedobs(model_cube, gb_gdf)       
        elif resolution =='2.2km_bng_regridded_12km_masked':
            model_cube = trim_to_bbox_of_region_obs(model_cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')               
        
        # Get rid of negative values
        compressed = model_cube.data.compressed()
        np.save(ddir + f'compressed_{yr}_UK_jja.npy', compressed) 
        print(f"over UK shape is {compressed.shape[0]}")
        
        iplt.contourf(model_cube[1,:,:])        
        plt.savefig("/nfs/a319/gy17m2a/PhD/" + ddir + f"model_cube_contour_{yr}_UK.png", dpi=300, bbox_inches='tight')
        plt.clf()
        
        #######################################################################
        # Just GB
        #######################################################################
        gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_12km_GB_Mask.npy")
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
        
        iplt.contourf(masked_cube[1,:,:])        
        plt.savefig("/nfs/a319/gy17m2a/PhD/" + ddir + f"model_cube_contour_{yr}_GB.png", dpi=300, bbox_inches='tight') 
        
        # Save to file
        np.save(ddir + f'compressed_{yr}_GB_jja.npy', compressed)     