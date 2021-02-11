import numpy as np
import os
from datetime import datetime
import pandas as pd
import glob
from shapely.geometry import Point, Polygon
import sys
import folium

# Set up path to root directory
root_fp = '/nfs/a319/gy17m2a/'
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

#############################################################################
# Spatial data
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:4326'})
# Convert to shapely geometry
geometry_poly = Polygon(leeds_at_centre_gdf['geometry'].iloc[0])

############################################################
# Read in monthly cubes and concatenate into one long timeseries cube
###########################################################
# For some reason a backslash was showing instead of a forward slash
filenames = [os.path.normpath(i) for i in glob.glob('Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_*')]

# Load in the rainfall cubes into a list, taking just the rainfall amount
monthly_cubes_list = iris.load(filenames, 'rainfall_amount')

# Concatenate the cubes
concat_cube = monthly_cubes_list.concatenate_cube()

# Read in the list of cubes, containing the lat and long cubes
one_cube = iris.load(filenames[0])

#
from pyproj import Proj, transform
inProj = Proj(init = 'epsg:4326') 
outProj = Proj(init = 'epsg:27700') 
lon_bng,lat_bng = transform(inProj, outProj, lon, lat)

sample_point = [('grid_latitude', lat_bng), ('grid_longitude', lon_bng)]

def define_loc_of_interest(cube, lon, lat):
    #############################################
    # Define a sample point at which we are interested in extracting the precipitation timeseries.
    # Assign this the same projection as the projection data
    #############################################
    # Create a cartopy CRS representing the coordinate sytem of the data in the cube.
    cs = obs_cubes[0].coord('projection_y_coordinate').coord_system.as_cartopy_crs()
    
    # Define a sample point of interest, in standard lat/long.
    # Use the rot_pole CRS to transform the sample point, with the stated original CRS into the same system
    original_crs = ccrs.Geodetic() # Instantiate an instance of Geodetic class i.e. that used in WGS
    target_xy = rot_pole.transform_point(lon, lat, original_crs) # https://scitools.org.uk/cartopy/docs/v0.14/crs/index.html
       
    # Store the sample point of interest as a tuples (with their coordinate name) in a list
    sample_points = [('projection_x_coordinate', target_xy[1]), 
                     ('projection_y_coordinate', target_xy[0])]
    return(sample_points)


sample_point = [('grid_latitude', lat), ('grid_longitude', lon)]
    concat_cube = concat_cube[0, :]
         
     # Create a list of all the tuple pairs of latitude and longitudes
     locations = list(itertools.product(concat_cube.coord('projection_y_coordinate').points,
                                        concat_cube.coord('projection_x_coordinate').points))
     
     
     # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
     tree = spatial.KDTree(locations)
     closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
     
     # Extract the lat and long values of this point using the index
     closest_lat = locations[closest_point_idx][0]
     closest_long = locations[closest_point_idx][1]
     
     # Use this closest lat, long pair to collapse the latitude and longitude dimensions
     # of the concatenated cube to keep just the time series for this closest point 
     time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
     return (time_series, closest_lat, closest_long, closest_point_idx)     


def concat_cube_multiple_neighbours_m3 (cube_list, sample_point, n_nearest_neighbours):
#Returns a dataframe.
#Not possible to create as a concatenated cube because the latitiude and longitude 
#values are not the same in every cube.
    # Remove attributes which aren't the same across all the cubes.
     for cube in cube_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
     
     # Concatenate the cubes into one
     concat_cube = cube_list.concatenate_cube()
     
     # Reduce the dimensions (remove ensemble member dimension)
     concat_cube = concat_cube[0, :]
     
     # Create a list of all the tuple pairs of latitude and longitudes
     locations = list(itertools.product(concat_cube.coord('grid_latitude').points, concat_cube.coord('grid_longitude').points))
     
     # Correct them so that 360 merges back into one
     corrected_locations = []
     for location in locations:
         if location[0] >360:
             new_lat = location[0] -360
         else: 
             new_lat = location[0]
         if location[1] >360:
             new_long = location[1] -360     
         else:
             new_long = location[1]
         new_location = new_lat, new_long 
         corrected_locations.append(new_location)
     
     # Find the index of the nearest neighbour(s) of the sample point in the list of locations present in concat_cube
     tree = spatial.KDTree(corrected_locations)
     #closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]
     closest_points_idxs = tree.query([(sample_point[0][1], sample_point[1][1])], k =n_nearest_neighbours )[1][0]
     
     time_series_dfs = []
     for point in closest_points_idxs:
         # Extract the lat and long values of this point using the index
         closest_lat = locations[point][0]
         closest_long = locations[point][1]
         # Use this closest lat, long pair to collapse the latitude and longitude dimensions
         # of the concatenated cube to keep just the time series for this closest point 
         time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
         
         # Store data as a dataframe
         #time_series = time_series[0:100000]
         start = timer()
         ts_df = pd.DataFrame({'Date': np.array(time_series.coord('yyyymmddhh').points),
                         'Precipitation (mm/hr)': np.array(time_series.lazy_data())})
         print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
          # Add to list of dataframes
         time_series_dfs.append(ts_df)
         print("Created dataframe for nearest neighbour at " + str(point))
     # Join all dataframes into one         
     df = pd.concat(time_series_dfs)
     return df  
 
