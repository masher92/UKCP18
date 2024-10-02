import pandas as pd
import numpy as np

def plot_polar_months_plot(event_props_dict, ax, title, rmax, name_variable_to_plot):
    
    months = [event['month'] for event in event_props_dict.values()]
    months_df = pd.DataFrame({'month':months})
    len(months_df)
    
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
    count = months_df['month'].value_counts().sort_index()
    count = count.reindex(list(range(count.index.min(),count.index.max()+1)),fill_value=0)
    
    # Calculate percentage
    total_events = count.sum()
    percentage = (count / total_events) * 100  # Calculate percentage for each month
    
    if name_variable_to_plot == 'Percentage':
        variable_to_plot = percentage
    elif name_variable_to_plot == 'Count':
        variable_to_plot = count
    
    # Define colors for each month
    colors = [
              '#0033cc',  # Jan (Light Blue)
              '#0033cc',  # Feb (Very Light Blue)
              '#ffcc00',  # Mar (Purple)
              '#ffcc00',  # Apr (Medium Purple)
              '#ffcc00',  # May (Bright Yellow)
              '#ff8c00',  # Jun (Red-Orange)
              '#ff8c00',  # Jul (Tomato Red)
              '#ff8c00',  # Aug (Dark Orange)
              '#8b4513',  # Sep (Saddle Brown)
              '#8b4513',  # Oct (Orange)
              '#8b4513',# Nov (Dark Goldenrod)
              '#0033cc',  # Dec (Dark Blue)
    ]  
    colors.reverse()
    
    # Plot
    ax.bar(circular_plot_position, variable_to_plot.iloc[::-1], width=width, color=colors)

    # Format
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
    
    
def plot_polar_months_plot_overlay(event_props_dict_present, event_props_dict_future, ax, title):
    
    months_present = [event['month'] for event in event_props_dict_present.values()]
    months_df_present = pd.DataFrame({'month':months_present})
    
    months_future = [event['month'] for event in event_props_dict_future.values()]
    months_df_future = pd.DataFrame({'month':months_future})
    
       
    N = 12
    width = (2 * np.pi) / N
    
    # Define bins and their positions
    circular_bins = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    circular_bins = np.append(circular_bins, 2 * np.pi)
    circular_plot_position = circular_bins + 0.5 * np.diff(circular_bins)[0]
    circular_plot_position = circular_plot_position[:-1]
    circular_plot_position = circular_plot_position + 0.5 * np.pi
    
    # Count numbers in each month for present and future datasets
    count_present = months_df_present['month'].value_counts().sort_index()
    count_present = count_present.reindex(list(range(count_present.index.min(), count_present.index.max() + 1)), fill_value=0)
    total_present = count_present.sum()
    percentage_present = (count_present / total_present) * 100
    
    count_future = months_df_future['month'].value_counts().sort_index()
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
    ax.set_title(title, fontsize=20, pad=50)
    ax.set_rlabel_position(90)
    ax.xaxis.grid(False)
    ax.set_ylim(0, 20)  # Set limit based on percentage (0 to 100)
    ax.set_xticks(circular_plot_position - 0.5 * np.pi)
    ax.set_xticklabels(['Mar', 'Feb', 'Jan',
                        'Dec', 'Nov', 'Oct',
                        'Sep', 'Aug', 'Jul',
                        'Jun', 'May', 'Apr'])
    
    # Add legend
    ax.legend(loc='upper right')