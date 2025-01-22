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

# For each file in the CEH-GEAR directory:
# Reformat and then regrid into same format as the UKCP18 model cube
i=0
for filename in glob.glob('/nfs/a161/gy17m2a/PhD/datadir/CEH-GEAR/1km/*')[60:80]:
    print(i)
    xr_ds=xr.open_dataset(filename)
    cube=make_bng_cube(xr_ds,'rainfall_amount')
    cube.coord('projection_y_coordinate').guess_bounds()
    cube.coord('projection_x_coordinate').guess_bounds()
    
    rf_filename = filename.replace('1km', '1km_reformatted')
    iris.save(cube, rf_filename)
    # Regrid with area weighted
    km12_filename = filename.replace('1km', '12km_regridded/AreaWeighted/')
    cube_aw= cube.regrid(cube_12km, iris.analysis.AreaWeighted()) 
    # File path to save to
    dir_to_save_to = f"/nfs/a161/gy17m2a/PhD/datadir/CEH-GEAR/12km_regridded/AreaWeighted/"
    filename_to_save_to = f"{filename}"
    iris.save(cube_aw, km12_filename)    
    i=i+1