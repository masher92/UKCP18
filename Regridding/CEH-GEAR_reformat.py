import iris
import xarray as xr
import numpy as np
from iris.coords import DimCoord
from iris.coord_systems import TransverseMercator,GeogCS
from iris.cube import Cube
#from iris.unit import Unit
from cf_units import Unit
import cf_units
import os
import glob

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Function to reformat the cube
def make_bng_cube(xr_ds,variable):
    # Store the northings values
    raw_northings=xr_ds['y'].values
    # Store the eastings values
    raw_eastings=xr_ds['x'].values
    # Find the length of northings and eastings 
    lrn=len(raw_northings)
    lre=len(raw_eastings)
    # Set up a OS_GB (BNG) coordinate system
    os_gb=TransverseMercator(latitude_of_projection_origin=49.0, longitude_of_central_meridian=-2.0, false_easting=400000.0, false_northing=-100000.0, scale_factor_at_central_meridian=0.9996012717, ellipsoid=GeogCS(semi_major_axis=6377563.396, semi_minor_axis=6356256.909))
    # Create northings and eastings dimension coordinates
    northings = DimCoord(raw_northings, standard_name=u'projection_y_coordinate', 
                         units=Unit('m'), var_name='projection_y_coordinate', coord_system=os_gb)
    eastings = DimCoord(raw_eastings, standard_name=u'projection_x_coordinate', 
                        units=Unit('m'), var_name='projection_x_coordinate', coord_system=os_gb)
    # Create a time dimension coordinate
    iris_time=(xr_ds['time'].values-np.datetime64("1970-01-01T00:00")) / np.timedelta64(1, "s")
    iris_time=DimCoord(iris_time, standard_name='time',units=cf_units.Unit('seconds since 1970-01-01', calendar='gregorian'))
    # Store the data array
    da=xr_ds[variable]
    # Recreate the cube with the data and the dimension coordinates
    cube = Cube(np.float32(da.values), standard_name=da.standard_name, units=da.units, dim_coords_and_dims=[(iris_time, 0), (northings, 1),(eastings, 2)])
    return cube


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
    # Filename to save regridded cube to
    filename_regrid = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_regridded_2.2km/rg_")
    # If files don't already exist, then create
    if not os.path.isfile(filename_regrid):
      # Open dataset with Xarray
      xr_ds=xr.open_dataset(filename)
      # Convert to cube in the correct format and save
      cube=make_bng_cube(xr_ds,'rainfall_amount')
      iris.save(cube, filename_reformat)
      
      # Regrid observaitons onto model grid
      reg_cube=cube.regrid(cube_model,iris.analysis.Linear())      
      
      reg_cube_aw =cube.regrid(cube_model,iris.analysis.AreaWeighted())   
      
      # Save 
      iris.save(reg_cube, filename_regrid)
    
    i = i+1




    
    