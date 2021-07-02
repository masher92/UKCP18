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
import warnings

warnings.filterwarnings("ignore")

ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

##########################################################################################
#########################################################################################
# Define variables and set up environment
##########################################################################################
##########################################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/RegriddingObservations')
from Regridding_functions import *

# Load UKCP18 12km model data to use in regriddding
file_model='/nfs/a319/gy17m2a/datadir/UKCP18/12km/01/pr_rcp85_land-rcm_uk_12km_01_day_19801201-19901130.nc'
cube_model=iris.load_cube(file_model)

##########################################################################################
##########################################################################################    
#### Regrid CEH-GEAR
##########################################################################################
##########################################################################################
#os.chdir("datadir/CEH-GEAR/CEH-GEAR_reformatted/")
#i = 0
#for filename in glob.glob("*"):
#  print(filename)
#  print(i)
#  cube = iris.load(filename)[0]
#  filename_to_save_to = "/nfs/a319/gy17m2a/datadir/CEH-GEAR/CEH-GEAR_regridded_12km/NearestNeighbour/rg_{}".format(filename[3:])
#  if not os.path.isfile(filename_to_save_to):
#    #print(cube)
#    #### Regrid observaitons onto 12km model grid
#    # Lienar interpolation
#    #reg_cube_lin =cube.regrid(cube_model,iris.analysis.Linear())      
#    # Nearest neighbour
#    reg_cube_nn =cube.regrid(cube_model,iris.analysis.Nearest())    
#    print("Regridded")
#    # Save 
#    #iris.save(reg_cube_lin, "/nfs/a319/gy17m2a/datadir/CEH-GEAR/CEH-GEAR_regridded_12km/LinearInterpolation/rg_{}".format(filename[3:]))
#    iris.save(reg_cube_nn, filename_to_save_to)
#    i=i+1
  
##########################################################################################
##########################################################################################    
#### Regrid UKCP18
##########################################################################################
##########################################################################################
for em in ems:
  os.chdir("/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/{}/1980_2001/".format(em))
  print(em)
  for filename in glob.glob("*"):     
      filename_to_save_to = "/nfs/a319/gy17m2a/datadir/UKCP18/2.2km_regridded_12km/{}/NearestNeighbour/1980_2001/rg_{}".format(em, filename)
      if not os.path.isfile(filename_to_save_to):
        print(filename)
        cube = iris.load(filename)[0]
        # Linear interpolation
        #reg_cube_lin =cube.regrid(cube_model,iris.analysis.Linear())      
        # Nearest neighbour
        reg_cube_nn =cube.regrid(cube_model,iris.analysis.Nearest())   
        # Save 
        #iris.save(reg_cube_lin, "datadir/UKCP18_2.2km_regridded_12km/{}/1980_2001/NearestNeighbour/{}/rg_".format(em))
        iris.save(reg_cube_nn, filename_to_save_to)     
