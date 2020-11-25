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
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/RegriddingObservations')
from Regridding_functions import *

# Load UKCP18 model data to use in regriddding
file_model='/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19911201-19911230.nc'
cube_model=iris.load_cube(file_model)
    
# For each file in the CEH-GEAR directory:
# Reformat and then regrid into same format as the UKCP18 model cube
i = 0
for filename in glob.glob("datadir/CEH-GEAR/*"):
    print(i)
    # Filename to save reformatted cube to
    filename_reformat = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_reformatted/rf_")
    # Filename to save regridded cube to -- linear
    filename_regrid_lin = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_regridded_2.2km/LinearRegridding/rg_")
    # Filename to save regridded cube to -- nearest neighbour
    filename_regrid_nn = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_")
    
    # If files don't already exist, then create
    #if not os.path.isfile(filename_regrid_nn):
    if 1 == 1:
      # Open dataset with Xarray
      xr_ds=xr.open_dataset(filename)
      # Convert to cube in the correct format and save
      cube=make_bng_cube(xr_ds,'rainfall_amount')
      iris.save(cube, filename_reformat)
      #### Regrid observaitons onto model grid
      # Lienar interpolation
      #reg_cube_lin =cube.regrid(cube_model,iris.analysis.Linear())      
      # Nearest neighbour
      reg_cube_nn =cube.regrid(cube_model,iris.analysis.Nearest())    
     
      # Area weighted regrid
      # First need to convert projection system
      # Store the crs of the model cube
      #cube_model_crs = cube_model.coord('grid_latitude').coord_system.as_cartopy_crs()
      #from pyproj.crs import CRS
      # cube_model_crs_proj = CRS.from_dict(cube_model_crs.proj4_params) 
      #cube_model_clone = cube_model.copy()
      #print(cube_model_clone)
      #cube_model_clone.remove_coord('longitude')
      #cube_model_clone.remove_coord('latitude')
      #iris.analysis.cartography.project(cube_model_clone, cube_model_crs_proj)
      #reg_cube_aw =cube.regrid(cube_model,iris.analysis.AreaWeighted())   
      
      # Save 
      #iris.save(reg_cube_lin, filename_regrid_lin)
      iris.save(reg_cube_nn, filename_regrid_nn)
    
    i = i+1
