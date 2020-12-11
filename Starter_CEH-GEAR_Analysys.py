import os
import xarray as xr
from iris.coords import DimCoord
from iris.coord_systems import TransverseMercator,GeogCS
from cf_units import Unit
import numpy as np
import cf_units
from iris.cube import Cube
import iris
import iris.plot as iplt

# Define function to reformat the netCDFm observation's cubes
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
    cube = Cube(np.float32(da.values), standard_name=da.standard_name,
                units=da.units, dim_coords_and_dims=[(iris_time, 0), (northings, 1),(eastings, 2)])
    return cube

#########################################################################
### Set your working directory
#########################################################################
# This is a filepath to a home directory where your data/other scripts are found
os.chdir("/nfs/a319/gy17m2a/")

#########################################################################
### Define the filepath for one of the netCDF files that you want to work with
#########################################################################
filepath = 'datadir/CEH-GEAR/CEH-GEAR-1hr_201408.nc'

#########################################################################
###  Load in the data from this filepath and reformat the data so it is easier
###  to work with
#########################################################################
# Load in data
xr_ds=xr.open_dataset(filepath)
# Reformat
cube=make_bng_cube(xr_ds,'rainfall_amount')

#########################################################################
### Save to file for using in the future
#########################################################################
filepath_to_save_to = 'datadir/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_201408.nc'
iris.save(cube, filepath_to_save_to)

#########################################################################
### Inspect cube
### It has 3 dimensions - time and two spatial coordinates
#########################################################################
print(cube) 

#########################################################################
### Extract just one hour of data 
#########################################################################
one_hour = cube[0,:,:]

#########################################################################
### Plot
#########################################################################
iplt.pcolormesh(one_hour)
