import iris.coord_categorisation
import iris
import numpy as np
import os
import geopandas as gpd
import sys
import matplotlib 
import numpy.ma as ma
import warnings
import iris.quickplot as qplt
import iris.plot as iplt
import cartopy.crs as ccrs
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

############################################
# Define variables and set up environment
#############################################
# Region over which to plot
region = 'UK' #['Northern', 'leeds-at-centre', 'UK']
# regridding method
regridding_method = 'LinearRegridding' #['NearestNeighbour', 'LinearRegridding']
# Stats to plot
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outline of the coast of the UK
uk_gdf = create_uk_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
uk_mask = np.load('Outputs/RegionalMasks/uk_mask_new.npy')  

##################################################################
# Trimming to region
##################################################################
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
    lats_rp_1d = cube.coord('grid_latitude').points
    lons_rp_1d = cube.coord('grid_longitude').points
    
    # Convert to 2D
    lons_rp_2d, lats_rp_2d = np.meshgrid(lons_rp_1d, lats_rp_1d)
    
    # Convert to WGS84
    cs = cube.coord_system()
    #cs = cube_model.coord('grid_latitude').coord_system
    lons, lats = iris.analysis.cartography.unrotate_pole(lons_rp_2d, lats_rp_2d, 
              cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1]
    
    return trimmed_cube

for stat in stats:
    print(stat)
    # Load in netcdf files containing the stats data over the whole UK
    stat_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/{}/{}.nc'.format(regridding_method, stat))[0] 
    stat_cube = stat_cube[0]    

    # Trim to smaller area
    if region == 'Northern':
         stat_cube = trim_to_bbox_of_region(stat_cube, northern_gdf)
    elif region == 'leeds-at-centre':
         stat_cube = trim_to_bbox_of_region(stat_cube, leeds_at_centre_gdf)
         
    # Find min and max vlues in data and set up contour levels
    local_min = np.nanmin(stat_cube.data)
    local_max = np.nanmax(stat_cube.data)     
    contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     
    
    ##### Plotting        
    # Create a colourmap                                   
    precip_colormap = create_precip_cmap()
    
    # Define figure size
    if region == 'leeds-at-centre':
        fig = plt.figure(figsize = (20,30))
    else:
        fig = plt.figure(figsize = (30,20))     
        
    # Set up projection system
    proj = ccrs.Mercator.GOOGLE
        
    # Create axis using this WM projection
    ax = fig.add_subplot(projection=proj)
    #ax = plt.subplot(projection=proj)
    # Plot
    mesh = iplt.pcolormesh(stat_cube, cmap = precip_colormap)
    
    # Add regional outlines, depending on which region is being plotted
    # And define extent of colorbars
    if region == 'Northern':
         leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
         northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
         colorbar_axes = plt.gcf().add_axes([0.73, 0.15, 0.015, 0.7])
    elif region == 'leeds-at-centre':
         leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
         colorbar_axes = plt.gcf().add_axes([0.92, 0.28, 0.015, 0.45])
    elif region == 'UK':
         plt.gca().coastlines(linewidth =3)
         colorbar_axes = plt.gcf().add_axes([0.76, 0.15, 0.015, 0.7])

    colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical',  boundaries = contour_levels)  
    colorbar.set_label('mm/hr', size = 20)
    colorbar.ax.tick_params(labelsize=28)
    colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
    
    # Save to file
    filename = "Outputs/RegionalRainfallStats/Plots/Observations/{}/{}/{}.png".format(regridding_method, region, stat)
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')
    plt.clf()
