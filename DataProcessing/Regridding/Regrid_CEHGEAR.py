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
import xarray as xr

warnings.filterwarnings("ignore")

root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

file_model_12km=f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_regridded_12km_masked/2002_2020/bc005/bng_bc005a.pr201912.nc'
cube_12km = iris.load(file_model_12km)[0]

file_model_2km=f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_masked/2002_2020/bc005/bng_bc005a.pr201912.nc'
cube_2km = iris.load(file_model_2km)[0]

# For each file in the CEH-GEAR directory:
# Reformat and then regrid into same format as the UKCP18 model cube
i=int(sys.argv[1])
for filename in  np.sort(glob.glob('/nfs/a161/gy17m2a/PhD/datadir/CEH-GEAR/1km/*'))[i:i+1]:
    print(filename)
    km2_filename = filename.replace('1km', '2.2km_regridded/AreaWeighted')
    if not os.path.isfile(km2_filename): 
        print(f"Creating {km2_filename}")
        xr_ds=xr.open_dataset(filename)
        cube=make_bng_cube(xr_ds,'rainfall_amount')
        cube.coord('projection_y_coordinate').guess_bounds()
        cube.coord('projection_x_coordinate').guess_bounds()

        rf_filename = filename.replace('1km', '1km_reformatted')
        iris.save(cube, rf_filename)

        # Regrid with area weighted
        cube_aw_12km  = cube.regrid(cube_12km, iris.analysis.AreaWeighted()) 
        print(f"12km cube shape: {cube_aw_12km.shape}")
        km12_filename = filename.replace('1km', '12km_regridded/AreaWeighted/')
        iris.save(cube_aw_12km, km12_filename)    

        cube_aw_2km = cube.regrid(cube_2km, iris.analysis.AreaWeighted())
        print(f"2km cube shape: {cube_aw_2km.shape}")
        km2_filename = filename.replace('1km', '2.2km_regridded/AreaWeighted/')
        iris.save(cube_aw_2km, km2_filename)  

        i=i+1
    else:
        print(f"{km2_filename} exists")