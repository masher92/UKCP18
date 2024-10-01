import numpy as np
from pyproj import Transformer
import itertools
from scipy import spatial
import pandas as pd
import numpy.ma as ma
import math
from shapely.geometry import Point, Polygon, MultiPolygon
import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
# import tilemapbase
from pyproj import Proj, transform
import warnings
import os

def convert_timeformat_array (example_time_coord, array_of_unformatted_times):
    formatted_dates = []
    # Convert each time point and store as a formatted string
    for time_point in array_of_unformatted_times:
        # Convert to datetime using the units of the DimCoord
        converted_time = example_time_coord.units.num2date(time_point)  # Convert to datetime object
        # Format datetime object as a string
        time_string = converted_time.strftime('%Y-%m-%d %H:%M:%S')
        # Append formatted time to the list
        formatted_dates.append(time_string)
    formatted_dates_array = np.array(formatted_dates)    
    return formatted_dates_array


def filtered_cube (cube, filter_above):
    '''
    Set values below 0, or above threshold defined in function input to np.nan
    '''
    cube.data = np.where(cube.data < 0, np.nan, cube.data)
    cube.data = np.where(cube.data > filter_above, np.nan, cube.data)
    return cube 

def create_df_with_gaps_filled_in(cube, data, time_resolution):
    
    # Defined based on resolution on data, used to calculate precip (mm) from precip (mm/hr) which is what the cube reports
    how_many_data_points_per_hour = 60/time_resolution
    
    # Make dataframe
    df_orig = pd.DataFrame({
    'times': cube.coord('time').units.num2date(cube.coord('time').points),
    'precipitation (mm/hr)': data, 'precipitation (mm)': data /how_many_data_points_per_hour })
    
    # Create copy and work with this (to avoid chance that when events with NANs are all set to NAN in df) that this then 
    # affects the original cube
    df = df_orig.copy()

    #############################################
    # Fill in missing values (e.g. some values just dont appear in the .nc files
    # Want these datetimes to still appear, but be recorded as np.nan
    #############################################
    df['times'] = pd.to_datetime([t.isoformat() for t in df['times']])

    # Determine the frequency
    freq = f'{time_resolution}T'  # 30 minutes

    # Create a full date range
    full_time_range = pd.date_range(start=df['times'].min(), end=df['times'].max(), freq=freq)

    # Set 'time' as index and reindex to the full range
    df.set_index('times', inplace=True)
    df = df.reindex(full_time_range)

    # Reset index and rename it back to 'time'
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'times'}, inplace=True)

    return df
                            
def find_gauge_Tb0_and_location_in_grid(tbo_vals, gauge_num, sample_cube):
    gauge1 = tbo_vals.iloc[gauge_num]
    Tb0 = int(gauge1['Critical_interarrival_time'])
    closest_point, idx_2d = find_position_obs(sample_cube, gauge1['Lat'], gauge1['Lon'], plot_radius=10, plot=False)
    return Tb0, idx_2d

def find_amax_indy_events_v2(df, duration, Tb0):
    rainfall_cores = find_rainfall_core(df, duration=duration, Tb0=Tb0)
    rainfall_events_expanded = []

    for rainfall_core in rainfall_cores:
        rainfall_core_after_search1 = search1(df, rainfall_core)
        rainfall_core_after_search2 = search2(df, rainfall_core_after_search1)
        rainfall_core_after_search3 = search3(df, rainfall_core_after_search2, Tb0=Tb0)
        if len(rainfall_core_after_search3[rainfall_core_after_search3['precipitation (mm/hr)'] > 0.1]) > 0:
            rainfall_events_expanded.append(rainfall_core_after_search3)
    
    return rainfall_events_expanded

def search_for_valid_events(df, duration, Tb0):
    # while True means the code will continue to execute until a 'return' statement is reached
    while True:
        # Find potential events
        events_v2 = find_amax_indy_events_v2(df, duration=duration, Tb0=Tb0)
        # Create a flag to record whether this event is valid (e.g. contains no NANs)
        valid_event_found = True

        # Check each event for NaNs, if any are found then valid_event_found set to False, this event is all set to NANs
        # in the original DF and we go back to searching for events
        for event in events_v2:
            if event['precipitation (mm)'].isna().any():
                valid_event_found = False
                print(f"Event contains NAN, total event precip is {event['precipitation (mm)'].sum()}")
                # Mark the event as NaNs in the original DataFrame
                df.loc[event.index, 'precipitation (mm)'] = np.nan
                # break exits the inner loop to restart process of finding events
                break
        
        if valid_event_found:
            print(f"Event doesnt contain NAN, total event precip is {events_v2[0]['precipitation (mm)'].sum()}")
            return events_v2


