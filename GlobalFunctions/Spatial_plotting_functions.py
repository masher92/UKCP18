import numpy as np
import geopandas as gpd
import iris
from pyproj import Proj, transform
from shapely.geometry import Point, Polygon, MultiPolygon
import matplotlib.pyplot as plt
import tilemapbase
import time 
#import bottleneck
import pandas as pd
from numba import jit
import re
import matplotlib

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"


def create_precip_cmap():
    tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
    "#72190E","#882E72","#000000"]                                      
    precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
    # Set the colour for any values which are outside the range designated in lvels
    precip_colormap.set_under(color="white")
    precip_colormap.set_over(color="white")
    return precip_colormap


@jit
def load_data(cube):
    '''
    Description
    ----------
        Loads the data from a cube so it is no longer lazy.
        Placed inside function to benefit from speed improvements of @jit.
    Parameters
    ----------
        rain_data: cube
            An iris cube
    Returns
    -------
        rain_data: array
            A 3D array containing for each location containing values for multiple time slices 
    '''
    
    # Load the data
    rain_data = cube.data
    return rain_data

@jit
def wet_hour_stats(rain_data, statistic_name):
    '''
    Description
    ----------
        Takes the data from a cube and loops through each cell in the array of data
        and extracts just the wet hours (>0.1mm/hr). Using these wet hours it calculates
        a single value related to the specified 'statistic_name' parameter. This value is the
        saved at that location. A 2d array of data values is returned containing one value
        for each cell corresponding to the input statistic_name.
    Parameters
    ----------
        rain_data: array
            3D array containing the data from an iris cube, with multiple timelices for each location
        statistic_name: String
            A string specifying the statistic to be calculated
    Returns
    -------
        stats_array: array
            A 2D array containing for each location the value corresponing to the statistic
            given as an input to the function      
    '''
    
    # Define length of lons
    imax=np.shape(rain_data)[1] 
    # Define length of lats
    jmax=np.shape(rain_data)[2]
    
    # Create empty array to populate with stats value
    stats_array =np.zeros((imax,jmax))

    # Loop through each of the cells, and find the value of the specified statistic
    # in that cell. Save this value to the correct position in the array
    print("Entering loop")
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            # Keep only values above 0.1 (wet hours)
            wet_hours = local_raindata[local_raindata>0.1]         
            
            # Calculate statistics on just the wet hours
            # If the statistic name is a percentile then need to first extract the 
            # percentile number from the string 'statistic_name'
            if statistic_name == 'jja_mean_wh':
               statistic_value  = np.mean(wet_hours)
            elif statistic_name == 'jja_max_wh':
              statistic_value  = np.max(wet_hours)
            elif statistic_name == 'wet_prop':
               statistic_value  = (len(wet_hours)/len(local_raindata)) *100
            else:
              percentile_str =re.findall(r'\d+', statistic_name)
              if len(percentile_str) == 1:
                  percentile_no = float(percentile_str[0])
              elif len(percentile_str) ==2:
                 percentile_no = float(percentile_str[0] + '.' + percentile_str[1])
              statistic_value =  np.percentile(wet_hours, percentile_no)
            
            # Store at correct location in array
            stats_array[i,j] = statistic_value

    return  stats_array
  

def find_cornerpoint_coordinates_obs (cube):
    '''
    Description
    ----------
        Using a cube of lat, longs in rotated pole and associated values the function
        creates new 2D lat, lon and data arrays in which the data values are associated
        with a point at the bottom left of each grid cell, rather than the middle.
    Parameters
    ----------
        cube: Iris Cube
            A cube containing only latitude and longitude dimensions
            In rotated pole coordinates so that...are constant..
    Returns
    -------
        lats_wm_midpoints_2d : array
            A 2d array of the mid point latitudes
        lons_wm_midpoints_2d : array
            A 2d array of the mid point longitudes
        
    '''
    
    # Extract lats and longs in rotated pol as a 2D array
    lats_1d = cube.coord('projection_y_coordinate').points
    lons_1d = cube.coord('projection_x_coordinate').points
    
    # Find the distance between each lat/lon and the next lat/lon
    # Divide this by two to get the distance to the half way point
    lats_differences_half = np.diff(lats_1d)/2
    lons_differences_half = np.diff(lons_1d)/2
    
    # Create an array of lats/lons at the midpoints
    lats_midpoints_1d = lats_1d[1:] - lats_differences_half
    lons_midpoints_1d = lons_1d[1:] - lons_differences_half
    
    # Convert to 2D
    lons_midpoints_2d, lats_midpoints_2d = np.meshgrid(lons_midpoints_1d, lats_midpoints_1d)

    # Convert to web mercator
    lons_wm_midpoints_2d, lats_wm_midpoints_2d = transform(Proj(init='epsg:27700'),Proj(init='epsg:3785'),
                                                           lons_midpoints_2d,lats_midpoints_2d)
    
    # Convert to 1d     
    #lons_wm_midpoints_1d = lons_wm_midpoints_2d.reshape(-1)
   # lats_wm_midpoints_1d = lats_wm_midpoints_2d.reshape(-1)
    
    # Remove same parts of data
    #data = cube.data
    #data_midpoints = data[1:,1:]
    
    return (lats_wm_midpoints_2d, lons_wm_midpoints_2d)

  

