import numpy as np
import datetime
import pandas as pd

def calc_mean_day_and_dispersion(theta):
    
    x = np.cos(theta)
    y = np.sin(theta)

    x_mean = np.mean(x)
    y_mean = np.mean(y)
    
    if x_mean <= 0:
        D_mean = (np.arctan(y_mean/x_mean) + np.pi) * 365.25/(2*np.pi)
    elif x_mean > 0 and y_mean >= 0:
        D_mean = np.arctan(y_mean/x_mean) * 365.25/(2*np.pi)
    elif x_mean > 0 and y_mean < 0:
        D_mean = (np.arctan(y_mean/x_mean) + 2*np.pi) * 365.25/(2*np.pi)
    
    R = np.sqrt(x_mean**2 + y_mean**2)

    return D_mean, R

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
    # Group the dataframe by the specified variables
    grouped = df.groupby(group_by_vars)
    results = []

    for group_keys, group in grouped:
        # Ensure group_keys is a tuple for consistency
        group_keys = (group_keys,) if isinstance(group_keys, str) else group_keys
        
        # Calculate mean day and dispersion
        D_mean, R = calc_mean_day_and_dispersion(group['theta'])
        total_events = len(group)
        
        # Calculate percentages for each loading profile type
        profile_counts = group['Loading_profile_molly'].value_counts(normalize=True) * 100
        F2_percentage = profile_counts.get('F2', 0)
        B2_percentage = profile_counts.get('B2', 0)
        C_percentage = profile_counts.get('C', 0)
        F1_percentage = profile_counts.get('F1', 0)
        B1_percentage = profile_counts.get('B1', 0)

        # Collect all statistics for each group
        results.append({
            **dict(zip(group_by_vars, group_keys)),
            'D_mean': D_mean,
            'R': R,
            'D50_mean': group[d50_variable].mean(),
            'D50_P90': group[d50_variable].quantile(0.9),
            'D50_P10': group[d50_variable].quantile(0.1),
            'D50_median': group[d50_variable].median(),
            'F2_percentage': F2_percentage,
            'B2_percentage': B2_percentage,
            'C_percentage': C_percentage,
            'F1_percentage': F1_percentage,
            'B1_percentage': B1_percentage
        })

    return pd.DataFrame(results)

def circular_day_difference(present_day, future_day):
    # Compute the circular difference
    circular_diff = ((future_day - present_day + 182.625) % 365.25) - 182.625
    return circular_diff

def find_change_values_in_groups_new(grouped_df, group_by_columns, sampling_duration):
    group_by_columns_no_climate = [col for col in group_by_columns if col != 'Climate']
    
    # Split data into present and future, renaming columns
    present_df = grouped_df[grouped_df['Climate'] == 'Present'].copy().rename(columns=lambda x: x + '_present' if x not in group_by_columns_no_climate else x)
    future_df = grouped_df[grouped_df['Climate'] == 'Future'].copy().rename(columns=lambda x: x + '_future' if x not in group_by_columns_no_climate else x)

    # Merge present and future data on common columns
    merged_df = pd.merge(present_df, future_df, on=group_by_columns_no_climate, how='outer', suffixes=('_present', '_future'))
    print(merged_df.columns)
    # Calculate differences between present and future values
    for metric in ['R', 'D50_mean', 'D50_median', 'D50_P90', 'D50_P10', 'F2_percentage', 'B2_percentage', 'C_percentage', 'F1_percentage', 'B1_percentage']:
        merged_df[f'{metric}_diff'] = merged_df[f'{metric}_future'] - merged_df[f'{metric}_present']
    
    merged_df['sampling_duration'] = sampling_duration

    # Step 2: Apply the function to the DataFrame columns and create a new column
    merged_df['D_mean_diff'] = merged_df.apply(
        lambda row: circular_day_difference(row['D_mean_present'], row['D_mean_future']), axis=1)
    
    return merged_df.drop(columns=['Climate_present', 'Climate_future'], errors='ignore')


# def find_change_values_in_groups_new(grouped_df, group_by_columns, sampling_duration):
#     group_by_columns_no_climate = [col for col in group_by_columns if col != 'Climate']
    
#     # Split data into present and future, renaming columns
#     present_df = grouped_df[grouped_df['Climate'] == 'Present'].copy().rename(columns=lambda x: x + '_present' if x not in group_by_columns_no_climate else x)
#     future_df = grouped_df[grouped_df['Climate'] == 'Future'].copy().rename(columns=lambda x: x + '_future' if x not in group_by_columns_no_climate else x)

#     # Merge present and future data on common columns
#     merged_df = pd.merge(present_df, future_df, on=group_by_columns_no_climate, how='outer', suffixes=('_present', '_future'))

#     # Calculate differences between present and future values
#     for metric in ['D_mean', 'R', 'D50_mean', 'D50_median', 'D50_P90', 'D50_P10', 'F2_percentage', 'B2_percentage', 'C_percentage', 'F1_percentage', 'B1_percentage']:
#         merged_df[f'{metric}_diff'] = merged_df[f'{metric}_future'] - merged_df[f'{metric}_present']
    
#     merged_df['sampling_duration'] = sampling_duration

#     return merged_df.drop(columns=['Climate_present', 'Climate_future'], errors='ignore')