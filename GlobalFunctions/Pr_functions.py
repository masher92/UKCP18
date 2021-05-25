import cartopy.crs as ccrs
import iris
import itertools
from scipy import spatial
from timeit import default_timer as timer
from iris.pandas import as_cube, as_series, as_data_frame 
import numpy as np
import numpy.ma as ma

def create_grid_highlighted_cell (concat_cube, closest_point_idx):
    
    # Create cube containing hour's worth of data
    hour_uk_cube = concat_cube[0,:,:]
        
    # Recreate data so that only the cell containing the lat, long location 
    # has a data value
    # Create data of the same shape as the cube and set all the values to 0
    test_data = np.full((hour_uk_cube.shape),0,dtype = int)
    # Reshape to be 1D
    test_data_rs = test_data.reshape(-1)
    # Set the grid cell closest to the lat/long to 1
    test_data_rs[closest_point_idx] = 1
    # Reshape to the original shape
    test_data = test_data_rs.reshape(test_data.shape)
    # Mask out all values that aren't 1
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Set the dummy data back on the cube
    hour_uk_cube.data = test_data
    
    return (hour_uk_cube)


def define_loc_of_interest(cube, lon, lat):
    #############################################
    # Define a sample point at which we are interested in extracting the precipitation timeseries.
    # Assign this the same projection as the projection data
    #############################################
    # Create a cartopy CRS representing the coordinate sytem of the data in the cube.
    rot_pole = cube[0].coord('grid_latitude').coord_system.as_cartopy_crs()
    
    # Define a sample point of interest, in standard lat/long.
    # Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
    original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
    target_xy = rot_pole.transform_point(lon, lat, original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
       
    # Store the sample point of interest as a tuples (with their coordinate name) in a list
    sample_points = [('grid_latitude', target_xy[1]), ('grid_longitude', target_xy[0])]
    return(sample_points)


def create_concat_cube_one_location_m3 (concat_cube, sample_point):
     # Reduce the dimensions (remove ensemble member dimension)
     #concat_cube = concat_cube[0, :]
         
     # Create a list of all the tuple pairs of latitude and longitudes
     locations = list(itertools.product(concat_cube.coord('grid_latitude').points, concat_cube.coord('grid_longitude').points))
     
     # Correct them so that 360 merges back into one
     corrected_locations = []
     for location in locations:
         if location[0] >360:
             new_lat = location[0] -360
         else: 
             new_lat = location[0]
         if location[1] >360:
             new_long = location[1] -360     
         else:
             new_long = location[1]
         new_location = new_lat, new_long 
         corrected_locations.append(new_location)
     
     # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
     tree = spatial.KDTree(corrected_locations)
     closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
     
     # Extract the lat and long values of this point using the index
     closest_lat = locations[closest_point_idx][0]
     closest_long = locations[closest_point_idx][1]
     
     # Use this closest lat, long pair to collapse the latitude and longitude dimensions
     # of the concatenated cube to keep just the time series for this closest point 
     time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
     return (time_series, closest_lat, closest_long, closest_point_idx)     


def concat_cube_multiple_neighbours_m3 (cube_list, sample_point, n_nearest_neighbours):
#Returns a dataframe.
#Not possible to create as a concatenated cube because the latitiude and longitude 
#values are not the same in every cube.
    # Remove attributes which aren't the same across all the cubes.
     for cube in cube_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
     
     # Concatenate the cubes into one
     concat_cube = cube_list.concatenate_cube()
     
     # Reduce the dimensions (remove ensemble member dimension)
     concat_cube = concat_cube[0, :]
     
     # Create a list of all the tuple pairs of latitude and longitudes
     locations = list(itertools.product(concat_cube.coord('grid_latitude').points, concat_cube.coord('grid_longitude').points))
     
     # Correct them so that 360 merges back into one
     corrected_locations = []
     for location in locations:
         if location[0] >360:
             new_lat = location[0] -360
         else: 
             new_lat = location[0]
         if location[1] >360:
             new_long = location[1] -360     
         else:
             new_long = location[1]
         new_location = new_lat, new_long 
         corrected_locations.append(new_location)
     
     # Find the index of the nearest neighbour(s) of the sample point in the list of locations present in concat_cube
     tree = spatial.KDTree(corrected_locations)
     #closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
     closest_points_idxs = tree.query([(sample_point[0][1], sample_point[1][1])], k =n_nearest_neighbours )[1][0]
     
     time_series_dfs = []
     for point in closest_points_idxs:
         # Extract the lat and long values of this point using the index
         closest_lat = locations[point][0]
         closest_long = locations[point][1]
         # Use this closest lat, long pair to collapse the latitude and longitude dimensions
         # of the concatenated cube to keep just the time series for this closest point 
         time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
         
         # Store data as a dataframe
         #time_series = time_series[0:100000]
         start = timer()
         ts_df = pd.DataFrame({'Date': np.array(time_series.coord('yyyymmddhh').points),
                         'Precipitation (mm/hr)': np.array(time_series.lazy_data())})
         print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
          # Add to list of dataframes
         time_series_dfs.append(ts_df)
         print("Created dataframe for nearest neighbour at " + str(point))
     # Join all dataframes into one         
     df = pd.concat(time_series_dfs)
     return df  
 
# Testing of fastest method
# time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# time_series = time_series[0:100000]
# print(time_series.has_lazy_data())
# # Store data as a dataframe
# start = timer()
# ts_df = pd.DataFrame({'Date': np.array(time_series.coord('yyyymmddhh').points),
#                  'Precipitation (mm/hr)': np.array(time_series.data)})
# print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
# print(time_series.has_lazy_data())
   
# time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# time_series = time_series[0:100000]
# print(time_series.has_lazy_data())
# start = timer()
# time_series.remove_coord("time")
# time_series.remove_coord("month_number")
# time_series.remove_coord("year")
# test = iris.pandas.as_data_frame  (time_series) 
# print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
# print(time_series.has_lazy_data())

# time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# time_series = time_series[0:100000]
# print(time_series.has_lazy_data())
# start = timer()
# ts_df = pd.DataFrame({'Date': np.array(time_series.coord('yyyymmddhh').points),
#                  'Precipitation (mm/hr)': np.array(time_series.lazy_data())})
# print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
# print(time_series.has_lazy_data())


# def create_concat_cube_one_location_m1 (cube_list, sample_point):

#     # Create a list to store the interpolated cubes
#     interpolated_cubes = []  
    
#     # Loop through each cube in cubes, perform interpolation, save interpolated cube
#     # to list and delete larger cube
#     for cube_idx in range(0,len(cube_list)):
#         print('Interpolating cube with index: ', cube_idx)
#         # Check whether data is fully loaded
#         #print(cubes[0].has_lazy_data())
#         # Remove attributes which aren't the same across all the cubes (otherwise later concat fails)
#         for attr in ['creation_date', 'tracking_id', 'history']:
#             if attr in cube_list[cube_idx].attributes:
#                 del cube_list[cube_idx].attributes[attr]
#                     # Do the interpolation
        
#         # Interpolate data to the sample location
#         interpolated = cube_list[cube_idx].interpolate(sample_point, iris.analysis.Nearest())
#         # Check whether at this point data is fully loaded
#         # print(interpolated.has_lazy_data())
#         # Add interpolated cube to list of cubes
#         interpolated_cubes.append(interpolated)
#         # Delete the cube from the list and the interpolated cube from memory
#         #del(interpolated)
#         #del(cubes[cube_idx])
    
#     # Create a cube list from the (standard python) list of cubes
#     interpolated_cube_list = iris.cube.CubeList(interpolated_cubes)    
        
#     # Concatenate the cubes into one
#     interpolated_cubes_concat = interpolated_cube_list.concatenate_cube()
    
#     # reduce the dimensions (remove ensemble member dimension)
#     interpolated_cubes_concat = interpolated_cubes_concat[0, :]
#     print ("Single interpolated cube created")
#     return (interpolated_cubes_concat)

# def create_concat_cube_one_location_m2 (cube_list, sample_point):
#     for cube_idx in range(0,len(cube_list)):      
#         for attr in ['creation_date', 'tracking_id', 'history']:
#                     if attr in cube_list[cube_idx].attributes:
#                         del cube_list[cube_idx].attributes[attr]
#                         # Do the interpolation
     
#     # Concatenate the cubes into one
#     interpolated_cubes_concat = cube_list.concatenate_cube()
        
#     # reduce the dimensions (remove ensemble member dimension)
#     interpolated_cubes_concat = interpolated_cubes_concat[0, :]
         
#     # Interpolate data to the sample location
#     interpolated = interpolated_cubes_concat.interpolate(sample_point, iris.analysis.Nearest())
#     return (interpolated)