def find_cornerpoint_coordinates (cube):
    '''
    Description
    ----------
        Using a cube of lat, longs in rotated pole and associated values the function
        creates new 2D lat, lon and data arrays in which the data values are associated
        with a point at the bottom left of each grid cell, rather than the middle.
    Parameters
    ----------
        cube: Iris Cube
            A cube containing only latitude and longitude dimensions
            In rotated pole coordinates so that...are constant..
    Returns
    -------
        lats_wm_midpoints_2d : array
            A 2d array of the mid point latitudes
        lons_wm_midpoints_2d : array
            A 2d array of the mid point longitudes
        
    '''
    
    # Extract lats and longs in rotated pol as a 2D array
    lats_rp_1d = cube.coord('grid_latitude').points
    lons_rp_1d = cube.coord('grid_longitude').points
    
    # Find the distance between each lat/lon and the next lat/lon
    # Divide this by two to get the distance to the half way point
    lats_rp_differences_half = np.diff(lats_rp_1d)/2
    lons_rp_differences_half = np.diff(lons_rp_1d)/2
    
    # Create an array of lats/lons at the midpoints
    lats_rp_midpoints_1d = lats_rp_1d[1:] - lats_rp_differences_half
    lons_rp_midpoints_1d = lons_rp_1d[1:] - lons_rp_differences_half
    
    # Convert to 2D
    lons_rp_midpoints_2d, lats_rp_midpoints_2d = np.meshgrid(lons_rp_midpoints_1d, lats_rp_midpoints_1d)
    
    # Convert to wgs84
    cs = cube.coord_system()
    lons_wgs84_midpoints_2d, lats_wgs84_midpoints_2d = iris.analysis.cartography.unrotate_pole(lons_rp_midpoints_2d, lats_rp_midpoints_2d, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
    # Convert to web mercator
    lons_wm_midpoints_2d, lats_wm_midpoints_2d = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_wgs84_midpoints_2d,lats_wgs84_midpoints_2d)
    
    # Convert to 1d     
    #lons_wm_midpoints_1d = lons_wm_midpoints_2d.reshape(-1)
   # lats_wm_midpoints_1d = lats_wm_midpoints_2d.reshape(-1)
    
    # Remove same parts of data
    #data = cube.data
    #data_midpoints = data[1:,1:]
    
    return (lats_wm_midpoints_2d, lons_wm_midpoints_2d)
 
def GridCells_within_geometry(lats, lons, geometry_gdf, data):
    '''
    Description
    ----------
        Check whether each lat, long pair from provided arrays is found within
        the geometry.
        Create an array with points outwith Leeds masked

    Parameters
    ----------
        lats_1d_arr : array
            1D array of latitudes
        lons_1d_arr : array
            1D array of longitudes
    Returns
    -------
    within_geometry : masked array
        Array with values of 0 for points outwith Leeds
        and values of 1 for those within Leeds.
        Points outwith Leeds are masked (True)

    '''
    # Reset index, either the number in [] to refer to geometry does not match 
    geometry_gdf = geometry_gdf.reset_index()
    
    # Convert the geometry to a shapely geometry
    if geometry_gdf.geom_type[0] == 'MultiPolygon':
        geometry_poly = MultiPolygon(geometry_gdf['geometry'].iloc[0])
    elif geometry_gdf.geom_type[0] == 'Polygon':
        geometry_poly = Polygon(geometry_gdf['geometry'].iloc[0])

    i= 0 
    within_geometry = []
    
    for lon, lat in zip(lons, lats):
        this_point = Point(lon, lat)
        res = this_point.within(geometry_poly)
        print(i)
        within_geometry.append(res)
        i = i+1
        
    # # Convert to array
    # within_geometry = np.array(within_geometry)
    # # Convert from a long array into one of the shape of the data
    # within_geometry = np.array(within_geometry).reshape(data[:,:].shape)
    # # Convert to 0s and 1s
    # within_geometry = within_geometry.astype(int)
    # # Mask out values of 0
    # #within_geometry = np.ma.masked_array(within_geometry, within_geometry < 1)
    
    return within_geometry

 
