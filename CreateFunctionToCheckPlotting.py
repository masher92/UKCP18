regional_cube = wy_cube

### Think this bit should happen outside the function 
means = regional_cube.collapsed('time', iris.analysis.MEAN)

cube = means
region_outline_gdf = northern_gdf
region_outline_gdf = wy_gdf


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
    cube = cube[1:, 1:]
    
    # Get points in WGS84
    lats_centrepoints = cube.coord('latitude').points
    lons_centrepoints = cube.coord('longitude').points
    # Convert to WM
    lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)
    
    #############################################################################
    # Find which grid cells are within the geometry being used e.g. Leeds, WY etc
    # This uses the central coordinate
    ##############################################################################
    # Find which cells are within the geometry
    cells_within_geometry = GridCells_within_geometry(lats_centrepoints.reshape(-1),lons_centrepoints.reshape(-1), region_outline_gdf, cube)
    # Set any cells not withn the geometry as NAN
    values_within_geometry = np.where(cells_within_geometry, cube.data, np.nan)  
    
    # This doesnt blank out those outside the boundaries
    #stats_array = cube.data
    
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
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, values_within_geometry,
                  linewidths=3, alpha = 1, cmap = 'GnBu')
    cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
    cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
    #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
    plot =ax.tick_params(labelsize='xx-large')
    plot =region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
    
        
    
    
    
    
    
    
    