import pickle 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from statsmodels.graphics.mosaicplot import mosaic
from tabulate import tabulate

from Analyse_Events_Functions import *

def find_quintile_with_max_value(intensities):
    
    # Number of elements in each quintile
    quintile_size = len(intensities) // 5
    
    # Calculate the indices that will split the array into quintiles
    quintile_indices = [i * quintile_size for i in range(1, 5)] + [len(intensities)]
    
    # Split the array into quintiles
    quintiles = np.array_split(intensities, 5)
    
    # Find the quintile that contains the maximum value
    max_value = np.max(intensities)
    for i, quintile in enumerate(quintiles):
        if max_value in quintile:
            return i
        
def plot_profiles(axs, profile_fp, durations_fp, volumes_fp, real_durations_fp, num_clusters, row, color, linestyle):
    
    ###########################
    # Read in profiles
    ###########################    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{profile_fp}.pkl", 'rb') as f:
        profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{durations_fp}.pkl", 'rb') as f:
        durations_for_profiles = pickle.load(f)    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{volumes_fp}.pkl", 'rb') as f:
        volumes_for_profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{real_durations_fp}.pkl", 'rb') as f:
        real_durations_for_profiles = pickle.load(f)        
    
    ###########################
    # Get just top 10%
    ###########################
    # Calculate the cutoff for the top 10%
    cutoff = np.percentile(volumes_for_profiles, 90)

    # Get indices of values in the top 10%
    top_10_percent_indices = [i for i, x in enumerate(volumes_for_profiles) if x >= cutoff]

    # Extract corresponding values from the other list
    top_10_percent_profiles = [profiles[i] for i in top_10_percent_indices]
    top_10_percent_durations = [durations_for_profiles[i] for i in top_10_percent_indices]
    
    # Create and fit the model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(top_10_percent_profiles)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    df = pd.DataFrame({'cluster_num': labels, 'duration': top_10_percent_durations})
    df['duration'] = pd.to_numeric(df['duration'])
    df.groupby('cluster_num')['duration'].mean()

    for num, centroid_cumulative in enumerate(centroids):
        
        # Time in hours
        time_hours = np.arange(len(centroid_cumulative))  
        
        # Convert cumulative to intensity (mm/hour)
        intensity = np.diff(centroid_cumulative) / np.diff(time_hours)
        
        # Calculate average intensity
        average_intensity = np.sum(intensity) / (time_hours[-1] - time_hours[0])

        # Normalize intensity by average intensity
        normalized_intensity = intensity / average_intensity
        
        # Find portion which is heaviest
        # heaviest_segment = categorize_normalized_rainstorm(centroid_cumulative)
        quintile_with_max_value = find_quintile_with_max_value(intensity)
        i = quintile_with_max_value

        axs[row, i].plot(time_hours[1:], normalized_intensity, color=color, linestyle=linestyle)
        if row == 0:
            axs[row, i].set_title(f'Quintile {i + 1}')
            
def plot_profiles_onerow(axs, profile_fp, durations_fp, volumes_fp, num_clusters, row, color, linestyle):
    ###########################
    # Read in profiles
    ###########################    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{profile_fp}.pkl", 'rb') as f:
        profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{durations_fp}.pkl", 'rb') as f:
        durations_for_profiles = pickle.load(f)    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{volumes_fp}.pkl", 'rb') as f:
        volumes_for_profiles = pickle.load(f)
    
    ###########################
    # Get just top 10%
    ###########################
    # Calculate the cutoff for the top 10%
    cutoff = np.percentile(volumes_for_profiles, 90)

    # Get indices of values in the top 10%
    top_10_percent_indices = [i for i, x in enumerate(volumes_for_profiles) if x >= cutoff]

    # Extract corresponding values from the other list
    top_10_percent_profiles = [profiles[i] for i in top_10_percent_indices]
    top_10_percent_durations = [durations_for_profiles[i] for i in top_10_percent_indices]
    
    # Create and fit the model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(top_10_percent_profiles)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    df = pd.DataFrame({'cluster_num': labels, 'duration': top_10_percent_durations})
    df['duration'] = pd.to_numeric(df['duration'])
    df.groupby('cluster_num')['duration'].mean()

    for num, centroid_cumulative in enumerate(centroids):
        
        # Time in hours
        time_hours = np.arange(len(centroid_cumulative))  
        
        # Convert cumulative to intensity (mm/hour)
        intensity = np.diff(centroid_cumulative) / np.diff(time_hours)
        
        # Calculate average intensity
        average_intensity = np.sum(intensity) / (time_hours[-1] - time_hours[0])

        # Normalize intensity by average intensity
        normalized_intensity = intensity / average_intensity
        
        # Find portion which is heaviest
        # heaviest_segment = categorize_normalized_rainstorm(centroid_cumulative)
        quintile_with_max_value = find_quintile_with_max_value(intensity)
        i = quintile_with_max_value

        axs[i].plot(time_hours[1:], normalized_intensity, color=color, linestyle=linestyle)
        axs[i].set_title(f'Quintile {i + 1}')     

