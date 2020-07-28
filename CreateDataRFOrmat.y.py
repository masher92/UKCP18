import sys
import iris
import cartopy.crs as ccrs
import os
from scipy import spatial
import itertools
import iris.quickplot as qplt
import warnings
import copy
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
import numpy as np
import iris.coord_categorisation

# Provide root_fp as argument
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
em = '01'

# Create geodataframe of the outline of West Yorkshire
# Data from https://data.opendatasoft.com/explore/dataset/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england%40ons-public/export/
wy_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
wy_gdf = wy_gdf.to_crs({'init' :'epsg:3785'}) 

uk_regions = gpd.read_file(root_fp + "datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_regions_gdf = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'Yorkshire and The Humber'])]
northern_regions_gdf = northern_regions_gdf.to_crs({'init' :'epsg:3785'}) 


#############################################
# Read in files
#############################################
# Create list of names of cubes for between the years specified
filenames =[]
for year in range(start_year,end_year+1):
    # Create filepath to correct folder using ensemble member and year
    general_filename = root_fp + 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
        filenames.append(filename)
   
filenames = root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc'  
     
monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
print(str(len(monthly_cubes_list)) + " cubes found for this time period.")

#############################################
# Concat the cubes into one
#############################################
# Remove attributes which aren't the same across all the cubes.
for cube in monthly_cubes_list:
     for attr in ['creation_date', 'tracking_id', 'history']:
         if attr in cube.attributes:
             del cube.attributes[attr]
 
 # Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Remove ensemble member dimension
concat_cube = concat_cube[0,:,:,:]

############################################
# Trim to include only grid cells whose coordinate is within a certain region 
#############################################
regional_cube = trim_to_gdf(concat_cube, wy_gdf)
regional_cube = trim_to_gdf(concat_cube, northern_regions_gdf)

############################################
# Find the maximum value in each June-July_August period
#############################################
## Add season and season_year variables
iris.coord_categorisation.add_season_year(regional_cube,'time', name = "season_year")
iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")

# Aggregate to get just the maximum value in each seasonal yearly period
annual_seasonal_max = wy_cube.aggregated_by(['season_year', 'clim_season'], iris.analysis.MAX)
#iris.save(annual_seasonal_max, "/nfs/a319/gy17m2a/Scripts/UKCP18/Outputs/wy_cube_em01_seasonalmax.nc")

# Keep only JJA
jja = annual_seasonal_max.extract(iris.Constraint(clim_season = 'djf'))

############################################
# Check plotting 
#############################################
stats_array = jja.data

#############################################################################
#### # Plot - uses the lats and lons of the corner points but with the values 
# derived from the associated centre point
##############################################################################
within_region = GridCells_within_geometry(lats_centrepoints.reshape(-1),lons_centrepoints.reshape(-1), polygon_northern, wy_cube)
Leeds_stats_array = np.where(within_leeds_outline, stat.data, np.nan)  

#############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(polygon_northern)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
plot =polygon_northern.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, Leeds_stats_array,
              linewidths=3, alpha = 1, cmap = 'GnBu')
cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
#cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
#plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
plot =ax.tick_params(labelsize='xx-large')
plot =polygon_northern.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
