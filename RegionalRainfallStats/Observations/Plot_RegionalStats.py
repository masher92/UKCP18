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

##################################################################
# Trimming to region
##################################################################
for stat in stats:
    print(stat)
    
    # Load in netcdf files containing the stats data over the whole UK
    obs_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/{}.nc'.format(stat))[0][0]

    # Trim to smaller area
    if region == 'Northern':
         obs_cube = trim_to_bbox_of_region_obs(obs_cube, northern_gdf)
    elif region == 'leeds-at-centre':
         obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)
    
    # Find min and max vlues in data and set up contour levels
    local_min = np.nanmin(obs_cube.data)
    local_max = np.nanmax(obs_cube.data)     
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
    # Plot
    mesh = iplt.pcolormesh(obs_cube, cmap = precip_colormap)
    
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
    filename = "Outputs/RegionalRainfallStats/Plots/Observations/{}/{}.png".format(region, stat)
    
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')
    plt.clf()