def find_rainfall_core(df, duration, Tb0):
    """
    Analyzes rainfall data to find the core period of rainfall and checks for independence of the event.
    
    Args:
    df (pd.DataFrame): DataFrame containing precipitation data.
    duration (float): The duration over which to calculate the rolling sum, in hours.
    Tb0 (float): Threshold used to define a 'dry' period for splitting events.
    
    Returns:
    list: A list containing either one or two DataFrames, depending on whether the rainfall event splits.
    """

    ################
    # Find window of dataframe which has max rainfall accumulation for this duration
    ################
    
    # Determine the length of the window based on provided duration
    window_length = int(duration * 2)

    # Identify dry periods based on a precipitation threshold
    df['is_dry'] = df['precipitation (mm/hr)'] < 0.1

    # Calculate the rolling sum of precipitation over the specified window length
    df['Rolling_Sum'] = df['precipitation (mm)'].rolling(window=window_length).sum()

    # Identify the end index of the window where the maximum total rainfall occurs
    max_rainfall_end_index = df['Rolling_Sum'].idxmax()

    # Convert index to a positional integer for slicing
    max_rainfall_end_pos = df.index.get_loc(max_rainfall_end_index)

    # Calculate the start position of the window, ensuring it doesn't go below the DataFrame's range
    max_rainfall_start_pos = max(0, max_rainfall_end_pos - window_length)

    # Extract the window of maximum rainfall from the DataFrame
    max_rainfall_window = df.iloc[max_rainfall_start_pos:max_rainfall_end_pos].copy()

    ################
    # Check whether this is one independent event, or two
    ################
    # Initialize a column to keep track of consecutive dry periods within the window
    max_rainfall_window['consecutive_dry'] = 0

    # Iterate through the rows of the extracted window to count consecutive dry periods
    consecutive_dry_count = 0
    for i in range(len(max_rainfall_window)):
        if max_rainfall_window.iloc[i]['is_dry']:
            consecutive_dry_count += 1
        else:
            consecutive_dry_count = 0
        max_rainfall_window.iloc[i, max_rainfall_window.columns.get_loc('consecutive_dry')] = consecutive_dry_count
    
    # Check if the maximum consecutive dry period exceeds twice the Tb0 threshold
    if np.nanmax(max_rainfall_window['consecutive_dry']) > Tb0 * 2:
        print('2 events')
        split_index = max_rainfall_window[max_rainfall_window['consecutive_dry'] == (Tb0 * 2)].index[0]
        event1 = max_rainfall_window.loc[:split_index]
        event2 = max_rainfall_window.loc[split_index:]
        return [event1, event2]
    else:
        return [max_rainfall_window]

    
def search1(df, max_rainfall_window):
    
    ######## Forewards
    # Find the ending index of max_rainfall_window
    end_index_position = df.index.get_loc(max_rainfall_window.last_valid_index())

    # Initialize a variable to keep track of the current position being checked
    current_position = end_index_position + 1  # Start from the row just after the max_rainfall_window

    # Iterate forward through the DataFrame from the end of the max_rainfall_window
    while current_position < len(df):
        # Get the row at the current position
        row_by_position_df = df.iloc[current_position:current_position+1]
        #print(f"Checking row at position {current_position}:")
        #print(row_by_position_df)

        # Check if the row is dry
        if row_by_position_df['precipitation (mm)'].values[0]>0.2:
            # If the row is dry, append it to max_rainfall_window
            # print("foreward")
            max_rainfall_window = pd.concat([max_rainfall_window, row_by_position_df], axis=0)
        else:
            #print("Row is wet. Stopping the search.")
            # If the row is wet, stop the search
            break

        # Move to the next row to check
        current_position += 1
    max_rainfall_window

    ######## Backwards
    # Find the starting index of max_rainfall_window
    start_index = max_rainfall_window.first_valid_index()

    # Initialize a variable to keep track of the current position being checked
    current_position = start_index - 1  # Start from the row just before the max_rainfall_window

    # Iterate backwards through the DataFrame from the start of the max_rainfall_window
    while current_position >= 0:
        # Get the row at the current position
        row_by_position_df = df.iloc[current_position:current_position+1]
        #print(f"Checking row at position {current_position}:")

        # Check if the row is dry
        if row_by_position_df['precipitation (mm)'].values[0]>0.2:
            # If the row is dry, append it to max_rainfall_window
            max_rainfall_window = pd.concat([row_by_position_df, max_rainfall_window], axis=0)
            #print('Row is dry. Including it in the window.')
        else:
            #print(f"{current_position}, less than 0.2mm/hr, stopping search")
            break

        # Move to the next row to check
        current_position -= 1
    return max_rainfall_window
    

