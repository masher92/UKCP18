import iris
import glob
import datetime
from iris.time import PartialDateTime
import sys
#import xarray as xr
import os

date, radardir = str(sys.argv[1]), str(sys.argv[2])
#print(date)
file_list=glob.glob(radardir+"/*"+date+"*composite_1km_merged")

cube = iris.load(file_list)
#print('loaded')
if len(cube) > 1:
    iris.util.equalise_attributes(cube)
    try:
        out_cube = cube.concatenate_cube()[:,600:1310,480:1090]
    except:
        split_cubes = list(cube[0].slices_over('time'))
        for i in range(1,len(cube)):
            split_cubes = split_cubes + list(cube[i].slices_over('time'))
        out_cube = iris.cube.CubeList(split_cubes).merge_cube()
        out_cube = out_cube[:,600:1310,480:1090]
else:
    out_cube = cube[0][:,600:1310,480:1090]

outcubename=file_list[0][:-58] + date + file_list[0][-46:] + ".nc"
try:
    out_cube.remove_coord('experiment_number')
    out_cube.remove_coord('realization')
    out_cube.remove_coord("forecast_period")
except:
    out_cube = out_cube

iris.save(out_cube,outcubename)
