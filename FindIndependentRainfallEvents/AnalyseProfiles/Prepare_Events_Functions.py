import numpy as np
import pandas as pd
import matplotlib.pyplot as plt    
import pickle

def is_multiple_of_5(lst):
    return len(lst) % 5 == 0

# Function definition
def amalgamate_loadings(value):
    # print(f"Processing value: {value}")
    if value == 'F2' or value == 'F1':
        return 'F'
    elif value == 'B2' or value == 'B1':
        return 'B'
    else:
        return 'C'

def extract_year(df):
    if df is not None and 'times' in df.columns:
        df['times'] = pd.to_datetime(df['times'], errors='coerce')
        return df['times'].dt.year.iloc[0]
    return None

def read_and_format_events (filepath, n, quintile_mapping, quintile_cats):

    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_trimmed_events.pkl", 'rb') as f:
        trimmed_events = pickle.load(f)    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_normalised_interpolated_events.pkl", 'rb') as f:
        profiles = pickle.load(f)    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_raw_events.pkl", 'rb') as f:
        raw_events = pickle.load(f)    
        
    # # ### Create dataframe
    precip_values = [df['precipitation (mm/hr)'].tolist() if df is not None else None for df in raw_events]
    precip_sums = [sum(precip_list) if precip_list is not None else 0 for precip_list in precip_values]
    seasons_summary = [get_season(extract_first_date(df)) if df is not None else None for df in raw_events]
    years = [extract_year(df) for df in raw_events]
    trimmed_events = pd.DataFrame({'precipitation (mm/hr)': precip_values, 'Season':seasons_summary, 'Volume':precip_sums,
                                  'Profile':profiles, 'Year':years})

    # Add the durations
    trimmed_events['duration'] = trimmed_events['precipitation (mm/hr)'].apply(lambda x: len(x) / 2 if x is not None else None)

    trimmed_events = add_duration_cats_based_on_data(trimmed_events)
    trimmed_events = add_duration_cats_predetermined(trimmed_events)
    # Add the max quintile
    trimmed_events['max_quintile'] = trimmed_events['precipitation (mm/hr)'].apply(lambda x: find_part_with_most_rain(x, n) if x is not None else None)

    # Add the loadings
    trimmed_events['Loading'] = trimmed_events['max_quintile'].map(quintile_mapping)
    trimmed_events['Loading'] = pd.Categorical(trimmed_events['Loading'], categories=quintile_cats, ordered=True)

    
    return trimmed_events
    
    

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

# from Analyse_Events_Functions import *
def find_part_with_most_rain(array, n, plot=False):
    # Compute differences
    # Split the array into 5 equal parts
    splits = np.array_split(array, n)
    
    max_array_rainfall = 0
    max_array_num = None
    
    # Find the fifth with the most rainfall
    for i, split in enumerate(splits, 1):
        if split.sum() > max_array_rainfall:
            max_array_num = i
            max_array_rainfall = split.sum()
            
    if plot ==True:
        # Plot the array
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, len(array) + 1), array, label='Precipitation', marker='o')

        # Add dotted lines to show the fifths
#         for i in range(0, 6):
#             plt.axvline(x=len(array) * i / 5, color='r', linestyle='--', label=f'Fifth {i}')

        # Shade the fifth with the most rainfall
        split_indices = np.linspace(0, len(array), 6, dtype=int)
        start_index = split_indices[max_array_num - 1] 
        end_index = split_indices[max_array_num] + 1
        plt.fill_between(range(start_index, end_index), array[start_index-1:end_index-1], color='yellow', alpha=0.3, label=f'Fifth {max_array_num} with most rain')

        plt.title('Precipitation Values with Fifths Marked')
        plt.xlabel('Time')
        plt.ylabel('Precipitation')
        plt.legend()
        plt.show()

    return max_array_num


def get_season(date_str, date_format='%Y-%m-%d %H:%M:%S'):
    """
    Determine the season based on custom dates where each month is considered to have 30 days.
    """
    custom_date = parse_custom_date(date_str, date_format)
    # print(custom_date)
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


# Add the season column based on the first 'date' in the 'times' column
def extract_first_date(df):
    # Extract the first date from the 'times' column of the DataFrame
    if not df.empty and 'times' in df.columns:
        return df['times'].iloc[0]  # Assuming 'times' column is not empty
    return None


def select_events_with_multiples_of_x(events, x):
    events_len_x = []
    
    for event in events:
        if len(event) % x == 0:
            events_len_x.append(event)      
    return events_len_x
