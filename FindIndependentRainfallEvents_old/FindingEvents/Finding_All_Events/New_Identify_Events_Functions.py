import numpy as np
from datetime import datetime
import cftime

def convert_timeformat_array(time_coord, time_points):
    """
    Convert time points from Iris time coordinates to human-readable datetime format.
    
    Parameters:
    - time_coord: The time coordinate from the Iris cube (e.g., cube.coord('time'))
    - time_points: The array of numerical time points to be converted (e.g., time_coord.points)
    
    Returns:
    - A list of human-readable datetime strings corresponding to the time points.
    """
    # Get the units and calendar from the time coordinate
    time_unit = time_coord.units
    calendar = time_coord.units.calendar
    
    # Convert the time points to datetime objects
    datetimes = [cftime.num2date(time, time_unit.origin, calendar) for time in time_points]
    
    # Format the datetimes into human-readable strings (e.g., YYYY-MM-DD HH:MM:SS)
    formatted_times = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in datetimes]
    
    return formatted_times


def remove_leading_and_trailing_values(arr, threshold=0.1):
    """
    Remove leading and trailing values less than the threshold from a numpy array.
    
    Parameters:
    - arr: numpy array of precipitation values.
    - threshold: Values below this threshold will be considered for removal at the front and end of the array.
    
    Returns:
    - A numpy array with leading and trailing values less than the threshold removed.
    """
    # Remove leading values below the threshold
    start_idx = 0
    while start_idx < len(arr) and arr[start_idx] < threshold:
        start_idx += 1
    
    # Remove trailing values below the threshold
    end_idx = len(arr)
    while end_idx > start_idx and arr[end_idx - 1] < threshold:
        end_idx -= 1
    
    return arr[start_idx:end_idx]

def trim_arrays(precip_arr, time_arr, threshold=0.05):
    """
    Remove leading and trailing values less than the threshold from a precipitation array and its corresponding time array.
    
    Parameters:
    - precip_arr: numpy array of precipitation values.
    - time_arr: numpy array of corresponding time values.
    - threshold: Values below this threshold will be considered for removal at the front and end of the precipitation array.
    
    Returns:
    - Tuple of (trimmed_precip_array, trimmed_time_array)
    """
    # Ensure both arrays are of the same length
    if len(precip_arr) != len(time_arr):
        raise ValueError("Precipitation and time arrays must be the same length.")

    # Remove leading values below the threshold
    start_idx = 0
    while start_idx < len(precip_arr) and precip_arr[start_idx] < threshold:
        start_idx += 1
    
    # Remove trailing values below the threshold
    end_idx = len(precip_arr)
    while end_idx > start_idx and precip_arr[end_idx - 1] < threshold:
        end_idx -= 1
    
    # Trim both arrays
    trimmed_precip_array = precip_arr[start_idx:end_idx]
    trimmed_time_array = time_arr[start_idx:end_idx]
    
    return trimmed_precip_array, trimmed_time_array

