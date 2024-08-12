from statsmodels.graphics.mosaicplot import mosaic
from sklearn.cluster import KMeans
import numpy as np
import pandas as pd

def plot_profiles_by_percentile(df, percent_10=90, percent_1=99):
    """
    Plot profiles categorized by volume percentiles (top 1%, top 10%, and others).
    
    Parameters:
    - volumes (array-like): Array of volumes.
    - profiles (array-like): Array of profiles.
    - max_quintiles (array-like): Array indicating max quintiles.
    - percent_10 (int, optional): Percentile for top 10% (default is 90).
    - percent_1 (int, optional): Percentile for top 1% (default is 99).
    """
    volumes = ukcp18_present['Volume']
    profiles = ukcp18_present['Profile']
    max_quintiles =  ukcp18_present['max_quintile']

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

def create_mosaic_plot(ax, data, cross_variable1, cross_variable2, quintile_cats, include_all=False, filter_events=True):
    data = data.copy()
    #if "Loading_profile" in cross_variable2:
    data[cross_variable2] = pd.Categorical(data[cross_variable2], categories=quintile_cats, ordered=True)
    
    if filter_events:
        data = data[data['interpolated12_cumulative_rainfall'].notnull()]
    
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
    if "Loading_profile" in cross_variable2: 
        color_mapping = {
            'F2': (0.0, 0.0, 1.0, 0.6),    # darkblue with 0.6 alpha (semi-transparent)
            'F1': (0.0, 0.6902, 1.0, 0.6), # deepskyblue with 0.6 alpha
            'C': (0.5, 0.5, 0.5, 0.6),     # grey with 0.6 alpha
            'B1': (0.8039, 0.0, 0.0, 0.6), # indianred with 0.6 alpha
            'B2': (0.5451, 0.0, 0.0, 0.6)  # darkred with 0.6 alpha
        }
    elif cross_variable2 == 'season':
        color_mapping = {
            'Summer': (1.0, 0.6471, 0.0, 0.6), # orange with 0.6 alpha
            'Winter': (0.0, 0.0, 1.0, 0.6)     # blue with 0.6 alpha
        }
    else:
        color_mapping = {}  # Add more mappings as needed
    
    # Function to specify properties including colors based on cross_variable
    def props(key):
        return {'color': color_mapping.get(key[1], (0.0, 0.0, 0.0, 0.6))}  # Default to black with 0.6 alpha if not found
    
    # Plot the mosaic plot with labels inside the plot
    _, mosaic_ax = mosaic(mosaic_data, title='', properties=props, ax=ax, gap=0.015, horizontal=False, labelizer=lambda k: k[1])
    
    # Remove the redundant labels that appear on the top x-axis
    ax.set_xticks([])  # Remove x-axis ticks
    ax.set_xticklabels([])  # Remove x-axis labels
    ax.xaxis.label.set_visible(False)  # Hide the x-axis label
    ax.invert_yaxis()  # Invert y-axis to match typical orientation

    
    
def create_single_variable_mosaic_plot_pctlabels(ax, data, split_variable, order, color_mapping, title, filter_events=True):
    if filter_events == True:
         data= data[data['interpolated12_cumulative_rainfall'].notnull()]
            
    # Count the occurrences and reshape for mosaic plot
    count_data = data[split_variable].value_counts().reindex(order, fill_value=0)
    
    # Convert to dictionary format suitable for mosaic plot
    mosaic_data = count_data.to_dict()
    
    # Function to specify properties including colors based on cross_variable
    def props(key):
        # Extract category from key if it's a tuple
        if isinstance(key, tuple):
            category = key[0]  # Extract the first element from the tuple
        else:
            category = key  # Use directly if it's not a tuple
        color = color_mapping.get(category, (0.0, 0.0, 0.0, 0.6))  # Default to black if not found
        return {'color': color}
    
    # Calculate total number of occurrences for percentage calculation
    total_count = count_data.sum()
    
    # Plot the mosaic plot with automatic labels
    labelizer = lambda key: ''
    fig, rects = mosaic(mosaic_data, title='', labelizer = labelizer, properties=props, ax=ax, gap=0.015, horizontal=True)
    ax.invert_yaxis()  # Optional: Invert y-axis to match standard bar plot orientation
    ax.set_xticklabels([])  # Remove x-axis labels

    # Manually replace the labels with percentage labels
    counter=0
    for key, (x1, y1, x2, y2) in rects.items():
        count = mosaic_data[key[0]]
        percentage = (count / total_count) * 100
        label = f'{percentage:.2f}%'
        #print(counter)
        # Find the label at this position and replace its text
        for text in ax.texts:
            if counter in [0,6,12,18,24]:
                text.set_text(label)
                text.set_fontsize(10)
                text.set_color('black')
