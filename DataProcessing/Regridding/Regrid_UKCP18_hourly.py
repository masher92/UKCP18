##### THIS IS for 30 mins - needs updating for 1hour

##########################
# Set up environment
##########################
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
os.chdir(root_fp)

# Read in functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

ems_hourly = ['01', '04', '06', '07', '08', '09', '10', '11', '12', '13', '15']
yrs_range = '2060_2081'

gb_gdf = create_gb_outline({'init' :'epsg:3857'})

##########################
# Create GB mask to use
##########################
# load in 5km land sea mask
lsm = iris.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/lsm_land-cpm_BI_5km.nc")[0]

# Load in example UKCP18 data at 2.2km BNG
file_model_12km=f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/12km/01/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
# cube_12km=iris.load_cube(file_model_12km)
file_model_2_2km_bng ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng/01/1980_2001/bng_pr_rcp85_land-cpm_uk_2.2km_01_1hr_19910601-19910630.nc'
cube_2km_bng =iris.load_cube(file_model_2_2km_bng)

# Regrid the LSM to 2km
lsm_2km = lsm.regrid(cube_2km_bng, iris.analysis.Nearest()) 

# Broadcast the LSM (so it has as many layers as the cube does)
broadcasted_lsm_2km_data = np.broadcast_to(lsm_2km.data.data, cube_2km_bng.shape)
broadcasted_lsm_2km_int = broadcasted_lsm_2km_data.astype(int)
broadcasted_lsm_2km_data_reversed = ~broadcasted_lsm_2km_data.astype(bool)

##########################
#
##########################
for em in ems_hourly:
    print(em)
    os.chdir(f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_original/{yrs_range}/{em}/")
    # establish paths to directories
    output_fp_bng = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/{yrs_range}/{em}/"
    output_fp_bng_masked = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_masked/{yrs_range}/{em}/"
    output_fp_bng_regridded_12km = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_regridded_12km_masked/{em}/AreaWeighted/{yrs_range}/"

    # create the directories
    if not os.path.isdir(output_fp_bng):
        os.makedirs(output_fp_bng)
    if not os.path.isdir(output_fp_bng_masked):
        os.makedirs(output_fp_bng_masked)    
    # if not os.path.isdir(output_fp_bng_regridded_12km):
    #      os.makedirs(output_fp_bng_regridded_12km)    
            
    # loop through the files
    for filename in np.sort(glob.glob("*")): 
        print(filename)
        if not os.path.isfile(output_fp_bng +  f"bng_{filename}"):
            print("creating")

            # Load the data
            cube_2km = iris.load(filename)[0]
            # Trim
            cube_2km = trim_to_bbox_of_region_regriddedobs(cube_2km, gb_gdf)
            # Transform to BNG
            cube_2km_bng, lats_bng, lons_bng = convert_rotatedpol_to_bng(cube_2km.copy())
            # Mask to GB
            cube_2km_bng_masked = iris.util.mask_cube(cube_2km_bng.copy(), broadcasted_lsm_2km_30mins_data_reversed)
            # Regrid to 12km
            # cube_2km_bng_masked_regridded_12km = cube_2km_bng_masked.regrid(cube_12km, iris.analysis.AreaWeighted(mdtol=0.8)) 
            # Save 
            iris.save(cube_2km_bng, output_fp_bng +  f"bng_{filename}")     
            iris.save(cube_2km_bng_masked, output_fp_bng_masked +  f"bng_{filename}")
            # iris.save(cube_2km_bng_masked_regridded_12km, output_fp_bng_regridded_12km +  f"bng_rg_{filename}") 
            
        else:
            print("already exists")    