def plot_profiles_onerow_oneduration(axs, profile_fp, durations_fp, volumes_fp, real_durations_fp, dur_range, color, linestyle):
    ###########################
    # Read in profiles
    ###########################    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{profile_fp}.pkl", 'rb') as f:
        profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{durations_fp}.pkl", 'rb') as f:
        durations_for_profiles = pickle.load(f)    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{volumes_fp}.pkl", 'rb') as f:
        volumes_for_profiles = pickle.load(f)
    
    ###########################
    # Get just top 10%
    ###########################
    # Calculate the cutoff for the top 10%
    cutoff = np.percentile(volumes_for_profiles, 90)

    # Get indices of values in the top 10%
    top_10_percent_indices = [i for i, x in enumerate(volumes_for_profiles) if x >= cutoff]

    # Extract corresponding values from the other list
    top_10_percent_profiles = [profiles[i] for i in top_10_percent_indices]
    top_10_percent_durations = [durations_for_profiles[i] for i in top_10_percent_indices]
    
    # Create and fit the model
    range_1_rainfall = []
    range_1_durations= []
    # Iterate through the top_10_percent_profiles and durations simultaneously
    for profile, duration in zip(top_10_percent_profiles, top_10_percent_durations):
        if dur_range[0] <= np.float64(duration) < dur_range[1]:
                # Append the profile to the corresponding rainfall list
                range_1_rainfall.append(profile)
                range_1_durations.append(duration)
    kmeans = KMeans(n_clusters=15, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(range_1_rainfall)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    df = pd.DataFrame({'cluster_num': labels, 'duration': range_1_durations})
    df['duration'] = pd.to_numeric(df['duration'])
    df.groupby('cluster_num')['duration'].mean()

    for num, centroid_cumulative in enumerate(centroids):
        
        # Time in hours
        time_hours = np.arange(len(centroid_cumulative))  
        
        # Convert cumulative to intensity (mm/hour)
        intensity = np.diff(centroid_cumulative) / np.diff(time_hours)
        
        # Calculate average intensity
        average_intensity = np.sum(intensity) / (time_hours[-1] - time_hours[0])

        # Normalize intensity by average intensity
        normalized_intensity = intensity / average_intensity
        
        # Find portion which is heaviest
        # heaviest_segment = categorize_normalized_rainstorm(centroid_cumulative)
        quintile_with_max_value = find_quintile_with_max_value(intensity)
        i = quintile_with_max_value

        axs[i].plot(time_hours[1:], normalized_intensity, color=color, linestyle=linestyle)
        axs[i].set_title(f'Quintile {i + 1}')         
        
        
        
def plot_profiles_split_by_duration(axs, profile_fp, durations_fp, volumes_fp, real_durations_fp, dur_range, row, color, linestyle):
    
    ###########################
    # Read in profiles
    ###########################    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{profile_fp}.pkl", 'rb') as f:
        profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{durations_fp}.pkl", 'rb') as f:
        durations_for_profiles = pickle.load(f)    
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{volumes_fp}.pkl", 'rb') as f:
        volumes_for_profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{real_durations_fp}.pkl", 'rb') as f:
        real_durations_for_profiles = pickle.load(f)        
    
    ###########################
    # Get just top 10%
    ###########################
    # Calculate the cutoff for the top 10%
    cutoff = np.percentile(volumes_for_profiles, 90)

    # Get indices of values in the top 10%
    top_10_percent_indices = [i for i, x in enumerate(volumes_for_profiles) if x >= cutoff]

    # Extract corresponding values from the other list
    top_10_percent_profiles = [profiles[i] for i in top_10_percent_indices]
    top_10_percent_durations = [durations_for_profiles[i] for i in top_10_percent_indices]
    
    # Create and fit the model
    range_1_rainfall = []
    range_1_durations= []
    # Iterate through the top_10_percent_profiles and durations simultaneously
    for profile, duration in zip(top_10_percent_profiles, top_10_percent_durations):
        if dur_range[0] <= np.float64(duration) < dur_range[1]:
                # Append the profile to the corresponding rainfall list
                range_1_rainfall.append(profile)
                range_1_durations.append(duration)
    kmeans = KMeans(n_clusters=15, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(range_1_rainfall)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    df = pd.DataFrame({'cluster_num': labels, 'duration': range_1_durations})
    df['duration'] = pd.to_numeric(df['duration'])
    df.groupby('cluster_num')['duration'].mean()
    
    for num, centroid_cumulative in enumerate(centroids):
        
        # Time in hours
        time_hours = np.arange(len(centroid_cumulative))  
        
        # Convert cumulative to intensity (mm/hour)
        intensity = np.diff(centroid_cumulative) / np.diff(time_hours)
        
        # Calculate average intensity
        average_intensity = np.sum(intensity) / (time_hours[-1] - time_hours[0])

        # Normalize intensity by average intensity
        normalized_intensity = intensity / average_intensity
        
        # Find portion which is heaviest
        # heaviest_segment = categorize_normalized_rainstorm(centroid_cumulative)
        quintile_with_max_value = find_quintile_with_max_value(intensity)
        i = quintile_with_max_value

        axs[row, i].plot(time_hours[1:], normalized_intensity, color=color, linestyle=linestyle)
        if row == 0:
            axs[row, i].set_title(f'Quintile {i + 1}')   #
            
            
def format_data_for_plots(filepath, duration_style ='Real', seasons_flag = False, percent=10):

    ###########################################################################
    # Read in required data
    ###########################################################################
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_profiles.pkl", 'rb') as f:
        profiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_durations_for_profiles.pkl", 'rb') as f:
        durations = pickle.load(f)
        durations = np.float64(durations) 
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_real_durations_for_profiles.pkl", 'rb') as f:
        real_durations = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_volumes_for_profiles.pkl", 'rb') as f:
        volumes = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_max_quintiles.pkl", 'rb') as f:
        max_quintiles = pickle.load(f)
    with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_dimensionless_profiles.pkl", 'rb') as f:
        dimensionless_profiles = pickle.load(f)
#     with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_normalised_rainfall.pkl", 'rb') as f:
#         normalised_rainfalls = pickle.load(f)        
    print(len(profiles))   
    if seasons_flag == True:
        with open(f"/nfs/a319/gy17m2a/PhD/ProcessedData/Profiles/{filepath}_seasons.pkl", 'rb') as f:
            seasons = pickle.load(f)    
    
    if duration_style == 'Real':
        durations = real_durations
    elif duration_style == 'AMAX_length':
        durations = durations    
        
    print(percent)
    volumes, profiles, durations,  max_quintiles, dimensionless_profiles, seasons = keep_top_percent([volumes, profiles, durations, max_quintiles, dimensionless_profiles, seasons],percent = percent)
        
    ###########################################################################
    # Sort loadings 
    ###########################################################################
    # Define loading classes
    loading_classes = ['F2', 'F1', 'C', 'B1', 'B2']
    season_classes = ['Winter', 'Summer']

    # Recode max_quintiles into loading classes
    quintile_mapping = {1: 'F2', 2: 'F1', 3: 'C', 4: 'B1', 5: 'B2'}
    loadings = [quintile_mapping[q] for q in max_quintiles] 

    ###########################################################################
    # Create a DataFrame with the data
    ###########################################################################
    data = pd.DataFrame({'Profile': profiles, 'Duration': durations,'Loading': loadings, 
                         # 'NormalisedRainfall':normalised_rainfalls,
                         'DimensionlessProfiles':dimensionless_profiles, 'MaxQuintile':max_quintiles, 
                        'Volume':volumes})
    
    if seasons_flag == True:
        data['Seasons'] = seasons
        data['Seasons'] = pd.Categorical(data['Seasons'], categories=season_classes, ordered=True)

    data=data[data['Duration']>1]
    data.reset_index(inplace=True, drop=True)

    # Adjust order of loading
    data['Loading'] = pd.Categorical(data['Loading'], categories=loading_classes, ordered=True)

    ###########################################################################
    # Split into 4 equally sized duration categories
    ###########################################################################
    # Define the bin edges and labels
    bin_edges = [0.25, 2.10, 6.45, 19.25, np.max(durations)]
    duration_labels = ['0.25-2.10 hr', '2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']

    # Bin durations into categories based on bin_edges
    data['DurationRange_notpersonalised'] = pd.cut(data['Duration'], bins=bin_edges, labels=duration_labels, right=True)

    # Now, if you also want to create quartile categories based on the index, similar to the previous logic:
    data = data.sort_values(by='Duration')
    data.reset_index(inplace=True, drop=True)

    # Calculate the number of events in each quartile
    total_events = len(data)
    events_per_quartile = total_events // 4

    # Assign quartile categories based on index position
    data['DurationCategory'] = pd.cut(data.index,
                                      bins=[-1, events_per_quartile, 2 * events_per_quartile, 3 * events_per_quartile, total_events],
                                      labels=['Q1', 'Q2', 'Q3', 'Q4'], include_lowest=True)
    grouped = data.groupby('DurationCategory')['Duration']
    quartile_ranges = grouped.agg(['min', 'max'])

    # Create a new column with labels for quartile ranges
    data['DurationRange_personalised'] = data['DurationCategory'].map(quartile_ranges.apply(lambda x: f'{x["min"]:.1f}-{x["max"]:.1f}', axis=1))

    return data

def plot_profiles_by_percentile(volumes, profiles, max_quintiles, percent_10=90, percent_1=99):
    """
    Plot profiles categorized by volume percentiles (top 1%, top 10%, and others).
    
    Parameters:
    - volumes (array-like): Array of volumes.
    - profiles (array-like): Array of profiles.
    - max_quintiles (array-like): Array indicating max quintiles.
    - percent_10 (int, optional): Percentile for top 10% (default is 90).
    - percent_1 (int, optional): Percentile for top 1% (default is 99).
    """
    # Calculate volume thresholds for top percentiles
    threshold_10_percent = np.percentile(volumes, percent_10)
    threshold_1_percent = np.percentile(volumes, percent_1)

    # Prepare the subplots
    fig, axs = plt.subplots(ncols=5, nrows=1, figsize=(13, 3), sharey=True)

    # Split profiles into top 1%, top 10%, and others
    top_1_indices = np.where(volumes >= threshold_1_percent)[0]
    top_10_indices = np.where((volumes >= threshold_10_percent) & (volumes < threshold_1_percent))[0]
    other_indices = np.where(volumes < threshold_10_percent)[0]

    # Function to plot profiles by indices
    def plot_profiles(indices, color, zorder, label_suffix=''):
        for idx in indices:
            profile = profiles[idx]
            segment = max_quintiles[idx] - 1
            axs[segment].plot(profile, color=color, zorder=zorder, label=f'Profile{label_suffix}')

    # Plot profiles in the order: others -> top 10% -> top 1%
    plot_profiles(other_indices, color='lightgrey', zorder=1)  # Others with lowest z-order
    plot_profiles(top_10_indices, color='plum', zorder=2, label_suffix=' (Top 10%)')  # Top 10%
    plot_profiles(top_1_indices, color='darkmagenta', zorder=3, label_suffix=' (Top 1%)')  # Top 1% with highest z-order

    # Adjust layout
    fig.tight_layout()
    fig.supylabel('Dimensionless rainfall Rd', x=-0.01)
    plt.show()



def create_mosaic_plot(ax, data, cross_variable1, cross_variable2, include_all = False):    

    # Count the occurrences and reshape for mosaic plot
    count_data = data.groupby([cross_variable1, cross_variable2]).size().unstack(fill_value=0)
    
    if include_all:
        # Calculate total counts for each 'DurationRange'
        count_data['All Durations'] = count_data.sum(axis=1)

        # Calculate total counts across all categories
        total_counts = count_data.sum(axis=0)
        count_data.loc['All'] = total_counts
        del count_data['All Durations']
    
    # Convert to dictionary format suitable for mosaic plot
    mosaic_data = count_data.stack().to_dict()
    
    # Define color mapping based on cross_variable with transparency (alpha)
    if cross_variable2 == 'Loading':
        color_mapping = {
            'F2': (0.0, 0.0, 1.0, 0.6),    # darkblue with 0.6 alpha (semi-transparent)
            'F1': (0.0, 0.6902, 1.0, 0.6), # deepskyblue with 0.6 alpha
            'C': (0.5, 0.5, 0.5, 0.6),     # grey with 0.6 alpha
            'B1': (0.8039, 0.0, 0.0, 0.6), # indianred with 0.6 alpha
            'B2': (0.5451, 0.0, 0.0, 0.6)  # darkred with 0.6 alpha
        }
    elif cross_variable2 == 'Seasons':
        color_mapping = {
            'Summer': (1.0, 0.6471, 0.0, 0.6), # orange with 0.6 alpha
            'Winter': (0.0, 0.0, 1.0, 0.6)     # blue with 0.6 alpha
        }
    else:
        color_mapping = {}  # Add more mappings as needed
    
    # Function to specify properties including colors based on cross_variable
    def props(key):
        return {'color': color_mapping.get(key[1], (0.0, 0.0, 0.0, 0.6))}  # Default to black with 0.6 alpha if not found
    
    # Plot the mosaic plot
    _, mosaic_ax = mosaic(mosaic_data, title='', properties=props, ax=ax, gap=0.015, horizontal=False, labelizer=lambda k: k[1])
    
    ax.invert_yaxis()

def create_mosaic_plot_old(ax, data, cross_variable1, cross_variable2, include_all = False):    

    # Count the occurrences and reshape for mosaic plot
    count_data = data.groupby([cross_variable1, cross_variable2]).size().unstack(fill_value=0)
    
    if include_all == True:
        # Calculate total counts for each 'DurationRange'
        count_data['All Durations'] = count_data.sum(axis=1)

        # Calculate total counts across all categories
        total_counts = count_data.sum(axis=0)
        count_data.loc['All'] = total_counts
        del count_data['All Durations']
    
    # Convert to dictionary format suitable for mosaic plot
    mosaic_data = count_data.stack().to_dict()
    
    color_mapping = {'F2': 'darkblue','F1': 'deepskyblue','C': 'grey', 'B1': 'indianred','B2': 'darkred'}

    # Function to specify properties including colors
    def props(key):
        return {'color': color_mapping[key[0]]}
    
    # Plot the mosaic plot
    _, mosaic_ax = mosaic(mosaic_data, title='', properties=props, ax=ax, gap=0.015,horizontal=False,labelizer=lambda k: k[1])
    
    ax.invert_yaxis()
    
def create_contingency_table(data, col):    
    # Create a contingency table
    contingency_table = pd.crosstab(data[col], data['Loading'])

    # Convert counts to row-wise proportions (percentages)
    row_proportional_table = contingency_table.div(contingency_table.sum(axis=1), axis=0) * 100

    # Round to 1 decimal place
    row_proportional_table = row_proportional_table.round(1)

    # Calculate the overall proportion for each loading category
    total_counts = contingency_table.sum(axis=0)  # Sum across all duration categories
    overall_proportion = (total_counts / total_counts.sum()) * 100  # Divide by total count to get percentage
    overall_proportion = overall_proportion.round(1)

    # Add the 'All' row to the proportional table
    row_proportional_table.loc['All'] = overall_proportion

    # Convert the proportional table to a list of lists for tabulate
    table_data = row_proportional_table.reset_index().values.tolist()
    headers = ['DurationCategory'] + row_proportional_table.columns.tolist()

    # Print the formatted table using tabulate
    print("Proportional Contingency Table with 'All' Row:")
    print(tabulate(table_data, headers=headers, tablefmt='pretty'))

def create_absolute_contingency_table(data, column):
    # Create a contingency table with absolute counts
    contingency_table = pd.crosstab(data[column], data['Loading'])

    # Calculate the overall sum for each loading category
    overall_counts = contingency_table.sum(axis=0)  # Sum across all duration categories

    # Add the 'All' row with the overall counts
    contingency_table.loc['All'] = overall_counts

    # Convert the absolute contingency table to a list of lists for tabulate
    table_data = contingency_table.reset_index().values.tolist()
    headers = [column] + list(contingency_table.columns)

    # Print the formatted table using tabulate
    print("Absolute Contingency Table with 'All' Row:")
    print(tabulate(table_data, headers=headers, tablefmt='pretty'))    
    
    
def keep_top_percent(data_lists, percent=10):
    """
    Keep the top percent of values from multiple lists based on the last list.
    
    Parameters:
    - data_lists (list of lists): Lists of data to filter.
    - percent (int, optional): Percentile cutoff to keep (default is 10).

    Returns:
    - filtered_lists (list of lists): Lists containing only the top percentile values.
    """
    # Extract the last list as volumes (assuming it contains the values to filter by)
    volumes = data_lists[0]
    
    # Calculate the cutoff for the top percentile
    cutoff = np.percentile(volumes, 100 - percent)

    # Get indices of values in the top percentile
    top_percent_indices = [i for i, x in enumerate(volumes) if x >= cutoff]

    # Extract corresponding values from all lists
    filtered_lists = []
    for data_list in data_lists:
        filtered_list = [data_list[i] for i in top_percent_indices]
        filtered_lists.append(filtered_list)
    
    return filtered_lists

def run_kmeans_clustering (num_clusters, profiles, durations):
    # Create and fit the model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(profiles)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    df = pd.DataFrame({'cluster_num': labels, 'duration': durations})
    df['duration'] = pd.to_numeric(df['duration'])
    df.groupby('cluster_num')['duration'].mean()
    return df