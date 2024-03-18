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
ems_30mins = ['bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = '1980_2001'


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
gb_mask_2km = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_2.2km_GB_Mask.npy")
gb_mask_12km_wgs84 = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_12km_wgs84_GB_Mask.npy")
gb_mask_12km = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_12km_GB_Mask.npy")


##########################################################################################
#########################################################################################
# Define variables and set up environment
##########################################################################################
##########################################################################################
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
file_model_12km=f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/12km/01/{yrs_range}/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
cube_12km=iris.load_cube(file_model_12km)

file_model_2_2km ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19910601-19910630.nc'
cube_2km =iris.load_cube(file_model_2_2km)

file_model_2_2km_bng ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng/01/1980_2001/bng_pr_rcp85_land-cpm_uk_2.2km_01_1hr_19910601-19910630.nc'
cube_2km_bng =iris.load_cube(file_model_2_2km_bng)

# remove ensemble member dimension
cube_2km = cube_2km[0,:,:,:]
cube_12km = cube_12km[0,:,:,:]

yrs_range = '1980_2001'
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)
# this is the crs that we want to transform to
source_crs_2km = ccrs.RotatedGeodetic(pole_latitude=37.5,
                                        pole_longitude=177.5,
                                            central_rotated_longitude=0)
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
cube_12km_trimmed_to_leeds =  trim_to_bbox_of_region_obs(cube_12km, leeds_at_centre_gdf, 'projection_y_coordinate',
                                                        "projection_x_coordinate")

for em in ems_30mins:
    print(em)
    os.chdir(f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km/{em}/2002_2020/")
    # establish paths to directories
    output_fp_bng = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{em}/{yrs_range}/"
    output_fp_bng_regridded = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_regridded_12km/{em}/AreaWeighted/{yrs_range}/"
    # create the directories
    if not os.path.isdir(output_fp_bng):
        os.makedirs(output_fp_bng)
    if not os.path.isdir(output_fp_bng_regridded):
        os.makedirs(output_fp_bng_regridded)      
    # loop through the files
    for filename in np.sort(glob.glob("*")):   
        print(filename)
        if os.path.isfile(output_fp_bng_regridded +  f"bng_rg_{filename}"):
            print("creating")
            # print(filename)
            cube_2km = iris.load(filename)[0]
            # trim 
            cube_2km = trim_to_bbox_of_region_regriddedobs(cube_2km, gb_gdf)
            # convert to bng
            cube_2km_bng, lats_bng, lons_bng = convert_rotatedpol_to_bng (cube_2km.copy()) 
            # Mask to GB
            cube_2km_bng_masked = mask_cube(cube_2km_bng, gb_mask_2km)
            # Regrid to 12km
            cube_2km_bng_masked_regridded = cube_2km_bng_masked.regrid(cube_12km, iris.analysis.AreaWeighted()) 
            # Save 
            iris.save(cube_2km_bng_masked, output_fp_bng +  f"bng_{filename}")
            iris.save(cube_2km_bng_masked_regridded, output_fp_bng_regridded +  f"bng_rg_{filename}")     
        else:
            print("already exists")    