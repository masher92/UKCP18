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

ems_hourly = ['01', '04', '06', '07', '08', '09', '10', '11', '12', '13', '15']
ems_30mins = ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = '2002_2020'

def mask_cube(cube, gb_mask):
    masked_cube_data = cube * gb_mask[np.newaxis, :, :]

    # APPLY THE MASK
    reshaped_mask = np.tile(gb_mask, (cube.shape[0], 1, 1))
    reshaped_mask = reshaped_mask.astype(int)
    reversed_array = ~reshaped_mask.astype(bool)

    # Mask the cube
    masked_cube = iris.util.mask_cube(cube, reversed_array)
    
    return masked_cube

### Get the mask
gb_mask_2km = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_2.2km_GB_Mask.npy")
gb_mask_2km_bng = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_2.2km_bng_GB_Mask.npy")
gb_mask_12km_wgs84 = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_12km_wgs84_GB_Mask.npy")
gb_mask_12km = np.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/UKCP18_12km_GB_Mask.npy")
gb_mask_nimrod = np.load('/nfs/a319/gy17m2a/PhD/datadir/Masks/nimrod_1km_GB_Mask_[1100,200].npy')
# gb_mask_12km_bng = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_12km_bng_GB_Mask.npy")

root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

gb_gdf = create_gb_outline({'init' :'epsg:3857'})

# Load UKCP18 12km model data to use in regriddding
file_model_12km=f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/12km/01/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
cube_12km=iris.load_cube(file_model_12km)

file_model_2_2km ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_original/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19910601-19910630.nc'
cube_2km =iris.load_cube(file_model_2_2km)

file_model_2_2km_bng ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng/01/1980_2001/bng_pr_rcp85_land-cpm_uk_2.2km_01_1hr_19910601-19910630.nc'
cube_2km_bng =iris.load_cube(file_model_2_2km_bng)

file_model_2_2km_bng_30mins = '/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_original/bc005/2002_2020/bc005a.pr200101.nc'
file_model_2_2km_bng_30mins = '/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_original/bc005/2002_2020/bc005a.pr200101.nc'
cube_2km_30mins = iris.load_cube(file_model_2_2km_bng_30mins)
# # Trim ensemble member dimension
cube_2km_30mins = trim_to_bbox_of_region_regriddedobs(cube_2km_30mins, gb_gdf)
# # Transform to BNG
cube_2km_30mins_bng, lats_bng, lons_bng = convert_rotatedpol_to_bng(cube_2km_30mins.copy())

# remove ensemble member dimension
cube_2km = cube_2km[0,:,:,:]
cube_12km = cube_12km[0,:,:,:]

in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

lsm = iris.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/lsm_land-cpm_BI_5km.nc")[0]
lsm_2km = lsm.regrid(cube_2km_bng, iris.analysis.AreaWeighted(mdtol=0.9)) 
lsm_2km = lsm.regrid(cube_2km_bng, iris.analysis.Nearest()) 

broadcasted_lsm_2km_data = np.broadcast_to(lsm_2km.data.data, cube_2km_bng.shape)
broadcasted_lsm_2km_int = broadcasted_lsm_2km_data.astype(int)
broadcasted_lsm_2km_data_reversed = ~broadcasted_lsm_2km_data.astype(bool)

broadcasted_lsm_2km_30mins_data = np.broadcast_to(lsm_2km.data.data, cube_2km_30mins_bng.shape)
broadcasted_lsm_2km_30mins_data_reversed = ~broadcasted_lsm_2km_30mins_data.astype(bool)

file_nimrod_1km =f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/Unfiltered/2018/metoffice-c-band-rain-radar_uk_20180601_30mins.nc"
nimrod_1km =iris.load_cube(file_nimrod_1km)
nimrod_1km= trim_to_bbox_of_region_obs(nimrod_1km, gb_gdf, 'projection_y_coordinate', 'projection_x_coordinate')

lsm_1km = lsm.regrid(nimrod_1km, iris.analysis.Nearest()) 

for year in range(2020,2021):
    print(year)
    # Change directory to be for correct year
    os.chdir(f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/Filtered_100/{year}")
    # Define filepaths to save files to
    output_dir_2_2km = f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/NIMROD_regridded_2.2km/Filtered_100/AreaWeighted/{year}/"
    # Create these directories if they don't exist already
    if not os.path.isdir(output_dir_2_2km):
        os.makedirs(output_dir_2_2km)
    # Loop through all the diles in the 1km folder    
    for filename in sorted(glob.glob("*")):
        if filename[35:37] not in ['06','07','08']:
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