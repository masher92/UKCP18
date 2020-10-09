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
import warnings
warnings.simplefilter(action = 'ignore', category = FutureWarning)

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

shared_axis = False

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
#sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
#from CreatingMask import *

ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
lons = [54.130260, 54.130260, 53.486836, 53.486836]
lats = [-2.138282, -0.895667, -0.895667, -2.138282]
polygon_geom = Polygon(zip(lats, lons))
leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:3785'}) 

uk_regions = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_regions = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
#uk_regions = gpd.read_file(root_fp + "datadir/SpatialData/NUTS_Level_1__January_2018__Boundaries-shp/NUTS_Level_1__January_2018__Boundaries.shp") 
#northern_regions = uk_regions.loc[uk_regions['nuts118nm'].isin(['North East (England)', 'North West (England)', 'Yorkshire and The Humber'])]
# Merge the three regions into one
northern_regions['merging_col'] = 0
northern_gdf = northern_regions.dissolve(by='merging_col')
northern_gdf = northern_gdf.to_crs({'init' :'epsg:3785'}) 

### Create larger northern region
# England part
wider_northern_gdf = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber', 'East Midlands', 'West Midlands'])]
wider_northern_gdf['merging_col'] = 0
wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
wider_northern_gdf = wider_northern_gdf[['geometry']]

# Scotland part
dg = gpd.read_file("datadir/SpatialData/2011_Census_Dumfries_and_Galloway_(shp)/DC_2011_EoR_Dumfries___Galloway.shp")
dg['merging_col'] = 0
dg = dg.dissolve(by='merging_col')
borders = gpd.read_file('datadir/SpatialData/Scottish_Borders_shp/IZ_2001_EoR_Scottish_Borders.shp')
borders['merging_col'] = 0
borders = borders.dissolve(by='merging_col')

southern_scotland = pd.concat([dg, borders])
southern_scotland['new_merging_col'] = 0
southern_scotland = southern_scotland.dissolve(by='new_merging_col')
southern_scotland = southern_scotland[['geometry']]

# Join the two
wider_northern_gdf = pd.concat([southern_scotland, wider_northern_gdf])
wider_northern_gdf['merging_col'] = 0
wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
wider_northern_gdf = wider_northern_gdf.to_crs({'init' :'epsg:3785'}) 

# Load mask data
mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')

##################################################################
# Create dictionaries storing the maximum and minimum values found for 
# each statistic, considering all ensemble members and all grid cells
##################################################################

# List of stats to loop through
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

# Create a dictionary.
# The keys will be ensemble member numbers and the values will be dictionarys
# Each ensemble member's dictionary will in turn have statistic names as keys
# and the cube of that statistic as values
ems_dict = {}
# Create dictionaries to store max and min values for each stat
max_vals_dict = {}
min_vals_dict = {}

# Loop through ensemble members
for em in ems:
    print(em)
    # Create dictionary for that ensemble member to store results of differnet stats
    em_dict = {}
    # Loop through stats
    for stat in stats:
          # Load in netcdf files containing the stats data over the whole UK
          stat_cube = iris.load('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_' + stat + '.nc')[0] 
          # Trim to smaller area
          stat_cube = trim_to_bbox_of_region(stat_cube, wider_northern_gdf)
          # If this is the first time through the loop e.g. the first ensemble member, 
          # then create dictionary which will store the max and min values for each 
          # statistic across all the ensemble members
          if em == '01':
            # Loop through stats setting max = 10000 and min = 0
            #name = namestr(stat, globals())[0]
            max_vals_dict[stat] = 0
            min_vals_dict[stat] = 10000
          # For all ensemble members store the file in a dictionary
          # And check if it's max/min value is higher/lower than the current value
          # and store it if it is
          print(stat)
          print (stat_cube.data.max()) 
          em_dict[stat] = stat_cube
          max_vals_dict[stat] = stat_cube.data.max() if stat_cube.data.max() > max_vals_dict[stat] else max_vals_dict[stat]
          min_vals_dict[stat] = stat_cube.data.min() if stat_cube.data.min() < min_vals_dict[stat] else min_vals_dict[stat]       
          
          # Save the dictionary of stat cubes to 
          ems_dict[em] = em_dict         

#############################################
# Plotting
#############################################
# Create a colourmap                                   
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      
precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="white")

# stats = []
# for key, value in em_dict.items() :
#     stats.append(key)
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

for stat in stats:
    print(stat)
    # Extract the max, min values
    # For shared axis plotting
    max_value = max_vals_dict[stat]
    min_value = min_vals_dict[stat]
    # Set up counters
    i=0
    # Set up plot
    fig=plt.figure(figsize=(24,32))
    columns = 3
    rows = 4
    
    for new_i in range(1, 13):
    for em in ems:
        
            
            # Extract data for correct ensemble member and stat
            # Remove time dimension (only had one value)
            em_dict = ems_dict[em]
            stats_cube = em_dict[stat][0]
                      
            # Mask the data so as to cover any cells not within
            # The wider northern region
            stats_cube.data = ma.masked_where(mask == 0, stats_cube.data)
            
            # Trim to the BBOX of Northern England
            # This ensures the plot shows nly the bbox around northern england
            # but that all land values are plotted
            stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)

            # Extract lats and lons for ploting and change projection
            lats_2d = stats_cube.coord('latitude').points
            lons_2d = stats_cube.coord('longitude').points
            lons_2d, lats_2d = transform(Proj(init='epsg:4326'),Proj(init='epsg:3857'),lons_2d, lats_2d)
           
            # CHecking plotting 
            #fig, ax = plt.subplots()
            #my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3, 
            #                      alpha = 1, cmap = precip_colormap)
            #northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
            
            # Create subplot and plot
            #(should we really find the corner coordinates?)
            ax = fig.add_subplot(rows, columns, new_i)
            ax.set_axis_off()
            if shared_axis == True:
                my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3, 
                                        alpha = 1, cmap = precip_colormap,vmin = min_value,vmax = max_value)
                leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=3)
                northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)

            
            elif shared_axis == False:
                my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3, 
                                        alpha = 1, cmap = precip_colormap)
                leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=3)
                northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
                #fig.colorbar(my_plot, ax=ax, fraction=0.036, pad=0.02)
                cb1 = fig.colorbar(my_plot, ax=ax, fraction=0.16, pad=0.02)
                cb1.ax.tick_params(labelsize=40)
                        
            # Move counter on to next ensemble member
            i = i+1
        
    fig.tight_layout()
    if shared_axis == True:
        cbar_ax = fig.add_axes([1.05, 0.15, 0.05, 0.7])
        cb1 = fig.colorbar(my_plot, cax=cbar_ax, fraction=0.36, pad=0.04)
        cb1.ax.tick_params(labelsize=50)
        filename = "Outputs/Stats_Spatial_plots/Northern/{}_diffscales.png".format(stat)
    elif shared_axis == False:
        filename = "Outputs/Stats_Spatial_plots/Northern/{}.png".format(stat)
    fig.savefig(filename, bbox_inches = 'tight')
   

