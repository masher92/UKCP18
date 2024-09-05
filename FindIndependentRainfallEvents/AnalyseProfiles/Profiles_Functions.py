import numpy as np
from sklearn.cluster import KMeans
import pandas as pd 

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

def create_kmeans_centroids(data, num_clusters):
    data = data[data['interpolated12_incremental_rainfall'].notna()]
    profiles = np.array(data['interpolated12_incremental_rainfall'].tolist())
    # Create and fit the model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(profiles)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    return labels, centroids

            
def keep_top_ten_percent(profiles, durations, real_durations, volumes):
    # Calculate the cutoff for the top 10%
    cutoff = np.percentile(volumes, 90)

    # Get indices of values in the top 10%
    top_10_percent_indices = [i for i, x in enumerate(volumes) if x >= cutoff]

    # Extract corresponding values from the other list
    top_10_percent_profiles = [profiles[i] for i in top_10_percent_indices]
    top_10_percent_durations = [durations[i] for i in top_10_percent_indices]
    top_10_percent_volumes = [volumes[i] for i in top_10_percent_indices]
    top_10_percent_real_durations = [real_durations[i] for i in top_10_percent_indices]
    
    return top_10_percent_profiles, top_10_percent_durations, top_10_percent_real_durations, top_10_percent_volumes

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

def create_kmeans_centroids(data, num_clusters):
    profiles = np.array(data['irain_14vals'].tolist())
    # Create and fit the model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(profiles)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    return labels, centroids 


def plot_centroids(axs, row, centroids, color):
    for num, centroid_cumulative in enumerate(centroids):

        # Time in hours
        time_hours = np.arange(len(centroid_cumulative))  

        # Find portion which is heaviest
        # heaviest_segment = categorize_normalized_rainstorm(centroid_cumulative)
        quintile_with_max_value = find_quintile_with_max_value(centroid_cumulative)
        i = quintile_with_max_value
        
        axs[row, i].plot(time_hours, centroid_cumulative, color=color, linestyle='-')
        
        if row == 0:
            axs[row, i].set_title(f'Quintile {i + 1}')  