import numpy as np
from pyproj import Transformer
import itertools
from scipy import spatial
import pandas as pd

def find_rainfall_core(df, duration, Tb0):    

    window_length= int(duration*2)

    df['is_dry'] = df['precipitation (mm)'] < 0.1
    # Calculate the rolling sum of precipitation for each duration length window
    df['Rolling_Sum'] = df['precipitation (mm)'].rolling(window=window_length).sum()

    # Find the index of the maximum total rainfall within a 2-hour window
    max_rainfall_end_index = df['Rolling_Sum'].idxmax()

    # Find the position of max_rainfall_end_index in the DataFrame's index
    max_rainfall_end_pos = df.index.get_loc(max_rainfall_end_index)

    # Calculate the start position of the 2-hour window with the most rainfall
    # This accounts for 3 periods before the max index, as the max index is inclusive
    max_rainfall_start_pos = max(0, max_rainfall_end_pos - window_length)  # Ensure it doesn't go below the DataFrame's range

    # Extract the 2-hour window using iloc
    max_rainfall_window = df.iloc[max_rainfall_start_pos:max_rainfall_end_pos].copy()

    # Check it's one independent event (e.g. doesnt contain a dry period longer than Tb0)
    max_rainfall_window['consecutive_dry'] = 0

    # Start the count of consecutive dry periods
    consecutive_dry_count = 0

    # # Iterate through the DataFrame rows to count consecutive dry periods, excluding the current row
    # max_rainfall_window.reset_index(inplace=True, drop=True)
    for i in range(1, len(max_rainfall_window)):
        if max_rainfall_window.at[max_rainfall_window.first_valid_index()+i - 1, 'is_dry']:
            consecutive_dry_count += 1
        else:
            consecutive_dry_count = 0
        max_rainfall_window.at[max_rainfall_window.first_valid_index()+i, 'consecutive_dry'] = consecutive_dry_count

    if np.nanmax(max_rainfall_window['consecutive_dry'])>Tb0*2:
        print('2 events')
    return max_rainfall_window

def search1(df, max_rainfall_window):
    ######## Backwards
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
        if row_by_position_df['is_dry'].values[0] == False:
            #print('Row is dry. Including it in the window.')
            if row_by_position_df['precipitation (mm)'].values[0]>0.2:
                # If the row is dry, append it to max_rainfall_window
                max_rainfall_window = pd.concat([max_rainfall_window, row_by_position_df], axis=0)
        else:
            #print("Row is wet. Stopping the search.")
            # If the row is wet, stop the search
            break

        # Move to the next row to check
        current_position += 1
    max_rainfall_window

    ######## Forewards
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
        if row_by_position_df['is_dry'].values[0] == False:
            if row_by_position_df['precipitation (mm)'].values[0] >0.2:
                # If the row is dry, append it to max_rainfall_window
                max_rainfall_window = pd.concat([max_rainfall_window, row_by_position_df], axis=0)
            #print('Row is dry. Including it in the window.')
        else:
            # print("Row is wet. Stopping the search.")
            # If the row is wet, stop the search
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

def search3(df, max_rainfall_window):
    
    '''
    Searches for any rainfall values within Tbo of the last rainfall value currently included, 
    and if any of these have a rainfall value >1mm/hr then the intervening values up to the occurrence of this value 
    are included
    '''
    
    #### Backwards search
    start_index = max_rainfall_window.first_valid_index()
    backward_position = start_index - Tb0*2

    while backward_position >= 0:
        backward_slice = df.iloc[backward_position:start_index]
        if (backward_slice['precipitation (mm)'] > 1).any():
            first_true_index = (backward_slice['precipitation (mm)'] > 1).idxmax()
            max_rainfall_window = pd.concat([df.loc[first_true_index:start_index-1], max_rainfall_window], axis=0)
            start_index = first_true_index - Tb0*2  # Update the start index for further searches if needed
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
        condition_met = forward_slice['precipitation (mm)'] > 1
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

