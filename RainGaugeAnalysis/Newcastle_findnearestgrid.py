import numpy as np
import os
from datetime import datetime
import pandas as pd
import glob
from shapely.geometry import Point, Polygon
import sys
import folium
from pyproj import Proj, transform
import itertools
from scipy import spatial
import iris.quickplot as qplt
import iris.plot as iplt
import cartopy.crs as ccrs
import numpy.ma as ma
import matplotlib as mpl
from pyproj import Proj, transform
import numpy.ma as ma

# Set up path to root directory
root_fp = '/nfs/a319/gy17m2a/'
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

#############################################################################
# Spatial data
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# # Convert to shapely geometry
# geometry_poly = Polygon(leeds_at_centre_gdf['geometry'].iloc[0])
# # Outline of Northern England
# northern_gdf = create_northern_outline({'init' :'epsg:27700'})

#############################################
## Load in the data
#############################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_*'
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    #print(filename)
    filenames.append(filename)
    print(len(filenames))
# Load all cubes into list
monthly_cubes_list = iris.load(filenames,'rainfall_amount')

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Test plotting
iplt.pcolormesh(concat_cube[12])

#############################################
## Trim cube to outline of leeds-at-centre geodataframe
#############################################
concat_cube = trim_to_bbox_of_region_obs(concat_cube, leeds_at_centre_gdf)

# Test plotting
iplt.pcolormesh(concat_cube[12])

#############################################
## Rename grid latitude and longitude
#############################################
#### Rename to be grid_latitude and grid_longitude
# y_coord = concat_cube.dim_coords[1]
# y_coord.rename('grid_latitude')

# x_coord= concat_cube.dim_coords[2] 
# x_coord.rename('grid_longitude')

############################################################
# Testing with lat, long point
############################################################
# Define lat, long point
lat = 53.80228
lon = -1.587669

# Create time series cube at this location, and return the associated         
result = create_concat_cube_one_location_obs(concat_cube, lat, lon)

# 
closest_lat = result[1]
closest_long = result[2]
closest_point_idx = result[3]


#############################################
## 
#############################################

cube_higlighted_cell = create_grid_highlighted_cell(concat_cube, closest_point_idx)
cube_higlighted_cell_data = cube_higlighted_cell.data

# Find cornerpoint coordinates
lats_cornerpoints = find_cornerpoint_coordinates_obs(cube_higlighted_cell)[0]
lons_cornerpoints = find_cornerpoint_coordinates_obs(cube_higlighted_cell)[1]

# Trim the data timeslice to be the same dimensions as the corner coordinates
cube_higlighted_cell_data = cube_higlighted_cell_data[1:,1:]

    
#############################################################################
#### # Plot - highlighting grid cells whose centre point falls within Leeds
# Uses the lats and lons of the corner points but with the values derived from 
# the associated centre point
##############################################################################
lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)

cmap = mpl.colors.ListedColormap(['yellow'])

fig, ax = plt.subplots(figsize=(20,10))
extent = tilemapbase.extent_from_frame(leeds_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
# Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cube_higlighted_cell_data,
              linewidths=1, alpha = 1, cmap = cmap, edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 2)     






############################################################
#
############################################################

# Convert WGS84 coordinate to BNG
lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)


# Find min and max vlues in data and set up contour levels
local_min = np.nanmin(hour_uk_cube.data)
local_max = np.nanmax(hour_uk_cube.data)     
contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     

##### Plotting        
# Create a colourmap                                   
precip_colormap = create_precip_cmap()

# Define figure size
fig = plt.figure(figsize = (20,30))

    # Set up projection system
proj = ccrs.Mercator.GOOGLE
    
# Create axis using this WM projection
ax = fig.add_subplot(projection=proj)
# Plot
mesh = iplt.pcolormesh(hour_uk_cube, cmap = precip_colormap)

# Add regional outlines, depending on which region is being plotted
# And define extent of colorbars
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
plt.plot(lon_wm, lat_wm,  'o', color='red', markersize = 15) 
colorbar_axes = plt.gcf().add_axes([0.92, 0.28, 0.015, 0.45])

colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical',  boundaries = contour_levels)  
colorbar.set_label('mm/hr', size = 20)
colorbar.ax.tick_params(labelsize=28)
colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
 









































############################################################
# Read in observation cubes
###########################################################
# List all the filenames
filenames = [os.path.normpath(i) for i in glob.glob('Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_*')]

# Load in the rainfall cubes into a list, taking just the rainfall amount
monthly_cubes_list = iris.load(filenames, 'rainfall_amount')

# Concatenate the cubes
concat_cube = monthly_cubes_list.concatenate_cube()

##### Read in the list of cubes, containing the lat and long cubes
one_cube = iris.load(filenames[0])

############################################################
# Trim to smaller spatial area
############################################################
concat_cube = trim_to_bbox_of_region_obs(concat_cube, northern_gdf)

########### Trim to BBOX of region
# CReate function to find
minmax = lambda x: (np.min(x), np.max(x))

# Convert the regional gdf to WGS84 (same as cube)
northern_gdf = northern_gdf.to_crs({'init' :'epsg:27700'}) 

