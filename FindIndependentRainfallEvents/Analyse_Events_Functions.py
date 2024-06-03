import numpy as np
from scipy.interpolate import interp1d


def create_dimensionless_profile(rainfall_times, rainfall_amounts):
    """
    Create a dimensionless rainfall profile by normalizing the cumulative rainfall 
    and time arrays.
    
    Parameters:
        rainfall_times (np.array): Array of time measurements in any consistent unit.
        rainfall_amounts (np.array): Array of corresponding rainfall amounts.
        
    Returns:
        tuple: Two numpy arrays representing the normalized time and cumulative rainfall.
    """
    # Calculate cumulative rainfall
    cumulative_rainfall = np.cumsum(rainfall_amounts)
    
    # Normalize time from 0 to 1
    normalized_time = (rainfall_times - rainfall_times[0]) / (rainfall_times[-1] - rainfall_times[0])
    
    # Normalize cumulative rainfall from 0 to 1
    normalized_rainfall = cumulative_rainfall / cumulative_rainfall[-1]
    
    return normalized_time, normalized_rainfall


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
    target_points = np.linspace(0, 1, 12)
    
    # Create interpolation function based on existing data points
    interpolation_func = interp1d(normalized_time, normalized_rainfall, kind='linear', fill_value="extrapolate")
    
    # Interpolate values at target points
    interpolated_values = interpolation_func(target_points)
    
    return interpolated_values

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