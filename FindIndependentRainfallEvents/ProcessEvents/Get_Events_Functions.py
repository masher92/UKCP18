import numpy as np
from scipy.interpolate import interp1d
import pandas as pd


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


def add_duration_cats_predetermined(df):
    '''
    Based on categories determined by RVH in order to have same number of events in each category.
    '''
    # Define the bin edges and labels
    if df is None:
        return None
    else:
        bin_edges = [0.25, 2.10, 6.45, 19.25, np.max(df['duration'].dropna())]
        duration_labels = ['0.25-2.10 hr', '2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']

        # Ensure 'duration' column is treated as numeric, coerce errors to NaN
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

        # Bin durations into categories based on bin_edges
        df['DurationRange_notpersonalised'] = pd.cut(df['duration'], 
                                                    bins=bin_edges, 
                                                    labels=duration_labels, 
                                                    right=True,
                                                    include_lowest=True)

    return df

def add_duration_cats_based_on_all_ems(df):
    '''
    Based on categories determined by RVH in order to have same number of events in each category.
    '''
    # Define the bin edges and labels
    if df is None:
        return None
    else:
        bin_edges = [1.5, 5.0, 11.5, 22.5, 166.5]
        duration_labels = ['0.25-2.10 hr', '2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']

        # Ensure 'duration' column is treated as numeric, coerce errors to NaN
        df['duration'] = pd.to_numeric(df['duration'], errors='coerce')

        # Bin durations into categories based on bin_edges
        df['DurationRange_personalised_allems'] = pd.cut(df['duration'], 
                                                    bins=bin_edges, 
                                                    labels=duration_labels, 
                                                    right=True,
                                                    include_lowest=True)

    return df


def add_duration_cats_based_on_data(df):
    '''
    Uses the dataframe to work out which categories would give same number of events in each category
    '''
    # Now, if you also want to create quartile categories based on the index, similar to the previous logic:
    df = df.sort_values(by='duration')
    df.reset_index(inplace=True, drop=True)

    # Calculate the number of events in each quartile
    total_events = len(df)
    events_per_quartile = total_events // 4

    # Assign quartile categories based on index position
    df['DurationCategory'] = pd.cut(df.index,
                                      bins=[-1, events_per_quartile, 2 * events_per_quartile, 3 * events_per_quartile, total_events],
                                      labels=['Q1', 'Q2', 'Q3', 'Q4'], include_lowest=True)
    grouped = df.groupby('DurationCategory')['duration']
    quartile_ranges = grouped.agg(['min', 'max'])

    # Create a new column with labels for quartile ranges
    df['DurationRange_personalised'] = df['DurationCategory'].map(quartile_ranges.apply(lambda x: f'{x["min"]:.1f}-{x["max"]:.1f}', axis=1))
    return df