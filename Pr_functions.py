import cartopy.crs as ccrs
import iris
import itertools
from scipy import spatial

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


def create_concat_cube_one_location_m1 (cube_list, sample_point):

    # Create a list to store the interpolated cubes
    interpolated_cubes = []  
    
    # Loop through each cube in cubes, perform interpolation, save interpolated cube
    # to list and delete larger cube
    for cube_idx in range(0,len(cube_list)):
        print('Interpolating cube with index: ', cube_idx)
        # Check whether data is fully loaded
        #print(cubes[0].has_lazy_data())
        # Remove attributes which aren't the same across all the cubes (otherwise later concat fails)
        for attr in ['creation_date', 'tracking_id', 'history']:
            if attr in cube_list[cube_idx].attributes:
                del cube_list[cube_idx].attributes[attr]
                    # Do the interpolation
        
        # Interpolate data to the sample location
        interpolated = cube_list[cube_idx].interpolate(sample_point, iris.analysis.Nearest())
        # Check whether at this point data is fully loaded
        # print(interpolated.has_lazy_data())
        # Add interpolated cube to list of cubes
        interpolated_cubes.append(interpolated)
        # Delete the cube from the list and the interpolated cube from memory
        #del(interpolated)
        #del(cubes[cube_idx])
    
    # Create a cube list from the (standard python) list of cubes
    interpolated_cube_list = iris.cube.CubeList(interpolated_cubes)    
        
    # Concatenate the cubes into one
    interpolated_cubes_concat = interpolated_cube_list.concatenate_cube()
    
    # reduce the dimensions (remove ensemble member dimension)
    interpolated_cubes_concat = interpolated_cubes_concat[0, :]
    print ("Single interpolated cube created")
    return (interpolated_cubes_concat)

def create_concat_cube_one_location_m2 (cube_list, sample_point):
    for cube_idx in range(0,len(cube_list)):      
        for attr in ['creation_date', 'tracking_id', 'history']:
                    if attr in cube_list[cube_idx].attributes:
                        del cube_list[cube_idx].attributes[attr]
                        # Do the interpolation
     
    # Concatenate the cubes into one
    interpolated_cubes_concat = cube_list.concatenate_cube()
        
    # reduce the dimensions (remove ensemble member dimension)
    interpolated_cubes_concat = interpolated_cubes_concat[0, :]
         
    # Interpolate data to the sample location
    interpolated = interpolated_cubes_concat.interpolate(sample_point, iris.analysis.Nearest())
    return (interpolated)


def create_concat_cube_one_location_m3 (cube_list, sample_point):
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
     
     # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
     tree = spatial.KDTree(corrected_locations)
     closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
     
     # Extract the lat and long values of this point using the index
     closest_lat = locations[closest_point_idx][0]
     closest_long = locations[closest_point_idx][1]
     
     # Use this closest lat, long pair to collapse the latitude and longitude dimensions
     # of the concatenated cube to keep just the time series for this closest point 
     time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
     return (time_series)     

def log_discrete_bins(min_value,max_value,bins_if_log_spaced,discretisation):
    delta_log_i_l_s=(np.log10(max_value)-np.log10(min_value))/bins_if_log_spaced
    bin_edges=[min_value]
    prev_edge=min_value
    lstopped=False
    while(lstopped==False):
        log10prev=np.log10(prev_edge)
        if(log10prev>np.log10(max_value)):
            lstopped=True
        else:
            next_delta=10**(log10prev+delta_log_i_l_s)-10**(log10prev)
            # conservative estimate, round bin size to lower number
            next_edge=prev_edge+max(discretisation,discretisation*int(next_delta/discretisation))
            bin_edges.append(next_edge)
            prev_edge=next_edge
    return bin_edges