def my_find_independent_events(precip_data, time_coord, Tb0, dry_threshold=0.05):
    # Create a boolean array identifying dry periods (where rainfall <= dry_threshold)
    is_timestep_dry = precip_data < dry_threshold

    # Convert Tb0 to represent the number of 30-minute time steps
    dry_window_size = int(Tb0 * 2) 
    
    # Create a boolean array which identifies which timesteps are in the middle of a period
    # of length 'dry_window_size', which are all dry (according to is_timestep_dry)
    # count = np.convolve(is_timestep_dry, np.ones(dry_window_size, dtype=int), mode='same') 
    
    # the convolution operation effectively counts how many "True" (1) values exist within a sliding window
    # centered at each row (time step). The size of the window is defined by dry_window_size.
    is_timestep_in_a_dry_interval = np.convolve(is_timestep_dry, np.ones(dry_window_size, dtype=int), mode='same') == dry_window_size

    # Group non-dry periods into rainfall events
    rainfall_events = []
    start_index = None

    # For each row in the precipitation data,
    for i in range(len(precip_data)):
         
        # If it's a wet time step, then record this as the start of an event, and move to the next row
        # This means whilst its raining, we will keep moving through the time steps
        if is_timestep_dry[i] == False:
            if start_index is None:
                # Mark the start of a rainfall event
                start_index = i  
        
        # If we encounter a dry time step, but we're not currently inside an event then we pass over it
        # but don't need to specify this explicitly
        # elif start_index is not None:
        #    pass
        
        # If we encounter a dry time step, AND we already are within an event, but we're not within
        # a sufficiently long dry spell for this dry timestep to end the event, then we pass over
        # this time step to the next one.
        # but don't need to specify this explicitly
        # elif start_index is None and is_timestep_in_a_dry_interval[i] == False:  
        #    pass
        
        # Once we get to a dry time step, AND we already are within an event, 
        # AND we're within a sufficiently long dry spell for us to decide the event has ended 
        # THEN: end the event and store it, and reset start_index, so we start recording a new
        # event at the next wet time step
        elif start_index is not None and is_timestep_in_a_dry_interval[i] == True:  
            event_data = precip_data[start_index:i]
            event_time_points = time_coord[start_index:i]
            event_times = convert_timeformat_array(time_coord[0],event_time_points.points)
            
            # Trim leading and trailing zeroes
            event_data, event_times = trim_arrays(event_data, event_times)
            
            rainfall_events.append((event_data, event_times))
            # Reset start index for the next event
            start_index = None  

    # If there's a rainfall event that extends to the last time step
    # We know this because we've gone thru all rows by now, but if the event in progress
    # had ended, or we weren't within an event, then start_index would now be set to None
    if start_index is not None:
        event_data = precip_data[start_index:]
        event_time_points = time_coord.points[start_index:]
        rainfall_events.append((event_data, event_time_points))
        
    # Output the results
    # print(f"Number of independent rainfall events: {len(rainfall_events)}")
    
    return rainfall_events

def find_independent_events(df, Tb0):
    # Mark periods as dry or not
    df['is_dry'] = df['precipitation (mm/hr)'] < 0.1

    # Initialize the column for consecutive dry counts
    df['consecutive_dry'] = 0
    consecutive_dry_count = 0

    for i in range(1, len(df)):
        if df.at[i - 1, 'is_dry']:
            consecutive_dry_count += 1
        else:
            consecutive_dry_count = 0
        df.at[i, 'consecutive_dry'] = consecutive_dry_count

    df['starts_after_dry_period'] = (df['consecutive_dry'] >= Tb0 * 2)
    event_start_indices = df.index[df['starts_after_dry_period'] & (~df['is_dry'])].tolist()
    rainfall_events = []
            
    for start_index in event_start_indices:
        # Current index records the row that we are considering to be the end of the dataframe
        # So set it to be the next row, and check if this (next) row should be included 
        end_index = start_index + 1

        # If it's not the last timeslice
        if start_index != df.index[-1]:
            # Searches through each of the next rows, until it either reaches the end fo the dataframe
            # or the row with a consecutive_dry which is >= Tb0*2
            while end_index < len(df) - 1 and df.at[end_index, 'consecutive_dry'] < Tb0*2:
                end_index = end_index + 1
            # Not sure why we need this line
            event_end = end_index if df.at[end_index, 'consecutive_dry'] >= (Tb0*2) else len(df)

            # Add this event to the list, including all rows up to (but not including) the row marking the end
            event_data = df.iloc[start_index:event_end].copy()
            
def find_top_n_events_for_duration(rainfall_events, n_events, duration_in_hrs):
    # Account for the data being in 30 minute chunks (Convert hours to time steps)
    aggregation_size = int(duration_in_hrs *2)  
    
    # Create a list to store the size of each event
    event_totals = []
    
    # Loop thru events
    for event_data, event_time_points in rainfall_events:
        event_data_mm =event_data/2
        # Sum rainfall over the specified time window
        summed_rainfall = np.convolve(event_data_mm, np.ones(aggregation_size), mode='valid')
        max_rainfall = summed_rainfall.max() if summed_rainfall.size > 0 else 0
        event_totals.append((max_rainfall, event_data_mm, event_time_points))

    # Sort events by the maximum rainfall in descending order and take the top 40
    top_events = sorted(event_totals, key=lambda x: x[0], reverse=True)[:n_events]

    return top_events      