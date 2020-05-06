import numpy as np
from numpy import array, shape
from cartopy import geodesic

# Function which extracts the indices of the closest location in the observations
# cube, to a point of interest 
def find_idx_closestpoint (coords_cube, target_lat, target_lon, flip):
           
    # Extract the latitude and longitude values from the cube into arrays.
    # In each of the latitude and longitude cubes the coordinate values are stored 
    # as an array of values over two dimensions, rather than a list of values in one dimension.
    lats=coords_cube[3].data
    lons=coords_cube[4].data

    # If flip is true, then flip them to match the later flipping of the precipitation data    
    if flip == True:
            lats=np.flipud(lats)
            lons=np.flipud(lons)
        
    # Find the dimensions of the coordinates
    dims=shape(lats)
      
    # Initialise the variable which holds the distance to the nearest grid point
    min_dist=1e10 # big number 
    
    # Define an ellipsoid on which to solve Geodesic (e.g. on a sphere) problems
    # e.g. the shape of the Earth
    myGeod = geodesic.Geodesic(6378137.0,1 / 298.257223563)
        
    # Find the lat and long associated with each array position 
    # (defined by col, row indices)
    # Test the distance between our location of interest, and this location.
    # If it is the shortest yet, then save the index values, and reset the 
    # minimum distance to this distance value.
    for i in range(dims[0]):
        for j in range(dims[1]):
            # Create array containing the location of interest and a lat, long
            # pair from the cube.
            this_lat=lats[i,j]
            this_lon=lons[i,j]
            latlon = array([[this_lat, this_lon], [target_lat, target_lon]])
            # Find distance betwen two pairs of points?
            this_dist= myGeod.geometry_length(latlon)
            if(this_dist<min_dist):
                i_min_dist=i
                j_min_dist=j
                min_dist=this_dist
            
    print ("The closest location to the location of interest was", min_dist, "metres away")
    return (i_min_dist, j_min_dist)
            
            
