import numpy as np
from numpy import array, shape
from cartopy import geodesic
from pyproj import Proj, transform
import itertools
from scipy import spatial
import iris 
import numpy.ma as ma

def create_concat_cube_one_location_obs (concat_cube, lat, lon):

    # Convert WGS84 coordinate to BNG
    lon_bng,lat_bng = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:27700'),
                                lon, lat)
    # Create as a list
    sample_point = [('grid_latitude', lat_bng), ('grid_longitude', lon_bng)]
             
    # Create a list of all the tuple pairs of latitude and longitudes
    locations = list(itertools.product(concat_cube.coord('projection_y_coordinate').points,
                                       concat_cube.coord('projection_x_coordinate').points))
    
    # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
    tree = spatial.KDTree(locations)
    closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
    
    # Extract the lat and long values of this point using the index
    closest_lat = locations[closest_point_idx][0]
    closest_long = locations[closest_point_idx][1]

    # Use this closest lat, long pair to collapse the latitude and longitude dimensions
    # of the concatenated cube to keep just the time series for this closest point 
    time_series = concat_cube.extract(iris.Constraint(projection_y_coordinate =closest_lat, 
                                                      projection_x_coordinate = closest_long))

    return (time_series, closest_lat, closest_long, closest_point_idx)     



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