def trim_to_bbox_of_region_obs (obs_cube, gdf):
    '''
    Description
    ----------
        Trims a cube to the bounding box of a region, supplied as a geodataframe.
        This is much faster than looking for each point within a geometry as in
        GridCellsWithin_geometry
        Tests whether the central coordinate is within the bbox

    Parameters
    ----------
        cube : iris cube
            1D array of latitudes
        gdf: GeoDataFrame
            GeoDataFrame containing a geometry by which to cut the cubes spatial extent
    Returns
    -------
        trimmed_cube : iris cube
            Cube with spatial extent equivalent to the bounding box of the supplied geodataframe

    '''
     # CReate function to find   
    minmax = lambda x: (np.min(x), np.max(x))
    
    #### Find the lats and lons of the cube in BNG
    lats_1d = obs_cube.coord('projection_y_coordinate').points
    lons_1d = obs_cube.coord('projection_x_coordinate').points
    
    # Convert to 2D
    lons_2d, lats_2d = np.meshgrid(lons_1d, lats_1d)
    
    # Convert to WGS84
    lons_2d ,lats_2d= transform(Proj(init='epsg:27700'),
                                      Proj(init='epsg:4326'),
                                      lons_2d,lats_2d)
    
    # Convert the regional gdf to WGS84 (same as cube)
    gdf = gdf.to_crs({'init' :'epsg:4326'}) 
    # Find the bounding box of the region
    bbox = gdf.total_bounds
    
    inregion = np.logical_and(np.logical_and(lons_2d > bbox[0],
                                             lons_2d < bbox[2]),
                              np.logical_and(lats_2d > bbox[1],
                                             lats_2d < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    obs_cube = obs_cube[..., imin:imax+1, jmin:jmax+1]
    
    return obs_cube

def trim_to_bbox_of_region_regriddedobs (cube, gdf):
    '''
    Description
    ----------
        Trims a cube to the bounding box of a region, supplied as a geodataframe.
        This is much faster than looking for each point within a geometry as in
        GridCellsWithin_geometry
        Tests whether the central coordinate is within the bbox

    Parameters
    ----------
        cube : iris cube
            1D array of latitudes
        gdf: GeoDataFrame
            GeoDataFrame containing a geometry by which to cut the cubes spatial extent
    Returns
    -------
        trimmed_cube : iris cube
            Cube with spatial extent equivalent to the bounding box of the supplied geodataframe

    '''
    minmax = lambda x: (np.min(x), np.max(x))
    # Convert the regional gdf to WGS84 (same as cube)
    gdf = gdf.to_crs({'init' :'epsg:4326'}) 
    
    # Find the bounding box of the region
    bbox = gdf.total_bounds
    
    #### Find the lats and lons of the cube in WGS84
    # Define lats and lons in rotated pole
    lats_rp_1d = cube.coord('grid_latitude').points
    lons_rp_1d = cube.coord('grid_longitude').points
    
    # Convert to 2D
    lons_rp_2d, lats_rp_2d = np.meshgrid(lons_rp_1d, lats_rp_1d)
    
    # Convert to WGS84 (unrotate)
    cs = cube.coord_system()
    #cs = cube_model.coord('grid_latitude').coord_system
    lons_wgs84_2d, lats_wgs84_2d = iris.analysis.cartography.unrotate_pole(lons_rp_2d, lats_rp_2d, 
              cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
    
    # Create array specifying whether each grid cell is within the bounding box
    inregion = np.logical_and(np.logical_and(lons_wgs84_2d > bbox[0],
                                             lons_wgs84_2d < bbox[2]),
                              np.logical_and(lats_wgs84_2d > bbox[1],
                                         lats_wgs84_2d < bbox[3]))
    # Find index of lat and long positions which are within the bounding box
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    # Trim the cube to just contain these positions
    trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1]
    
    return trimmed_cube

   
def trim_to_bbox_of_region (cube, gdf):
    '''
    Description
    ----------
        Trims a cube to the bounding box of a region, supplied as a geodataframe.
        This is much faster than looking for each point within a geometry as in
        GridCellsWithin_geometry
        Tests whether the central coordinate is within the bbox

    Parameters
    ----------
        cube : iris cube
            1D array of latitudes
        gdf: GeoDataFrame
            GeoDataFrame containing a geometry by which to cut the cubes spatial extent
    Returns
    -------
        trimmed_cube : iris cube
            Cube with spatial extent equivalent to the bounding box of the supplied geodataframe

    '''
    # CReate function to find
    minmax = lambda x: (np.min(x), np.max(x))
    
    # Convert the regional gdf to WGS84 (same as cube)
    gdf = gdf.to_crs({'init' :'epsg:4326'}) 
    
    # Find the bounding box of the region
    bbox = gdf.total_bounds
    
    # Find the lats and lons of the cube in WGS84
    lons = cube.coord('longitude').points
    lats = cube.coord('latitude').points

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1]
    
    return trimmed_cube

def trim_to_bbox_of_uk (cube):
    '''
    Description
    ----------


    Parameters
    ----------
        cube : iris cube
            1D array of latitudes
    Returns
    -------
        trimmed_cube : iris cube
            Cube with spatial extent equivalent to the bounding box of the UK

    '''
    # CReate function to find
    minmax = lambda x: (np.min(x), np.max(x))
       
    # Define the bounding box of the UK
    bbox = np.array([-10.1500, 49.8963187 ,  1.7632199, 58.8458677])
    
    # Find the lats and lons of the cube in WGS84
    lons = cube.coord('longitude').points
    lats = cube.coord('latitude').points

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1] 
    
    return trimmed_cube




