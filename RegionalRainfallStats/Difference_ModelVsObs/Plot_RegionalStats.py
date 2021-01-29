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
from matplotlib import colors
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
region = 'leeds-at-centre' #['Northern', 'leeds-at-centre', 'UK']


##################################################################
# Load necessary spatial data
##################################################################

# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

##################################################################
# Trimming to region
##################################################################
for stat in stats:
    print(stat)
    
    # Load in netcdf files containing the stats data over the whole UK
    model_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Summaries/{}_EM_mean.nc'.format(stat))[0]
    obs_cube= iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/NearestNeighbour/{}.nc'.format(stat))[0][0]

    # Remove coordinates present in model cube, but not in observations
    model_cube.remove_coord('latitude')
    model_cube.remove_coord('longitude')    
    
    # Find the difference between the two
    diff_cube = model_cube-obs_cube
    
    # Find the percentage difference
    diff_cube = (diff_cube/obs_cube) * 100
    
    #diff_cube = iris.analysis.maths.abs(diff_cube)
    
    # Trim to smaller area
    if region == 'Northern':
         diff_cube = trim_to_bbox_of_region_obs(diff_cube, northern_gdf)
    elif region == 'leeds-at-centre':
         diff_cube = trim_to_bbox_of_region_obs(diff_cube, leeds_at_centre_gdf)
    
    # Find min and max vlues in data and set up contour levels
    local_min = np.nanmin(diff_cube.data)
    local_max = np.nanmax(diff_cube.data)  
    
    if abs(local_min) > abs(local_max):
        local_max = abs(local_min)
    elif abs(local_max) > abs(local_min):
        local_min = -(local_max)
    
    contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     
    
    ##### Plotting        
    # Create a colourmap            
    precip_colormap = create_precip_cmap()
    # Create a divergine colormap
    diverging_cmap = matplotlib.cm.RdBu_r
    #diverging_cmap.set_under(color="white")
    #diverging_cmap.set_bad(color="white", alpha = 1.)

    # Normalise data with a defined centre point (in this case 0)
    if local_min < 0:
        norm = colors.TwoSlopeNorm(vmin = local_min, vmax = local_max,
                                    vcenter = 0)
    else:
        norm = None
        diverging_cmap = matplotlib.cm.Reds
    
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
    mesh = iplt.pcolormesh(diff_cube, cmap = diverging_cmap, norm=norm)
                          # norm = MidpointNormalize(midpoint=0))
    
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

    colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical')  
    colorbar.set_label('mm/hr', size = 20)
    colorbar.ax.tick_params(labelsize=28)
    colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
    
    # Set plot title
    ax.set_title(stat, fontsize = 50)
    # Save to file
    filename = "Outputs/RegionalRainfallStats/Plots/Difference_ModelVsObs/{}/percentage_diff_{}.png".format(region, stat)
    
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')
    plt.clf()
