import numpy as np
import datetime
import pandas as pd

def calculate_R(theta):
    """
    Calculate theta (angle in radians) and R (resultant length) for a series of dates.

    Parameters:
    - dates: Pandas Series of datetime objects (e.g., dates of events)

    Returns:
    - theta: Numpy array of angles (in radians) for each date
    - R: The resultant length (measure of how clustered the dates are)
    """

    # Calculate Cartesian coordinates (x, y) on the unit circle
    x = np.cos(theta)
    y = np.sin(theta)

    # Calculate the mean of x and y
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    # Calculate the resultant length R, which represents the dispersion
    R = np.sqrt(x_mean**2 + y_mean**2)
    # Return theta and the resultant length R
    return R

def date_from_D(D, year=2020):
    # Create a date object for January 1st of the given year
    jan_1st = datetime.date(year, 1, 1)
    
    # Add D-1 days to January 1st to get the corresponding date
    result_date = jan_1st + datetime.timedelta(days=D-1)
    
    return result_date

def get_season(date):
    """
    Returns the season for a given date.
    
    Parameters:
    date (datetime): A datetime object representing the date.

    Returns:
    str: The season (Winter, Spring, Summer, or Autumn).
    """
    year = date.year
    # Define the start of each season
    spring = datetime.date(year, 3, 21)
    summer = datetime.date(year, 6, 21)
    autumn = datetime.date(year, 9, 23)
    winter = datetime.date(year, 12, 21)
    
    if date >= winter or date < spring:
        return 'Winter'
    elif spring <= date < summer:
        return 'Spring'
    elif summer <= date < autumn:
        return 'Summer'
    else:
        return 'Autumn'
    
def group_data_calc_means(df, d50_variable, group_by_vars):
    
    # Grouping the dataframe by the specified variables
    grouped = df.groupby(group_by_vars)

    # Define a list to hold results
    results = []

    # Iterate through each group
    for group_keys, group in grouped:
        # If group_keys is a tuple, unpack it based on the number of group-by variables
        if len(group_by_vars) == 1:
            group_keys = (group_keys,)  # Make it a tuple if only one grouping variable
        
        # Calculate R (assuming calculate_R is a defined function)
        R = calculate_R(group['theta'])

        # Calculate the percentage of events where 'loading_profile_molly' == 'F2'
        total_events = len(group)  # Total number of events in the group
        F2_events = len(group[group['Loading_profile_molly'] == 'F2'])  # Number of 'F2' events
        F2_percentage = (F2_events / total_events) * 100 if total_events > 0 else 0  # Percentage of 'F2' events
        
        B2_events = len(group[group['Loading_profile_molly'] == 'B2'])  # Number of 'F2' events
        B2_percentage = (B2_events / total_events) * 100 if total_events > 0 else 0  # Percentage of 'F2' events        

        # Store the mean of theta, R, and other statistics in the results list for each group
        results.append({
            **dict(zip(group_by_vars, group_keys)),  # Unpack the group keys into the result dictionary
            'theta_mean': np.mean(group['theta']),  # Mean theta for the group
            'D_mean': np.mean(group['D']),          # Mean of D for the group
            'R': R,                                 # R value for the group
            'D50_mean': np.mean(group[d50_variable]),      # Mean of D50 for the group
            'D50_P90': np.percentile(group[d50_variable], 90),
            'D50_P10': np.percentile(group[d50_variable], 10),
            'D50_median': np.median(group[d50_variable]),  # Median of D50 for the group
            'F2_percentage': F2_percentage,           # Percentage of 'F2' events
            'B2_percentage': B2_percentage           # Percentage of 'F2' events
        })

    # Convert the results list into a DataFrame
    return pd.DataFrame(results)


def find_change_values_in_groups_new(grouped, group_by_columns, sampling_duration):
    group_by_columns_copy = group_by_columns.copy()
    group_by_columns_copy.remove('Climate')
    # Split the dataframe into present and future data
    df_present = grouped[grouped['Climate'] == 'Present'].copy()
    df_future = grouped[grouped['Climate'] == 'Future'].copy()

    # Rename columns for clarity when merging
    df_present = df_present.rename(columns={
        'theta_mean': 'theta_mean_present',
        'D_mean': 'D_mean_present',
        'R': 'R_present',
        'D50_mean': 'D50_mean_present',
        'D50_median': 'D50_median_present',
        'D50_P90': 'D50_P90_present',
        'D50_P10': 'D50_P10_present',    
        'F2_percentage': 'F2_percentage_present',   
        'B2_percentage': 'B2_percentage_present',   
    })

    df_future = df_future.rename(columns={
        'theta_mean': 'theta_mean_future',
        'D_mean': 'D_mean_future',
        'R': 'R_future',
        'D50_mean': 'D50_mean_future',
        'D50_median': 'D50_median_future',
        'D50_P90': 'D50_P90_future',
        'D50_P10': 'D50_P10_future',      
        'F2_percentage': 'F2_percentage_future',  
        'B2_percentage': 'B2_percentage_future',           
    })

    merged_df = pd.merge(df_present, df_future, 
                         on=group_by_columns_copy, 
                         how='outer',  # Use 'outer' for an outer join
                         suffixes=('_present', '_future'))
    
    # Calculate the differences between present and future values
    merged_df['theta_mean_diff'] = merged_df['theta_mean_future'] - merged_df['theta_mean_present']
    merged_df['D_mean_diff'] = merged_df['D_mean_future'] - merged_df['D_mean_present']
    merged_df['R_diff'] = merged_df['R_future'] - merged_df['R_present']
    merged_df['D50_mean_diff'] = merged_df['D50_mean_future'] - merged_df['D50_mean_present']
    merged_df['D50_median_diff'] = merged_df['D50_median_future'] - merged_df['D50_median_present']
    merged_df['D50_P90_diff'] = merged_df['D50_P90_future'] - merged_df['D50_P90_present']
    merged_df['D50_P10_diff'] = merged_df['D50_P10_future'] - merged_df['D50_P10_present']    
    merged_df['F2_percentage_diff'] = merged_df['F2_percentage_future'] - merged_df['F2_percentage_present']    
    merged_df['B2_percentage_diff'] = merged_df['B2_percentage_future'] - merged_df['B2_percentage_present']      
    merged_df.drop(['Climate_present', 'Climate_future'], axis=1, inplace=True)
    
    merged_df['sampling_duration'] = sampling_duration
    
    return merged_df