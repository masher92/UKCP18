lats_idxs = np.array([269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281,
       282, 283, 284, 285, 286, 287, 288, 289])
lons_idxs = np.array([295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307,
       308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320,
       321, 322])

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
wy_cube = trimmed_concat_cube[0,:,lats_idxs,lons_idxs]

#############################################
# Create shapely geometries of the outline of West Yorks and Leeds
#############################################
# Create geodataframe of the outline of West Yorkshire
# Data from https://data.opendatasoft.com/explore/dataset/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england%40ons-public/export/
wy_gdf = gpd.read_file("combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
# Convert to web mercator
#wy_gdf.crs = {'init' :'epsg:4783'}
wy_gdf = wy_gdf.to_crs({'init' :'epsg:3785'}) 

# Convert outline of Leeds into a polygon
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})

#############################################
# Check with plotting the right area of cube has been subsetted
# NB: this isn't quite right; not sure why.
#############################################
# Keep only one timeslice
wy_cube_ts = wy_cube[0,:,:]

# Find lats and lons and check plotting
lats_centrepoints = wy_cube_ts.coord('latitude').points
lons_centrepoints = wy_cube_ts.coord('longitude').points
lons_centrepoints,lats_centrepoints= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lons_centrepoints,lats_centrepoints)

# Plot
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(wy_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
wy_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
# Add points at corners of grids
ax.plot(lons_centrepoints.reshape(-1), lats_centrepoints.reshape(-1), "bo", markersize =10)
ax.pcolormesh(lons_centrepoints, lats_centrepoints, wy_cube_ts.data, 
              linewidths=3, alpha = 0.5, edgecolor = 'black')

#############################################
# Find which grid cell is closest to the point of interest
#############################################
lon_sp = -1.588883
lat_sp = 53.801994
sample_point = define_loc_of_interest(monthly_cubes_list, lon_sp, lat_sp)
lon_sp_wm,lat_sp_wm= transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),lon_sp,lat_sp)

# Extract just the grid cell which covers this point
interpolated = wy_cube_ts.interpolate(sample_point, iris.analysis.Nearest())
print(interpolated)

# Need to find out what the indicies are of this cube
lat = interpolated.coord('latitude').points
lon = interpolated.coord('longitude').points
test = np.where(wy_cube_ts.coord('latitude').points == lat)
idx_closestgrid = test[0][0], test[1][0]

#############################################
# Find which grid cell is closest to the point of interest
#############################################
# n=1, 3x3; n=2, 5x5; n=3, 7x7
n=2
central_lon = idx_closestgrid[0]
central_lat = idx_closestgrid[1]
lats = list(range(central_lat-n,central_lat + (n+1)))
lons = list(range(central_lon-n,central_lon + (n+1)))

data = wy_cube_ts.data
data.fill(0)
for i in list(itertools.product(lons, lats)):
    print(i)
    data[i] = 1
data[14,17] = 3

fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_gdf, buffer=5)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plotter.plot(ax)
leeds_gdf.plot(ax=ax, categorical=True, alpha=0.9, edgecolor='green', color='none', linewidth=6)
# Add points at corners of grids
ax.plot(lons_centrepoints.reshape(-1), lats_centrepoints.reshape(-1), "bo", markersize =10)
ax.pcolormesh(lons_centrepoints, lats_centrepoints, data, 
              linewidths=3, alpha =0.3, edgecolor = 'black')



# Need to find out what the indicies are of this cube
lats = interpolated_timeslice.coord('latitude').points
lons = interpolated_timeslice.coord('longitude').points
test = np.where(lats == 53.796748726911396)
test = np.where(lons == -1.6016034200884306)

# Need to find out what the indicies are of this cube
lats = ff.coord('latitude').points
lons = ff.coord('longitude').points
test = np.where(lats == 53.796748726911396)
test = np.where(lons == -1.6016034200884306)




def GridCells_within_geometry(lats, lons, geometry_gdf, data_shape):
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
    within_geometry = np.array(within_geometry).reshape(data_shape)
    # Convert to 0s and 1s
    within_geometry = within_geometry.astype(int)
    # Mask out values of 0
    within_geometry = np.ma.masked_array(within_geometry, within_geometry < 1)
    
    return within_geometry













        #############################################
        # Convert the WGS coordiantes of the point of interest into the same coordinate
        # system as the precipitation cubes
        #############################################
        sample_point = define_loc_of_interest(monthly_cubes_list, lon, lat)
        
        # Reconvert
        #cs = monthly_cubes_list[0].coord_system()
        #lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(sample_point[1][1]), np.array(sample_point[0][1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        
        #############################################
        # Create a single cube containing a precipitation timeseries for the 
        # location of interest
        #############################################    
        start = timer()
        results = create_concat_cube_one_location_m3(monthly_cubes_list, sample_point)
        ts_cube = results[0]
        print("Cubes joined and interpolated to location at " + str(lat)+ "," + str(lon) + ' in ' + str(round((timer() - start)/60, 1)) + ' minutes')
        
        # Check centre location of grid cell it used (in lat, lon)
        lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(results[2]), np.array(results[1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        # Find the index of the closest point
        index = results[3]
        
        ## Cmpare outputs
        #qplt.plot(ts_cube3)
        #(ts_cube2.data==ts_cube.data).all()
                        
        #############################################
        # Convert to a dataframe
        #############################################
        print("Converting to dataframe")       
        start_dfconversion_timer = timer()
        ts_df = pd.DataFrame({'Date': np.array(ts_cube.coord('yyyymmddhh').points),
                          'Precipitation (mm/hr)': np.array(ts_cube.data)})
        print("Cube converted to DF in " + str(round((timer() - start_dfconversion_timer)/60, 1)) + ' minutes')
        
        # Format the date column
        ts_df['Date_Formatted'] =  pd.to_datetime(ts_df['Date'], format='%Y%m%d%H',  errors='coerce')
        
        ###########################################################
        # Save cube  and df
        ###########################################################
        # Create directory if it doesn't exist already
        if not os.path.isdir(cubefolder_fp):
            os.makedirs(cubefolder_fp)
        # Save cube
        print("Saving cube to " + cube_fp)
        start_saving_timer = timer()
        iris.save(ts_cube, cube_fp)  
        print("Cube saved in " + str(round((timer() - start_saving_timer)/60, 1)) + ' minutes')
        print("Cube saved in " + str(round(timer() - start_saving_timer, 1)) + ' seconds')

          
        # Create directory if it doesn't exist already
        if not os.path.isdir(csvfolder_fp):
            os.makedirs(csvdolder_fp)
        # Write to a csv
        ts_df.to_csv(csv_fp, index = False)
        print("Saving csv to " + csv_fp)
                
        print("Complete")
        #iris.fileformats.netcdf.save(ts_cube, '/nfs/a319/gy17m2a/Outputs/TimeSeries_cubes/Armley/2.2km/EM07_1980-2001_test.nc', unlimited_dimensions = ['time'], chunksizes = [50])
        
   

##############################################################################
### Checking this approach
##############################################################################
# It is possible to conduct a check on which grid cell the data is being extracted
# for using the index of the grid cell returned by the create_concat_cube_one_location_m3
# function.
        
# Create a test dataset with all points with same value
# Set value at the index returned above to something different
# And then plot data spatially, and see which grid cell is highlighted.        
# test_data = np.full((hour_uk_cube.shape), 7, dtype=int)
# test_data_rs = test_data.reshape(-1)
# test_data_rs[INDEX] = 500
# test_data = test_data_rs.reshape(test_data.shape)



