import pickle 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

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
            axs[row, i].set_title(f'Quintile {i + 1}')        