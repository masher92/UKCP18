import iris
import glob
import datetime
from iris.time import PartialDateTime
import sys
import os
import warnings
from iris.coords import DimCoord
import numpy as np
import cftime
import cf_units
import iris.fileformats
warnings.simplefilter(action = 'ignore', category = FutureWarning)


TIME_UNIT = cf_units.Unit(
    "seconds since 1970-01-01 00:00:00", calendar=cf_units.CALENDAR_GREGORIAN
)

NIMROD_DEFAULT = -32767.0

def is_missing(field, value):
    """Returns True if value matches an "is-missing" number."""
    return any(
        np.isclose(value, [field.int_mdi, field.float32_mdi, NIMROD_DEFAULT])
    )


def _new_time(cube, field):
    """Add a time coord to the cube based on validity time and time-window."""
    if field.vt_year <= 0:
        # Some ancillary files, eg land sea mask do not
        # have a validity time.
        return
    else:
        valid_date = cftime.datetime(
            field.vt_year,
            field.vt_month,
            field.vt_day,
            field.vt_hour,
            field.vt_minute,
            #field.vt_second,
        )
    point = np.around(TIME_UNIT.date2num(valid_date)).astype(np.int64)

    period_seconds = None
    if field.period_minutes == 32767:
        period_seconds = field.period_seconds
    elif (
        not is_missing(field, field.period_minutes)
        and field.period_minutes != 0
    ):
        period_seconds = field.period_minutes * 60
    if period_seconds:
        bounds = np.array([point - period_seconds, point], dtype=np.int64)
    else:
        bounds = None

    time_coord = DimCoord(
        points=point, bounds=bounds, standard_name="time", units=TIME_UNIT
    )

    cube.add_aux_coord(time_coord)


iris.fileformats.nimrod_load_rules.time=_new_time


# Get the year
year = sys.argv[1]

# Create path to files containing functions
sys.path.insert(0, '/nfs/a319/gy17m2a/PhD/Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline('epsg:3857')

# Define list of files
radardir = f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/"
print(radardir)
file_list=glob.glob(radardir +"*.dat")
print(file_list)

# Load the files
cube_list = iris.load(file_list)
cube_list

# Concatenate the cubes
try:
    # Merge the list        
    model_cube = cube_list.concatenate_cube()
    # print(out_cube)
    
except:
    #print("Sorting atttributes")
    # Create a list of all the cubes which have the same attribute 
    split_cubes = list(cube_list[0].slices_over('time'))

    # Add to that list the cubes which don't have the same attribute
    for i in range(1,len(cube_list)):
        # print(i)
        split_cubes = split_cubes + list(cube_list[i].slices_over('time'))

    # Go through the list of cubes and delete the trouble making attribute
#     for i in range(1,len(split_cubes)):
#         if 'Probability methods' in split_cubes[i].attributes:
#             # print("Deleting attribute")
#             del split_cubes[i].attributes['Probability methods']

    attributes = split_cubes[0].attributes
    metadata = split_cubes[0].metadata
    # Go through the list of cubes and delete the trouble making attribute
    for i in range(0,len(split_cubes)):
        #print(split_cubes[i].attributes)
        if  split_cubes[i].attributes != attributes:
            # print("Changing attribute")
            split_cubes[i].attributes = attributes
            split_cubes[i].metadata = metadata
            
            
    # Get rid of ones which are wrong shape        
    to_del = []
    for i in range(0,len(split_cubes)):
        if split_cubes[i].shape[1] != 1725 and split_cubes[0].shape[1] != 2175:
            to_del.append(i)
    for index in sorted(to_del, reverse=True):
        del split_cubes[index]            

    # Merge the list    
    try:
        model_cube = iris.cube.CubeList(split_cubes).merge_cube()
    #print(model_cube)
    except:
        cube_template = split_cubes[0]
        for i in range(0,len(split_cubes)):
            #print(split_cubes[i].shape)
            if  split_cubes[i].shape != cube_template.shape:
                split_cubes[i] = split_cubes[i].regrid(cube_template,iris.analysis.Nearest())
            else:
                pass
            
            # 
            try:
                model_cube = iris.cube.CubeList(split_cubes).merge_cube()
            except:
                for i in range(0,len(split_cubes)):
                    #print(split_cubes[i].shape)
                    try:
                        split_cubes[i].remove_coord('forecast_reference_time')
                    except:
                        pass

                    try:
                        split_cubes[i].remove_coord('forecast_period')
                    except:
                        pass

                model_cube = iris.cube.CubeList(split_cubes).merge_cube()


# Trim to the region
#model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
print(model_cube.shape)
print(file_list[0])
iris.save(model_cube, file_list[0][0:106]+ '.nc')
print(file_list[0][0:106]+ '.nc')