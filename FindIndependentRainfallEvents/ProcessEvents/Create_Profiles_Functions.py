import numpy as np
from scipy.interpolate import interp1d
import pandas as pd

def remove_leading_and_trailing_zeroes(df, threshold = 0.005):
    
    # Identify the start and end of the event where values are above the threshold
    event_start = df[df['precipitation (mm)'] >= threshold].index.min()
    event_end = df[df['precipitation (mm)'] >= threshold].index.max()

    # Handle cases where no values are above the threshold
    if pd.isna(event_start) or pd.isna(event_end):
        print("No events found with precipitation >= threshold.")
    else:
        # Remove values < threshold from the start and end of the event
        trimmed_test = df.loc[event_start:event_end].reset_index(drop=True)

    return trimmed_test

def remove_events_with_problems(df, verbose=True):
    
    if len(df) < 2:
        if verbose:
            print(f"Too short to be an event")
            #print(df)
        return None
    if (df['time_since_last_minutes'] > 30).any(): 
        if verbose:
            #print(df)
            print(f"More than 30 minute gap between each time step")
        return None
    if not len(df[df['precipitation (mm/hr)'] > 0]) > 3:
        if verbose:
            #print(test)
            print(f"Doesn't contain more than 1 value which isn't 0")
        return None
    if df['precipitation (mm/hr)'].isna().any():
        if verbose:
            #print(test)
            print(f"Contains NANs")
        return None
    
    return df

def read_event(gauge_num, fp):
    test = pd.read_csv(fp)
    test['timestamp'] = pd.to_datetime(test['times'])
    test['time_since_last_minutes'] = test['timestamp'].diff().fillna(pd.Timedelta(seconds=0)).dt.total_seconds() / 60
    return test

def find_duration(file):
    # Find duration from file name
    pattern = re.compile(r'(\d+\.?\d*)hrs')
    match = pattern.search(file)
    if match:
        duration = match.group(1)
    else:
        duration = None
    return duration

def find_fifth_with_most_rain(array):
    
    array = np.diff(array)
    splits = np.array_split(array, 5)
    
    max_array_rainfall = 0
    max_array_num = None
    # Print the resulting splits
    for i, split in enumerate(splits, 1):
        if split.sum() > max_array_rainfall:
            max_array_num = i
            max_array_rainfall = split.sum()
        #print(f"Set {i}: {split}, Length: {len(split)}, Sum: {round(split.sum(),1)}")
    return max_array_num    


def find_quintile_with_max_cumulative_rainfall(cumulative_rainfall):
    total_rainfall = cumulative_rainfall[-1]  # Total cumulative rainfall at the end
    total_time = len(cumulative_rainfall)  # Total time steps

    # Calculate the time index for each quintile
    quintile_times = np.linspace(0, total_time, 6, dtype=int)  # Divide into 5 equal parts

    # Calculate cumulative rainfall in each quintile
    quintile_rainfall = np.zeros(5)
    for i in range(5):
        start_idx = quintile_times[i]
        end_idx = quintile_times[i + 1] if i < 4 else total_time
        quintile_rainfall[i] = cumulative_rainfall[end_idx - 1] - cumulative_rainfall[start_idx]

    # Find the quintile with the maximum cumulative rainfall
    max_quintile = np.argmax(quintile_rainfall)

    # Return the quintile index (1-indexed)
    return max_quintile + 1


