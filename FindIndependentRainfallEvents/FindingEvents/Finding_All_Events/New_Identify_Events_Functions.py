import numpy as np

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

            # Add this event to the list, including all rows up to (but not including) the row that marks the end
            event_data = df.iloc[start_index:event_end].copy()
            
def find_top_rainfall_events(rainfall_events, aggregation_window=2):
    # Calculate total rainfall over the specified aggregation window for each event
    aggregation_size = int(aggregation_window / 0.5)  # Convert hours to time steps
    event_totals = []

    for event_data, event_time_points in rainfall_events:
        # Sum rainfall over the specified time window
        summed_rainfall = np.convolve(event_data, np.ones(aggregation_size), mode='valid')
        max_rainfall = summed_rainfall.max() if summed_rainfall.size > 0 else 0
        event_totals.append((max_rainfall, event_data, event_time_points))

    # Sort events by the maximum rainfall in descending order and take the top 40
    top_events = sorted(event_totals, key=lambda x: x[0], reverse=True)[:40]

    return top_events            

            # Remove trailing 0 values
            #last_wet_index = event_data[event_data['is_dry'] == False].last_valid_index()
            #event_data = event_data.loc[:last_wet_index]  # Use loc to keep original indexing

#             # Store event data
#             rainfall_events.append({
#                 'start_index': start_index,
#                 'end_index': event_data.index[-1],  # Adjust if you want to include/exclude the boundary
#                 'event_data': event_data})            
            

    # Step 6: Output the results
    print(f"Number of independent rainfall events: {len(rainfall_events)}")
    
#     for idx, event in enumerate(rainfall_events):
#         event['event_data'].reset_index(inplace=True)
#         start_time = event['event_data'].iloc[0]['Time']
#         end_time = event['event_data'].iloc[-1]['Time']
#         total_rainfall = event['event_data']['precipitation (mm/hr)'].sum()
#         print(f"Event {idx + 1}: from {start_time} to {end_time}, total rainfall = {total_rainfall:.2f} mm")

#     return rainfall_events


def my_find_independent_events(precip_data, time_coord, Tb0, dry_threshold=0.1):
    # Step 3: Identify the dry periods (where rainfall <= dry_threshold)
    dry_periods = precip_data < dry_threshold

    # Step 4: Find consecutive dry periods of at least 11 hours
    dry_window_size = int(Tb0 / 0.5)  # Assuming 30-minute time steps
    dry_window_size = int(Tb0 * 2) 
    
    # Find dry intervals of at least 11 consecutive hours (dry_window_size time steps)
    dry_intervals = np.convolve(dry_periods, np.ones(dry_window_size, dtype=int), mode='same') == dry_window_size
    dry_intervals = np.convolve(dry_periods, np.ones(dry_window_size, dtype=int), mode='same') == dry_window_size


    # Step 5: Group non-dry periods into rainfall events
    rainfall_events = []
    start_index = None

    for i in range(len(precip_data)):
        if not dry_periods[i] == True:  # If it's a wet time step
            if start_index is None:
                start_index = i  # Mark the start of a rainfall event
        elif start_index is not None and dry_intervals[i]:  # If it's dry and long enough to be independent
            # End the event and store it
            event_data = precip_data[start_index:i]
            event_time_points = time_coord.points[start_index:i]
#             # Trim trailing zeros from event_data
#             last_wet_index = np.max(np.nonzero(event_data)) if np.any(event_data) else -1
            
#             if last_wet_index >= 0:
#                 event_data = event_data[:last_wet_index + 1]
#                 event_time_points = event_time_points[:last_wet_index + 1]

            rainfall_events.append((event_data, event_time_points))
            start_index = None  # Reset start index for the next event

    # If there's a rainfall event that extends to the last time step
    if start_index is not None:
        event_data = precip_data[start_index:]
        event_time_points = time_coord.points[start_index:]

        # Trim trailing zeros
       # last_wet_index = np.max(np.nonzero(event_data >= dry_threshold)) if np.any(event_data >= dry_threshold) else -1
#         last_wet_index = np.max(np.nonzero(event_data)) if np.any(event_data) else -1
        
        #if last_wet_index >= 0:
        #    event_data = event_data[:last_wet_index + 1]
        #    event_time_points = event_time_points[:last_wet_index + 1]

        rainfall_events.append((event_data, event_time_points))
        
    # Step 6: Output the results
    print(f"Number of independent rainfall events: {len(rainfall_events)}")
#     for idx, (event_data, event_times) in enumerate(rainfall_events):
#         start_time = time_coord.units.num2date(event_times[0])
#         end_time = time_coord.units.num2date(event_times[-1])
#         print(f"Event {idx + 1}: from {start_time} to {end_time}, total rainfall = {event_data.sum()} mm")

    return rainfall_events