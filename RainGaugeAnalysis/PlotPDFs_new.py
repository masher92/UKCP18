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
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis"
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
# Loop through every text file in the directory
# Check if its lat-long coordinates are within the leeds-at-centre area
# If so, then find the date times that correspond to the precipitation values
# and save as a CSV.
#############################################################################
#############################################################################
i=0
dict_all_stations = {}
station_names= []
grid_closest_point_idxs = []
ukcp18_closest_point_idxs = []
lats = []
lons = []
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
        res_old=this_point.within(leeds_poly)
    
        # If the point is within leeds-at-centre geometry 
        if res ==True :
            print(i)
            print(station_name)
            station_names.append(station_name)
            print(lat,lon)
            lats.append(lat)
            lons.append(lon)
            
            dict_this_station = {}
           
            ############################################################################
            # Gauge data: Create a csv containing the data and the dates from the 
            ############################################################################
            print('Loading Gauge Data')
            # #Read in data entries containing precipitation values
            data=np.loadtxt(filename, skiprows = 21)
            
            # Store start and end dates
            startdate = firstNlines[7][16:26]
            enddate = firstNlines[8][14:24]

            # Convert to datetimes
            d1 = datetime(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8]), int(startdate[8:10]))
            d2 = datetime(int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), int(enddate[8:10]))
            
            # Find all hours between these dates
            time_range = pd.date_range(d1, d2, freq='H')    
            
            # Check if there are the correct number
            n_lines = firstNlines[10][19:-1]
            if int(n_lines) != len(time_range):
                print('Incorrect number of lines')
            
            # Create dataframe containing precipitation values as times
            gauge_df = pd.DataFrame({'Datetime': time_range,
                                      'Precipitation (mm/hr)': data})
            
            # Find na values and remove
            print('NA values in Gauge: ' + str(len(gauge_df[gauge_df['Precipitation (mm/hr)'] == -999])))
            gauge_df = gauge_df[gauge_df['Precipitation (mm/hr)'] != -999]
          
            # Create a formatted date column
            gauge_df['Datetime'] = pd.to_datetime(gauge_df['Datetime'], dayfirst = False)
          
            # # Save to file
            # precip_df.to_csv("datadir/GaugeData/Newcastle/leeds-at-centre_csvs/{}.csv".format(station_name),
            #                   index = False)
            
            #############################################################################
            # Create a csv containing the data and the dates for the CEH-GEAR grid cell which
            # the gauge is located within
            #############################################################################
            print('Loading CEH-GEAR data')
            filename = 'Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_201412.nc'
            obs_cube = iris.load(filename,'rainfall_amount')[0]
            # Trim concatenated cube to outline of leeds-at-centre geodataframe
            obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)

            # Get the data values at this location
            cehgear_df, closest_point_idx_grid = find_position_obs(obs_cube, lat, lon, station_name)
            # Add 
            grid_closest_point_idxs.append(closest_point_idx_grid)
            
            # Create a formatted date column
            cehgear_df['Datetime'] = pd.to_datetime(cehgear_df['Times'], dayfirst = True)
            
            # remove na values
            print('NA values in CEH-GEAR: ' + str(cehgear_df['Precipitation (mm/hr)'].isna().sum()))
            cehgear_df.dropna(inplace = True)
            
            #############################################################################
            # Create a csv containing the data and the dates for the CEH-GEAR grid cell which
            # the gauge is located within
            #############################################################################
            print('Loading UKCP18 data')
            for em in ems:
                print(em)
                filename = "Outputs/TimeSeries/UKCP18/Baseline/leeds-at-centre/{}/leeds-at-centre.nc".format(em)
                em_cube = iris.load(filename, 'lwe_precipitation_rate')[0]
                
                # Get the data values at this location
                ukcp18_df, closest_point_idx_ukcp18 = find_position(em_cube, em, lon, lat, station_name)
                ukcp18_closest_point_idxs.append(closest_point_idx_ukcp18)

                # add data to dictionary
                dict_this_station["UKCP18_{}".format(em)] = ukcp18_df
            
            # Add data to dicionary
            dict_this_station["Gauge"] = gauge_df
            dict_this_station["CEH-GEAR"] = cehgear_df
            `
            #### add to overall dictionary
            dict_all_stations[station_name] = dict_this_station
           
            # Add to counter 
            i = i+1 

#######################################################################
gauges_dict ={}
for station_name in station_names:
    this_dict = dict_all_stations[station_name]
    gauge_df = this_dict['Gauge']
    
    # Trim to same time period
    if "earliesttime" not in locals():
        earliesttime = gauge_df['Datetime'].min() 
    earliesttime = gauge_df['Datetime'].min() if gauge_df['Datetime'].min() > earliesttime else earliesttime
    if 'latesttime' not in locals():
        latesttime = gauge_df['Datetime'].max() 
    latesttime = gauge_df['Datetime'].max() if gauge_df['Datetime'].max() < latesttime else latesttime 
       
    gauges_dict[station_name] = gauge_df
    
for station_name in station_names:
    this_dict = dict_all_stations[station_name]  
    gauge_df = this_dict['Gauge']
    gauge_df = gauge_df[(gauge_df['Datetime'] > earliesttime)& (gauge_df['Datetime']< latesttime)]
    gauges_dict[station_name] = gauge_df
  
# Define a dictionary of colours
cols_dict = {}
for station_name in station_names:
    cols_dict[station_name] = 'blue'
             
# Set plotting parameters
x_axis = 'linear'
y_axis = 'log'
bin_nos = 20 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = False # False lets plot define aprpopriate xlims
bins_if_log_spaced= bin_nos

# Create patches, used for labelling
patches= []
               
numbers_in_each_bin = log_discrete_with_inset(gauges_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim)     
  
    
##############################################################

earliest_times = []
latest_times = []

for station_name in station_names:
    this_dict = dict_all_stations[station_name]
    gauge_df = this_dict['Gauge']
    ceh_gear_df = this_dict['CEH-GEAR']
    df_ukcp18 = this_dict['UKCP18_01']    
   

    # earliesttime = gauge_df['Datetime'].min() 
    # latesttime = gauge_df['Datetime'].max() 
    # print(earliesttime)
    
    # earliest_times.append(earliesttime)
    # latest_times.append(latesttime)
    
    # Trim to same time period
    earliesttime = gauge_df['Datetime'].min() if gauge_df['Datetime'].min() > cehgear_df['Datetime'].min() else cehgear_df['Datetime'].min()
    latesttime = gauge_df['Datetime'].max() if gauge_df['Datetime'].max() < cehgear_df['Datetime'].max() else cehgear_df['Datetime'].max()
    
    # Override with latestime from UKCP18     
    if include_ukcp18 ==True:
        latesttime_ukcp18 = pd.to_datetime(df_ukcp18['Times'].max(), format = '%Y%m%d%H')
        latesttime = latesttime if latesttime < latesttime_ukcp18 else latesttime_ukcp18
        earliesttime_ukcp18 = pd.to_datetime(df_ukcp18['Times'].min(), format = '%Y%m%d%H')
        earliesttime = earliesttime if earliesttime > earliesttime_ukcp18 else earliesttime_ukcp18
            
    # Filter to only be between these times
    cehgear_df = cehgear_df[(cehgear_df['Datetime'] >= earliesttime)& (cehgear_df['Datetime']<= latesttime)]
    gauge_df = gauge_df[(gauge_df['Datetime'] > earliesttime)& (gauge_df['Datetime']< latesttime)]
    
    # Add data to dicionary
    this_dict["Gauge_overlapping"] = gauge_df
    this_dict["CEH-GEAR_overlapping"] = cehgear_df
    
    if include_ukcp18 ==True:
      frames =[]
      for em in ems:
        this_em = this_dict['UKCP18_{}'.format(em)]
        this_em = this_em[(this_em['Times'] >= datetime.strftime(earliesttime, format = '%Y%m%d%H'))& (this_em['Times']<= datetime.strftime(latesttime, format = '%Y%m%d%H'))]
        frames.append(this_em)
      this_dict['UKCP18_combined'] = pd.concat(frames)      
        
    # earliesttime = gauge_df['Datetime'].min() 
    # latesttime = gauge_df['Datetime'].max() 
    # earliest_times_filtered.append(earliesttime)
    # latest_times_filtered.append(latesttime)
    
    
    print(earliesttime)
    
# test = pd.DataFrame({'Station': station_names,
#                       'From':earliest_times,
#                       'To': latest_times})
# test.to_csv('Scripts/UKCP18/gauge_times.csv')
 
    
# Plotting 
ukcp18_frames = 
gauge_frames = []
gauge_overlapping_frames = []
grid_frames = []
grid_overlapping_frames = []
for station_name in station_names:    
    gauge_frames.append(dict_all_stations[station_name]['Gauge'] )
    grid_frames.append(dict_all_stations[station_name]['CEH-GEAR'] )
    gauge_overlapping_frames.append(dict_all_stations[station_name]['Gauge_overlapping'] )
    grid_overlapping_frames.append(dict_all_stations[station_name]['CEH-GEAR_overlapping'] )

all_gauges = pd.concat(gauge_frames)    
all_gauges_overlapping = pd.concat(gauge_overlapping_frames)   
all_grids = pd.concat(grid_frames)   
all_grids_overlapping = pd.concat(grid_overlapping_frames)    

combined_dict = {'Gauge':all_gauges_overlapping,
                  'CEH-GEAR': all_grids_overlapping}

#########################################################################
# Plotting
#########################################################################
# Define a dictionary of colours
cols_dict = {'Gauge' : 'firebrick',
             'CEH-GEAR'  : 'green'}

if combined_ems == 'Combined':
    cols_dict[station_name + '_UKCP18Data'] = 'grey'
else:
    for em in ems:
       cols_dict[station_name + '_UKCP18Data{}'.format(em)] = 'grey'
             
# Set plotting parameters
x_axis = 'linear'
y_axis = 'log'
bin_nos = 20 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
xlim = False # False lets plot define aprpopriate xlims
bins_if_log_spaced= bin_nos

# Create patches, used for labelling
patches= []
patch = mpatches.Patch(color='firebrick', label='Gauge')
patches.append(patch)
patch = mpatches.Patch(color='green', label='CEH-GEAR')
patches.append(patch)
# if include_ukcp18 == True:
#     patch = mpatches.Patch(color='grey', label='UKCP18')
#     patches.append(patch)
               
numbers_in_each_bin = log_discrete_with_inset(combined_dict, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                  patches, True, xlim) 

# Save
if include_ukcp18 == True:
    plt.savefig("Scripts/UKCP18/RainGaugeAnalysis/Figs/PDF_GaugevsGridCellvsUKCP18/{}_{}_{}_{}.png".format(station_name, just_jja, overlapping_time_period, combined_ems))
else:
    plt.savefig("Scripts/UKCP18/RainGaugeAnalysis/Figs/PDF_GaugevsGridCell/{}_{}_{}.png".format(station_name, just_jja, overlapping_time_period))




######## Check plotting 
# Get cube containing one hour worth of data
hour_uk_cube = obs_cube[0,:,:]

# Create a list of all the tuple positions
indexs_lst = []
for i in range(0,hour_uk_cube.shape[0]):
    for j in range(0,hour_uk_cube.shape[1]):
        # Print the position
        #print(i,j)
        indexs_lst.append((i,j))

# Set all the values to 0
test_data = np.full((hour_uk_cube.shape),0,dtype = int)
# Set the values at the index position fond above to 1
for closest_point_idx in closest_point_idxs:
    test_data[indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1]] = 1
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


# Create a colormap
cmap = matplotlib.colors.ListedColormap(['yellow'])

fig, ax = plt.subplots(figsize=(30,30))
extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
plot =plotter.plot(ax)
# # Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
      linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
for lat, lon in zip(lats, lons):
    lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
    plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 10)     
plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Figs/CheckingLocations/CEH-GEAR/AllLocations.png',
            bbox_inches = 'tight')
plt.show()
    