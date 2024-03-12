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
ems_30mins = ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = '1980_2001'



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

#file_model_12km_wgs84 ='/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/12km_wgs84/01/1980_2001/wgs84_pr_rcp85_land-#rcm_uk_12km_01_day_20701201-20801130.nc'
#cube_12km_wgs84 =iris.load_cube(file_model_12km_wgs84)

# remove ensemble member dimension
cube_2km = cube_2km[0,:,:,:]
cube_12km = cube_12km[0,:,:,:]

def convert_rotatedpol_to_bng(cube):
    # Define the original crs (rotated pole) and the target crs (BNG)
    source_crs = ccrs.RotatedGeodetic(pole_latitude=37.5,
                                      pole_longitude=177.5,
                                      central_rotated_longitude=0)
    target_crs = ccrs.OSGB()
    
    os_gb=TransverseMercator(latitude_of_projection_origin=49.0, longitude_of_central_meridian=-2.0, 
                         false_easting=400000.0, false_northing=-100000.0, scale_factor_at_central_meridian=0.9996012717, 
                         ellipsoid=GeogCS(semi_major_axis=6377563.396, semi_minor_axis=6356256.909))

    # Extract the 2D meshgrid of lats/lons in rotated pole
    x = cube.coord('grid_longitude').points # long
    y = cube.coord('grid_latitude').points # lat
    # Convert to 2D
    xx, yy = np.meshgrid(x, y)

    # Use transform_points to project your coordinates into BNG
    transformed_points = target_crs.transform_points(source_crs, xx.flatten(), yy.flatten())

    # Reshape the array back to your original grid shape and separate the components
    lons_bng, lats_bng = transformed_points[..., 0].reshape(xx.shape), transformed_points[..., 1].reshape(yy.shape)

    # Here's a simplified way to create a new cube with the transformed coordinates,
    # assuming your original data is 2-dimensional and compatible with the new grid.
    new_cube_data = cube.data  # This might require adjustment if the data needs to be interpolated onto the new grid.
    latitude_coord = iris.coords.DimCoord(lats_bng[:, 0], standard_name='projection_y_coordinate', units='m',
                                          coord_system=os_gb)
    longitude_coord = iris.coords.DimCoord(lons_bng[0, :], standard_name='projection_x_coordinate', units='m',
                                          coord_system=os_gb)

    # Guess bounds
    latitude_coord.guess_bounds()
    longitude_coord.guess_bounds()

    cube_2km_bng = cube.copy()
    cube_2km_bng.remove_coord('grid_latitude')
    cube_2km_bng.remove_coord('grid_longitude')
    # If your data is indeed 2-dimensional as suggested, these should be added as dimension coordinates
    cube_2km_bng.add_dim_coord(latitude_coord, 1)  # Assuming latitude corresponds to the first dimension
    cube_2km_bng.add_dim_coord(longitude_coord, 2)  # And longitude to the second
    
    return cube_2km_bng

# this is the crs that we want to transform to
source_crs_2km = ccrs.RotatedGeodetic(pole_latitude=37.5,
                                        pole_longitude=177.5,
                                        central_rotated_longitude=0)

# these are the crs we are transforming from
target_crs = ccrs.Geodetic()

##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
cube_12km_trimmed_to_leeds =  trim_to_bbox_of_region_obs(cube_12km, leeds_at_centre_gdf, 'projection_y_coordinate',
                                                        "projection_x_coordinate")

yrs_range = '1980_2001'
# ems_hourly = ['04', '06', '07', '08', '09', '10', ]


for em in ['05']:
    print(em)
    os.chdir(f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km/{em}/{yrs_range}/")
    output_fp_bng = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng/{em}/{yrs_range}/"
    output_fp_bng_regridded = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_bng_regridded_12km/{em}/AreaWeighted/{yrs_range}/"
    if not os.path.isdir(output_fp_bng):
        os.makedirs(output_fp_bng)
    if not os.path.isdir(output_fp_bng_regridded):
        os.makedirs(output_fp_bng_regridded)        
    for filename in np.sort(glob.glob("*")):     
            if filename[47:49] in ['06', '07', '08']:
                if os.path.isfile(output_fp_bng +  f"bng_{filename}"):
                    print("already exist")                    
                else:
                    print(filename)
                    cube_2km = iris.load(filename)[0]
                    cube_2km = cube_2km[0,:,:,:]
                    # transform to BNG
                    cube_2km_bng= convert_rotatedpol_to_bng (cube_2km)
                    # regrid to 12km
                    cube_2km_regridded_12km_bng = cube_2km_bng.regrid(cube_12km, iris.analysis.AreaWeighted()) 
                    # Save 
                    iris.save(cube_2km_bng, output_fp_bng +  f"bng_{filename}")
                    iris.save(cube_2km_regridded_12km_bng, output_fp_bng_regridded +  f"bng_rg_{filename}")     