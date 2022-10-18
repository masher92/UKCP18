### Finding diff between NN and linear interpolation is not working -- not yet implemented erro

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
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

overlapping = '_overlapping' # '' , _overlapping

############################################
# Define variables and set up environment
#############################################
# Region over which to plot
region = 'leeds' #['Northern', 'leeds-at-centre', 'UK']
# Stats to plot
stats = ['jja_whprop', 'jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

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


##################################################################
# Trimming to region
##################################################################
for region in ['Northern', 'leeds-at-centre', 'leeds', 'UK']:
    for overlapping in ['', '_overlapping']:
        for stat in stats:
            print(stat)
            
            # Load in netcdf files containing the stats data over the whole UK
            nn_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/NearestNeighbour/{}{}.nc'.format(stat, overlapping))[0]
            lr_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/LinearRegridding/{}{}.nc'.format(stat, overlapping))[0]       
            
            # Remove uneeded dimensions
            if stat != 'jja_whprop':
                nn_cube = nn_cube[0]
                lr_cube = lr_cube[0]
            
            # Trim to smaller area
            if region == 'Northern':
                 nn_cube = trim_to_bbox_of_region_regriddedobs(nn_cube, northern_gdf)
                 lr_cube = trim_to_bbox_of_region_regriddedobs(lr_cube, northern_gdf)
            elif region == 'leeds-at-centre':
                 nn_cube = trim_to_bbox_of_region_regriddedobs(nn_cube, leeds_at_centre_gdf)
                 lr_cube = trim_to_bbox_of_region_regriddedobs(lr_cube, leeds_at_centre_gdf)
            elif region == 'leeds':
                 nn_cube = trim_to_bbox_of_region_regriddedobs(nn_cube, leeds_gdf)
                 lr_cube = trim_to_bbox_of_region_regriddedobs(lr_cube, leeds_gdf)
            
            # Find difference cube   
            diff_cube = nn_cube - lr_cube
            diff_cube = iris.analysis.maths.abs(diff_cube)
            
            # Create dictionary storing cubes and their name/type
            cubes_dict = {'LinearRegridding': lr_cube, 'NearestNeighbour': nn_cube,
                         'Regridding_Difference': diff_cube}
            
            # Loop through each cube
            for key, cube in cubes_dict.items():
                print(key)
        
                # Find min and max vlues in data and set up contour levels
                local_min = np.nanmin(cube.data)
                local_max = np.nanmax(cube.data)     
                contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     
                
                ##### Plotting        
                # Create a colourmap                                   
                precip_colormap = create_precip_cmap()
                
                # Define figure size
                if region == 'leeds-at-centre' or region == 'leeds':
                    fig = plt.figure(figsize = (20,20))
                else:
                    fig = plt.figure(figsize = (30,20))     
                    
                # Set up projection system
                proj = ccrs.Mercator.GOOGLE
                    
                # Create axis using this WM projection
                ax = fig.add_subplot(projection=proj)
                # Plot
                mesh = iplt.pcolormesh(cube, cmap = precip_colormap)
                
                # Add regional outlines, depending on which region is being plotted
                # And define extent of colorbars
                if region == 'Northern':
                     leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
                     northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
                     colorbar_axes = plt.gcf().add_axes([0.73, 0.25, 0.015, 0.7])
                elif region == 'leeds-at-centre' or region == 'leeds':
                     leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
                     colorbar_axes = plt.gcf().add_axes([0.92, 0.20, 0.015, 0.62])
                elif region == 'UK':
                     plt.gca().coastlines(linewidth =3)
                     colorbar_axes = plt.gcf().add_axes([0.76, 0.15, 0.015, 0.7])
            
                colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical',  boundaries = contour_levels)  
                if stat != 'jja_whprop':
                    colorbar.set_label('mm/hr', size = 35)
                else:
                    colorbar.set_label('%', size = 35)
                colorbar.ax.tick_params(labelsize=28)
                colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
                
                # Save to file
                if key == 'LinearRegridding':
                    filename = "Scripts/UKCP18/RegionalRainfallStats/RegriddedObservations/Figs/LinearRegridding/{}/{}{}.png".format(region, stat, overlapping)
                elif key == 'NearestNeighbour':
                    filename = "Scripts/UKCP18/RegionalRainfallStats/RegriddedObservations/Figs/NearestNeighbour/{}/{}{}.png".format(region, stat, overlapping)       
                elif key == 'Regridding_Difference':
                    filename = "Scripts/UKCP18/RegionalRainfallStats/RegriddedObservations/Figs/Regridding_Difference/{}/{}{}.png".format(region, stat, overlapping)
                    
                # Save plot        
                plt.savefig(filename, bbox_inches = 'tight')
                plt.clf()