def check_for_nan(profiles_list, normalized_rainfall_ls, dimensionless_profiles_list, durations_for_nimrod_profiles,
                  real_durations_for_nimrod_profiles,volumes_for_nimrod_profiles, max_quintiles_ls, seasons_ls):
    
    new_profiles_ls = []
    new_normalized_rainfall_ls = []
    new_dimensionless_profiles_ls = []
    new_real_durations_ls = []
    new_durations_ls = []
    new_volumes_ls = []
    new_max_quintile_ls = []
    new_seasons_ls = []
    
    for i, profile in enumerate(profiles_list):
        if np.isnan(profile).any():
            print(f"NaN values found in profile {i}")
        else:
            new_profiles_ls.append(profile)
            new_normalized_rainfall_ls.append(normalized_rainfall_ls[i])
            new_dimensionless_profiles_ls.append(dimensionless_profiles_list[i])
            new_durations_ls.append(durations_for_nimrod_profiles[i])
            new_real_durations_ls.append(real_durations_for_nimrod_profiles[i])
            new_volumes_ls.append(volumes_for_nimrod_profiles[i])
            new_max_quintile_ls.append(max_quintiles_ls[i])
            new_seasons_ls.append(seasons_ls[i])
    return new_profiles_ls,new_normalized_rainfall_ls, new_dimensionless_profiles_ls, new_durations_ls, new_real_durations_ls, new_volumes_ls,new_max_quintile_ls, new_seasons_ls

def parse_custom_date(date_str, date_format='%Y-%m-%d %H:%M:%S'):
    """
    Parses a date string and extracts month and day, assuming each month has 30 days.
    """
    try:
        # Split the date and time parts based on the format
        date_part, time_part = date_str.split()
        year, month, day = map(int, date_part.split('-'))
        hour, minute, second = map(int, time_part.split(':'))

        # Ensure the day does not exceed 30
        if day > 30:
            # print(f"Adjusting day {day} to 30 for custom 30-day month calendar.")
            day = 30
        
        return year, month, day, hour, minute, second
    except ValueError as e:
        print(f"Error parsing date: {e}")
        return None

def get_season(date_str, date_format='%Y-%m-%d %H:%M:%S'):
    """
    Determine the season based on custom dates where each month is considered to have 30 days.
    """
    custom_date = parse_custom_date(date_str, date_format)
    if custom_date is None:
        return 'Unknown'
    
    year, month, day, hour, minute, second = custom_date

    # Define the summer period: May 15 to September 30
    if (month == 5 and day >= 15) or (5 < month < 10) or (month == 9 and day <= 30):
        season = 'Summer'
    else:
        season = 'Winter'

    # print(date_str, season)
    return season    

def create_normalised_event(df):
    """
    Create a dimensionless rainfall profile by normalizing the cumulative rainfall 
    and time arrays.
    
    Parameters:
        rainfall_times (np.array): Array of time measurements in any consistent unit.
        rainfall_amounts (np.array): Array of corresponding rainfall amounts.
        
    Returns:
        tuple: Two numpy arrays representing the normalized time and cumulative rainfall.
    """
    
    rainfall_times = np.array(range(0, len(df)))
    rainfall_amounts = np.array(df['precipitation (mm/hr)'])
    
    # Calculate cumulative rainfall
    cumulative_rainfall = np.cumsum(rainfall_amounts)
    
    # Normalize time from 0 to 1
    normalized_time = (rainfall_times - rainfall_times[0]) / (rainfall_times[-1] - rainfall_times[0])
    
    # Normalize cumulative rainfall from 0 to 1
    normalized_rainfall = cumulative_rainfall / cumulative_rainfall[-1]
    
    return normalized_time, normalized_rainfall


def find_heaviest_rainfall_window(rainfall, window_fraction=0.20):
    """
    Find the 20% duration window that concentrates the heaviest rainfall.

    Args:
        rainfall (np.array): Array of rainfall measurements.
        window_fraction (float): Fraction of total duration to consider for the window.

    Returns:
        tuple: The start and end indices of the window with the heaviest rainfall.
    """
    # Calculate cumulative rainfall
    cumulative_rainfall = np.cumsum(rainfall)
    
    # Number of points to include in the window
    window_size = int(len(rainfall) * window_fraction)
    
    # Ensure at least one point is included in the window
    window_size = max(window_size, 1)
    
    # Initialize maximum rainfall increase found and the start index of this window
    max_rainfall_increase = 0
    max_start_index = 0
    
    # Slide the window across the cumulative rainfall data
    for start in range(len(rainfall) - window_size + 1):
        end = start + window_size
        rainfall_increase = cumulative_rainfall[end - 1] - cumulative_rainfall[start]
        
        if rainfall_increase > max_rainfall_increase:
            max_rainfall_increase = rainfall_increase
            max_start_index = start
    
    # Calculate end index based on the start index and window size
    max_end_index = max_start_index + window_size
    
    return max_start_index, max_end_index
    
    
