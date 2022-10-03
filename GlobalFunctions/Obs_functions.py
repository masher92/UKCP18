import numpy as np
from numpy import array, shape
from cartopy import geodesic
from pyproj import Proj, transform
import itertools
from scipy import spatial
import iris 
import numpy.ma as ma
import pandas as pd
from Spatial_plotting_functions import *
import matplotlib
import matplotlib.pyplot as plt
import tilemapbase
import sys

# Create path to files containing functions
sys.path.insert(0, root_fp + 'PhD/Scripts/GlobalFunctions')
from Spatial_geometry_functions import *

#############################################################################
#############################################################################
# Load in spatial data
# As geodataframes for plotting
# As shapely geometries for checking whether lat/long points are witihn the areas
#############################################################################
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

# Create outlines as shapely geometries
leeds_at_centre_poly = Polygon(create_leeds_at_centre_outline({'init' :'epsg:4326'})['geometry'].iloc[0])
leeds_poly = Polygon(create_leeds_outline({'init' :'epsg:4326'})['geometry'].iloc[0])


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

def find_position_obs (concat_cube, lat, lon, station_name):
    lat_length = concat_cube.shape[1]
    lon_length = concat_cube.shape[2]
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
    closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])], k =1)[1][0]
    
    # Create a list of all the tuple positions
    indexs_lst = []
    for i in range(0,lat_length):
        for j in range(0,lon_length):
            # Print the position
            #print(i,j)
            indexs_lst.append((i,j))
         
    # Extract the lat and long values of this point using the index
    filename = "Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/{}_{}.npy".format(indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1])
    data_slice = np.load(filename)
     
    # Get the times
    times = np.load('Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/timestamps.npy', allow_pickle = True)
         
    # Create dataframe
    df = pd.DataFrame({'Times': times, 'Precipitation (mm/hr)':data_slice})
     
    ######## Check plotting 
    # Get cube containing one hour worth of data
    hour_uk_cube = concat_cube[0,:,:]

    # Set all the values to 0
    test_data = np.full((hour_uk_cube.shape),0,dtype = int)
    # Set the values at the index position fond above to 1
    test_data[indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1]] = 1
    # Mask out all values that aren't 1
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Set the dummy data back on the cube
    hour_uk_cube.data = test_data
    
    # Find cornerpoint coordinates (for use in plotting)
    lats_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    hour_uk_cube = hour_uk_cube[1:,1:]
    test_data = hour_uk_cube.data

    # Create location in web mercator for plotting
    print('Creating plot')
    lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
    
    # Create a colormap
    cmap = matplotlib.colors.ListedColormap(['red'])
    
    fig, ax = plt.subplots(figsize=(30,30))
    extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
    plot =plotter.plot(ax)
    # # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
          linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 10)     
    #plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Figs/CheckingLocations/CEH-GEAR/{}.png'.format(station_name),
    #            bbox_inches = 'tight')
    plt.show()
 
    return (df, closest_point_idx)    


def create_grid_highlighted_cell_obs (concat_cube, closest_point_idx):
    
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