# Testing of fastest method
# time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# time_series = time_series[0:100000]
# print(time_series.has_lazy_data())
# # Store data as a dataframe
# start = timer()
# ts_df = pd.DataFrame({'Date': np.array(time_series.coord('yyyymmddhh').points),
#                  'Precipitation (mm/hr)': np.array(time_series.data)})
# print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
# print(time_series.has_lazy_data())
   
# time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# time_series = time_series[0:100000]
# print(time_series.has_lazy_data())
# start = timer()
# time_series.remove_coord("time")
# time_series.remove_coord("month_number")
# time_series.remove_coord("year")
# test = iris.pandas.as_data_frame  (time_series) 
# print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
# print(time_series.has_lazy_data())

# time_series = concat_cube.extract(iris.Constraint(grid_latitude=closest_lat, grid_longitude = closest_long))
# time_series = time_series[0:100000]
# print(time_series.has_lazy_data())
# start = timer()
# ts_df = pd.DataFrame({'Date': np.array(time_series.coord('yyyymmddhh').points),
#                  'Precipitation (mm/hr)': np.array(time_series.lazy_data())})
# print("Cubes joined and interpolated to location at " + str(round((timer() - start)/60, 2)) + ' minutes')
# print(time_series.has_lazy_data())






#############################################################################
# Loop through every text file in the directory
# Check if its lat-long coordinates are within the leeds-at-centre area
# If so, then find the date times that correspond to the precipitation values
# and save as a CSV.
#############################################################################
filenames= []
lats = []
lons = []
prop_nas = {}
for filename in glob.glob("datadir/GaugeData/Newcastle/E*"):
    with open(filename) as myfile:
        # read in the lines of text at the top of the file
        firstNlines=myfile.readlines()[0:21]
        
        # Extract the lat, lon and station name
        station_name = firstNlines[3][23:-1]
        lat = float(firstNlines[5][10:-1])
        lon = float(firstNlines[6][11:-1])
        
        # Check if point is within leeds-at-centre geometry
        this_point = Point(lon, lat)
        res = this_point.within(geometry_poly)
       
        #### 
        if res ==True:
            print('yes')
                
            # Find the index of the point in the grid which is closest to the point of interest
            # Considering the grid both flipped and not flipped
            # For just creating a time series and not plotting, flipping is not really necesary
            # but can be used in the testing below
            closest_idx = find_idx_closestpoint(one_cube, lat, lon, flip = False)
            closest_idx_fl = find_idx_closestpoint(one_cube, lat, lon, flip = True)

# Hours worth of data
hour = obs_cubes[1]
#Extract the data
hour_data = hour.data
# Flip the data so it's not upside down
hour_data_fl = np.flipud(hour_data)
# Fill empty values with NaN
hour_data_fl = hour_data_fl.filled(np.nan) 
# Fill all places with 0
hour_data_fl.fill(0)
# Fill the location with a different value
hour_data_fl[closest_idx_fl[0],closest_idx_fl[1]] = 7
# # # Plot
contour = plt.contourf(hour_data_fl)
contour = plt.colorbar()
contour =plt.axes().set_aspect('equal') 
plt.plot(closest_idx_fl[1], closest_idx_fl[0], 'o', color='black', markersize = 3) 




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

        # Load in filenames into a cube
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
        # Convert the WGS coordinates of the point of interest into the same coordinate
        # system as the precipitation cubes (e.g. rotated pole)
        #############################################
        # Store the coordinate system of the cube
        cs = monthly_cubes_list[0].coord_system()
        
        # Define the location of interest in rotated pole coordinate system
        sample_point = define_loc_of_interest(monthly_cubes_list, lon, lat)
        
        # Reconvert the sample point into lat and longs to check
        #lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(sample_point[1][1]), np.array(sample_point[0][1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        