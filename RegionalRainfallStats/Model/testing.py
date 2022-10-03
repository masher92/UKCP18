
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
import numpy.ma as ma

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Set up variables
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
yrs_range = "1980_2001" 
region = 'leeds' #['Northern', 'leeds-at-centre', 'UK']
regions = ['leeds', 'leeds-at-centre', 'Northern', 'UK']

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
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
leeds_at_centre_narrow_gdf = create_leeds_at_centre_narrow_outline({'init' :'epsg:3857'})


# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  
uk_mask = uk_mask.reshape(458,383)

# create square gdf
def create_square_outline (required_proj):
    # Define lats and lons to make box around Leeds
    lons = [54.06, 54.06, 53.54, 53.54]
    lats = [-1.99,-0.96, -0.96, -1.99] 
    
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_narrow_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    leeds_at_centre_narrow_gdf = leeds_at_centre_narrow_gdf.to_crs(required_proj) 

    return leeds_at_centre_narrow_gdf

run_number =25
stat = 'jja_p95'

em_cube_stat = 'EM_mean'
overlapping = ''
region = 'leeds-at-centre-narrow'

def create_leeds_at_centre_narrow_outline (required_proj, run_number):
    # #first two control height above outlnie (bigger number extends it higher)
    # second 2 (smaller number extends it down)
    # #First and last control left hand verticla sdie (smaller number moves it to right)

    #### 1. 
    # lons = [54.2, 54.2, 53.2, 53.2]
    # lats = [-1.50,-1.0, -1.0, -1.50] 

    # ### 2.
    # lons = [54.0, 54.0, 53.6, 53.6]
    # lats = [-1.50,-1.0, -1.0, -1.50] 

    # ### 3.
    # # leeds bouding box
    
    # ###4.
    # lons = [54.0, 54.0, 53.6, 53.6]
    # lats = [-1.50,-0.8, -0.8, -1.50] 

    # ### 5.
    # lons = [54.0, 54.0, 53.6, 53.6]
    # lats = [-2.0,-1.5, -1.5, -2.0] 
    
    # ###6.
    # lons = [54.2, 54.2, 53.75, 53.75]
    # lats = [-1.82,-1.29, -1.29, -1.82] 
    
    # ### 7.
    # lons = [53.85, 53.85, 53.55, 53.55]
    # lats = [-1.82,-1.29, -1.29, -1.82] 
    
    ### 8.
    # lons = [53.94, 53.94, 53.68, 53.68]
    # lats = [-1.50,-0.94, -0.94, -1.50] 
    
    if run_number == 9:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.82,-1.08, -1.08, -1.82]     
    
    elif run_number == 10: ##leeds-box
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.82,-1.28, -1.28, -1.82]    
    
    elif run_number == 11:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.99,-1.28, -1.28, -1.99]   
    
    elif run_number == 12:
        lons = [54.04, 54.04 ,53.68, 53.68]
        lats = [-1.82,-1.28, -1.28, -1.82]        
     
    elif run_number == 13:   
        lons = [53.94, 53.94, 53.58, 53.58]
        lats = [-1.82,-1.28, -1.28, -1.82]    
    
    elif run_number == 14:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.53,-1.0, -1.0, -1.53] 
   
    elif run_number == 15:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-2.00,-1.53, -1.53, -2.00] 
 
    elif run_number == 16:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.82,-1.54, -1.54, -1.82] 

    elif run_number == 17:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.54,-1.28, -1.28, -1.54] 
    
    elif run_number == 18:
        lons = [54.04, 54.04, 53.81, 53.81]
        lats = [-1.82,-1.28, -1.28, -1.82]      
     
    elif run_number == 19:
        lons = [53.81, 53.81, 53.57, 53.57]
        lats = [-1.82,-1.28, -1.28, -1.82]      
    
    elif run_number == 20:
        lons = [53.82, 53.82, 53.69, 53.69]
        lats = [-1.82,-1.28, -1.28, -1.82]   
    
    elif run_number == 21:
        lons = [53.95, 53.95, 53.82, 53.82]
        lats = [-1.82,-1.28, -1.28, -1.82]       
  
    elif run_number == 22:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.72,-0.99, -0.99, -1.72]    
    
    elif run_number == 23:
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.72,-1.18, -1.18, -1.72]     
        
    elif run_number ==24:    
        lons = [54.06, 54.06, 53.54, 53.54]
        lats = [-1.99,-0.96, -0.96, -1.99] 

    elif run_number ==25:    
        lons = [53.94, 53.94, 53.68, 53.68]
        lats = [-1.72,-1.28, -1.28, -1.72]    
        
            
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_narrow_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    leeds_at_centre_narrow_gdf = leeds_at_centre_narrow_gdf.to_crs(required_proj) 

    return leeds_at_centre_narrow_gdf


for run_number in [9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24, 25]:
    leeds_at_centre_narrow_gdf = create_leeds_at_centre_narrow_outline({'init' :'epsg:3857'}, run_number)
    square_gdf = create_square_outline({'init' :'epsg:3857'})
    # Load in the cube for the correct statistic and ensemble summary metric 
    stats_cube = iris.load("Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Summaries/{}_{}{}.nc".format(stat, em_cube_stat, overlapping))[0]
      
    # Trim to smaller area
    stats_cube = trim_to_bbox_of_region(stats_cube, leeds_at_centre_narrow_gdf)                       
     
    # Find the minimum and maximum values to define the spread of the pot
    local_min = stats_cube.data.min()
    local_max = stats_cube.data.max()
    percent_diff = round((local_max-local_min)/((local_max+local_min)/2)*100,2)
    local_min = 0.22 #2.07
    local_max = 0.92 #3.12
    contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)
    
    #############################################################################
    # Set up environment for plotting
    #############################################################################
    # Set up plotting colours
    precip_colormap = create_precip_cmap()   
    # Set up a plotting figurge with Web Mercator projection
    proj = ccrs.Mercator.GOOGLE
    fig = plt.figure(figsize=(20,20), dpi=200)
    ax = fig.add_subplot(122, projection = proj)
       
    # Define number of decimal places to use in the rounding of the colour bar
    # This ensures smaller numbers have decimal places, but not bigger ones.  
    if stats_cube.data.max() >10:
        n_decimal_places = 0
    elif stats_cube.data.max() < 0.1:
        n_decimal_places  =3
    else:
        n_decimal_places =2
        
    #############################################################################
    # Plot
    #############################################################################
    mesh = iplt.pcolormesh(stats_cube, cmap = precip_colormap, vmin = local_min, vmax = local_max)
         
    # Add regional outlines, depending on which region is being plotted
    square_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=0.1)
    leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2.3)
    cb1 = plt.colorbar(mesh, ax=ax, fraction=0.041, pad=0.03, boundaries = contour_levels)
    
    cb1.ax.tick_params(labelsize=25)
    if stat != 'whprop':
        cb1.set_label('mm/hr', size = 25)
    elif stat == 'whprop':
        cb1.set_label('%', size = 25)
    cb1.ax.set_yticklabels(["{:.{}f}".format(i, n_decimal_places) for i in cb1.get_ticks()])   
    
    print(percent_diff)
    
    num_cells = stats_cube.shape[0] * stats_cube.shape[1] 
    print(num_cells)
    
    # Save files
    filename = "Scripts/UKCP18/RegionalRainfallStats/Model/Figs/{}/Testing_{}_{}_{}_{}cells.png".format(stat, stat, run_number, percent_diff, num_cells)
    fig.savefig(filename, bbox_inches = 'tight')
      


