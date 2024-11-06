import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
import matplotlib.pyplot as plt

# Filter for Great Britain
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gb_outline = gdf[(gdf.name == "United Kingdom")]

def plot_values_on_map(ax, data, title, tbo_vals, value_column, vmin, vmax, cmap='viridis'):
    
    gauge_locs = data['gauge_num'].copy()

    # Now index into gauge_locations with the copied values
    lon = tbo_vals.loc[gauge_locs, 'Lon']
    lat = tbo_vals.loc[gauge_locs, 'Lat']
    
    # Plot the background outline of Great Britain
    gb_outline.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1)
    
    # Scatter plot for the specified value column
    scatter = ax.scatter(lon, lat, c=data[value_column], cmap=cmap, edgecolor=None, alpha=0.9, s=8, 
                         vmin =vmin, vmax=vmax)
    ax.set_title(title)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xticklabels([]); ax.set_yticklabels([])
    
    # Create a color bar that is scaled to the size of the plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)  # Control the width and padding of the colorbar
    plt.colorbar(scatter, cax=cax, label=title)

# Function to plot the change in theta_mean for a given duration
def plot_change_variable_for_duration(ax, variable, duration, df_changes, tbo_vals, cmap = 'viridis'):
    # Filter the data for the given duration
    change_R_data = df_changes[df_changes['dur_for_which_this_is_amax'] == float(duration)][['gauge_num', variable]]
    
    # Get longitude and latitude from gauge locations
    gauge_locs = change_R_data['gauge_num'].copy()

    # Now index into gauge_locations with the copied values
    lon = tbo_vals.loc[gauge_locs, 'Lon']
    lat = tbo_vals.loc[gauge_locs, 'Lat']
    
    # Plot the background outline of Great Britain
    gb_outline.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1)
    
    # Scatter plot for theta change
    scatter = ax.scatter(lon, lat, c=change_R_data[variable], cmap=cmap, edgecolor=None, s= 8, alpha=0.9)
    ax.set_title(f'{variable} (Duration: {duration} hours)')
    #ax.set_xlabel('Longitude')
    #ax.set_ylabel('Latitude')
    ax.set_xticklabels([]); ax.set_yticklabels([])
    
    # Create a color bar that is scaled to the size of the plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)  # Control the width and padding of the colorbar
    plt.colorbar(scatter, cax=cax, label=f'{variable}')    

def filter_events_by_area(events_dict, area):
    """
    Filters the nested dictionary of events based on the specified area.
    
    Parameters:
    - events_dict: Dictionary containing durations and their associated events with properties.
    - area: The area (e.g., 'SW', 'NE', etc.) to filter the events by.
    
    Returns:
    - A new dictionary containing only events from the specified area.
    """
    # Create a filtered version containing only events for the specified area
    filtered_dict = {
        duration: {
            event_key: event_props for event_key, event_props in events.items() 
            if event_props.get('area') == area
        }
        for duration, events in events_dict.items()
    }

    # Remove empty dictionaries (where no events match the specified area)
    return {k: v for k, v in filtered_dict.items() if v}

def plot_polar_months_plot(df, ax, title_on, title, rmax, name_variable_to_plot):
    
    N = 12
    width = (2*np.pi) / N
    bottom = 8
    
    # Define bins and their positions
    circular_bins = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    circular_bins = np.append(circular_bins, 2 * np.pi)
    circular_plot_position = circular_bins + 0.5*np.diff(circular_bins)[0]
    circular_plot_position = circular_plot_position[:-1]
    circular_plot_position = circular_plot_position + 0.5*np.pi
    
    # Count numbers in each month
    count = df['month'].value_counts().sort_index()
    # Reindex to ensure all months from 1 to 12 are included, filling missing months with 0
    count = count.reindex(list(range(1, 13)), fill_value=0)

    # Calculate percentage
    total_events = count.sum()
    percentage = (count / total_events) * 100  # Calculate percentage for each month
    
    if name_variable_to_plot == 'Percentage':
        variable_to_plot = percentage
    elif name_variable_to_plot == 'Count':
        variable_to_plot = count
    
    # Define colors for each month
    colors = [
              'royalblue',  # Jan (Light Blue)
              'royalblue',  # Feb (Very Light Blue)
              '#ffcc00',  # Mar (Purple)
              '#ffcc00',  # Apr (Medium Purple)
              '#ffcc00',  # May (Bright Yellow)
              '#ff8c00',  # Jun (Red-Orange)
              '#ff8c00',  # Jul (Tomato Red)
              '#ff8c00',  # Aug (Dark Orange)
              '#8b4513',  # Sep (Saddle Brown)
              '#8b4513',  # Oct (Orange)
              '#8b4513',# Nov (Dark Goldenrod)
              'royalblue',  # Dec (Dark Blue)
    ]  
    colors.reverse()
    
    # Plot
    ax.bar(circular_plot_position, variable_to_plot.iloc[::-1], width=width, color=colors)

    # Format
    if title_on ==True:
        ax.set_title(title, fontsize=20, pad=50)
    ax.set_rlabel_position(90)
    ax.xaxis.grid(False)
    if name_variable_to_plot == 'Percentage':
        ax.set_ylim(0, rmax)
    ax.set_xticks(circular_plot_position - 0.5*np.pi)
    ax.set_xticklabels(['Mar', 'Feb', 'Jan',
                         'Dec', 'Nov', 'Oct',
                        'Sep', 'Aug', 'Jul',
                        'Jun', 'May', 'Apr'])
    
    
    
    
def plot_polar_months_plot_overlay(df_present, df_future, ax, title_on, title, legend_on, vmax):
    
    N = 12
    width = (2 * np.pi) / N
    
    # Define bins and their positions
    circular_bins = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    circular_bins = np.append(circular_bins, 2 * np.pi)
    circular_plot_position = circular_bins + 0.5 * np.diff(circular_bins)[0]
    circular_plot_position = circular_plot_position[:-1]
    circular_plot_position = circular_plot_position + 0.5 * np.pi
    
    # Count numbers in each month for present and future datasets
    count_present = df_present['month'].value_counts().sort_index()
    count_present = count_present.reindex(list(range(count_present.index.min(), count_present.index.max() + 1)), fill_value=0)
    total_present = count_present.sum()
    percentage_present = (count_present / total_present) * 100
    
    count_future = df_future['month'].value_counts().sort_index()
    count_future = count_future.reindex(list(range(count_future.index.min(), count_future.index.max() + 1)), fill_value=0)
    total_future = count_future.sum()
    percentage_future = (count_future / total_future) * 100
    
    # Define colors for each dataset
    colors_present = '#ffcc00'  # Yellow for present
    colors_future = '#0033cc'    # Blue for future

    # Plot percentage for present and future datasets
    ax.bar(circular_plot_position, percentage_present.iloc[::-1], width=width, color=colors_present, alpha=0.5, label='Present')
    ax.bar(circular_plot_position, percentage_future.iloc[::-1], width=width, color=colors_future, alpha=0.5, label='Future')

    # Format
    if title_on ==True:
        ax.set_title(title, fontsize=20, pad=50)
    if legend_on==True:
        ax.legend(loc='upper right')
    ax.set_rlabel_position(90)
    ax.xaxis.grid(False)
    ax.set_ylim(0, vmax)  # Set limit based on percentage (0 to 100)
    ax.set_xticks(circular_plot_position - 0.5 * np.pi)
    ax.set_xticklabels(['Mar', 'Feb', 'Jan',
                        'Dec', 'Nov', 'Oct',
                        'Sep', 'Aug', 'Jul',
                        'Jun', 'May', 'Apr'])
    
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
