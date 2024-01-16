#### Install packages
import iris
import xarray as xr
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

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/PhD"
os.chdir(root_fp)

time_resolution  = '5mins'

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
# from Regridding_functions import *

# Load UKCP18 model data to use in regriddding
file_model_2_2km ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19911201-19911230.nc'
cube_model_2_2km =iris.load_cube(file_model_2_2km)

# Load UKCP18 12km model data to use in regriddding
file_model_12km ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18/12km/01/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
cube_model_12km=iris.load_cube(file_model_12km)

for year in range(2013,2020):
    print(year)
    folder_regrid_2_2km_lin = (f"datadir/NIMROD/{time_resolution}/OriginalFormat_1km/{year}").replace('OriginalFormat_1km', 'NIMROD_regridded_2.2km/LinearRegridding')
    folder_regrid_2_2km_nn = (f"datadir/NIMROD/{time_resolution}/OriginalFormat_1km/{year}").replace('OriginalFormat_1km', 'NIMROD_regridded_2.2km/NearestNeighbour')

    folder_regrid_12km_lin = (f"datadir/NIMROD/{time_resolution}/OriginalFormat_1km/{year}").replace('OriginalFormat_1km', 'NIMROD_regridded_12km/LinearRegridding')
    folder_regrid_12km_nn = (f"datadir/NIMROD/{time_resolution}/OriginalFormat_1km/{year}").replace('OriginalFormat_1km', 'NIMROD_regridded_12km/NearestNeighbour')
    print("Making folders")
                
    for folder_fp in [folder_regrid_2_2km_lin, folder_regrid_2_2km_nn, folder_regrid_12km_lin, folder_regrid_12km_nn]:

        if not os.path.isdir(folder_fp):
            os.makedirs(folder_fp)
                
    print("Starting regridding")
    for filename in glob.glob(f"datadir/NIMROD/{time_resolution}/OriginalFormat_1km/{year}/*"):
        # Load data
        cube =iris.load_cube(filename)

        for regridding_resolution in ['2.2km', '12km']:
            # Specify model cube to use in regridding
            if regridding_resolution == '2.2km':
                cube_model = cube_model_2_2km
            elif regridding_resolution == '12km':
                cube_model = cube_model_12km

            #### Regrid observaitons onto model grid
            # Lienar interpolation
            reg_cube_lin =cube.regrid(cube_model,iris.analysis.Linear())      
            # Nearest neighbour
            reg_cube_nn =cube.regrid(cube_model,iris.analysis.Nearest())    

            # Filename to save regridded cube to - 2.2km -- linear/nearest neighbour
            filename_regrid_lin = filename.replace(f"OriginalFormat_1km/{year}/", f"NIMROD_regridded_{regridding_resolution}/LinearRegridding/{year}/rg_")
            filename_regrid_nn = filename.replace(f"OriginalFormat_1km/{year}/", f"NIMROD_regridded_{regridding_resolution}/NearestNeighbour/{year}/rg_")

            # Save regridded
            iris.save(reg_cube_lin, filename_regrid_lin)
            iris.save(reg_cube_nn, filename_regrid_nn)
