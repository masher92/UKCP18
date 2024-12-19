import os 
import numpy as np
import pandas as pd
import re
from scipy.interpolate import interp1d
import sys
from shapely.geometry import Point
import geopandas as gpd
import pickle

sys.path.insert(1, 'Old')
from Steef_Functions import *

quintile_mapping = {1: 'F2', 2: 'F1', 3: 'C', 4: 'B1', 5: 'B2'}
quintile_mapping_thirds = {1: 'F', 2: 'C', 3: 'B'}

def remove_leading_and_trailing_zeroes(df, fp, threshold = 0.05):
    
    # Identify the start and end of the event where values are above the threshold
    event_start = df[df['precipitation (mm)'] >= threshold].index.min()
    event_end = df[df['precipitation (mm)'] >= threshold].index.max()

    # Handle cases where no values are above the threshold
    if pd.isna(event_start) or pd.isna(event_end):
        print(df)
        print(fp)
        print("No events found with precipitation >= threshold.")
    else:
        # Remove values < threshold from the start and end of the event
        trimmed_test = df.loc[event_start:event_end].reset_index(drop=True)

    return trimmed_test


def check_for_gauge_in_areas(tbo_vals,home_dir, areas):
    """
    Check if each row of the DataFrame with 'Lat' and 'Lon' falls within the shapefiles of multiple areas.
    
    Parameters:
    - tbo_vals: DataFrame containing 'Lat' and 'Lon' columns for the gauges.
    - areas: List of area names corresponding to shapefiles (e.g., ['NW', 'NE', 'C', 'SE', 'SW']).
    
    Returns:
    - DataFrame with additional columns indicating if the gauge is within each area,
      and a column specifying which areas it belongs to.
    """
    
    # Create a GeoDataFrame from the DataFrame
    geometry = [Point(xy) for xy in zip(tbo_vals['Lon'], tbo_vals['Lat'])]
    geo_df = gpd.GeoDataFrame(tbo_vals, geometry=geometry)
    
    # Set the CRS for the GeoDataFrame using the new syntax
    geo_df.crs = "EPSG:4326"
    
    # Loop through each area and check if the points are within the shapefile
    for area_name in areas:
        # Read the shapefile for the area
        shape = gpd.read_file(home_dir + f'datadir/SpatialData/RoughExtremeRainfallRegions/{area_name}.shp')
        
        # Ensure the CRS of the shapefile matches the GeoDataFrame
        if shape.crs != geo_df.crs:
            shape = shape.to_crs(geo_df.crs)
        
        # Perform the spatial check to see if points are within the shapefile area
        geo_df[f'within_{area_name}'] = geo_df.within(shape.unary_union)
    
    # Create a column to specify which areas the point belongs to
    geo_df['within_area'] = geo_df[[f'within_{area}' for area in areas]].apply(
        lambda x: ', '.join([area for area in areas if x[f'within_{area}']]), axis=1
    )

    return geo_df


def read_event(gauge_num, fp):
    test = pd.read_csv(fp)
    test['timestamp'] = pd.to_datetime(test['times'], errors='coerce')
    test['time_since_last_minutes'] = test['timestamp'].diff().fillna(pd.Timedelta(seconds=0)).dt.total_seconds() / 60#
    # Detect rows where coercion occurred
    invalid_dates = test[test['timestamp'].isna()]

    if not invalid_dates.empty:
        pass
        #print("Some dates were invalid and have been coerced to NaT:")
        # print(invalid_dates)
    
    return test