#                 text.set_weight('bold')
            counter=counter+1
            
        #print(f'Key: {key}, count {count} Percentage: {percentage:.2f}%, Label: {label}, x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2}')

    for key, (x1, y1, x2, y2) in rects.items():
        if x1 == 0:  # Check if this is the leftmost bar
            ax.text(x1-0.01, (y1 + y2) / 2, title, va='center', ha='right', fontsize=15, color='black', weight='bold')      

def create_single_variable_mosaic_plot(ax, data, variable, order, color_mapping, label, filter_events):
    if filter_events == True:
         data= data[data['Profile'].notnull()]
    # Count the occurrences and reshape for mosaic plot
    count_data = data[variable].value_counts().reindex(order, fill_value=0)
    
    # Convert to dictionary format suitable for mosaic plot
    mosaic_data = count_data.to_dict()
    
    # Function to specify properties including colors based on cross_variable
    def props(key):
        # Extract category from key if it's a tuple
        if isinstance(key, tuple):
            category = key[0]  # Extract the first element from the tuple
        else:
            category = key  # Use directly if it's not a tuple
        color = color_mapping.get(category, (0.0, 0.0, 0.0, 0.6))  # Default to black if not found
        return {'color': color}
    
    # Plot the mosaic plot without a title
    labelizer = lambda key: ''  # Disable default labeling
    fig, rects = mosaic(mosaic_data, title='', properties=props, ax=ax, gap=0.015,horizontal=True)
    ax.invert_yaxis()  # Optional: Invert y-axis to match standard bar plot orientation
    ax.set_xticklabels([])  # Remove x-axis labels

    # Manually add the custom label at the left edge of each bar
    for key, (x1, y1, x2, y2) in rects.items():
        if x1 == 0:  # Check if this is the leftmost bar
            ax.text(x1-0.01, (y1 + y2) / 2, label, va='center', ha='right', fontsize=15, color='black', weight='bold')


def create_normalised_event(df):
    
    rainfall_times = np.array(range(0, len(df['precipitation (mm/hr)'])))
    rainfall_amounts = np.array(df['precipitation (mm/hr)'])
    
    # Calculate cumulative rainfall
    cumulative_rainfall = np.cumsum(rainfall_amounts)
    
    # Normalize time from 0 to 1
    normalized_time = (rainfall_times - rainfall_times[0]) / (rainfall_times[-1] - rainfall_times[0])
    
    # Normalize cumulative rainfall from 0 to 1
    normalized_rainfall = cumulative_rainfall / cumulative_rainfall[-1]
    
    return normalized_time, normalized_rainfall


def interpolate_and_bin(normalized_time, normalized_rainfall):
    # Define target points for 12 bins
    target_points = np.linspace(0, 1, 15)
    
    # Create interpolation function based on existing data points
    interpolation_func = interp1d(normalized_time, normalized_rainfall, kind='linear', fill_value="extrapolate")
    
    # Interpolate values at target points
    interpolated_values = interpolation_func(target_points)
    
    return interpolated_values


def create_kmeans_centroids(profiles, num_clusters):
    
    # Create and fit the model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10, max_iter=300)
    kmeans.fit(profiles)

    # Get cluster labels for each profile
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    return centroids

def create_interpolated_profiles(df):
    interpolated_profiles = []

    for num, event in df.iterrows():
        normalized_time, normalized_rainfall = create_normalised_event(event)
        normalized_interpolated_rainfall = interpolate_and_bin(normalized_time, normalized_rainfall)
        interpolated_profiles.append(normalized_interpolated_rainfall)    
    return interpolated_profiles

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
        
def plot_monthly_spread_bydataset(ax, data, color, name):
    # Drop rows where 'month' is NaN
    data_clean = data.dropna(subset=['month'])
    
    option1={'lowerlimit':0, 'upper_limit':4, 'linestyle' : 'solid', 'Label':'<4h', "color":'red', "linewidth":3}
    option2={'lowerlimit':4, 'upper_limit':12, 'linestyle' :'dashed', 'Label':'4-12h', "color":'blue', "linewidth":1.5}
    option3={'lowerlimit':12, 'upper_limit':120, 'linestyle':'dotted', 'Label':'>12h', 'color': 'green', "linewidth":1.5}
    
    for option in [option1, option2, option3]:
        data_clean_copy = data_clean.copy()
        data_clean_copy = data_clean_copy[(data_clean_copy['duration'] > option['lowerlimit']) & (data_clean_copy['duration'] < option['upper_limit'])]
        
        # Count the occurrences of rainstorms in each month
        monthly_counts = data_clean_copy['month'].value_counts().sort_index()

        # Calculate the proportion of rainstorms in each month
        total_rainstorms = monthly_counts.sum()
        monthly_proportions = (monthly_counts / total_rainstorms) * 100

        # Create a DataFrame to display the results
        monthly_summary = pd.DataFrame({
            'Count': monthly_counts,
            'Proportion (%)': monthly_proportions
        }).reset_index()
        monthly_summary.columns = ['Month', 'Count', 'Proportion (%)']

        ax.plot(monthly_summary['Month'], monthly_summary['Proportion (%)'], marker='', linestyle=option['linestyle'], 
                color=option['color'], label= option['Label'], linewidth=option['linewidth'])

        ax.set_xlabel('Month')
        ax.set_title(name)  
        