# def categorize_normalized_rainstorm(rainfall, num_segments=5):
#     """
#     Categorize a normalized cumulative rainstorm by which 20% segment 
#     of the duration concentrates the heaviest rainfall.
    
#     Args:
#         rainfall (np.array): Array of normalized cumulative rainfall.
#         num_segments (int): Number of equal segments to divide the duration, 
#                             default is 5 for 20% segments.
    
#     Returns:
#         int: The segment number (1-indexed) with the heaviest rainfall concentration.
#     """
#     # Determine the number of points per segment
#     points_per_segment = len(rainfall) // num_segments
#     max_rainfall_increase = 0
#     heaviest_segment = 0
    
#     # Iterate over each segment to find the one with the maximum rainfall increase
#     for i in range(num_segments):
#         start_index = i * points_per_segment
#         # Handle the last segment differently to include any remaining points
#         if i == num_segments - 1:
#             end_index = len(rainfall)
#         else:
#             end_index = start_index + points_per_segment
        
#         if start_index == 0:
#             segment_rainfall_increase = rainfall[end_index - 1]
#         else:
#             segment_rainfall_increase = rainfall[end_index - 1] - rainfall[start_index - 1]
        
#         if segment_rainfall_increase > max_rainfall_increase:
#             max_rainfall_increase = segment_rainfall_increase
#             heaviest_segment = i + 1  # 1-indexed segment number
    
#     return heaviest_segment

def categorize_normalized_rainstorm(rainfall, num_segments=5):
    """
    Categorize a normalized cumulative rainstorm by which 20% segment 
    of the duration concentrates the heaviest rainfall.
    
    Args:
        rainfall (np.array): Array of normalized cumulative rainfall.
        num_segments (int): Number of equal segments to divide the duration, 
                            default is 5 for 20% segments.
    
    Returns:
        int: The segment number (1-indexed) with the heaviest rainfall concentration.
    """
    points_per_segment = len(rainfall) // num_segments
    max_rainfall_increase = 0
    heaviest_segment = 0
    
    for i in range(num_segments):
        start_index = i * points_per_segment
        end_index = len(rainfall) if i == num_segments - 1 else start_index + points_per_segment
        
        if start_index == 0:
            segment_rainfall_increase = rainfall[end_index - 1]
        else:
            segment_rainfall_increase = rainfall[end_index - 1] - rainfall[start_index - 1]
        
        if segment_rainfall_increase > max_rainfall_increase:
            max_rainfall_increase = segment_rainfall_increase
            heaviest_segment = i
    
    return heaviest_segment

def interpolate_and_bin(normalized_time, normalized_rainfall):
    """
    Interpolate missing data points and bin the dimensionless profile into 12 segments.
    
    Parameters:
        normalized_time (np.array): Normalized time array.
        normalized_rainfall (np.array): Normalized cumulative rainfall array.
    
    Returns:
        np.array: Binned and interpolated rainfall profile.
    """
    # Define target points for 12 bins
    target_points = np.linspace(0, 1, 13)
    
    # Create interpolation function based on existing data points
    interpolation_func = interp1d(normalized_time, normalized_rainfall, kind='linear', fill_value="extrapolate")
    
    # Interpolate values at target points
    interpolated_values = interpolation_func(target_points)
    
    return interpolated_values