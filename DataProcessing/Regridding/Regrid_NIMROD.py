import iris
import iris.plot as iplt
import numpy as np
from iris.coords import DimCoord
from iris.coord_systems import TransverseMercator,GeogCS
from iris.cube import Cube
from cf_units import Unit
import cf_units
import os
import glob
from pyproj import Proj, transform
import sys
import warnings
import multiprocessing as mp
import cartopy.crs as ccrs
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

root_fp = "/nfs/a319/gy17m2a/"
# Create path to files containing functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

##########################################
# Define dataset and years to work on
##########################################
filtering_name = "filtered_300"
yrs_range = '2002_2020'

gb_gdf = create_gb_outline({'init' :'epsg:3857'})

##########################################
# Load UKCP18 2km model data to use in regriddding
##########################################
file_model_2_2km_bng ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng/01/1980_2001/bng_pr_rcp85_land-cpm_uk_2.2km_01_1hr_19910601-19910630.nc'
cube_2km_bng =iris.load_cube(file_model_2_2km_bng)

##########################################
# Load LSM and use a NIMROD file to regrid it to 1km
##########################################
file_nimrod_1km =f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/{filtering_name}/2018/metoffice-c-band-rain-radar_uk_20180601_30mins.nc"
nimrod_1km =iris.load_cube(file_nimrod_1km)
nimrod_1km= trim_to_bbox_of_region_obs(nimrod_1km, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')

lsm = iris.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/lsm_land-cpm_BI_5km.nc")[0]
lsm_1km = lsm.regrid(nimrod_1km, iris.analysis.Nearest()) 

##############
### Loop through all years of data
##############
for year in range(2006,2021):
    print(year)
    # Change directory to be for correct year
    os.chdir(f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/{filtering_name}/{year}")
    # Define filepaths to save files to
    output_dir_2_2km = f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/NIMROD_regridded_2.2km/{filtering_name}/AreaWeighted/{year}/"
    # Create these directories if they don't exist already
    if not os.path.isdir(output_dir_2_2km):
        os.makedirs(output_dir_2_2km)
    # Loop through all the diles in the 1km folder    
    for filename in sorted(glob.glob("*")):
        print(filename)

        # Create version of filename specifying it is regridded
        filename_to_save_to = f"rg_{filename}"
        if not os.path.isfile(output_dir_2_2km + filename_to_save_to):
            print("Doesn't exist: Creating now")
            cube = iris.load(filename)[0] 
            # Fill in missing bounds
            cube.coord('projection_y_coordinate').guess_bounds()
            cube.coord('projection_x_coordinate').guess_bounds()
            # Align small rounding error in coordinates
            cube.coord('projection_x_coordinate').coord_system = cube_2km_bng.coord('projection_x_coordinate').coord_system
            cube.coord('projection_y_coordinate').coord_system = cube_2km_bng.coord('projection_y_coordinate').coord_system

            # Trim 
            cube= trim_to_bbox_of_region_obs(cube, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')

            # Reshape to match the data (data not always same number of timeslices so eneds redoing each time)
            broadcasted_lsm_1km_data = np.broadcast_to(lsm_1km.data.data, cube.shape)
            broadcasted_lsm_1km_data_reversed = ~broadcasted_lsm_1km_data.astype(bool)

            # Apply mask
            cube_masked = iris.util.mask_cube(cube.copy(), broadcasted_lsm_1km_data_reversed)

            # Area Weighted
            reg_cube_masked =cube_masked.regrid(cube_2km_bng,iris.analysis.AreaWeighted())    
            print("Regridded")
            # Save 
            iris.save(reg_cube_masked, output_dir_2_2km + filename_to_save_to)    
        else:
            print("file existss")