def process_events_alltogether(home_dir, time_period, ems, tb0_vals, save_dir):
    events_dict = {}
    event_props_ls = []
    event_profiles_dict = {}

    for em in ems:
        for gauge_num in range(0, 1294):
            if gauge_num not in [444, 827, 888]:
                if gauge_num % 100 == 0:
                    print(f"Processing gauge {gauge_num}")
                indy_events_fp = home_dir + f"ProcessedData/IndependentEvents/UKCP18_30mins/{em}/{gauge_num}/WholeYear/"

                files = [f for f in os.listdir(indy_events_fp) if f.endswith('.csv')]
                files = np.sort(files)

                for event_num, file in enumerate(files):
                    fp = indy_events_fp + f"{file}"
                    if '2080' in fp:
                        continue
                    # Get event
                    this_event = read_event(gauge_num, fp)

                    # Get times and precipitation values
                    event_times = this_event['times']
                    event_precip = this_event['precipitation (mm)']

                    # Apply the function to adjust the dates in the 'times' column
                    event_times_fixed = event_times.apply(adjust_feb_dates)

                    # Create the DataFrame with corrected times
                    event_df = pd.DataFrame({'precipitation (mm)': event_precip, 'times': event_times_fixed})
                    # Remove leading and trailing zeroes
                    event_df = remove_leading_and_trailing_zeroes(event_df, indy_events_fp + f"{file}")
                    # Create characteristics dictionary
                    event_props = create_event_characteristics_dict(event_df)

                    # Add the duration
                    event_props['dur_for_which_this_is_amax'] = get_dur_for_which_this_is_amax(fp)
                    # Add gauge number and ensemble member
                    event_props['gauge_num'] = gauge_num
                    event_props['area'] = tb0_vals.iloc[gauge_num]['within_area']
                    event_props['em'] = em
                    event_props['filename'] = file
                    
                    event_props["max_precip"] =np.max(event_precip)
                    event_props["mean_precip"]= np.mean(event_precip)

                    ##########################################
                    # Specify the keys you want to check
                    keys_to_check = ['duration', 'year', 'gauge_num', 'month', 'Volume', 'max_intensity']

                    # Extract the values for the specified keys from dict_to_check
                    values_to_check = tuple(event_props[key] for key in keys_to_check)

                    # Initialize a variable to store the found dictionary
                    matched_dict = None

                    # Check if a matching dictionary exists in the list based on the specified keys
                    for index, d in enumerate(event_props_ls):
                        if tuple(d[key] for key in keys_to_check) == values_to_check:
                            matched_dict = d  # Store the matching dictionary
                            break  # Exit the loop since we found a match

                    if matched_dict:

                        ### Add duration
                        new_value = event_props['dur_for_which_this_is_amax']
                        existing_value = matched_dict.get('dur_for_which_this_is_amax', '')
                        # Create or update the value as a list
                        if isinstance(existing_value, list):
                            existing_value.append(new_value)
                        else:
                            existing_value = [existing_value, new_value]  # Convert existing string to list and add 'yes'
                        matched_dict['dur_for_which_this_is_amax'] = existing_value

                        ### Add filepath
                        new_value_fp = event_props['filename']
                        existing_value_fp = matched_dict.get('filename', '')

                        # Create or update the value as a list
                        if isinstance(existing_value_fp, list):
                            existing_value_fp.append(new_value_fp)
                        else:
                            existing_value_fp = [existing_value_fp, new_value_fp]  # Convert existing string to list and add 'yes'
                        matched_dict['filename'] = existing_value_fp

                        event_props_ls[index]= matched_dict

                    else:
                        # print("No matching dictionary found in the list.")

                        ##########################################
                        events_dict[f"{em}, {gauge_num}, {event_num}"] = event_df
                        event_props_ls.append(event_props)
                        event_profiles_dict[f"{em}, {gauge_num}, {event_num}"] = create_profiles_dict(event_df)
        
        with open(save_dir + f"ProcessedData/AMAX_Events/UKCP18_30mins/{time_period}/events_dict_{em}_NEW.pickle", 'wb') as handle:
            pickle.dump(events_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(save_dir + f"ProcessedData/AMAX_Events/UKCP18_30mins/{time_period}/event_profiles_dict_{em}_NEW.pickle", 'wb') as handle:
            pickle.dump(event_profiles_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

        with open(save_dir + f"ProcessedData/AMAX_Events/UKCP18_30mins/{time_period}/event_props_dict_{em}_NEW.pickle", 'wb') as handle:
            pickle.dump(event_props_ls, handle, protocol=pickle.HIGHEST_PROTOCOL)                       

    return events_dict, event_props_ls, event_profiles_dict                  

    return events_dict, event_props_ls, event_profiles_dict


def calc_d50_with_interpolation(sample):
    n=5
    cumulative_rainfall, cumulative_rainfall_times = create_cumulative_event(sample)
    dimensionless_cumulative_rainfall, dimensionless_times =  create_dimensionless_event(cumulative_rainfall, cumulative_rainfall_times)
    interpolated_n_cumulative_rainfall, interpolated_n_times = interpolate_rainfall(dimensionless_cumulative_rainfall,n)
    interpolated_n_incremental_rainfall = create_incremental_event(interpolated_n_cumulative_rainfall)
    max_quintile_profile = find_part_with_most_rain(interpolated_n_incremental_rainfall, n)
    
    percentile = 0.5
    
    time_percentage = (np.arange(0, len(sample) + 1) / len(sample)) * 100
    
    # Find the indices where the cumulative rainfall crosses the percentile_value
    indices_below = np.where(dimensionless_cumulative_rainfall < percentile)[0]
    indices_above = np.where(dimensionless_cumulative_rainfall >= percentile)[0]

    # Ensure there are indices both below and above the percentile value
    if len(indices_below) > 0 and len(indices_above) > 0:
        index_below = indices_below[-1]  # Last index below the percentile value
        index_above = indices_above[0]    # First index above the percentile value

        # Perform linear interpolation to find the exact intersection point
        x_below = time_percentage[index_below]
        y_below = dimensionless_cumulative_rainfall[index_below]

        x_above = time_percentage[index_above]
        y_above = dimensionless_cumulative_rainfall[index_above]

        # Calculate the slope
        slope = (y_above - y_below) / (x_above - x_below)
        # Use the formula to find the exact x value where the y value equals percentile_value
        time_for_percentile = x_below + (percentile - y_below) / slope

        return time_for_percentile

def process_events_alltogether_nimrod(home_dir, tb0_vals):
    events_dict = {}
    event_props_ls = []
    event_profiles_dict = {}

    for gauge_num in range(0, 1293):
        if gauge_num not in [444, 827, 888]:
            if gauge_num % 100 == 0:
                print(f"Processing gauge {gauge_num}")
            indy_events_fp = home_dir + f"ProcessedData/IndependentEvents/NIMROD_30mins/NIMROD_2.2km_filtered_100/{gauge_num}/WholeYear/"
            files = [f for f in os.listdir(indy_events_fp) if f.endswith('.csv')]
            files = np.sort(files)

            for event_num, file in enumerate(files):
                fp = indy_events_fp + f"{file}"
                if '2080' in fp:
                    continue

                # Get event
                this_event = read_event(gauge_num, fp)

                # Get times and precipitation values
                event_times = this_event['times']
                event_precip = this_event['precipitation (mm)']

                # Apply the function to adjust the dates in the 'times' column
                event_times_fixed = event_times.apply(adjust_feb_dates)

                # Create the DataFrame with corrected times
                event_df = pd.DataFrame({'precipitation (mm)': event_precip, 'times': event_times_fixed})
                event_df = remove_leading_and_trailing_zeroes(event_df)

                # Create characteristics dictionary
                event_props = create_event_characteristics_dict(event_df)

                # Add the duration
                event_props['dur_for_which_this_is_amax'] = get_dur_for_which_this_is_amax(fp)
                # Add gauge number and ensemble member
                event_props['gauge_num'] = gauge_num
                event_props['area'] = tb0_vals.iloc[gauge_num]['within_area']
                event_props['em'] = 'nimrod'
                event_props['filename'] = file

                ##########################################
                # Specify the keys you want to check
                keys_to_check = ['duration', 'year', 'gauge_num', 'month', 'Volume', 'max_intensity']

                # Extract the values for the specified keys from dict_to_check
                values_to_check = tuple(event_props[key] for key in keys_to_check)

                # Initialize a variable to store the found dictionary
                matched_dict = None

                # Check if a matching dictionary exists in the list based on the specified keys
                for index, d in enumerate(event_props_ls):
                    if tuple(d[key] for key in keys_to_check) == values_to_check:
                        matched_dict = d  # Store the matching dictionary
                        break  # Exit the loop since we found a match

                if matched_dict:
                    # print("A matching dictionary found:", matched_dict, event_props)

                    new_value = event_props['dur_for_which_this_is_amax']
                    existing_value = matched_dict.get('dur_for_which_this_is_amax', '')
                    # Create or update the value as a list
                    if isinstance(existing_value, list):
                        existing_value.append(new_value)
                    else:
                        existing_value = [existing_value, new_value]  # Convert existing string to list and add 'yes'
                    matched_dict['dur_for_which_this_is_amax'] = existing_value

                    event_props_ls[index]= matched_dict

                else:
                    # print("No matching dictionary found in the list.")
                    events_dict[f"nimrod, {gauge_num}, {event_num}"] = event_df
                    event_props_ls.append(event_props)
                    event_profiles_dict[f"nimrod, {gauge_num}, {event_num}"] = create_profiles_dict(event_df)

    
    print(f"Finished {em}")                        
        
    with open(home_dir + f"ProcessedData/AMAX_Events/NIMROD_30mins/events_dict_nimrod.pickle", 'wb') as handle:
        pickle.dump(events_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(home_dir + f"ProcessedData/AMAX_Events/NIMROD_30mins/event_profiles_dict_nimrod", 'wb') as handle:
        pickle.dump(event_profiles_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    with open(home_dir + f"ProcessedData/AMAX_Events/NIMROD_30mins/event_props_dict_nimrod.pickle", 'wb') as handle:
        pickle.dump(event_props_ls, handle, protocol=pickle.HIGHEST_PROTOCOL)  
    
    return events_dict, event_props_ls, event_profiles_dict



def calculate_storm_center_of_mass(event_df):
    """
    Calculate the center of mass of a rainstorm.
    
    Parameters:
    - event_df: A DataFrame containing 'times' and 'precipitation (mm)' columns.
    
    Returns:
    - Center of mass of the rainstorm (Cm), a value between 0 and 1.
    """
    # Calculate the time differences relative to the start of the storm
    event_df['time_diff'] = (event_df['times'] - event_df['times'].min()).dt.total_seconds() / 3600
    
    # Calculate the total storm duration in hours
    total_duration = len(event_df['time_diff'])/2
    # print(total_duration)

    # Normalize the time differences to get values between 0 and 1
    event_df['normalized_time'] = event_df['time_diff'] / total_duration
    
    # Calculate total rainfall
    total_rainfall = event_df['precipitation (mm)'].sum()
    
    # Calculate the center of mass (Cm)
    Cm = (event_df['precipitation (mm)'] * event_df['normalized_time']).sum() / total_rainfall
    
#     print(total_rainfall)
#     print(event_df)
    return Cm


def find_theta(event_df):
    D =  event_df["times"].dt.dayofyear[0]
    theta = D*2*np.pi/365.25
    return theta

def create_event_characteristics_dict(this_event):
    
    max_quintile_molly=find_max_quintile(this_event['precipitation (mm)'],5)
    max_third_molly=find_max_quintile(this_event['precipitation (mm)'],3)
    max_quintile_steef=analyse_event(this_event['precipitation (mm)'])[0]
    duration = len(this_event) / 2
    DurationRange_personalised_allems = find_dur_category([1.5, 5.0, 11.5, 22.5, 166.5], ['0.25-2.10 hr', '2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr'], duration)
    DurationRange_simple = find_dur_category([0, 4.0, 12, 166.5], ['<4hr', '4-12hr', '12hr+'], duration)
    
    DurationRange_notpersonalised = find_dur_category([0.25, 2.10, 6.45, 19.25, 1000], 
                                                      ['0.25-2.10 hr', '2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr'], duration)
    d50, d50_index, cumulative_precip =calculate_D50(this_event['precipitation (mm)'])
    d50_new = calc_d50_with_interpolation(this_event['precipitation (mm)'])
    
    
    return {
        "season" : get_season(this_event['times'][0]),
        'duration':duration,
        "DurationRange_personalised_allems": DurationRange_personalised_allems,
        'DurationRange_notpersonalised':DurationRange_notpersonalised,
        'DurationRange_simple':DurationRange_simple,
        "year":extract_year(this_event),
        "month":get_month(this_event),
        'Volume': sum(this_event['precipitation (mm)'].values),
        'max_intensity': this_event['precipitation (mm)'].max() *2,
        "max_quintile_molly":max_quintile_molly,
        "max_third_molly": max_third_molly,
        'max_quintile_steef' :max_quintile_steef,
        'Loading_profile_molly' :quintile_mapping[max_quintile_molly],
        'Loading_profile_third_molly':quintile_mapping_thirds[max_third_molly],
        'Loading_profile_steef':quintile_mapping[max_quintile_steef],
        'D50_index': d50_index,
        'theta': find_theta(this_event),
        'D50': d50,
        'D50_new':d50_new,
        'com':calculate_storm_center_of_mass(this_event)}

def find_max_quintile (precip, n):
    # Difference with this to Huff curve function, is it doesnt normalise
    cumulative_rainfall, cumulative_rainfall_times = create_cumulative_event(precip)
    dimensionless_cumulative_rainfall, dimensionless_times =  create_dimensionless_event(cumulative_rainfall, cumulative_rainfall_times)
    interpolated_n_cumulative_rainfall, interpolated_n_times = interpolate_rainfall(dimensionless_cumulative_rainfall,n)
    interpolated_n_incremental_rainfall = create_incremental_event(interpolated_n_cumulative_rainfall)
    max_quintile_profile = find_part_with_most_rain(interpolated_n_incremental_rainfall, n)
    
    return max_quintile_profile 


def create_cumulative_event(rainfall, interval=0.5):
    
    # Calculate cumulative rainfall
    cumulative_rainfall = np.cumsum(rainfall)
    cumulative_rainfall = [0] + cumulative_rainfall
    
    # Generate corresponding time points
    time_points = np.arange(0, len(rainfall) + 1) * interval
    
    return  [0] + cumulative_rainfall.tolist(), time_points.tolist()


def create_dimensionless_event(cumulative_rainfall, cumulative_rainfall_times):
    # Normalize the cumulative rainfall by the total event depth
    total_event_depth = cumulative_rainfall[-1]
    normalized_cumulative_rainfall = np.array(cumulative_rainfall) / total_event_depth

    # Normalize the cumulative rainfall times by the total event time
    total_event_time = cumulative_rainfall_times[-1]
    normalized_cumulative_rainfall_times = np.array(cumulative_rainfall_times) / total_event_time
    
    return normalized_cumulative_rainfall, normalized_cumulative_rainfall_times

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


def create_huff_curves(precip):
    cumulative_rainfall, cumulative_rainfall_times = create_cumulative_event(precip)
    dimensionless_cumulative_rainfall, dimensionless_times =  create_dimensionless_event(cumulative_rainfall, cumulative_rainfall_times)
    return dimensionless_cumulative_rainfall, dimensionless_times

def create_incremental_event(cumulative_rainfall):
    if cumulative_rainfall is None :
        return None
    raw_rainfall = np.diff(cumulative_rainfall, prepend=0)
    return raw_rainfall[1:]

# def find_max_quintile (precip):
#     if precip is None:
#         return None
#     else:
#         cumulative_rainfall, cumulative_rainfall_times = create_cumulative_event(precip)
#         dimensionless_cumulative_rainfall, dimensionless_times =  create_dimensionless_event(cumulative_rainfall, cumulative_rainfall_times)
#         interpolated5_cumulative_rainfall, interpolated5_times = interpolate_rainfall(dimensionless_cumulative_rainfall,5)
#         interpolated5_incremental_rainfall = create_incremental_event(interpolated5_cumulative_rainfall)
#         max_quintile_profile_5 = find_part_with_most_rain(interpolated5_incremental_rainfall, 5)
#         return max_quintile_profile_5

def find_intensity_as_proportion_of_mean_event(incremental_rainfall):
    mean_over_event = np.mean(incremental_rainfall)
    irain = incremental_rainfall/np.mean(incremental_rainfall)
    return irain

def create_irain_profile(interpolated_cumulative_rainfall, leading_trailing_zeros):
    interpolated_incremental_rainfall = create_incremental_event(interpolated_cumulative_rainfall)
    irain = find_intensity_as_proportion_of_mean_event(interpolated_incremental_rainfall)
    
    # Add extra 0/1 to start and end
    len_intensity = len(irain)  
    if leading_trailing_zeros == True:
        irain = np.append([0], irain)
        irain = np.append(irain, [0]) 
    
        # Also edit the times
        times = np.hstack((np.array([0.0]),(np.arange(len_intensity) + 0.5) / len_intensity,
                np.array([1.0])))
    else:
        times = np.arange(len_intensity) + 0.5 / len_intensity        
    
    return irain, times

def find_part_with_most_rain(array, n, plot=False, ax=False):

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



def find_dur_category (bin_edges, duration_labels, duration):
    # Create a pandas Series with the duration
    # Use pd.cut to assign the duration to a bin
    binned_duration = pd.cut(pd.Series([duration]), bins=bin_edges, labels=duration_labels, right=True,  include_lowest=True)
    return binned_duration.iloc[0]

def get_month (df):
    # Step 2: Calculate the median (middle value)
    median_time = df['times'].median()

    # Step 3: Extract the month from the median value
    median_month = median_time.month

    # Convert month number to month name (optional)
    month_name = median_time.strftime('%B')

    return median_month

def calculate_D50(precipitation_values):
    """
    Calculate D50, the point in time when 50% of cumulative precipitation has occurred during an event.
    
    Parameters:
    - precipitation_values: A list or array of precipitation values for a given event.
    
    Returns:
    - D50: The percentage of the event elapsed when 50% of cumulative precipitation has occurred.
    - D50_index: The index where 50% of cumulative precipitation has occurred.
    - cumulative_precip: The cumulative precipitation values for the event.
    """
    # Ensure input is a numpy array
    if len(precipitation_values) ==1:
        return np.nan, np.nan, np.array(precipitation_values)
    
    precipitation_values = np.array(precipitation_values)
    
    # Step 1: Calculate the cumulative precipitation
    cumulative_precip = np.cumsum(precipitation_values)
    
    # Step 2: Determine the total precipitation
    total_precip = cumulative_precip[-1]
    
    # Step 3: Find the index where 50% of the total precipitation is reached
    halfway_precip = total_precip / 2.0
    D50_index = np.where(cumulative_precip >= halfway_precip)[0][0]  # First index where cumulative precipitation >= 50%
    
    # Step 4: Calculate the percentage of the event duration (D50)
    total_timesteps = len(precipitation_values)
    D50 = (D50_index / (total_timesteps - 1)) * 100

    return D50, D50_index, cumulative_precip

def create_profiles_dict(this_event):
    dimensionless_cumulative_rainfall, dimensionless_cumulative_times = create_huff_curves(this_event['precipitation (mm)'])
    interpolated_cumulative_rainfall, interpolated_times = interpolate_rainfall(dimensionless_cumulative_rainfall,12)
    irain_14vals, irain_times_14vals = create_irain_profile(interpolated_cumulative_rainfall, True)
    irain, irain_times = create_irain_profile(interpolated_cumulative_rainfall, False)
    return {
        "dimensionless_cumulative_rainfall" : dimensionless_cumulative_rainfall,
        'dimensionless_cumulative_times':dimensionless_cumulative_times,
        "interpolated_cumulative_rainfall": interpolated_cumulative_rainfall,
        'interpolated_times':interpolated_times,
        "irain_14vals":irain_14vals,
        'irain_times_14vals': irain_times_14vals,
        "irain":irain,
        "irain_times": irain_times} 

def get_dur_for_which_this_is_amax(file):
    match = re.search(r'(\d+(\.\d+)?)hrs', file)

    # Extract and print the result if a match is found
    if match:
        extracted_value = match.group(1)
        return extracted_value
    
def adjust_feb_dates(datetime_str):
    try:
        # Split the string into date and time parts (assuming standard format)
        date_part, time_part = datetime_str.split(' ')
        year, month, day = map(int, date_part.split('-'))
        
        # Check if it's February and the day is invalid (29th or 30th)
        if month == 2 and day in [29, 30]:
            # Return the date as February 28th, keeping the time part intact
            return f'{year}-02-28 {time_part}'
        
        # Return the original datetime string if valid
        return datetime_str
    except:
        # In case of unexpected formats or errors, return the original string
        return datetime_str    
    
    
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
           
        

def extract_year(df):
    # Ensure the 'times' column is in datetime format
    df['times'] = pd.to_datetime(df['times'], errors='coerce')  # errors='coerce' will handle invalid parsing
    # Extract the year
    return df['times'].dt.year[0]            