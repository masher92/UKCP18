import numpy as np
import geopandas as gpd
import iris
from pyproj import Proj, transform
from shapely.geometry import Point, Polygon, MultiPolygon
import matplotlib.pyplot as plt
import tilemapbase

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"

def create_leeds_outline (required_proj):
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
    # Read in outline of Leeds wards  
    wards = gpd.read_file("datadir/SpatialData/england_cmwd_2011.shp")
    # Create column to merge on
    wards['City'] = 'Leeds'
    # Merge all wards into one outline
    leeds = wards.dissolve(by = 'City')

    # Convert Leeds outline geometry to WGS84
    leeds.crs = {'init' :'epsg:27700'}
    leeds_gdf = leeds.to_crs(required_proj)

    return leeds_gdf


def find_corner_coords (cube):
    '''
    Description
    ----------
        

    Parameters
    ----------


    Returns
    -------

    
    '''
    ##############################################################################
    ### Create a cube containing one timeslice 
    ##############################################################################
    # Get just one timeslice
    hour_uk_cube = cube[1,:,:]
    
    ##############################################################################
    # Get arrays of lats and longs of left corners in Web Mercator projection
    ##############################################################################
    coordinates_cornerpoints = find_cornerpoint_coordinates(hour_uk_cube)
    lats_cornerpoints= coordinates_cornerpoints[0]
    lons_cornerpoints= coordinates_cornerpoints[1]
    
    # Cut off edge data to match size of corner points arrays.
    # First row and column lost in process of finding bottom left corner points.
    trimmed_cube = cube[:,1:, 1:]
    
    ##############################################################################
    #### Get arrays of lats and longs of centre points in Web Mercator projection
    ##############################################################################
    # Get points in WGS84
    lats_centrepoints = trimmed_cube.coord('latitude').points
    lons_centrepoints = trimmed_cube.coord('longitude').points
    # Convert to WM
    lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)
    
    df = pd.DataFrame({"Lat_bottomleft" :lats_cornerpoints.reshape(-1),
                   "Lon_bottomleft" :lons_cornerpoints.reshape(-1),
                   "Lat_centre" :lats_centrepoints.reshape(-1),
                   "Lon_centre" :lons_centrepoints.reshape(-1)})
    
    return (df, trimmed_cube)


    ############################################
    for cube in monthly_cubes_list:
     for attr in ['creation_date', 'tracking_id', 'history']:
         if attr in cube.attributes:
             del cube.attributes[attr]
 
     # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    #
    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    cube = concat_cube


def trim_to_gdf (cube, gdf):
    '''
    Description
    ----------
        Masks the data in a cube so that cells outwith a provided geometry have no value
        
    Parameters
    ----------
        cube : Iris cube with 3 dimensions: Time, lat, long
        gdf: A geodataframe corresponding to the region by which to mask the cube
          
    Returns
    -------
        cube: Iris cube with 3 dimensions with the data masked to the provided region
    '''
    
    # Create a Shapely Polygon from the geodataframe
    #geometry_poly = Polygon(gdf['geometry'].iloc[0])
    
    # Create 1d array of lat and lons and convert to Web Mercator
    lons = cube.coord('longitude').points.reshape(-1)
    lats = cube.coord('latitude').points.reshape(-1)
    lons,lats= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons,lats)

    # Get one timeslice of data
    one_ts = cube[0,:,:]
    # Check spatial extent
    #qplt.contourf(one_ts)       
    #plt.gca().coastlines()    
    
    # Find which cells are within the geometry
    # This returns a masked array i.e. only cells that are within the geometry
    # have a value
    mask_2d = GridCells_within_geometry(lats,lons, gdf, one_ts)

    # Convert this into a 3D mask
    # i.e the mask is repeated for each data timeslice
    mask_3d = np.repeat(mask_2d[np.newaxis,:, :], cube.shape[0], axis=0)
    
    # Mask the cubes data across all timeslices
    #masked_data = np.ma.masked_array(data, mask_3d)
    masked_data = np.ma.masked_array(cube.data, np.logical_not(mask_3d))
    
    # Set this as the cubes data
    #cube.data = masked_data
           
    return masked_data


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
    # Convert the geometry to a shapely geometry
    
    if geometry_gdf.geom_type[0] == 'MultiPolygon':
        geometry_poly = MultiPolygon(geometry_gdf['geometry'].iloc[0])
    elif geometry_gdf.geom_type[0] == 'Polygon':
        geometry_poly = Polygon(geometry_gdf['geometry'].iloc[0])
        
    within_geometry = []
    for lon, lat in zip(lons, lats):
        this_point = Point(lon, lat)
        res = this_point.within(geometry_poly)
        #res = leeds_poly.contains(this_point)
        within_geometry.append(res)
    # Convert to array
    within_geometry = np.array(within_geometry)
    # Convert from a long array into one of the shape of the data
    within_geometry = np.array(within_geometry).reshape(data[:,:].shape)
    # Convert to 0s and 1s
    within_geometry = within_geometry.astype(int)
    # Mask out values of 0
    within_geometry = np.ma.masked_array(within_geometry, within_geometry < 1)
    
    return within_geometry


#mask_2d = GridCells_within_geometry(lats,lons, gdf, one_ts)



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
    

def plot_cube_within_region (cube, region_outline_gdf):
    '''
    Description
    ----------
    In the netCDF cube the coordinates refer to the central point in the grid cell.
    Plotting with pcolormesh assumes the coordiante is the bottom left corner of the
    grid cell.
    Thus, some conversion is needed.

    Parameters
    ----------
        cube: Iris Cube
            A cube containing just lats, longs (one timeslice)
    Returns
    -------
        lats_wm_midpoints_2d : array
        
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
    

    
    
    
    
    
    