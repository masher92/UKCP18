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

#############################################
## Create cube trimmmed to the UK
#############################################
filename = 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc'
cube = iris.load(filename,'lwe_precipitation_rate')[0]
# Remove ensemble member dimension
cube = cube[0,:,:,:]
minmax = lambda x: (np.min(x), np.max(x))
#bbox = np.array([-8.6500072, 49.863187 ,  1.7632199, 60.8458677])
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

cube = cube[..., imin:imax+1, jmin:jmax+1]

# Just one time dimension
cube = cube[0]

#####################
#############################################
# Create dictionaries storing the maximum and minimum values found for 
# each statistic, considering all ensemble members and all grid cells
##################################################################
# Create a dictionary to store results for each ensemble member (which is in itself a dictionary)
ems_dict = {}

# Loop through ensemble members
for em in ems:
    print(em)
    # Create dictionary for that ensemble member to store results of differnet stats
    em_dict = {}
    # Load in netcdf files containing the max, mean and percentiles values over the whole UK
    jja_stats =np.load('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Wethours/em_'+ em+ '_stats.npz', 'r')
    jja_wethourprop = np.load('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Wethours/em_'+ em+ '_wethoursprop.npy')
    
    jja_mean = cube.copy()
    jja_mean.data =jja_stats['mean']    
    jja_max = cube.copy()
    jja_max.data  = jja_stats['max']
    jja_p95 = cube.copy()
    jja_p95.data  = jja_stats['P95']
    jja_p97 = cube.copy()
    jja_p97.data  = jja_stats['P97']
    jja_p99 = cube.copy()
    jja_p99.data  = jja_stats['P99']
    jja_p99_5 = cube.copy()
    jja_p99_5.data  = jja_stats['P99_5']
    jja_p99_75 = cube.copy()
    jja_p99_75.data  = jja_stats['P99_75']
    jja_p99_9 = cube.copy()
    jja_p99_9.data  = jja_stats['P99_9']
    jja_wethoursprop= cube.copy()
    jja_wethoursprop.data  = jja_wethourprop
      
    # Trim to smaller area
    jja_max = trim_to_bbox_of_region(jja_max, wider_northern_gdf)
    jja_mean = trim_to_bbox_of_region(jja_mean, wider_northern_gdf)
    jja_p95 = trim_to_bbox_of_region(jja_p95, wider_northern_gdf)
    jja_p97 = trim_to_bbox_of_region(jja_p97, wider_northern_gdf)
    jja_p99 = trim_to_bbox_of_region(jja_p99, wider_northern_gdf)
    jja_p99_5 = trim_to_bbox_of_region(jja_p99_5, wider_northern_gdf)
    jja_p99_75 = trim_to_bbox_of_region(jja_p99_75, wider_northern_gdf)
    jja_p99_9 = trim_to_bbox_of_region(jja_p99_9, wider_northern_gdf)
    jja_wethoursprop = trim_to_bbox_of_region(jja_wethoursprop, wider_northern_gdf)
    
    # List the different stats included
    stats = [jja_mean, jja_max, jja_p95, jja_p97, jja_p99, jja_p99_5, jja_p99_75, jja_p99_9
             , jja_wethoursprop]
    
    # If this is the first time through the loop e.g. the first ensemble member, 
    # then create dictionary which will store the max and min values for each 
    # statistic across all the ensemble members
    # Loop through the stats and for each set the value to sometihng unfeasible
    if em == '01':
        max_vals_dict = {}
        min_vals_dict = {}
        # Loop through stats setting max = 10000 and min = 0
        for stat in stats:
                name = namestr(stat, globals())[0]
                print(name)
                max_vals_dict[name] = 0
                min_vals_dict[name] = 10000
        
    # Now loop through all the ensemble members and store the real values
    for stat in stats:
        name = namestr(stat, globals())[0]
        print(name)
        print (stat.data.max()) 
        em_dict[name] = stat
        max_vals_dict[name] = stat.data.max() if stat.data.max() > max_vals_dict[name] else max_vals_dict[name]
        min_vals_dict[name] = stat.data.min() if stat.data.min() < min_vals_dict[name] else min_vals_dict[name]      
    
    ems_dict[em] = em_dict       
#
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

stats = []
for key, value in em_dict.items() :
    stats.append(key)

for stat in stats:
    print(stat)
   # Extract the max, min values
    max_value = max_vals_dict[stat]
    min_value = min_vals_dict[stat]
    
    em_i=0
    i=0
    fig=plt.figure(figsize=(24,32))
    columns = 3
    rows = 4
    for new_i in range(1, 13):
            em = ems[em_i]
            print(em)
            em_dict = ems_dict[em]
            # Extract correct stat
            grid = em_dict[stat]
            
            #grid = trim_to_bbox_of_region(grid, wider_northern_gdf)
            #iplt.contourf(grid)
            
            # Mask out values outside SCotland, and below Midland and not land
            #mask = mask_by_region(grid, wider_northern_gdf)
            #np.save('mask.npy', mask)
            mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
            
            # Masked data
            masked_data = ma.masked_where(mask == 0, grid.data)
            grid.data = masked_data
            grid = trim_to_bbox_of_region(grid, northern_gdf)
            #masked_data_1d = pd.DataFrame(masked_data.reshape(-1))
            #masked_data_2d = masked
            
            # Trim to smaller area
            #grid = trim_to_bbox_of_region(grid, test)
            
            lats_2d = grid.coord('latitude').points
            lons_2d = grid.coord('longitude').points
            inProj = Proj(init='epsg:4326')
            outProj = Proj(init='epsg:3857')
            lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
           
            #northern_grid = mask_by_region(grid, test)
            
            # fig, ax = plt.subplots()
            # my_plot = ax.pcolormesh(lons_2d, lats_2d, grid.data, linewidths=3, 
            #                       alpha = 1, cmap = 'Blues')
            # northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
            # leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=1)
            # cb1 = fig.colorbar(my_plot, ax=ax, fraction=0.16, pad=0.02)
            # cb1.ax.tick_params(labelsize=40)
            
            #ata = grid.data
            #mask = northern_grid
            #dat_test = ma.masked_where(mask == 0, data)
            #dat_test_1d = dat_test.reshape(-1)
                        
            #data = northern_grid
        
            ax = fig.add_subplot(rows, columns, new_i)
            ax.set_axis_off()
            
            ### Comparing plotting methods
            #plt.contourf(lons_2d, lats_2d, data, linewidths=3, 
            #                        alpha = 1, cmap = precip_colormap, levels = levels)
            #plt.pcolormesh(lons_2d, lats_2d, data, linewidths=3, 
            #                        alpha = 1, cmap = precip_colormap, vmin = min_value,
            #                        vmax = max_value)

            my_plot = ax.pcolormesh(lons_2d, lats_2d, grid.data, linewidths=3, 
                                    alpha = 1, cmap = precip_colormap)
                                   #,vmin = min_value,vmax = max_value)
            leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=3)
            northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
            cb1 = fig.colorbar(my_plot, ax=ax, fraction=0.16, pad=0.02)
            cb1.ax.tick_params(labelsize=40)
            
            em_i = em_i +1
        
    fig.tight_layout()
    #cbar_ax = fig.add_axes([1.05, 0.15, 0.05, 0.7])
    #cb1 = fig.colorbar(my_plot, cax=cbar_ax, fraction=0.36, pad=0.04)
    #cb1.ax.tick_params(labelsize=50)
    filename = "Outputs/Stats_Spatial_plots/Northern/Wethours/{}_diffscales.png".format(stat)
    fig.savefig(filename, bbox_inches = 'tight')
    




