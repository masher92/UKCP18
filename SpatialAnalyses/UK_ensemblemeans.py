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

# Set up variables
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

# Load mask    
mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')

############################################
# Import and create requried spatial files
#############################################
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

##################################################################
# Set up plotting colours
##################################################################
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      
precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="white")


##################################################################
# Create dictionaries storing the maximum and minimum values found for 
# each statistic, considering all ensemble members and all grid cells
##################################################################
stats = ['jja_max', 'jja_mean', 'jja_percentiles']
for stat in stats:
  filenames = []
  #
  for em in ems:
      filename= '/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_' + stat + '.nc'
      filenames.append(filename)

  # Load 12 ensemble member files into a cube list
  cubes_list = iris.load(filenames,'lwe_precipitation_rate')
  # Concatenate the cubes into one
  cubes = cubes_list.concatenate_cube()
  # Remove time dimension
  cubes = cubes[:,0,:,:]

  # Collapse them to contain one mean value across 12 ensemble members
  EMmean = cubes.collapsed(['ensemble_member'], iris.analysis.MEAN)
  EMspread = cubes.collapsed(['ensemble_member'], iris.analysis.STD_DEV)
  
  stats_cubes = [EMmean, EMspread]
  
  for stats_cube in stats_cubes:
      # Save the name of the stats cube as a variable
      name = namestr(stats_cube, globals())[0]
      print(name)
      # Trim to bbox of wider northern region
      stats_cube = trim_to_bbox_of_region(stats_cube, wider_northern_gdf)            
      # Mask out data outwith this region (including the sea)
      masked_data = ma.masked_where(mask == 0, stats_cube.data)
      # Set this masked data as the cube's data
      stats_cube.data = masked_data
      
      # Trim the data to the bbox of northern GDF 
      # This zooms in on only the northern_gdf region
      stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)

      # Get the lats and lons
      lats_2d = stats_cube.coord('latitude').points
      lons_2d = stats_cube.coord('longitude').points
      inProj = Proj(init='epsg:4326')
      outProj = Proj(init='epsg:3857')
      lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
   
      # PLot
      fig, ax = plt.subplots(figsize=(30,25))
      ax.set_axis_off()
      my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3, 
                            alpha = 1, cmap = precip_colormap)
      northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
      leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=4)
      cb1 = fig.colorbar(my_plot, ax=ax, fraction=0.036, pad=0.02)
      cb1.ax.tick_params(labelsize=40)
      filename = "Outputs/Stats_Spatial_plots/Northern/{}_{}.png".format(stat, name)
      fig.savefig(filename, bbox_inches = 'tight')
    