def find_independent_events(df, Tb0):
    # Mark periods as dry or not
    df['is_dry'] = df['precipitation (mm)'] < 0.1
    
    ### Flag the dataset to count the number of dry 30-minutes which happened before the one in each row
    # Initialize the column for consecutive dry counts
    df['consecutive_dry'] = 0

    # Start the count of consecutive dry periods
    consecutive_dry_count = 0

    # Iterate through the DataFrame rows to count consecutive dry periods, excluding the current row
    for i in range(1, len(df)):
        if df.at[i - 1, 'is_dry']:
            consecutive_dry_count += 1
        else:
            consecutive_dry_count = 0
        df.at[i, 'consecutive_dry'] = consecutive_dry_count
        
    ### Identify rows marking the start of a rainfall event (i.e. it's raining and the number of consecutive dry days that came 
    ## before it are greater than Tb0)   
    # To identify the start of a new event, check for a shift from dry to wet conditions
    # A new event starts on the first wet period following at least 9 dry hours (18 consecutive dry periods)
    df['starts_after_dry_period'] = (df['consecutive_dry'] >= Tb0*2)

    # Extract indices where a new event starts
    event_start_indices = df.index[df['starts_after_dry_period'] & (~df['is_dry'])].tolist()
    
    ### Use the event start indices to create a set of rainfall events
    # This will end up being a list, which for each rainfall event contains a dictionary detailing key aspects of event
    rainfall_events = []

    # For each event start index
    for start_index in event_start_indices:
        # Take the points which we know to be the start of an event
        # Starting from the next row after this, check through each row until you find the consecutive dry day lengths has 
        # reached Tb0 
        current_index = start_index +1
        # Ensures that we don't keep searching beyond the length of the DF
        while current_index < len(df) - 1 and df.at[current_index, 'consecutive_dry'] < Tb0*2:
            current_index += 1

        # Add this event to the list, including all rows up to (but not including) the row that marks the end
        event_end = current_index if df.at[current_index, 'consecutive_dry'] >= Tb0*2 else len(df)
        event_data = df.iloc[start_index:event_end].copy()
        
        # Remove trailing 0 values
        last_wet_index = event_data[event_data['is_dry'] == False].last_valid_index()
        event_data = event_data.loc[:last_wet_index]  # Use loc to keep original indexing
        
#         last_wet_index = event_data[event_data['is_dry'] == False].last_valid_index()
#         event_data = event_data.iloc[0:last_wet_index+1]
        
        # Store event data
        rainfall_events.append({
            'start_index': start_index,
            'end_index': event_end - 1,  # Adjust if you want to include/exclude the boundary
            'event_data': event_data})
    
    return rainfall_events

def find_max_for_this_duration (rainfall_events, duration):
    
    # to account for each being 30mins
    window_length = duration *2
    
    # to store the outcomes
    max_val = 0
    max_df = pd.DataFrame({})
    
    filtered_events = [event for event in rainfall_events if len(event['event_data']) >= window_length]
    
    # Search each of the independent rainfall events for a maximum value at this duration
    for idx in range(1,len(filtered_events)):

        # Get this independent event
        one_independent_event_df = filtered_events[idx]['event_data']

        # Calculate the rolling sum of precipitation for each X-hour window
        one_independent_event_df['Rolling_Sum'] = one_independent_event_df['precipitation (mm)'].rolling(window=window_length).sum()

        # Find the index of the maximum total rainfall within a X-hour window
        max_rainfall_end_index = one_independent_event_df['Rolling_Sum'].idxmax()

        # Find the position of max_rainfall_end_index in the DataFrame's index
        max_rainfall_end_pos = one_independent_event_df.index.get_loc(max_rainfall_end_index)

        # Calculate the start position of the 2-hour window with the most rainfall
        max_rainfall_start_pos = max(0, max_rainfall_end_pos - window_length-1)  # Ensure it doesn't go below the DataFrame's range

        # Extract the 2-hour window using iloc
        max_rainfall_window = one_independent_event_df.iloc[max_rainfall_start_pos:max_rainfall_end_pos + 1]

        # Display the results
        # print(f"The 2-hour window with the most rainfall ends at {max_rainfall_end_index} and includes:")

        # If the maximum value for this duration in this independent event, is bigger than the biggest one that came before
        # then save these results
        if one_independent_event_df['Rolling_Sum'].max() > max_val:
            max_val = one_independent_event_df['Rolling_Sum'].max()
            max_df = one_independent_event_df
        else:
            pass
    
    
    return max_val, max_df