def plot_monthly_spread_byduration(ax, nimrod, bc005, bb198, bb189, lower_limit, upper_limit, title):
    
    nimrod={'data':nimrod, 'color':'black', 'name':'NIMROD'}
    bc005={'data':bc005, 'color':'green', 'name':'BC005'}
    bb198={'data':bb198, 'color':'orange', 'name':'BB198'}
    bb189={'data':bb189, 'color':'darkorange', 'name':'BB189'}
    
    for option in [nimrod, bc005, bb198, bb189]:  
        
        data_copy=option['data'].copy()
        
        # Drop rows where 'month' is NaN
        data_clean = data_copy.dropna(subset=['month'])
        data_clean_copy = data_clean[(data_clean['duration'] > lower_limit) & (data_clean['duration'] < upper_limit)]
        # Count the occurrences of rainstorms in each month
        monthly_counts = data_clean_copy['month'].value_counts().sort_index()

        # Calculate the proportion of rainstorms in each month
        total_rainstorms = monthly_counts.sum()
        monthly_proportions = (monthly_counts / total_rainstorms) * 100

        # Create a DataFrame to display the results
        monthly_summary = pd.DataFrame({
            'Count': monthly_counts,
            'Proportion (%)': monthly_proportions
        }).reset_index()
        monthly_summary.columns = ['Month', 'Count', 'Proportion (%)']

        ax.plot(monthly_summary['Month'], monthly_summary['Proportion (%)'], marker='.', linestyle='solid', 
                color=option['color'], label= option['name'])

        ax.set_xlabel('Month')
        ax.set_title(title)

        
        
def plot_centroids(axs, row, centroids, color):
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
        
        axs[row, i].plot(time_hours[1:], normalized_intensity, color=color, linestyle='-')
        
        if row == 0:
            axs[row, i].set_title(f'Quintile {i + 1}')   
            
            
def calculate_center_of_mass(rainfall_event):
    total_rainfall = np.sum(rainfall_event)
    time_steps = np.arange(len(rainfall_event))
    center_of_mass = np.sum(time_steps * rainfall_event) / total_rainfall
    return center_of_mass

def categorize_rainfall_events_five(rainfall_events):
    categories = {'F2': 0, 'F1': 0, 'C': 0, 'B1': 0, 'B2': 0}
    total_events = len(rainfall_events)
    
    for event in rainfall_events:
        center_of_mass = calculate_center_of_mass(event)
        normalized_com = center_of_mass / len(event)
        
        # Categorize based on the normalized center of mass
        if normalized_com < 0.2:
            categories['F2'] += 1
        elif 0.2 <= normalized_com < 0.4:
            categories['F1'] += 1
        elif 0.4 <= normalized_com < 0.6:
            categories['C'] += 1
        elif 0.6 <= normalized_com < 0.8:
            categories['B1'] += 1
        elif 0.8 <= normalized_com <= 1:
            categories['B2'] += 1
    
def categorize_rainfall_events_five(rainfall_events):
    categories = {'F2': 0, 'F1': 0, 'C': 0, 'B1': 0, 'B2': 0}
    total_events = len(rainfall_events)
    
    for event in rainfall_events:
        center_of_mass = calculate_center_of_mass(event)
        normalized_com = center_of_mass / len(event)
        
        # Categorize based on the normalized center of mass
        if normalized_com < 0.2:
            categories['F2'] += 1
        elif 0.2 <= normalized_com < 0.4:
            categories['F1'] += 1
        elif 0.4 <= normalized_com < 0.6:
            categories['C'] += 1
        elif 0.6 <= normalized_com < 0.8:
            categories['B1'] += 1
        elif 0.8 <= normalized_com <= 1:
            categories['B2'] += 1
    
    # Calculate proportions
    for key in categories:
        categories[key] = round(categories[key] /total_events,2)
#         categories[key] /= total_events
    
    return categories            