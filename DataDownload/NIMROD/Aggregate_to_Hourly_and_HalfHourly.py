import iris
import glob
import numpy as np
import os
import sys
import iris.coord_categorisation as cat

def process_hour(cube):
    if cube is None or len(cube.shape) == 2 or cube.shape[0] < 8:
        return None
    return cube.copy().aggregated_by(['hour'], iris.analysis.MEAN)

def process_half_hour(cube):
    if cube is None or len(cube.shape) == 2 or cube.shape[0] < 4:
        return None
    return cube.copy().aggregated_by(['hour'], iris.analysis.MEAN)

def create_year_directory(base_path, year):
    for label in ['filtered_300', 'unfiltered']:
        year_path = os.path.join(base_path.format(label), str(year))
        os.makedirs(year_path, exist_ok=True)

def process_and_save_cubes(cube_list, label, base_fp, year, iteration):
    if not cube_list:
        return
    for i in range(len(cube_list)):
        cube_list[i].data = cube_list[i].data.astype('float64')
    try:
        full_day_cube = cube_list.concatenate_cube()
    except:
        return
    save_path = base_fp.replace('unfiltered', label)
    print(save_path)
    iris.save(full_day_cube, save_path)

def process_year(year):
    radardir = f'/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/'
    sorted_files = sorted(glob.glob(radardir + "*.nc"))[120:]
    
    for i, file_path in enumerate(sorted_files):
        new_fp_base = file_path.replace('OriginalFormat_1km/', 'OriginalFormat_1km/unfiltered/')
        new_fp_base = new_fp_base.replace(f'/{year}/', f'/{year}/')
        new_fp_base_30mins = new_fp_base.replace('5mins', '30mins')[:-3] + '_30mins.nc'
        new_fp_base_hrly = new_fp_base.replace('5mins', '1hr')[:-3] + '_1h.nc'
        
        if not os.path.exists(new_fp_base_hrly.replace('unfiltered', 'filtered_300')):
            try:
                day_cube = iris.load_cube(file_path)    
                if len(day_cube.shape) == 2:
                    day_cube = iris.util.new_axis(day_cube, "time")
                day_cube = day_cube[:, 620:1800, 210:1075]
                cat.add_hour(day_cube, 'time', name='hour')

                first_half_constraint = iris.Constraint(time=lambda cell: cell.point.minute < 30)
                second_half_constraint = iris.Constraint(time=lambda cell: cell.point.minute >= 30)

                unfiltered_ls_30m, unfiltered_ls_h = iris.cube.CubeList(), iris.cube.CubeList()
                filtered_100_ls_30m, filtered_100_ls_h = iris.cube.CubeList(), iris.cube.CubeList()

                for hour in set(day_cube.coord('hour').points):
                    hour_constraint = iris.Constraint(time=lambda cell: cell.point.hour == hour)
                    this_hour_cube = day_cube.extract(hour_constraint)

                    if np.nanmin(this_hour_cube.data) < 0:
                        this_hour_cube.data = np.where(this_hour_cube.data < 0, np.nan, this_hour_cube.data)

                    hour_cube_filtered_100 = this_hour_cube.copy()
                    hour_cube_filtered_100.data = np.where(hour_cube_filtered_100.data > 300, np.nan, hour_cube_filtered_100.data)

                    hour_cube_unfiltered = process_hour(this_hour_cube)
                    hour_cube_filtered = process_hour(hour_cube_filtered_100)

                    if hour_cube_unfiltered:
                        unfiltered_ls_h.append(hour_cube_unfiltered)
                    if hour_cube_filtered:
                        filtered_100_ls_h.append(hour_cube_filtered)

                    first_half_unfiltered = process_half_hour(this_hour_cube.extract(first_half_constraint))
                    second_half_unfiltered = process_half_hour(this_hour_cube.extract(second_half_constraint))

                    first_half_filtered = process_half_hour(hour_cube_filtered_100.extract(first_half_constraint))
                    second_half_filtered = process_half_hour(hour_cube_filtered_100.extract(second_half_constraint))

                    for cube in [first_half_unfiltered, second_half_unfiltered]:
                        if cube:
                            unfiltered_ls_30m.append(cube)
                    for cube in [first_half_filtered, second_half_filtered]:
                        if cube:
                            filtered_100_ls_30m.append(cube)

                for label, cube_list in [('unfiltered', unfiltered_ls_30m), ('filtered_300', filtered_100_ls_30m)]:
                    process_and_save_cubes(cube_list, label, new_fp_base_30mins, year, i)

                for label, cube_list in [('unfiltered', unfiltered_ls_h), ('filtered_300', filtered_100_ls_h)]:
                    process_and_save_cubes(cube_list, label, new_fp_base_hrly, year, i)
            except:
                print("EEERRRROOOR")
        else:
            print(f" {new_fp_base.replace('unfiltered', 'filtered_300')[:-3] + '_1h.nc'} exists")            
       

year = sys.argv[1]
base_path_30m = '/nfs/a161/gy17m2a/PhD/datadir/NIMROD/30mins/OriginalFormat_1km/{}'
create_year_directory(base_path_30m, year)
base_path_1h = '/nfs/a161/gy17m2a/PhD/datadir/NIMROD/1hr/OriginalFormat_1km/{}'
create_year_directory(base_path_1h, year)
process_year(year)