def mask_by_region (cube, gdf):
    '''
    Description
    ----------
        Masks the data in a cube so that cells outwith a provided geometry have NA value
        
    Parameters
    ----------
        cube : Iris cube with 3 dimensions: Time, lat, long
        gdf: A geodataframe corresponding to the region by which to mask the cube
          
    Returns
    -------

    '''
       
    # Create 1d array of lat and lons and convert to Web Mercator
    lons = cube.coord('longitude').points.reshape(-1)
    lats = cube.coord('latitude').points.reshape(-1)
    lons,lats= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons,lats)

    #np.where(lons == 117524.7356318977)

    if cube.ndim == 3:
        # Get one timeslice of data
        one_ts = cube[0,:,:]
    else:
        one_ts = cube
    # Check spatial extent
    #qplt.contourf(one_ts)       
    #plt.gca().coastlines()    
    
    # Find which cells are within the geometry
    # This returns a masked array i.e. only cells that are within the geometry
    # have a value
    seconds = time.time()
    mask_2d = GridCells_within_geometry(lats,lons, gdf, one_ts)
    print("Seconds to run =", time.time() - seconds)	
    
    # Convert this into a 3D mask
    # i.e the mask is repeated for each data timeslice
    #seconds = time.time()
    #mask_3d = np.repeat(mask_2d[np.newaxis,:, :], cube.shape[0], axis=0)
    #print("Seconds to run =", time.time() - seconds)	
    
    # Mask the cubes data across all timeslices
    #masked_data = np.ma.masked_array(data, mask_3d)
    #masked_data = np.ma.masked_array(cube.data, np.logical_not(mask_3d))
    
    # Set this as the cubes data
    #masked_cube = cube.copy()
    #masked_cube.data = masked_data
           
    return mask_2d

def plot_cube_within_region (cube, region_outline_gdf):
    '''
    Description
    ----------
        Plots a cube within a geometry boundary.
        Maps the cube data which is provided as an array in which values are for the
        centre point of each grid cell, so that values are associated with the
        bottom left corner, as this is how the plotting function works.

    Parameters
    ----------
        cube: Iris Cube
            A cube containing just lats, longs (one timeslice)
        region_outline_gdf: GeoDataFrame
            A geodataframe of an area of interest
    Returns
    -------
        A plot
        
    '''    
    
    ##############################################################################
    # Get arrays of lats and longs of left corners in Web Mercator projection
    ##############################################################################
    coordinates_cornerpoints = find_cornerpoint_coordinates(cube)
    lats_cornerpoints= coordinates_cornerpoints[0]
    lons_cornerpoints= coordinates_cornerpoints[1]
    
    ##############################################################################
    #### Get arrays of lats and longs of centre points in Web Mercator projection
    ##############################################################################
    # Cut off edge data to match size of corner points arrays.
    # First row and column lost in process of finding bottom left corner points.
    # I think can do this so it works for either like [..., 1:,1:]
    #cube = cube[..., 1:,1:]
    if cube.ndim ==2:
      cube = cube[1:, 1:]  
    elif cube.ndim ==3:
        cube = cube[0, 1:, 1:]
    
    # Get points in WGS84
    lats_centrepoints = cube.coord('latitude').points
    lons_centrepoints = cube.coord('longitude').points
    # Convert to WM
    lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)
        
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    fig, ax = plt.subplots(figsize=(20,20))
    extent = tilemapbase.extent_from_frame(region_outline_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    plot =region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cube.data,
                  linewidths=3, alpha = 1, cmap = 'GnBu')
    cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot =ax.tick_params(labelsize='xx-large')
    plot =region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
  
    