def search2(df, max_rainfall_window):
    #### Foreward search
    # Find the ending index of max_rainfall_window
    end_index_position = df.index.get_loc(max_rainfall_window.last_valid_index())

    # Initialize a variable to keep track of the current position being checked
    current_position = end_index_position + 1  # Start from the row just after the max_rainfall_window

    # Iterate forward through the DataFrame from the end of the max_rainfall_window
    while current_position < len(df):
        # Get the row at the current position
        row_by_position_df = df.iloc[current_position:current_position+2]
        #print(f"Checking row at position {current_position}:")
        #print(row_by_position_df)

        if row_by_position_df['precipitation (mm)'].sum() > 0.4:
            max_rainfall_window = pd.concat([max_rainfall_window, row_by_position_df], axis=0)
        else:
            #print("Row is wet. Stopping the search.")
            # If the row is wet, stop the search
            break

        # Move to the next row to check
        current_position += 2
    
    #### Backward search
    # Find the starting index of max_rainfall_window
    start_index = max_rainfall_window.first_valid_index()

    # Initialize a variable to keep track of the current position being checked
    current_position = start_index - 1  # Start from the row just before the max_rainfall_window

    # Iterate backwards through the DataFrame from the start of the max_rainfall_window
    while current_position >= 0:
        # Get the row at the current position
        row_by_position_df = df.iloc[current_position:current_position+1]
        #print(f"Checking row at position {current_position}:")
        #print(row_by_position_df)

        # Check if the row is dry
        if row_by_position_df['precipitation (mm)'].sum() > 0.4:
            max_rainfall_window = pd.concat([row_by_position_df, max_rainfall_window], axis=0)
            #print('Row is dry. Including it in the window.')
        else:
            # print("Row is wet. Stopping the search.")
            # If the row is wet, stop the search
            break

        # Move to the next row to check
        current_position -= 2    
        
    return max_rainfall_window



def search3(df, max_rainfall_window, Tb0):
    
    '''
    Searches for any rainfall values within Tbo of the last rainfall value currently included, 
    and if any of these have a rainfall value >1mm/hr then the intervening values up to the occurrence of this value 
    are included
    '''
    
    #### Backwards search
    start_index = max_rainfall_window.first_valid_index()
    backward_position = start_index - Tb0*2

    while backward_position >= 0:
        # Get the data in the Tb0 before the start of the event core
        backward_slice = df.iloc[backward_position:start_index]
        # If any values are over 1, then 
        if (backward_slice['precipitation (mm/hr)'] > 1).any():
            # Find the index of the earliest row where this is true (precip mm/hr is over 1)
            first_true_index = (backward_slice['precipitation (mm/hr)'] > 1).idxmax()
            # Join this to the rainfall event 
            max_rainfall_window = pd.concat([df.loc[first_true_index:start_index-1], max_rainfall_window], axis=0)
            # Update the start index for further searches if needed 
            start_index = first_true_index 
            backward_position = start_index - Tb0*2  # Update the backward search position
        else:
            break  # Exit the loop if no such condition is met

    ### Foreward search: from the end of the existing max_rainfall_window
    end_index = max_rainfall_window.last_valid_index()

    while end_index < len(df):
        # Tracks the current position of where the forward search is starting from
        # e.g. (the row afer the max_rainfall_window)
        forward_search_start_position = end_index + 1
        # and ending from (e.g. 2*Tb0 after where it starts)
        forward_search_end_position = min(len(df), forward_search_start_position + (Tb0*2) + 1)  # Define the limit for forward search
        # Get the forward slice
        forward_slice = df.iloc[forward_search_start_position:forward_search_end_position]
        # Check for rows meeting the condition (> 1 mm/hr)
        condition_met = forward_slice['precipitation (mm/hr)'] > 1
        if condition_met.any():
            # Identify the last index where the condition is True
            last_true_index = condition_met[condition_met].index[-1]
            rows_to_add = df.loc[end_index+1:last_true_index]
            max_rainfall_window = pd.concat([max_rainfall_window, rows_to_add], axis=0)
        else:
            break

        # Update the end index
        end_index = max_rainfall_window.last_valid_index()
    
    return max_rainfall_window