def find_cornerpoint_coordinates_obs (cube):
    '''
    Description
    ----------
        Using a cube of lat, longs in rotated pole and associated values the function
        creates new 2D lat, lon and data arrays in which the data values are associated
        with a point at the bottom left of each grid cell, rather than the middle.
    Parameters
    ----------
        cube: Iris Cube
            A cube containing only latitude and longitude dimensions
            In rotated pole coordinates so that...are constant..
    Returns
    -------
        lats_wm_midpoints_2d : array
            A 2d array of the mid point latitudes
        lons_wm_midpoints_2d : array
            A 2d array of the mid point longitudes
        
    '''
    
    # Extract lats and longs in rotated pol as a 2D array
    lats_1d = cube.coord('projection_y_coordinate').points
    lons_1d = cube.coord('projection_x_coordinate').points
    
    # Find the distance between each lat/lon and the next lat/lon
    # Divide this by two to get the distance to the half way point
    lats_differences_half = np.diff(lats_1d)/2
    lons_differences_half = np.diff(lons_1d)/2
    
    # Create an array of lats/lons at the midpoints
    lats_midpoints_1d = lats_1d[1:] - lats_differences_half
    lons_midpoints_1d = lons_1d[1:] - lons_differences_half
    
    # Convert to 2D
    lons_midpoints_2d, lats_midpoints_2d = np.meshgrid(lons_midpoints_1d, lats_midpoints_1d)

    # Convert to web mercator
    transformer = Transformer.from_crs("EPSG:27700", "EPSG:3857", always_xy=True)
    lons_wm_midpoints_2d, lats_wm_midpoints_2d = transformer.transform(lons_midpoints_2d, lats_midpoints_2d)
    
    # Convert to 1d     
    lons_wm_midpoints_1d = lons_wm_midpoints_2d.reshape(-1)
    lats_wm_midpoints_1d = lats_wm_midpoints_2d.reshape(-1)
    
    # Remove same parts of data
    data = cube.data
    data_midpoints = data[1:,1:]
    
    return (lats_wm_midpoints_2d, lons_wm_midpoints_2d)

def calculate_bounding_box(latitude, longitude, distance_km):
    # Earth's radius in kilometers
    earth_radius_km = 6371.01

    # Calculate the change in latitude for the given distance
    delta_lat = distance_km / earth_radius_km * (180 / 3.141592653589793)

    # Calculate the change in longitude, adjusting for the latitude
    delta_lon = distance_km / (earth_radius_km * cos(radians(latitude))) * (180 / 3.141592653589793)

    # Calculate bounding box coordinates
    min_lat = latitude - delta_lat
    max_lat = latitude + delta_lat
    min_lon = longitude - delta_lon
    max_lon = longitude + delta_lon

    return min_lat, max_lat, min_lon, max_lon

def create_geodataframe_from_bbox(min_lat, max_lat, min_lon, max_lon):
    # Create a Polygon from the bounding box coordinates
    bbox_polygon = Polygon([(min_lon, min_lat), (min_lon, max_lat), 
                            (max_lon, max_lat), (max_lon, min_lat), 
                            (min_lon, min_lat)])
    
    # Create a GeoDataFrame with the Polygon
    gdf = gpd.GeoDataFrame(index=[0], crs='EPSG:4326', geometry=[bbox_polygon])
    
    return gdf


def find_position_obs (concat_cube, rain_gauge_lat, rain_gauge_lon, plot=False):
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
    indexs_lst = []
    for i in range(0,lat_length):
        for j in range(0,lon_length):
            # Print the position
            #print(i,j)
            indexs_lst.append((i,j))
            
    ######## Check by plotting         
    if plot == True:
        
        # Get cube containing one hour worth of data
        hour_uk_cube = concat_cube

        # Set all the values to 0
        test_data = np.full((hour_uk_cube.shape),0,dtype = int)
        # Set the values at the index position fond above to 1
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
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        lon_rain_gauge_wm, lat_rain_gauge_wm = transformer.transform(rain_gauge_lon,rain_gauge_lat)

        # Create bounding box to centre the map on
        min_lat, max_lat, min_lon, max_lon = calculate_bounding_box(rain_gauge_lat, rain_gauge_lon, distance_km =30)
        gdf_bbox = create_geodataframe_from_bbox(min_lat, max_lat, min_lon, max_lon)
        gdf_bbox_web_mercator = gdf_bbox.to_crs(epsg=3857)

        # Create a colormap
        cmap = matplotlib.colors.ListedColormap(['red'])

    
        fig, ax = plt.subplots(figsize=(15,15))
        extent = tilemapbase.extent_from_frame(gdf_bbox_web_mercator)
        plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
        plot =plotter.plot(ax)
        # # Add edgecolor = 'grey' for lines
        plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
              linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')
        plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
        plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
        #plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
        plt.plot(lon_rain_gauge_wm, lat_rain_gauge_wm, 'o', color='black', markersize = 10)     
        plt.show()

        print(indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1])    
    return locations[closest_point_idx], (indexs_lst[closest_point_idx][0],indexs_lst[closest_point_idx][1])