def n_largest_yearly_values_method2 (seasonal_cube, mask_data, mask = None):
    '''
    Description
    ----------
        Creates a shapely geometry of the outline of Leeds in the projection specified

    Parameters
    ----------
        required_proj : Dict
            Python dictionary with a key init that has a value epsg:4326. 
            This is a very typical way how CRS is stored in GeoDataFrames 
            e.g. {'init' :'epsg:3785'} for Web Mercator
            or   {'init' :'epsg:4326'} for WGS84

    Returns
    -------
        leeds_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of Leeds
    
    '''
    #############################################
    # Define years over which to search for data
    #############################################
    season_years = seasonal_cube.coord('season_year').points
    season_years = np.unique(season_years)    
    season_years = season_years.tolist()
    
    #############################################
    # Set-up variables required for for-loop
    #############################################
    # Create a counter (which is increased by one with each cycle of for loop)
    # to check whether the correct number of locations are being processed
    counter = 0
    # Lists to store results
    locations = []
    lats = []   
    lons = []      
    
    #############################################
    # Load in the cube's data
    # From testing, doing this increases the speed of processing compared to the
    # same code, but with this line missing
    #############################################
    seconds = time.time()
    seasonal_cube_data = seasonal_cube.data
    print("loaded whole cube's data in ", time.time() - seconds)
    
    #############################################
    # Find percentile values for each cell in the cube
    #### Testing indicates this method is slower, than using np.percentile for each 
    # cell individually
    #############################################
    # yearly_stats_percentiles = seasonal_cube.aggregated_by(['season_year'], iris.analysis.PERCENTILE, percent=[98.7])
        
    #############################################
    # Cycle through each lat, lon combination and create a cube containing just
    # the timeseries for that location
    # For each:
    #     Store the lat and lon in the appropriate list
    #     For each year in the timeseries:
    #       Extract all hourly accumulations in that year and find all values
    #       larger than the 98.7th percentile (which was calculated to give ten values)
    #       Store the results in a dictionary, with the name of year_n (n between 1 and N)
    #     Convert this dictionary into a dataframe and add to the list
    #############################################
    # True_counter counts the numbr of cells which have been processed i.e. not
    # masked out 
    true_counter = 0 
    for lat_idx in range(0,seasonal_cube.shape[1]):
            for lon_idx in range(0, seasonal_cube.shape[2]):
                print("Cell number: ", counter)
                counter = counter+1
                # Trim cube to contain all timeslices for that one location
                one_cell = seasonal_cube[:,lat_idx,lon_idx]
              
                #############################################
                # Block if using the mask
                #############################################
                if mask_data == True:
                    print("Processing only cells within mask")
                    
                    # Round mask lat/lon to 8 decimal places so it matches the cube
                    mask = mask.round({'lat': 8, 'lon': 8})
                                        
                    # Only perform following code on cells where lat/long value 
                    # is contained in the mask
                    if mask['lat'].isin([round(one_cell.coord('latitude').points[0],8)]).any() == True:
                        true_counter = true_counter +1                        
                        # Store the coordinates of the point, and print them for checking
                        lats.append(one_cell.coord('latitude').points[0])
                        #print(one_cell.coord('latitude').points[0])
                        lons.append(one_cell.coord('longitude').points[0])
                        #print(one_cell.coord('longitude').points[0])
            
                        # Create a dictionary to store the results for each of the N largest
                        # values in each year
                        n_largest_values_dict = {}
                        for year in season_years:
                            print(' Year: ', year)
                            # Extract just timeslices in that year
                            one_cell_one_year = one_cell.extract(iris.Constraint(season_year = year))
                            data = one_cell_one_year.data
                            data = np.sort(data)
                            
                            #### Method 1 - for finding percentiles
                            value = np.percentile(data, 99.1, interpolation = 'linear') # return 50th percentile, e.g median.
                            
                            ### Method 2 - for finding percentiles - slower
                            # yearly_stats_percentiles_one_year = yearly_stats_percentiles.extract(iris.Constraint(season_year = year))
                            #value = yearly_stats_percentiles_one_year[lat_idx, lon_idx].data
                            #top_ten = data>value 
                            
                            # Find top ten values, i.e. those that are greater than the
                            # 99.1st percentile
                            top_ten = data[data>value]
                            
                            # Print check length
                            print("number of values: ", len(top_ten))
                            
                            n_largest_value_counter = 1
                            for n in range(0,10):
                                n_largest_values_dict[str(year) + '_' + str(n_largest_value_counter)] =  top_ten[n]
                                n_largest_value_counter = n_largest_value_counter +1 
                            
                        # Convert the dictionary of N_largest values into a dataframe
                        n_largest_values_df = pd.DataFrame(n_largest_values_dict, index=[0])
                    
                        # Add to the list containing n_largest_values_df's for each location
                        locations.append(n_largest_values_df)
                
                #############################################
                # Block if not using the mask
                #############################################
                elif mask_data == False:
                    print("Processing all cells, no mask")
                    true_counter = true_counter +1 
                                           
                    # Store the coordinates of the point, and print them for checking
                    lats.append(one_cell.coord('latitude').points[0])
                    #print(one_cell.coord('latitude').points[0])
                    lons.append(one_cell.coord('longitude').points[0])
                    #print(one_cell.coord('longitude').points[0])
            
                    # Create a dictionary to store the results for each of the N largest
                    # values in each year
                    n_largest_values_dict = {}
                    for year in season_years:
                        print(' Year: ', year)
                        # Extract just timeslices in that year
                        one_cell_one_year = one_cell.extract(iris.Constraint(season_year = year))
                        data = one_cell_one_year.data
                        data = np.sort(data)
                        
                        #### Method 1
                        value = np.percentile(data, 98.7, interpolation = 'linear') # return 50th percentile, e.g median.
                        
                        ### Method 2
                        # yearly_stats_percentiles_one_year = yearly_stats_percentiles.extract(iris.Constraint(season_year = year))
                        #value = yearly_stats_percentiles_one_year[lat_idx, lon_idx].data
                        #top_ten = data>value 
                        
                        top_ten = data[data>value]
                        
                        # Print check length
                        print("number of values: ", len(top_ten))
                        
                        n_largest_value_counter = 1
                        for n in range(0,10):
                            #print(n)
                            n_largest_values_dict[str(year) + '_' + str(n_largest_value_counter)] =  top_ten[n]
                            n_largest_value_counter = n_largest_value_counter +1 
                        
                    # Convert the dictionary of N_largest values into a dataframe
                    n_largest_values_df = pd.DataFrame(n_largest_values_dict, index=[0])
                
                    # Add to the list containing n_largest_values_df's for each location
                    locations.append(n_largest_values_df)
    
    # Join the list of dataframes into one dataframe
    # Each row is a location
    total = pd.concat(locations, axis=0)
    
    # Join with lats and lons
    total['lat'], total['lon'] = [lats, lons]
    print(true_counter)
    
    return total
    
    
