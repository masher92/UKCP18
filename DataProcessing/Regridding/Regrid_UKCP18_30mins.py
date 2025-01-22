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
import ast

# Get the command-line argument and convert it into a list
ems = ['bc005']
print(ems)
yrs_range='2002_2020'

# Read in functions
sys.path.insert(0, root_fp + 'PhD/Scripts/DataProcessing/Regridding')
from Regridding_functions import *
# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

ems_hourly = ['01', '04', '06', '07', '08', '09', '10', '11', '12', '13', '15']
# yrs_range = '2060_2081'# '2002_2020' #'2060_2081'

gb_gdf = create_gb_outline({'init' :'epsg:3857'})

###################
# Create a LSM at 2.2km resolution 
####################
file_model_2_2km_bng_30mins = '/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_original/2002_2020/bc005/bc005a.pr200101.nc'

cube_2km_30mins = iris.load_cube(file_model_2_2km_bng_30mins)
cube_2km_30mins = trim_to_bbox_of_region_regriddedobs(cube_2km_30mins, gb_gdf)
cube_2km_30mins_bng, lats_bng, lons_bng = convert_rotatedpol_to_bng(cube_2km_30mins.copy())

lsm = iris.load("/nfs/a319/gy17m2a/PhD/datadir/Masks/lsm_land-cpm_BI_5km.nc")[0]
lsm_2km = lsm.regrid(cube_2km_30mins_bng, iris.analysis.Nearest()) 

broadcasted_lsm_2km_30mins_data = np.broadcast_to(lsm_2km.data.data, cube_2km_30mins_bng.shape)
broadcasted_lsm_2km_30mins_data_reversed = ~broadcasted_lsm_2km_30mins_data.astype(bool)

file_model_12km=f'/nfs/a161/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng_regridded_12km_masked/04/AreaWeighted/1980_2001/bng_rg_pr_rcp85_land-cpm_uk_2.2km_04_1hr_19810601-19810630.nc'
cube_12km=iris.load_cube(file_model_12km)

##################################################################
# 
##################################################################
for em in ems:
    print(em)
    os.chdir(f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_original/{yrs_range}/{em}/")
    # establish paths to directories
    output_fp_bng_masked = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_masked/{yrs_range}/{em}/"
    output_fp_bng_regridded_12km = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng_regridded_12km_masked/{yrs_range}/{em}/"
    
    # create the directories
    if not os.path.isdir(output_fp_bng_masked):
        os.makedirs(output_fp_bng_masked)    
    if not os.path.isdir(output_fp_bng_regridded_12km):
         os.makedirs(output_fp_bng_regridded_12km)    
            
    # loop through the files
    for filename in np.sort(glob.glob("*"))[1:]: 
        print(filename)
        if "2000" not in filename:
            if not os.path.isfile(output_fp_bng_regridded_12km +  f"bng_{filename}"):
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
                cube_2km_bng_masked_regridded_12km = cube_2km_bng_masked.regrid(cube_12km, iris.analysis.AreaWeighted(mdtol=0.8)) 
                # Save 
                iris.save(cube_2km_bng_masked, output_fp_bng_masked +  f"bng_{filename}")
                iris.save(cube_2km_bng_masked_regridded_12km, output_fp_bng_regridded_12km +  f"bng_{filename}") 

            else:
                print("already exists")    
                
                
                
# file_model_2_2km_bng_30mins = '/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/2.2km_bng/2002_2020/bc005/bng_bc005a.pr200101.nc'

# # Get a surrogate cube
# surrogate_cube = iris.load_cube(file_model_2_2km_bng_30mins)
# # Attach the data to it that I actually want
# cube_2km_data = cube_2km.data
# surrogate_cube.data = cube_2km_data
# # Attach the proper times

# time_coord = cube_2km.coord('time')

# # Ensure the time coordinate has a name
# time_coord.rename('time')

# # Remove the existing time coordinate from surrogate_cube if it exists
# try:
#     surrogate_cube.remove_coord('time')
# except iris.exceptions.CoordinateNotFoundError:
#     pass  # If the time coordinate is not found, proceed

# # Determine the correct dimension index for time in surrogate_cube
# # Assuming the time dimension should be the first dimension (index 0)
# time_dim_index = 0

# # Add the new time coordinate to surrogate_cube as a dimension coordinate
# surrogate_cube.add_dim_coord(time_coord, time_dim_index)

# # Verify the change
# print(surrogate_cube)

# cube_2km = surrogate_cube
# print(cube_2km.coord('time'))

# cube_2km = trim_to_bbox_of_region_regriddedobs(cube_2km, gb_gdf)
# # Transform to BNG
# cube_2km_bng, lats_bng, lons_bng = convert_rotatedpol_to_bng(cube_2km.copy())
# # Mask to GB
# cube_2km_bng_masked = iris.util.mask_cube(cube_2km_bng.copy(), broadcasted_lsm_2km_30mins_data_reversed)
# # Regrid to 12km
# # cube_2km_bng_masked_regridded_12km = cube_2km_bng_masked.regrid(cube_12km, iris.analysis.AreaWeighted(mdtol=0.8)) 
# # Save 
# iris.save(cube_2km_bng, output_fp_bng +  f"bng_{filename}")     
# iris.save(cube_2km_bng_masked, output_fp_bng_masked +  f"bng_{filename}")                