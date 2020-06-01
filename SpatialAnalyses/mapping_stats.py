#############################################
# Set up environment
#############################################
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

# Stops warning on loading Iris cubes
#iris.FUTURE.netcdf_promote = True
#iris.FUTURE.netcdf_no_unlimited = True

# Provide root_fp as argument
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Plotting_functions import *

start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
em = '01'
wy_lats_idxs = np.array([269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281,
       282, 283, 284, 285, 286, 287, 288, 289])
wy_lons_idxs = np.array([295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307,
       308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320,
       321, 322])
leeds_lats_idxs = np.array([10, 10, 11, 11, 11, 11, 11, 11, 11, 11, 12, 12, 12, 12, 12, 12, 12,
       12, 12, 12, 12, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 14, 14, 14,
       14, 14, 14, 14, 14, 14, 14, 14, 14, 15, 15, 15, 15, 15, 15, 15, 15,
       15, 15, 15, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 16, 17, 17,
       17, 17, 17, 17, 17, 17, 17, 17, 18, 18, 18, 18, 18, 18, 18, 18, 18,
       18, 18, 18, 18, 18, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19, 19,
       20, 20, 20, 20, 20])
leeds_lons_idxs = np.array([18, 19, 17, 18, 19, 20, 21, 22, 23, 24, 15, 16, 17, 18, 19, 20, 21,
       22, 23, 24, 25, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 14, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24, 25, 14, 15, 16, 17, 18, 19, 20, 21,
       22, 23, 24, 25, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 15, 16,
       17, 18, 19, 20, 21, 22, 23, 24, 12, 13, 14, 15, 16, 17, 18, 19, 20,
       21, 22, 23, 24, 25, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
       14, 22, 23, 24, 25])

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

#############################################
# Trim to just lats and lons within West Yorks
#############################################
# Trim the lats and lons in the same way as the other....
trimmed_concat_cube = concat_cube[:,:,0:605,0:483]

# Remove ensemble member dimension and keep just lats and lons within West Yorks
wy_cube = trimmed_concat_cube[0,:,wy_lats_idxs,wy_lons_idxs]

##############################################################################
#### Find mean and percentile values for each grid box (over a month)
##############################################################################
# Set up empty lists to store values
precip_values, means, p99s, p97s, p90s = [], [], [], [], []

# For each pair of indices, extract just the cube found at that position
# Store its precipitationd data values over the time period as a list
for lat_idx, long_idx in zip(lats_idxs, lons_idxs):
    print(lat_idx, long_idx)
    cube_at_location = wy_cube[:, lat_idx,long_idx]
    precip_at_location = cube_at_location.data.mean
    precip_values.append(precip_at_location)



cube_at_location.has_lazy_data()



f = cube_at_location.collapsed('time', iris.analysis.MEAN)



def GridCells_within_geometry(lats, lons, geometry_gdf):
    '''
    Description
    ----------
        Check whether each lat, long pair from provided arrays is found within
        the geometry.
        Create an array with points outwith Leeds masked

    Parameters
    ----------
        lats_1d_arr : array
            1D array of latitudes
        lons_1d_arr : array
            1D array of longitudes
    Returns
    -------
    within_geometry : masked array
        Array with values of 0 for points outwith Leeds
        and values of 1 for those within Leeds.
        Points outwith Leeds are masked (True)

    '''
    # Convert the geometry to a shapely geometry
    geometry_poly = Polygon(geometry_gdf['geometry'].iloc[0])
 
    within_geometry = []
    for lon, lat in zip(lons, lats):
        this_point = Point(lon, lat)
        res = this_point.within(geometry_poly)
        #res = leeds_poly.contains(this_point)
        within_geometry.append(res)
    # Convert to array
    within_geometry = np.array(within_geometry)
    # Convert from a long array into one of the shape of the data
    within_geometry = np.array(within_geometry).reshape(21,28)
    # Convert to 0s and 1s
    within_geometry = within_geometry.astype(int)
    # Mask out values of 0
    within_geometry = np.ma.masked_array(within_geometry, within_geometry < 1)
    
    return within_geometry



##############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
# Add points at corners of grids
ax.plot(df['Lon_centre'], df['Lat_centre'], "bo", markersize =10)
ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, centre_within_geometry, cmap =c.ListedColormap(['firebrick']),
              linewidths=3, alpha = 0.5, edgecolor = 'black')
#ax.pcolormesh(lons_wm_2d, lats_wm_2d, data)
leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
ax.tick_params(labelsize='xx-large')

##############################################################################
#### Find indices of points within Leeds
##############################################################################
index = np.where(centre_within_geometry== 1)









