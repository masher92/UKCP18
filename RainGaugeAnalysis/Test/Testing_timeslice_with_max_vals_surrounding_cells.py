'''
This script:
    Finds rain gauges within leeds-at-centre region
    Finds the CEH-GEAR grid cell which they are located within
    Plots a PDF of hourly precipitation intensities from the gauge vs from the grid cell
        Optional: also include data from UKCP18 grid cells
        
    Later in the script there is also code to combine the data from all the gauges
    and all the grid cells within which they are found
    And plot one PDF of the combined data

'''

#############################################################################
# Set up environment
#############################################################################
import numpy as np
import os
import pandas as pd
import glob
from shapely.geometry import Point, Polygon
import sys
from pyproj import Proj, transform
import iris.plot as iplt
import matplotlib as mpl
import warnings
from datetime import datetime
import pandas as pd
import matplotlib.patches as mpatches

# Set up path to root directory
root_fp = '/nfs/a319/gy17m2a/'
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *
from Pr_functions import *
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *
from PDF_plotting_functions import *

warnings.simplefilter(action='ignore', category = FutureWarning)
warnings.simplefilter(action='ignore', category = DeprecationWarning)

# Define whether to include UKCP18 data in the plot
include_ukcp18 = False
# Ensemble numbers
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

#############################################################################
#############################################################################
# Load in spatial data
# As geodataframes for plotting
# As shapely geometries for checking whether lat/long points are witihn the areas
#############################################################################
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

# Create outlines as shapely geometries
leeds_at_centre_poly = Polygon(create_leeds_at_centre_outline({'init' :'epsg:4326'})['geometry'].iloc[0])
leeds_poly = Polygon(create_leeds_outline({'init' :'epsg:4326'})['geometry'].iloc[0])

#############################################################################
#############################################################################
# Create lists to store station names, lat and long for all gauges within leeds region
station_names= []
lats = []
lons = []

# Create list to store all the indexs of grid cells closest to the gauges
closest_point_idx_grids = []

# Loop through each file
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
        res = this_point.within(leeds_at_centre_poly)
        res_in_leeds = this_point.within(leeds_poly)
        # If the point is within leeds-at-centre geometry 
        if res ==True :
            print(i)
            print(station_name)
            # Add station name and lats/lons to list
            station_names.append(station_name)
            lats.append(lat)
            lons.append(lon)
            
            # Create dictionary to store results for this station
            dict_this_station = {}
            
#############################################################################
#############################################################################           
# Find 10000 cells closest to Kitcliffe logger (which has an extreme value in 2006)     

kitcliffe_lat = df[df['names'] == 'bramham_logger']['lats'][32]
kitcliffe_lon = df[df['names'] == 'bramham_logger']['lons'][32]

# Convert WGS84 coordinate to BNG
kitcliffe_lon_bng,kitcliffe_lat_bng = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:27700'),
                            kitcliffe_lon, kitcliffe_lat)
# Create as a list
kitcliffe_sample_point = [('grid_latitude', kitcliffe_lat_bng), ('grid_longitude', kitcliffe_lon_bng)]


kitcliffe = gauge_dfs_dict['bramham_logger']
kitcliffe[kitcliffe['Precipitation (mm/hr)'] == kitcliffe['Precipitation (mm/hr)'].max()]['Datetime']
max_datetime = kitcliffe[kitcliffe['Precipitation (mm/hr)'] == kitcliffe['Precipitation (mm/hr)'].max()]['Datetime'][92333]

###############
lat_length = concat_cube.shape[1]
lon_length = concat_cube.shape[2]


# Create a list of all the tuple pairs of latitude and longitudes
locations = list(itertools.product(concat_cube.coord('projection_y_coordinate').points,
                                   concat_cube.coord('projection_x_coordinate').points))

# Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
tree = spatial.KDTree(locations)
closest_point_idxs = tree.query([(kitcliffe_sample_point[0][1], kitcliffe_sample_point[1][1])], k =5000)[1][0]

# Create a list of all the tuple positions
indexs_lst = []
for i in range(0,lat_length):
    for j in range(0,lon_length):
        # Print the position
        #print(i,j)
        indexs_lst.append((i,j))
                 
# Get the times
times = np.load('Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/timestamps.npy', allow_pickle = True)         
     
####### 
closest_point_dfs = pd.DataFrame({'Times' : times})

# Extract the lat and long values of this point using the index
for closest_point_idx in closest_point_idxs:
    print(closest_point_idx)
    filename = "Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/{}_{}.npy".format(indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1])
    data_slice = np.load(filename)
     
    # Create dataframe
    closest_point_dfs['Precipitation_{}'.format(closest_point_idx)] = data_slice

 
######## Check plotting 
# Get cube containing one hour worth of data
hour_uk_cube = concat_cube[0,:,:]

# Set all the values to 0
test_data = np.full((hour_uk_cube.shape),0,dtype = int)
for closest_point_idx in closest_point_idxs:
    
    filename = "Outputs/TimeSeries/CEH-GEAR/1km/leeds-at-centre/{}_{}.npy".format(indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1])
    data_slice = np.load(filename)
     
    # Create dataframe
    this_df = pd.DataFrame({'Times':times, 'Precips': data_slice})
    # Surrounding max point
    idx= this_df[this_df['Times'] == max_datetime].index[0]
    this_df = this_df[idx -3: idx+3]
    
    
    test_data[indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1]] = this_df['Precips'].max()

# Mask out all values that aren't 1
test_data = ma.masked_where(test_data<1,test_data)
    
# Set the dummy data back on the cube
hour_uk_cube.data = test_data

# Find cornerpoint coordinates (for use in plotting)
lats_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[0]
lons_cornerpoints = find_cornerpoint_coordinates_obs(hour_uk_cube)[1]

# Trim the data timeslice to be the same dimensions as the corner coordinates
hour_uk_cube = hour_uk_cube[1:,1:]
test_data = hour_uk_cube.data

# Create location in web mercator for plotting
print('Creating plot')

kitcliffe_lon_wm,kitcliffe_lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , kitcliffe_lon, kitcliffe_lat)

# Create a colormap
cmap = matplotlib.colors.ListedColormap('Blues')

fig, ax = plt.subplots(figsize=(30,30))
extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
plot =plotter.plot(ax)
# # Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
      linewidths=0.4, alpha = 1, cmap = 'Blues', edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plt.plot(kitcliffe_lon_wm, kitcliffe_lat_wm,  'o', color='black', markersize = 20)   
for station_name in [x for i, x in enumerate(station_names) if x != 'bramham_logger']:
    lon = df[df["names"] == station_name].reset_index()['lons'][0]
    lat =df[df["names"] == station_name].reset_index()['lats'][0]
    extra_lon_wm,extra_lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
    plt.plot(extra_lon_wm, extra_lat_wm,  'o', color='red', markersize = 10)   
   

    
    #plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Figs/CheckingLocations/CEH-GEAR/{}.png'.format(station_name),
    #                bbox_inches = 'tight')
    plt.show()          
            
           