def n_largest_yearly_values (seasonal_cube,  mask, number_of_annual_values = 10):
    '''
    # Create a dataframe containing the N largest values for each location 
    # in each year   
    '''

    #############################################
    # Define years over which to search for data
    #############################################
    season_years = seasonal_cube.coord('season_year').points
    season_years = np.unique(season_years)    
    season_years = season_years.tolist()
    
    #############################################
    # Set-up variables required for for-loop
    #############################################
    # Create a counter (which is increased by one with each cycle of for loop)
    # to check whether the correct number of locations are being processed
    counter = 0
    # Lists to store results
    locations = []
    lats = []   
    lons = []      
    
    #############################################
    # Cycle through each lat, lon combination and create a cube containing just
    # the timeseries for that location
    # For each:
    #     Store the lat and lon in the appropriate list
    #     For each year in the timeseries:
    #       Extract all hourly accumulations in that year and find the N largest
    #       Store the results in a dictionary, with the name of year_n (n between 1 and N)
    #     Convert this dictionary into a dataframe and add to the list
                
    #############################################
    
    seconds = time.time()
    seasonal_cube_data = seasonal_cube.data
    print("loaded whole cube's data in ", time.time() - seconds)
    
    true_counter = 0 
    for lat_idx in range(0,seasonal_cube.shape[1]):
        for lon_idx in range(0, seasonal_cube.shape[2]):
            print("Cell number: ", counter)
            #print('Indices: ', lat_idx, ",", lon_idx)
            counter = counter+1
            
            # Trim cube to contain all timeslices for that one location
            one_cell = seasonal_cube[:,lat_idx,lon_idx]
            #one_cell_data = one_cell.data
            #one_cell_data = one_cell.core_data
            mask = mask.round({'lat': 8, 'lon': 8})
            
            #seconds = time.time()
            #one_cell_data = one_cell.data
            #print("loaded one cell's data in ", time.time() - seconds)
            
            #if mask['lat'].isin([round(one_cell.coord('latitude').points[0],8)]).any() == True:
            if 1> 0: 
                true_counter = true_counter +1 
                #print(mask['lat'].isin([round(one_cell.coord('latitude').points[0],8)]).any())
                                       
                # Store the coordinates of the point, and print them for checking
                lats.append(one_cell.coord('latitude').points[0])
               # print(one_cell.coord('latitude').points[0])
                lons.append(one_cell.coord('longitude').points[0])
                #print(one_cell.coord('longitude').points[0])
        
                # Create a dictionary to store the results for each of the N largest
                # values in each year
                n_largest_values_dict = {}
                for year in season_years:
                    print(' Year: ', year)
                    # Extract just timeslices in that year
                    #print("Extracting one year-s data")
                    one_cell_one_year = one_cell.extract(iris.Constraint(season_year = year))
                    #print("Extracted one year-s data")
                    
                    # ############## Wrong
                    # seconds = time.time()
                    # # Find indices of top 10 precipitation values
                    # ind = np.argpartition(one_cell_one_year.data, number_of_annual_values)[-number_of_annual_values:]
                    # values = one_cell_one_year.data[ind]
                    # print("time taken to find indices - argpartition: ", time.time() - seconds)
                    # print(values)
                    
                    #print("Finding indices")
                    # seconds = time.time()
                    # values= one_cell_one_year.data[np.argpartition(one_cell_one_year.data, -10)[-10:]]
                    # print("time taken to find indices: ", time.time() - seconds)
                    #print(values)
                    
                    # seconds = time.time()
                    # ind2 = np.sort(one_cell_one_year.data)[-10:]
                    # print("time taken to find indices: ", time.time() - seconds)
                    # print(ind2)
                    
                    seconds = time.time()
                    values = -bottleneck.partition(-one_cell_one_year.data, 10)[:10]
                    print("time taken to find indices: ", time.time() - seconds)
                    
                    ## Store values in dictionary with key stating the year and a
                    ## number between one and ten
                    # Set up counter used to create the key
                    n_largest_value_counter = 1
                    for n in range(0,10):
                        n_largest_values_dict[str(year) + '_' + str(n_largest_value_counter)] =  values[n]
                        n_largest_value_counter = n_largest_value_counter +1 
                        
                # Convert the dictionary of N_largest values into a dataframe
                n_largest_values_df = pd.DataFrame(n_largest_values_dict, index=[0])
                        
                # Add to the list containing n_largest_values_df's for each location
                locations.append(n_largest_values_df)
    
    # Join the list of dataframes into one dataframe
    # Each row is a location
    total = pd.concat(locations, axis=0)
    
    # Join with lats and lons
    total['lat'], total['lon'] = [lats, lons]
    print(true_counter)    
    return total

    
