import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import os
import geopandas as gpd
import time 
import sys
import iris.quickplot as qplt
import cartopy.crs as ccrs
import matplotlib 
import iris.plot as iplt
from shapely.geometry import Point, Polygon
import itertools
from scipy import spatial
from pyproj import Proj, transform
import numpy.ma as ma
import matplotlib as mpl
import matplotlib.pyplot as plt
import tilemapbase

root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import create_leeds_outline

# Create region with Leeds at the centre
lons = [54.130260, 54.130260, 53.486836, 53.486836]
lats = [-2.138282, -0.895667, -0.895667, -2.138282]
polygon_geom = Polygon(zip(lats, lons))
leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:27700'}) 

# Create otuline of Leeds itself
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})


def find_closest_coordinates(cube, sample_point, n_closest_points):
    '''
    Description
    ----------
        Finds the grid cell(s) in a cube which cover(s) a sample point of interest

    Parameters
    ----------
        cube: Iris Cube
            A cube containing 3 dimensions (time, latitude and longitude)
        sample_point: List
            A list of two tuples containing (1) grid_latitude and its value and (2) grid_longitude and it's value
        n_closest_points: Integer
            The number of closest grid cells to find

    Returns
    -------
        closest_point_idxs: List
            
        closest_lats: List
        
        closest_lons : List
            Dataframe contaiing coordinates of outline of Leeds
    
    '''
    
    ##############################################################
    # Create a list of coordinates and ensure the sample point is in the same coordinate system
    ##############################################################
    # Define names of coordinate variables
    coord_names = [coord.name() for coord in cube.coords()]
    
    # Create variables storing lats/lons (or equivalent variables)
    lats = cube.coord(coord_names[1]).points
    lons = cube.coord(coord_names[2]).points
        
    # Create a list of all the tuple pairs of latitude and longitudes
    locations = list(itertools.product(lats, lons))
                                       
    # If cube coordinates are in rotated pole correct them so that 360 merges back into one
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")  
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
        locations = corrected_locations       
    
        # Convert the sample point also to a rotated pole coordinate system
        rot_pole = cube[0].coord('grid_latitude').coord_system.as_cartopy_crs()
        # Define a sample point of interest, in standard lat/long.
        # Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
        original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
        target_xy = rot_pole.transform_point(sample_point[1][1], sample_point[0][1], original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
           
        # Store the sample point of interest as a tuples (with their coordinate name) in a list
        sample_point = [('grid_latitude', target_xy[1]), ('grid_longitude', target_xy[0])]       
    
    # If cube coordinates are not in rotated pole (and therefore in OSGB36) then transform the sample point
    # to match
    else:
      lon_osgb36,lat_osgb36= transform(Proj(init='epsg:4326'),Proj(init='epsg:27700'),sample_point[1][1],sample_point[0][1])
      #lon_osgb36, lat_osgb36 = transform({'init' :'epsg:4326'}, {'init' :'epsg:27700'}, sample_point[0][1],sample_point[1][1 )
      sample_point = [('grid_latitude', lat_osgb36), ('grid_longitude', lon_osgb36)]

    ##############################################################
    # Find the locations closest to the sample point
    ##############################################################   
    # Find the indexes of the closest points to this sample location
    tree = spatial.KDTree(locations)
    closest_point_idxs = tree.query([(sample_point[0][1], sample_point[1][1])], k = n_closest_points)[1][0]
    
    ##############################################################
    # Format outputs
    ##############################################################     
    # If there is only one closest point index, then convert this to an array (so in same format as if there were more than 1) 
    if isinstance(closest_point_idxs, np.int64) :
        closest_point_idxs = np.array([closest_point_idxs])   
        
    # Return locations to uncorrected versions (only necessary for rotated pole coordinates)
    locations = list(itertools.product(lats, lons))    
    
    # Create list of the closest lats and lons
    closest_lats = []
    closest_lons =[]
    for i in closest_point_idxs:
        print(i)
        closest_lats.append(locations[i][0])
        closest_lons.append(locations[i][1])
    
    return closest_point_idxs, closest_lats, closest_lons


def plot_grid_highlight_cells (cube, input_crs, target_crs, sample_point, closest_point_idx = None, ):
    '''
    Description
    ----------
    Creates a plot which highlights the location of the grid cell(s) with a particular index - if no index is provided
    then a plot is created which shows the layout of the grid covering it.
    This is done by creating a test data set of the same size as the real dataset - but which sets the values at all
    positions except at the chosen index to 0.   


    Parameters
    ----------
        cube: Iris Cube
            A cube containing 3 dimensions (time, latitude and longitude)
        input_crs : Dictionary
            A dictionary containing a coordinate reference system
        target_crs: Dictionary
            A dictionary containing a coordinate reference system
        sample_point: List
            A list of two tuples containing (1) grid_latitude and its value and (2) grid_longitude and it's value
        closest_point_idx: Array
            Contains the indexes of the grid cells identified as being closest to the sample point
            Defaults to None. In this case no grid cells will be highlighted 

    Returns
    -------
        None
        A plot is generated 
    
    '''

    # Set the geodataframes as global variables so they are available within the function
    global leeds_at_centre_gdf
    global leeds_gdf
    
    #############################################################################
    # Generate test data
    ##############################################################################
    # Create a test dataset with all points with value 0
    # Set value(s) at the indexes of the grid cells closest to the sample point as 1
    # And then plot data spatially, and see which grid cell(s) are highlighted.   
    test_data = np.full((cube[0].shape), 0, dtype=int)
    if closest_point_idx is not None:
      test_data_rs = test_data.reshape(-1)
      test_data_rs[closest_point_idx] = 1
      test_data = test_data_rs.reshape(test_data.shape)
    
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Find cornerpoint coordiantes
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    test_data = test_data[1:,1:]
        
    #############################################################################
    # Set up correct coordinate systems
    ##############################################################################
    # Convert Leeds GDF to Web Mercator
    # And the location of interest  
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs)
    leeds_gdf = leeds_gdf.to_crs(target_crs) 
    
    if 'RotatedGeog' in str(cube.coord_system()):
        print("Rotated pole")
        cs = cube.coord_system()
        lons_cornerpoints, lats_cornerpoints = iris.analysis.cartography.unrotate_pole(lons_cornerpoints, lats_cornerpoints, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
      
    # Convert cornerpoints to target_crs
    lons_cornerpoints, lats_cornerpoints = transform(input_crs, target_crs, lons_cornerpoints, lats_cornerpoints)
    lon_wm, lat_wm = transform({'init' :'epsg:4326'}, target_crs, sample_point[1][1], sample_point[0][1])
         
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    cmap = mpl.colors.ListedColormap(['royalblue'])

    fig, ax = plt.subplots(figsize=(20,10))
    extent = tilemapbase.extent_from_frame(leeds_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=1, alpha = 1, cmap = cmap, edgecolors = 'grey')
    #cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    #cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    #plot =ax.tick_params(labelsize='xx-large')
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot=ax.plot(lon_wm, lat_wm, color='yellow', marker='o', markersize =5)

  
def find_cornerpoint_coordinates(cube):
    '''
    Description
    ----------
        Using a cube of lat/Y/Northing, longs/X/Easting and associated values the function 
        creates new 2D lat, lon and data arrays in which the data values are associated
        with a point at the bottom left of each grid cell, rather than the middle.
        This is required as plt.pcolormesh assumes lat/long values refer to the bottom left coordinate

    Parameters
    ----------
        cube: Iris Cube
            A cube containing 3 dimensions (time, latitude and longitude)

    Returns
    -------
        lats_cornerpoints_2d : array
            A 2d array containing 
        lons_cornerpoints_2d : array
            Array containing
    
    '''
    # Find the coordinate names 
    # This is required as coordinate names are not constant between different cubes 
    coord_names = [coord.name() for coord in cube.coords()]
    print(coord_names)
    
    # Create variables storing lats/lons (or equivalent variables)
    lats = cube.coord(coord_names[1]).points
    lons = cube.coord(coord_names[2]).points

    # Create as 2D arrays
    lons_2d, lats_2d = np.meshgrid(lons, lats)
    
    # Find the distance between each lat/lon and the next lat/lon
    # Divide this by two to get the distance to the half way point
    lats_differences_half = np.diff(lats)/2
    lons_differences_half = np.diff(lons)/2
    
    # Create an array of lats/lons at the midpoints
    lats_cornerpoints_1d = lats[1:] - lats_differences_half
    lons_cornerpoints_1d = lons[1:] - lons_differences_half
    
    # Convert to 2D
    lons_cornerpoints_2d, lats_cornerpoints_2d = np.meshgrid(lons_cornerpoints_1d, lats_cornerpoints_1d)
    
    return lats_cornerpoints_2d, lons_cornerpoints_2d


def create_trimmed_cube(leeds_at_centre_gdf, string, target_crs):    
    '''
    Description
    ----------
       Loads in data and trims it to the extent of the geodataframe

    Parameters
    ----------
        leeds_at_centre_gdf: GeoDataFrame
            A geodataframe
        string: string
            A string giving the path to the files
        target_crs: Dictionary
            A dictionary containing a coordinate reference system

    Returns
    -------
        trimmed_cube: Iris cube
            sds
    
    '''
    
    
    ################################################################
    # 
    ################################################################  
    filenames=glob.glob('Outputs/CEH-GEAR' +string + 'CEH-GEAR-1hr_*')
    monthly_cubes_list = iris.load(filenames,'rainfall_amount')
    
    # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()      
                                   
    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    # Find coordinate names of lats/long or x/y
    coord_names = [coord.name() for coord in concat_cube.coords()]
    
    # Create lambda function for...
    minmax = lambda x: (np.min(x), np.max(x))              
    
    #global leeds_at_centre_gdf
    # Create GDF in correct CRS
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(target_crs) 
                                   
    # Find the bounding box of the region   
    bbox = leeds_at_centre_gdf.total_bounds                
    
    # Create 2d lats and lons from trimmed cube 
    coord_names = [coord.name() for coord in concat_cube.coords()]
      
    # Find the lats and lons of the cube in OSGB36   
    print("lats = ", coord_names[1])
    print("lons = ", coord_names[2])
    lats = concat_cube.coord(coord_names[1]).points
    lons = concat_cube.coord(coord_names[2]).points
    lons_2d, lats_2d = np.meshgrid(lons, lats)   
              
    # For regridded cube
    if string == '_regridded_2.2km/rg_':
      cs = concat_cube.coord_system()
      lons_2d, lats_2d = iris.analysis.cartography.unrotate_pole(lons_2d, lats_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
    
    # Find which are within the BBOX                       
    inregion = np.logical_and(np.logical_and(lons_2d > bbox[0], lons_2d < bbox[2]),
      np.logical_and(lats_2d > bbox[1],  lats_2d < bbox[3]))
    region_inds = np.where(inregion)                       
    imin, imax = minmax(region_inds[0])                    
    jmin, jmax = minmax(region_inds[1])                    
                                   
    # trim the cube                                        
    trimmed_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]
    
    return trimmed_cube

  
