import iris
import os
import sys
import glob
from datetime import datetime

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


###################################################################################
###################################################################################
# Load data
###################################################################################
###################################################################################
# Read in rain gauge data
gauge_lats = []
gauge_lons = []
station_names = []
filenames = []
firstNlines_list = []
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
        if res ==True  :
            print(station_name)
            # Add station name and lats/lons to list
            gauge_lats.append(lat)
            gauge_lons.append(lon)
            station_names.append(station_name)
            filenames.append(filename)
            firstNlines_list.append(firstNlines)

# Load in CEH-GEAR - one timeslice
print('Loading CEH-GEAR data')
filename = 'Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_201311.nc'
obs_cube = iris.load(filename,'rainfall_amount')[0]
# Trim concatenated cube to outline of leeds-at-centre geodataframe
obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)


###################################################################################
###################################################################################
# Define lat, long of random point
###################################################################################
###################################################################################
random_point_lats = [54.083,53.71, 53.868, 54.13, 53.585, 53.59]
random_point_lons = [-1.7784, -0.977, -1.11, -2.18, -0.998]
plot_num=0
for lat, lon in zip(random_point_lats, random_point_lons):
    print(lat, lon)
    # Create as a list
    sample_point = [('grid_latitude', lat), ('grid_longitude', lon)]

    ###################################################################################
    ###################################################################################
    # Find the rain gauges closest to this location
    ###################################################################################
    ##################################################################################
    # Create a list of all the tuple pairs of gauge locations, latitude and longitudes
    locations = list(zip(gauge_lats, gauge_lons))
    
    # Find the index of the nearest neighbour of the sample point in the list of locations present in concat_cube
    tree = spatial.KDTree(locations)
    closest_point_idxs = tree.query([(sample_point[0][1], sample_point[1][1])], k=3)[1][0]
    
    ####
    dict_this_station ={}
    for closest_point_idx in closest_point_idxs:
        print(closest_point_idx)
    
        # Find name of closest station
        station_name = station_names[closest_point_idx]
        print(station_name)
        filename = filenames[closest_point_idx]
        firstNlines = firstNlines_list[closest_point_idx]     
            
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
      
        # Add to dictionary
        dict_this_station[station_name] = gauge_df
        
        
    ###################################################################################
    ###################################################################################
    # Find CEH-GEAR grid cell that point is within
    ###################################################################################
    ##################################################################################
    # Get the data values at this location
    # think the obs cube is only for finding position - hence why its one timeslice
    cehgear_df, closest_point_idx_grid = find_position_obs(obs_cube, lat, lon, station_name)
    
    dict_this_station['CEH-GEAR'] = cehgear_df
    
    ######## Check plotting 
    # Get cube containing one hour worth of data
    hour_uk_cube = obs_cube[0,:,:]
    
    lat_length = obs_cube.shape[1]
    lon_length = obs_cube.shape[2]
    # Create a list of all the tuple positions
    indexs_lst = []
    for i in range(0,lat_length):
        for j in range(0,lon_length):
            # Print the position
            #print(i,j)
            indexs_lst.append((i,j))
    
    # Set all the values to 0
    test_data = np.full((hour_uk_cube.shape),0,dtype = int)
    # Set the values at the index position fond above to 1
    test_data[indexs_lst[closest_point_idx_grid][0],indexs_lst[closest_point_idx_grid][1]] = 1
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
        
    print('Creating plot')
    # Create a colormap
    cmap = matplotlib.colors.ListedColormap(['red'])
    
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
    for closest_point_idx in closest_point_idxs:
        print(closest_point_idx)
        lon, lat = gauge_lons[closest_point_idx],  gauge_lats[closest_point_idx]
        lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
        plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 15)   
    plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Figs/PDF_AwayFromGauges/CellVsRainGaugeLocations/{}.png'.format(plot_num),
                bbox_inches = 'tight')
    
    ############################################################################################################################
    ############################################################################################################################
    # For each gauge, trim the gauge data and the CEH-GEAR data to only cover the overlapping time period
    ############################################################################################################################
    ############################################################################################################################
    # Find earliest/latest time in the CEH-GEAR data
    earliest_time =  cehgear_df['Times'].min() 
    latest_time = cehgear_df['Times'].max() 
           
    # Check if earliest/latest time in any of the gauge data is earlier/later
    for closest_point_idx in closest_point_idxs:
        station_name= station_names[closest_point_idx]
        # Find earliest and latest time amongst gauges
        earliest_time =  dict_this_station[station_name]['Datetime'].min() if dict_this_station[station_name]['Datetime'].min() > earliest_time else earliest_time
        latest_time  =  dict_this_station[station_name]['Datetime'].max() if dict_this_station[station_name]['Datetime'].max() < latest_time  else latest_time 
     
    # Filter to only be between these times - Gauge and CEH-GEAR
    cehgear_df = cehgear_df[(cehgear_df['Times'] >= earliest_time)& (cehgear_df['Times']<= latest_time)]
    dict_this_station['CEH-GEAR'] = cehgear_df
    
    for closest_point_idx in closest_point_idxs:
        station_name= station_names[closest_point_idx]
        gauge_df =dict_this_station[station_name]
        gauge_df = gauge_df[(gauge_df['Datetime'] > earliest_time)& (gauge_df['Datetime']< latest_time)]
        dict_this_station[station_name] = gauge_df
    
    
    ############################################################################
    ############################################################################
    # Plots for individual gauges
    ############################################################################
    ############################################################################
    # Create patches, used for labelling
    patches= []
    patches.append(mpatches.Patch(color='green', label='CEH-GEAR'))
    
    # Define a dictionary of colours
    cols_dict = {'CEH-GEAR' : 'green'}
    cols = ['lightsalmon',  'tomato', 'firebrick']
    i=0
    for closest_point_idx in closest_point_idxs:
        station_name= station_names[closest_point_idx]
        cols_dict[station_name] = cols[i]
        patches.append(mpatches.Patch(color=cols[i], label=station_name))
        i=i+1
                 
    # Set plotting parameters
    x_axis = 'linear'
    y_axis = 'log'
    bin_nos = 20 #(10 gives 12, 30 gives 29, 45 gives 41 bins)
    xlim = False # False lets plot define aprpopriate xlims
    bins_if_log_spaced= bin_nos
    
    numbers_in_each_bin = log_discrete_with_inset(dict_this_station, cols_dict, bin_nos, "Precipitation (mm/hr)", 
                                      patches, True, xlim) 
    plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Figs/PDF_AwayFromGauges/{}.png'.format(plot_num),
                bbox_inches = 'tight')
    
    # Increase counter
    plot_num=plot_num+1