# def trim_to_gdf (cube, gdf):
#     '''
#     Description
#     ----------
#         Masks the data in a cube so that cells outwith a provided geometry have no value
        
#     Parameters
#     ----------
#         cube : Iris cube with 3 dimensions: Time, lat, long
#         gdf: A geodataframe corresponding to the region by which to mask the cube
          
#     Returns
#     -------
#         cube: Iris cube with 3 dimensions with the data masked to the provided region
#     '''
    
#     # Create a Shapely Polygon from the geodataframe
#     #geometry_poly = Polygon(gdf['geometry'].iloc[0])
    
#     # Create 1d array of lat and lons and convert to Web Mercator
#     lons = cube.coord('longitude').points.reshape(-1)
#     lats = cube.coord('latitude').points.reshape(-1)
#     lons,lats= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons,lats)

#     # Get one timeslice of data
#     one_ts = cube[0,:,:]
#     # Check spatial extent
#     #qplt.contourf(one_ts)       
#     #plt.gca().coastlines()    
    
#     # Find which cells are within the geometry
#     # This returns a masked array i.e. only cells that are within the geometry
#     # have a value
#     mask_2d = GridCells_within_geometry(lats,lons, gdf, one_ts)

#     # Convert this into a 3D mask
#     # i.e the mask is repeated for each data timeslice
#     mask_3d = np.repeat(mask_2d[np.newaxis,:, :], cube.shape[0], axis=0)
    
#     # Mask the cubes data across all timeslices
#     #masked_data = np.ma.masked_array(data, mask_3d)
#     masked_data = np.ma.masked_array(cube.data, np.logical_not(mask_3d))
    
