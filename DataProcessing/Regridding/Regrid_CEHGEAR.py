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

# Create path to files containing functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

ems_hourly = ['01', '04', '06', '07', '08', '09', '10', '11', '12', '13', '15']
ems_30mins = ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = '2002_2020'

### Get the mask
### Read in reformatted data and set coordinate bounds
# (Might have deleted bit of code from previous versions that do the reformatting, check git history)
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)

cube_1km = iris.load('/nfs/a161/gy17m2a/PhD/datadir/CEH-GEAR/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_199006.nc', in_jja)[0]
cube_1km.coord('projection_y_coordinate').guess_bounds()
cube_1km.coord('projection_x_coordinate').guess_bounds()

### Regrid to 12km using different available methods
cube_aw= cube_1km.regrid(cube_2km_bng, iris.analysis.AreaWeighted()) 
cube_nn= cube_1km.regrid(cube_2km_bng, iris.analysis.Nearest()) 
cube_l= cube_1km.regrid(cube_2km_bng, iris.analysis.Linear()) 

# contraint so we only bother for JJA data
# Directory where data will be saved 
dir_to_save_to = f"/nfs/a161/gy17m2a/PhD/datadir/CEH-GEAR/CEH-GEAR_regridded_12km/AreaWeighted/"
# For all files in the directory
for filename in np.sort(glob.glob("/nfs/a161/gy17m2a/PhD/datadir/CEH-GEAR/CEH-GEAR_reformatted/*")):
    print(filename)
    filename_to_save_to = f"rg_{filename}"
    # Check if it doesn't already exist
    if not os.path.isfile(dir_to_save_to + filename_to_save_to):
        print("Creating")
        # if it's in JJA
        try:
            cube_1km = iris.load(filename, in_jja)[0] 
            print("JJA")
            # Coordinates dont have bounds
            cube_1km.coord('projection_y_coordinate').guess_bounds()
            cube_1km.coord('projection_x_coordinate').guess_bounds()
            # Regrid with area weighted
            cube_aw= cube_1km.regrid(cube_12km, iris.analysis.AreaWeighted()) 
            # File path to save to
            dir_to_save_to = f"/nfs/a319/gy17m2a/PhD/datadir/CEH-GEAR/CEH-GEAR_regridded_12km/AreaWeighted/"
            filename_to_save_to = f"rg_{filename}"
            iris.save(cube_aw, dir_to_save_to + filename_to_save_to)
        except:
            print("Not JJA")
    else:
        print("already exists")