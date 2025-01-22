##########################
# Set up environment
##########################
import iris
import iris.plot as iplt
import numpy as np
from iris.coords import DimCoord
from iris.coord_systems import TransverseMercator, GeogCS
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

ems_hourly = ['01', '04', '05', '06', '07', '09', '10', '11', '12', '13', '15']
yrs_range = '2002_2020'

gb_gdf = create_gb_outline({'init': 'epsg:3857'})

##########################
# Create GB mask to use
##########################
# load in 5km land sea mask
lsm = iris.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/lsm_land-cpm_BI_5km.nc")[0]

# Load in example UKCP18 data at 2.2km BNG
file_model_12km = f'/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/12km/01/01/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
cube_12km = iris.load_cube(file_model_12km)[0]
file_model_2_2km_bng = '/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng_masked/01/1980_2001/bng_pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810601-19810630.nc'
cube_2km_bng = iris.load_cube(file_model_2_2km_bng)

# Regrid the LSM to 2km
lsm_2km = lsm.regrid(cube_2km_bng, iris.analysis.Nearest())

# Broadcast the LSM (so it has as many layers as the cube does)
broadcasted_lsm_2km_data = np.broadcast_to(lsm_2km.data.data, cube_2km_bng.shape)
broadcasted_lsm_2km_int = broadcasted_lsm_2km_data.astype(int)
broadcasted_lsm_2km_data_reversed = ~broadcasted_lsm_2km_data.astype(bool)

in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

##########################
# Process only JJA (June, July, August)
##########################
for em in ems_hourly:
    print(em)
    os.chdir(f"/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_original/{em}/{yrs_range}/")
    # establish paths to directories
    output_fp_bng_masked = f"/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng_masked/{em}/{yrs_range}/"
    output_fp_bng_regridded_12km = f"/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng_regridded_12km_masked/{em}/AreaWeighted/{yrs_range}/"

    if not os.path.isdir(output_fp_bng_masked):
        os.makedirs(output_fp_bng_masked)
    if not os.path.isdir(output_fp_bng_regridded_12km):
        os.makedirs(output_fp_bng_regridded_12km)

    # loop through the files
    for filename in np.sort(glob.glob("*")): 
        if not os.path.isfile(output_fp_bng_regridded_12km + f"bng_rg_{filename}"):
            # Load the data
            cube_2km = iris.load(filename, in_jja)
            if len(cube_2km) ==0:
                continue
            else:
                cube_2km = cube_2km[0]
            print(f"{filename} creating")
            cube_2km = cube_2km[0, :, :, :]  # Ensure only the first time coordinate is selected

            # Trim
            cube_2km = trim_to_bbox_of_region_regriddedobs(cube_2km, gb_gdf)
            # Transform to BNG
            cube_2km_bng, lats_bng, lons_bng = convert_rotatedpol_to_bng(cube_2km.copy())
            # Mask to GB
            cube_2km_bng_masked = iris.util.mask_cube(cube_2km_bng.copy(), broadcasted_lsm_2km_data_reversed)
            # Regrid to 12km
            cube_2km_bng_masked_regridded_12km = cube_2km_bng_masked.regrid(cube_12km, iris.analysis.AreaWeighted(mdtol=0.8))
            # Save 
            iris.save(cube_2km_bng_masked, output_fp_bng_masked + f"bng_{filename}")
            iris.save(cube_2km_bng_masked_regridded_12km, output_fp_bng_regridded_12km + f"bng_rg_{filename}")


        else:
            print(f"{filename} already exists")

