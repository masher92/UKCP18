import numpy as np
from scipy.interpolate import interp1d
import pandas as pd

def interpolate_rainfall(rainfall, bin_number):
    if rainfall is None or len(rainfall) < 2:
        return None

    # Define target points for bin_number bins
    target_points = np.linspace(0, 1, bin_number+1)
    
    # Create interpolation function based on existing data points
    rainfall_times = np.array(range(0, len(rainfall)))

    # Normalize time from 0 to 1
    normalized_time = (rainfall_times - rainfall_times[0]) / (rainfall_times[-1] - rainfall_times[0])
    interpolation_func = interp1d(normalized_time, rainfall, kind='linear', fill_value="extrapolate")
    
    # Interpolate values at target points
    interpolated_values = interpolation_func(target_points)
    
    return interpolated_values, target_points

def create_cumulative_event(rainfall, interval=0.5):

    # Calculate cumulative rainfall
    cumulative_rainfall = np.cumsum(rainfall)
    cumulative_rainfall = [0] + cumulative_rainfall
    
    # Generate corresponding time points
    time_points = np.arange(0, len(rainfall) + 1) * interval
    
    return  [0] + cumulative_rainfall.tolist(), time_points.tolist()

def find_intensity_as_proportion_of_mean_event(incremental_rainfall):
    mean_over_event = np.mean(incremental_rainfall)
    irain = incremental_rainfall/np.mean(incremental_rainfall)
    return irain

def create_incremental_event(cumulative_rainfall):
    if cumulative_rainfall is None :
        return None
    raw_rainfall = np.diff(cumulative_rainfall, prepend=0)
    return raw_rainfall[1:]

def find_max_quintile (precip):
    if precip is None:
        return None
    else:
        cumulative_rainfall, cumulative_rainfall_times = create_cumulative_event(precip)
        dimensionless_cumulative_rainfall, dimensionless_times =  create_normalised_event(cumulative_rainfall, cumulative_rainfall_times)
        interpolated5_cumulative_rainfall, interpolated5_times = interpolate_rainfall(dimensionless_cumulative_rainfall,5)
        interpolated5_incremental_rainfall = create_incremental_event(interpolated5_cumulative_rainfall)
        max_quintile_profile_5 = find_part_with_most_rain(interpolated5_incremental_rainfall, 5)
        return max_quintile_profile_5
    
    
def create_irain_profile(precip, bins =12 ):
    cumulative_rainfall, cumulative_rainfall_times = create_cumulative_event(precip)
    dimensionless_cumulative_rainfall, dimensionless_times =  create_dimensionless_event(cumulative_rainfall, cumulative_rainfall_times)
    interpolated_cumulative_rainfall, interpolated_times = interpolate_rainfall(dimensionless_cumulative_rainfall,bins)
    interpolated_incremental_rainfall = create_incremental_event(interpolated_cumulative_rainfall)

    irain = find_intensity_as_proportion_of_mean_event(interpolated_incremental_rainfall)
    irain = np.append([0], irain)
    irain = np.append(irain, [0])    
    
    len_intensity = len(irain)
    # Time points: start of event, end of event, midpoint of the intervals
    times = np.hstack((np.array([0.0]),
            (np.arange(len_intensity) + 0.5) / len_intensity,
            np.array([1.0])))
    
    return irain

################# Steef functions
def get_normalised_intensity(array_in, len_out):
    len_in = len(array_in)
    # Calculates the total accumulated value at each original point
    # Adds a zero at the start of the array
    csum = np.cumsum(np.hstack((np.array([0.0]), array_in)))
    # Normalise accumulation to 0 to 1
    csum = csum / csum[-1]
    # Array going from 0 up to 1: normalised time
    # corresponding to these points
    normalised_time_in = np.arange(len_in + 1) / (1.0 * len_in)
    # Array of the "time points" corresponding to
    # Boundaries of output intervals
    normalised_time_out = np.arange(len_out + 1) / (1.0 * len_out)
    # Interpolate total accumulated value to desired output points
    csum_out = np.interp(normalised_time_out, normalised_time_in, csum)
    # Interpolate back to accumulations over the desired number of intervals
    # Scale with the number of points to normalise
    normalised_intensity = (csum_out[1:] - csum_out[:-1]) * len_out
    return normalised_intensity

def analyse_event(array_in):
    # Remove leading/trailing zeros from array
    # can we always do this?
    trimmed_array = np.trim_zeros(array_in)
    # Go from raw data directly to 12 and 5 points
    event_curve_12 = get_normalised_intensity(trimmed_array, 12)
    event_curve_12 = np.append([0], event_curve_12)
    event_curve_12 = np.append(event_curve_12, [0])    
    
    event_curve_5 = get_normalised_intensity(trimmed_array, 5)
    # Get the category as a number from 1 to 5
    # add 1 as python indexing starts at 0
    category = np.argmax(event_curve_5) + 1
    return category