def find_position_obs (concat_cube, rain_gauge_lat, rain_gauge_lon, plot_radius = 500, plot=False):
    lat_length = concat_cube.shape[0]
    lon_length = concat_cube.shape[1]
    
    ### Rain gauge data 
    # Convert WGS84 coordinate to BNG
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
    # Use the transformer to convert longitude and latitude to British National Grid coordinates
    rain_gauge_lon_bng, rain_gauge_lat_bng = transformer.transform(rain_gauge_lon, rain_gauge_lat)
    
    # Create as a list
    rain_gauge_point = [('grid_latitude', rain_gauge_lat_bng), ('grid_longitude', rain_gauge_lon_bng)]
                 
    ### Model data
    # Create a list of all the tuple pairs of latitude and longitudes
    locations = list(itertools.product(concat_cube.coord('projection_y_coordinate').points,
                                       concat_cube.coord('projection_x_coordinate').points))
    
    # Find the index of the nearest neighbour of the rain gague location point in the list of locations present in concat_cube
    tree = spatial.KDTree(locations)
    closest_point_idx = tree.query([(rain_gauge_point[0][1], rain_gauge_point[1][1])], k =1)[1][0]
    
    # Create a list of all the tuple positions
    indexs_lst = [(i, j) for i in range(lat_length) for j in range(lon_length)]
    selected_index = indexs_lst[closest_point_idx]
    # print(selected_index)
    
    # Check if the selected index is masked and find a nearby valid index if necessary
    # Define the search order of neighboring cells relative to the original index
    neighbor_offsets = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    # Check if the selected index is masked and find a nearby valid index if necessary
    if np.ma.is_masked(concat_cube[selected_index[0], selected_index[1]].data):
        print("yep its masked")
        found = False
        for di, dj in neighbor_offsets:
            ni, nj = selected_index[0] + di, selected_index[1] + dj
            # Check if the index is within bounds and not masked
            if 0 <= ni < lat_length and 0 <= nj < lon_length and not np.ma.is_masked(concat_cube[ni, nj].data):
                # Update the closest_point_idx and selected_index if a non-masked index is found
                closest_point_idx = indexs_lst.index((ni, nj))
                selected_index = (ni, nj)
                found = True
                print(selected_index)
                break
            # If no unmasked index is found among neighboring cells in the first ring, check the next ring
            neighbor_offsets = [(2, 0), (-2, 0), (0, 2), (0, -2), (2, 2), (-2, 2), (2, -2), (-2, -2)]
            if not found:
                print("No unmasked index found among neighboring cells in the first ring.")
                for di, dj in neighbor_offsets:
                    ni, nj = selected_index[0] + di, selected_index[1] + dj
                    # Check if the index is within bounds and not masked
                    if 0 <= ni < lat_length and 0 <= nj < lon_length and not np.ma.is_masked(concat_cube[ni, nj].data):
                        # Update the closest_point_idx and selected_index if a non-masked index is found
                        closest_point_idx = indexs_lst.index((ni, nj))
                        selected_index = (ni, nj)
                        found = True
                        print(selected_index)
                        break
                # If no unmasked index is found among neighboring cells in the second ring, print a message
                if not found:
                    print("No unmasked index found among neighboring cells in the second ring.")
        
       
    ######## Check by plotting         
    if plot == True:
        
        # Set all the values to 0
        test_data = np.full((concat_cube.shape),0,dtype = int)
        # Set the values at the index position fond above to 1
        test_data[selected_index[0],selected_index[1]] = 1
        # Mask out all values that aren't 1
        test_data = ma.masked_where(test_data<1,test_data)

        # Set the dummy data back on the cube
        concat_cube.data = test_data

        # Find cornerpoint coordinates (for use in plotting)
        lats_cornerpoints =concat_cube.coord('projection_y_coordinate').points
        lons_cornerpoints = concat_cube.coord('projection_x_coordinate').points
        lons_cornerpoints, lats_cornerpoints = np.meshgrid(lons_cornerpoints, lats_cornerpoints)
        # Convert to wgs84
        # Create the transformer
        transformer = Transformer.from_crs(CRS('epsg:27700'), CRS('epsg:3785'))
        # Perform the transformation
        lons_cornerpoints, lats_cornerpoints = transformer.transform(lons_cornerpoints, lats_cornerpoints)
        
        # Trim the data timeslice to be the same dimensions as the corner coordinates
        test_data = concat_cube.data

        # Create location in web mercator for plotting
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        lon_rain_gauge_wm, lat_rain_gauge_wm = transformer.transform(rain_gauge_lon,rain_gauge_lat)

        # Create bounding box to centre the map on
        min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(rain_gauge_lat, rain_gauge_lon, distance_km =plot_radius)
        gdf_bbox = create_geodataframe_from_bbox(min_lat, max_lat, min_lon, max_lon)
        gdf_bbox_web_mercator = gdf_bbox.to_crs(epsg=3857)

        # Create a colormap
        cmap = matplotlib.colors.ListedColormap(['red', 'blue'])

        fig, ax = plt.subplots(figsize=(8,8))
        extent = tilemapbase.extent_from_frame(gdf_bbox_web_mercator)
        plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=200)
        plot =plotter.plot(ax)
        # # Add edgecolor = 'grey' for lines
        plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
              linewidths=0.1, alpha = 1, cmap = cmap, edgecolors = 'grey')
        plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
        plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
        plt.plot(lon_rain_gauge_wm, lat_rain_gauge_wm, 'o', color='black', markersize = 10)     
        
        plt.show()

    return locations[closest_point_idx], (indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1])