# Find the bounding box of the region
bbox = northern_gdf.total_bounds

# Find the lats and lons of the cube in BNG
lats_1d = concat_cube.coord('projection_y_coordinate').points
lons_1d = concat_cube.coord('projection_x_coordinate').points

# Define projections
inProj = Proj(init = 'epsg:27700') 
outProj = Proj(init = 'epsg:4326') 

# Convert to 2D
lons_2d, lats_2d = np.meshgrid(lons_1d, lats_1d)


# Convert WGS84 coordinate to BNG
lats_bng,lons_bng = transform(inProj, outProj, lats_2d, lons_2d)


inregion = np.logical_and(np.logical_and(lons_1d > bbox[0],
                                         lons_1d < bbox[2]),
                          np.logical_and(lats_1d > bbox[1],
                                         lats_1d < bbox[3]))
region_inds = np.where(inregion)
imin, imax = minmax(region_inds[0])
jmin, jmax = minmax(region_inds[1])

trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1]
    

   # Trim to smaller area
    if region == 'Northern':
         obs_cube = trim_to_bbox_of_region_obs(obs_cube, northern_gdf)
    elif region == 'leeds-at-centre':
         obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)
    
    # Find min and max vlues in data and set up contour levels
    local_min = np.nanmin(obs_cube.data)
    local_max = np.nanmax(obs_cube.data)     
    contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     
    
    ##### Plotting        
    # Create a colourmap                                   
    precip_colormap = create_precip_cmap()
    
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
    mesh = iplt.pcolormesh(obs_cube, cmap = precip_colormap)
    
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

    colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical',  boundaries = contour_levels)  
    colorbar.set_label('mm/hr', size = 20)
    colorbar.ax.tick_params(labelsize=28)
    colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
    
    # Save to file
    filename = "Outputs/RegionalRainfallStats/Plots/Observations/{}/{}.png".format(region, stat)
    
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')
    plt.clf()








hour = concat_cube[20]
#Extract the data
hour_data = hour.data
# Flip the data so it's not upside down
hour_data_fl = np.flipud(hour_data)
# Fill empty values with NaN
hour_data_fl = hour_data_fl.filled(np.nan)  

# Create the contour plot, with colourbar, with axes correctly spaced
contour = plt.contourf(hour_data_fl, cmap=precip_colormap)
contour = plt.colorbar()
contour =plt.axes().set_aspect('equal') 

# Use this closest lat, long pair to co############################################################
# Testing with lat, long point
############################################################
# Define lat, long point
lat = 53.480546999999994
lon = -1.4410031

# Define projections
inProj = Proj(init = 'epsg:4326') 
outProj = Proj(init = 'epsg:27700') 

# Convert WGS84 coordinate to BNG
lon_bng,lat_bng = transform(inProj, outProj, lon, lat)

sample_point = [('grid_latitude', lat_bng), ('grid_longitude', lon_bng)]
#sample_point = [('grid_latitude', lat_bng), ('grid_longitude', lon_bng)]

         
# Create a list of all the tuple pairs of latitude and longitudes
locations = list(itertools.product(concat_cube.coord('projection_y_coordinate').points,
                                   concat_cube.coord('projection_x_coordinate').points))


# Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
tree = spatial.KDTree(locations)
closest_point_idx = tree.query([(sample_point[0][1], sample_point[1][1])])[1][0]

# Extract the lat and long values of this point using the index
closest_lat = locations[closest_point_idx][0]
closest_long = locations[closest_point_idx][1]llapse the latitude and longitude dimensions
# of the concatenated cube to keep just the time series for this closest point 
time_series = concat_cube.extract(iris.Constraint(projection_x_coordinate=closest_lat, projection_y_coordinate = closest_long))

ts_df = pd.DataFrame({'Date': np.array(time_series.coord('time').points),
                'Precipitation (mm/hr)': np.array(time_series.lazy_data())})
 
# Add to list of dataframes
time_series_dfs.append(ts_df)

hour_uk_cube = concat_cube[0,:,:]
# And then plot data spatially, and see which grid cell is highlighted.        
test_data = np.full((hour_uk_cube.shape), 0, dtype=int)
test_data_rs = test_data.reshape(-1)
test_data_rs[closest_point_idx] = 500
for i in range(0,50000):
    test_data_rs[i] = 500

test_data = test_data_rs.reshape(test_data.shape)

hour_uk_cube.data = test_data
qplt.pcolormesh(hour_uk_cube)
iplt.pcolormesh(hour_uk_cube)




hour = concat_cube[1]
#Extract the data
hour_data = hour.data
# Flip the data so it's not upside down
hour_data_fl = hour_data
# Fill empty values with NaN
hour_data_fl = hour_data_fl.filled(np.nan) 
# Fill all places with 0
hour_data_fl.fill(0)
# Fill the location with a different value
hour_data_fl[closest_lat,closest_long] = 7
# # # Plot
contour = plt.contourf(hour_data_fl)
contour = plt.colorbar()
contour =plt.axes().set_aspect('equal') 
plt.plot(closest_idx_fl[1], closest_idx_fl[0], 'o', color='black', markersize = 3) 

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
        