#     # Set this as the cubes data
#     #cube.data = masked_data
           
#     return masked_data    
    
    
# def find_corner_coords (cube):
#     '''
#     Description
#     ----------
        

#     Parameters
#     ----------


#     Returns
#     -------

    
#     '''
#     ##############################################################################
#     ### Create a cube containing one timeslice 
#     ##############################################################################
#     # Get just one timeslice
#     hour_uk_cube = cube[1,:,:]
    
#     ##############################################################################
#     # Get arrays of lats and longs of left corners in Web Mercator projection
#     ##############################################################################
#     coordinates_cornerpoints = find_cornerpoint_coordinates(hour_uk_cube)
#     lats_cornerpoints= coordinates_cornerpoints[0]
#     lons_cornerpoints= coordinates_cornerpoints[1]
    
#     # Cut off edge data to match size of corner points arrays.
#     # First row and column lost in process of finding bottom left corner points.
#     trimmed_cube = cube[:,1:, 1:]
    
#     ##############################################################################
#     #### Get arrays of lats and longs of centre points in Web Mercator projection
#     ##############################################################################
#     # Get points in WGS84
#     lats_centrepoints = trimmed_cube.coord('latitude').points
#     lons_centrepoints = trimmed_cube.coord('longitude').points
#     # Convert to WM
#     lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)
    
#     df = pd.DataFrame({"Lat_bottomleft" :lats_cornerpoints.reshape(-1),
#                    "Lon_bottomleft" :lons_cornerpoints.reshape(-1),
#                    "Lat_centre" :lats_centrepoints.reshape(-1),
#                    "Lon_centre" :lons_centrepoints.reshape(-1)})
    
#     return (df, trimmed_cube)


#     ############################################
#     for cube in monthly_cubes_list:
#      for attr in ['creation_date', 'tracking_id', 'history']:
#          if attr in cube.attributes:
#              del cube.attributes[attr]
 
#      # Concatenate the cubes into one
#     concat_cube = monthly_cubes_list.concatenate_cube()
#     #
#     # Remove ensemble member dimension
#     concat_cube = concat_cube[0,:,:,:]
#     cube = concat_cube
    
# def GridCells_within_geometry(df, geometry_gdf, data):
#     '''
#     Description
#     ----------
#         Check whether each lat, long pair from provided arrays is found within
#         the geometry.
#         Create an array with points outwith Leeds masked

#     Parameters
#     ----------
#         lats_1d_arr : array
#             1D array of latitudes
#         lons_1d_arr : array
#             1D array of longitudes
#     Returns
#     -------
#     within_geometry : masked array
#         Array with values of 0 for points outwith Leeds
#         and values of 1 for those within Leeds.
#         Points outwith Leeds are masked (True)

#     '''
#     # Convert the geometry to a shapely geometry
#     geometry_poly = Polygon(geometry_gdf['geometry'].iloc[0])
 
#     within_geometry = []
#     for lon, lat in zip(df['Lon_centre'], df['Lat_centre']):
#         this_point = Point(lon, lat)
#         res = this_point.within(geometry_poly)
#         #res = leeds_poly.contains(this_point)
#         within_geometry.append(res)
#     # Convert to array
#     within_geometry = np.array(within_geometry)
#     # Convert from a long array into one of the shape of the data
#     within_geometry = np.array(within_geometry).reshape(605,483)
#     # Convert to 0s and 1s
#     within_geometry = within_geometry.astype(int)
#     # Mask out values of 0
#     within_geometry = np.ma.masked_array(within_geometry, within_geometry < 1)
    
#     return within_geometry
   
    
# def get1D_lats (cube):
    
#     # Extract lats and longs in WGS84 as a 2D array
#     lats = hour_uk_cube.coord('latitude').points
#     lons = hour_uk_cube.coord('longitude').points
    
#     # Reshape to 1D for easier iteration.
#     lons_1d = lons.reshape(-1)
#     lats_1d = lats.reshape(-1)
       
#     ## Option 2 - using proj reprojections
#     inProj = Proj(init='epsg:4326')
#     outProj = Proj(init='epsg:3785')
#     lons_wm_1d,lats_wm_1d = transform(inProj,outProj,lons_1d,lats_1d)
    
#     ############
#     #test_df = pd.DataFrame({"lats": lats_wm_1d, 'lons': lons_wm_1d, 'data':data })
    
#     # Reshape them to the shape of the grid
#     lats_wm_2d = np.array(lats_wm_1d).reshape(606,484)
#     lons_wm_2d = np.array(lons_wm_1d).reshape(606,484)  

    
    
