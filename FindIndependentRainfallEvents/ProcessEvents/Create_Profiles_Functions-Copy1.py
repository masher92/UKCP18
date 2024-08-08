import numpy as np
from scipy.interpolate import interp1d
import pandas as pd

def extract_year(df):
    # Ensure the 'times' column is in datetime format
    df['times'] = pd.to_datetime(df['times'], errors='coerce')  # errors='coerce' will handle invalid parsing
    # Extract the year
    df['year'] = df['times'].dt.year
    return df


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
    problem_events = 0
    
    # Check if the DataFrame is too short to be an event
    if len(df) < 2:
        if verbose:
            print(f"Too short to be an event")
        problem_events += 1
        return None, problem_events

    # Check for more than 30 minute gap between time steps
    if (df['time_since_last_minutes'] > 30).any(): 
        if verbose:
            print(f"More than 30 minute gap between each time step")
        problem_events += 1
        return None, problem_events

    # Check if it contains more than 1 non-zero value in 'precipitation (mm/hr)'
    if not len(df[df['precipitation (mm/hr)'] > 0]) > 2:
        if verbose:
            print(f"Doesn't contain more than 1 value which isn't 0")
        problem_events += 1
        return None, problem_events

    # Check for any NaN values in 'precipitation (mm/hr)'
    if df['precipitation (mm/hr)'].isna().any():
        if verbose:
            print(f"Contains NANs")
        problem_events += 1
        return None, problem_events

    return df, problem_events


def read_event(gauge_num, fp):
    test = pd.read_csv(fp)
    test['timestamp'] = pd.to_datetime(test['times'], errors='coerce')
    test['time_since_last_minutes'] = test['timestamp'].diff().fillna(pd.Timedelta(seconds=0)).dt.total_seconds() / 60#
    # Detect rows where coercion occurred
    invalid_dates = test[test['timestamp'].isna()]

    if not invalid_dates.empty:
        print("Some dates were invalid and have been coerced to NaT:")
        # print(invalid_dates)
    
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

def find_part_with_most_rain_using_cumulative_rainfall(array,n):
    
    array = np.diff(array)
    splits = np.array_split(array, n)
    
    max_array_rainfall = 0
    max_array_num = None
    # Print the resulting splits
    for i, split in enumerate(splits, 1):
        if split.sum() > max_array_rainfall:
            max_array_num = i
            max_array_rainfall = split.sum()
        #print(f"Set {i}: {split}, Length: {len(split)}, Sum: {round(split.sum(),1)}")
    return max_array_num    


def find_part_with_most_rain(array, n, plot=False, ax= False):
    # Compute differences
    # Split the array into 5 equal parts
    splits = np.array_split(array, n)
    
    max_array_rainfall = 0
    max_array_num = None
    
    total_precipitations = []  # To store total precipitation for each split
    split_ranges = []  # To store start and end indices for each split
    
    # Calculate total precipitation for each split
    split_start = 0
    for split in splits:
        total_precipitation = split.sum()
        total_precipitations.append(total_precipitation)
        split_end = split_start + len(split)
        split_ranges.append((split_start, split_end))
        if total_precipitation > max_array_rainfall:
            max_array_num = len(total_precipitations)
            max_array_rainfall = total_precipitation
        split_start = split_end
    
    colors = ['lightblue'] * n  # Default color for all splits
    highlight_color = 'yellow'  # Color for the split with the most rainfall
    
    if plot:
        # Plot the array
        ax.plot(range(1, len(array) + 1), array, label='Precipitation', marker='o')
        
        # Add vertical lines and shading for each split segment
        for i, (start_index, end_index) in enumerate(split_ranges):
            color = highlight_color if (i + 1) == max_array_num else colors[i]
            
            # Add vertical lines at the start and end of each split
            ax.axvline(x=start_index + 1, color=color, linestyle='--', label=f'Split {i+1} Start' if i == 0 or (i + 1) == max_array_num else "")
            ax.axvline(x=end_index, color=color, linestyle='--', label=f'Split {i+1} End' if i == 0 or (i + 1) == max_array_num else "")
            
            # Shade the region for the split
            ax.fill_between(range(start_index + 1, end_index + 1), array[start_index:end_index], color=color, alpha=0.3)
            
            # Add the total precipitation value behind the shading
            ax.text((start_index + end_index) / 2+0.5, max(array) * 0.05,  # Adjust y-position if needed
                    f'{total_precipitations[i]:.2f}',
                    ha='center', va='center', fontsize=10, color='black', weight='bold', zorder=1)
        
        ax.set_title(f'Precipitation Values with Splits Marked. Max at {max_array_num}')
        ax.set_xlabel('Time')
        ax.set_ylabel('Precipitation')

    return max_array_num



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


def interpolate_and_bin(normalized_time, normalized_rainfall, bin_number):
    """
    Interpolate missing data points and bin the dimensionless profile into 12 segments.
    
    Parameters:
        normalized_time (np.array): Normalized time array.
        normalized_rainfall (np.array): Normalized cumulative rainfall array.
    
    Returns:
        np.array: Binned and interpolated rainfall profile.
    """
    # Define target points for 12 bins
    target_points = np.linspace(0, 1, bin_number+1)
    
    # Create interpolation function based on existing data points
    interpolation_func = interp1d(normalized_time, normalized_rainfall, kind='linear', fill_value="extrapolate")
    
    # Interpolate values at target points
    interpolated_values = interpolation_func(target_points)
    
    return interpolated_values