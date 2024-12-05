import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
import matplotlib.pyplot as plt
from statsmodels.graphics.mosaicplot import mosaic
import seaborn as sns

# Filter for Great Britain
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gb_outline = gdf[(gdf.name == "United Kingdom")]

home_dir = '/nfs/a319/gy17m2a/PhD/'

tbo_vals = pd.read_csv(home_dir + 'datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
tbo_vals = tbo_vals[tbo_vals['Lon']!=-999.0]
tbo_vals['gauge_num'] = tbo_vals.index

def plot_boxplot(data, ax, color_mapping):
    sns.boxplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  dodge=True, palette=color_mapping) 
    
def plot_boxplot_by_season(data, ax):
    season_palette = {"Autumn": "darkorange", "Summer": "yellow", "Winter":"lightskyblue", 'Spring':'lightgreen'}
    sns.boxplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  hue='season', dodge=True, palette = season_palette)       


def create_single_variable_mosaic_plot_pctlabels(ax, data, split_variable, order, color_mapping, title):
           
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
    
    the_ls = range(0,len(order))
    if split_variable == 'Loading_profile_molly': 
        the_ls = [the_ls[0]] + [x * 6 for x in the_ls[1:]]
    else:
        the_ls = [the_ls[0]] + [x * 4 for x in the_ls[1:]]

    # Manually replace the labels with percentage labels
    counter=0
    for key, (x1, y1, x2, y2) in rects.items():
        count = mosaic_data[key[0]]
        percentage = (count / total_count) * 100
        label = f'{percentage:.2f}%'
        
        # Find the label at this position and replace its text
        for text in ax.texts:
            if counter in the_ls:
                text.set_text(label)
                text.set_fontsize(10)
                text.set_color('black')
            counter=counter+1
            
    for key, (x1, y1, x2, y2) in rects.items():
        if x1 == 0:  # Check if this is the leftmost bar
            ax.text(x1-0.01, (y1 + y2) / 2, title, va='center', ha='right', fontsize=15, color='black', weight='bold')      



def plot_present_future_changes(axes, row, input_df_changes, variable, variable_to_plot_present, variable_to_plot_future, 
                                variable_to_plot_diff, cmap, cmap_diff, low_lim, high_lim, diff_high_lim, diff_low_lim):
    # Present Climate 
    present_data = input_df_changes[['gauge_num', variable_to_plot_present]].copy()
    present_data['Climate'] = 'present'  # Add a Climate column for clarity
    # Future Climate
    future_data = input_df_changes[['gauge_num', variable_to_plot_future]].copy()
    future_data['Climate'] = 'future'  # Add a Climate column for clarity
    # Change 
    change_data = input_df_changes[['gauge_num', variable_to_plot_diff]].copy()
    change_data['Climate'] = 'change'  # Add a Climate column for clarity

    global_min = min(present_data[variable_to_plot_present].min(),
                     future_data[variable_to_plot_future].min())
    global_max = max(present_data[variable_to_plot_present].max(),
                     future_data[variable_to_plot_future].max())
    
    ### Plot
    if len(axes.shape) == 1:
        # Case with just one row of axes
        plot_values_on_map(axes[0], present_data, f'Present Climate - {variable} Values', tbo_vals,
                           variable_to_plot_present, low_lim, high_lim, cmap)
        plot_values_on_map(axes[1], future_data, f'Future Climate - {variable} Values', tbo_vals, 
                           variable_to_plot_future, low_lim, high_lim, cmap)
        plot_values_on_map(axes[2], change_data, f'Change in {variable} Values', tbo_vals, 
                           variable_to_plot_diff, vmin=diff_low_lim, vmax=diff_high_lim, cmap=cmap_diff)
    else:
        # Case with multiple rows of axes
        plot_values_on_map(axes[row, 0], present_data, f'Present Climate - {variable} Values', tbo_vals,
                           variable_to_plot_present, low_lim, high_lim, cmap)
        plot_values_on_map(axes[row, 1], future_data, f'Future Climate - {variable} Values', tbo_vals, 
                           variable_to_plot_future, low_lim, high_lim, cmap)
        plot_values_on_map(axes[row, 2], change_data, f'Change in {variable} Values', tbo_vals, 
                           variable_to_plot_diff, vmin=diff_low_lim, vmax=diff_high_lim, cmap=cmap_diff)
        
    # Adjust layout
    plt.tight_layout()  
    
    
def plot_values_on_map(ax, data, title, tbo_vals, value_column, vmin, vmax, cmap='viridis'):
    
    gauge_locs = data['gauge_num'].copy()

    # Now index into gauge_locations with the copied values
    lon = tbo_vals.loc[gauge_locs, 'Lon']
    lat = tbo_vals.loc[gauge_locs, 'Lat']
    
    # Plot the background outline of Great Britain
    gb_outline.plot(ax=ax, color='lightgrey', edgecolor='black', linewidth=1)
    
    # Scatter plot for the specified value column
    scatter = ax.scatter(lon, lat, c=data[value_column], cmap=cmap, edgecolor=None, alpha=0.9, s=6, 
                         vmin =vmin, vmax=vmax)
    ax.set_title(title)
    #ax.set_xlabel('Longitude')
    #ax.set_ylabel('Latitude')
    ax.set_xticklabels([]); ax.set_yticklabels([])
    
    # Create a color bar that is scaled to the size of the plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)  # Control the width and padding of the colorbar
    plt.colorbar(scatter, cax=cax)   
    
    
def make_plot(df_changes_all, df_changes_byduration, variable, cmap, low_lim = None, high_lim=None):

    fig, axes = plt.subplots(3, 4, figsize=(16, 11))

    #################################################
    # Present
    #################################################
    variable_to_plot = f'{variable}_present'

    # Get all data
    present_data = df_changes_all[['gauge_num', variable_to_plot]].copy()
    present_data['Climate'] = 'present'  # Add a Climate column for clarity   
    
    if high_lim != None:
        low_lim=present_data[variable_to_plot].min()
        high_lim=present_data[variable_to_plot].max()

    # Plot for each duration
    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(1)][['gauge_num', variable_to_plot]]
    # low_lim=this_duration['R_present'].min()
    # high_lim=this_duration['R_present'].max()
    plot_values_on_map(axes[0,0], this_duration, '1h', tbo_vals,
                       variable_to_plot, low_lim, high_lim, cmap)

    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(6)][['gauge_num', variable_to_plot]]
    # low_lim=this_duration['R_present'].min()
    # high_lim=this_duration['R_present'].max()
    plot_values_on_map(axes[0,1], this_duration, '6h', tbo_vals, 
                       variable_to_plot, low_lim, high_lim, cmap)

    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(24)][['gauge_num', variable_to_plot]]
    # low_lim=this_duration['R_present'].min()
    # high_lim=this_duration['R_present'].max()
    plot_values_on_map(axes[0,2], this_duration, '24h', tbo_vals, 
                       variable_to_plot, low_lim, high_lim, cmap=cmap)  

    ### Plot 'All' values
    plot_values_on_map(axes[0,3], present_data, 'All', tbo_vals, 
                       variable_to_plot, vmin=low_lim, vmax=high_lim, cmap=cmap)

    #################################################
    # Future
    #################################################   
    variable_to_plot = f'{variable}_future'

    future_data = df_changes_all[['gauge_num', variable_to_plot]].copy()
    future_data['Climate'] = 'future'  # Add a Climate column for clarity   

    low_lim=future_data[variable_to_plot].min()
    high_lim=future_data[variable_to_plot].max()

    # Plot for each duration
    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(1)][['gauge_num', variable_to_plot]]
    plot_values_on_map(axes[1,0], this_duration, '1h', tbo_vals,
                       variable_to_plot, low_lim, high_lim, cmap)

    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(6)][['gauge_num', variable_to_plot]]
    plot_values_on_map(axes[1,1], this_duration, '6h', tbo_vals, 
                       variable_to_plot, low_lim, high_lim, cmap)

    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(24)][['gauge_num', variable_to_plot]]
    plot_values_on_map(axes[1,2], this_duration, '24h', tbo_vals, 
                       variable_to_plot, low_lim, high_lim, cmap=cmap)    


    ### Plot 'All' values
    plot_values_on_map(axes[1,3], future_data, 'All', tbo_vals, 
                       variable_to_plot, vmin=low_lim, vmax=high_lim, cmap=cmap)


    #################################################
    # Difference
    #################################################
    variable_to_plot = f'{variable}_diff'

    ## All
    diff_data = df_changes_all[['gauge_num', variable_to_plot]].copy()
    diff_data['Climate'] = 'present'  # Add a Climate column for clarity    

    low_lim=diff_data[variable_to_plot].min()
    high_lim=diff_data[variable_to_plot].max()
    cmap = 'bwr'

    ## By duration
    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(1)][['gauge_num', variable_to_plot]]
    plot_values_on_map(axes[2,0], this_duration, '1h', tbo_vals,
                       variable_to_plot, low_lim, high_lim, 'bwr')

    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(6)][['gauge_num', variable_to_plot]]
    plot_values_on_map(axes[2,1], this_duration, '6h', tbo_vals, 
                       variable_to_plot, low_lim, high_lim, 'bwr')

    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(24)][['gauge_num', variable_to_plot]]
    plot_values_on_map(axes[2,2], this_duration, '24h', tbo_vals, 
                       variable_to_plot, low_lim, high_lim, cmap='bwr')    

    # Plot all
    plot_values_on_map(axes[2,3], diff_data, 'All', tbo_vals, 
                       variable_to_plot, vmin=low_lim, vmax=high_lim, cmap='bwr')

    fig.text(0.08, 0.750, 'Present', va='center', ha='center', fontsize=12, rotation='horizontal');
    fig.text(0.08, 0.5, 'Future', va='center', ha='center', fontsize=12, rotation='horizontal');
    fig.text(0.08, 0.22, 'Difference', va='center', ha='center', fontsize=12, rotation='horizontal');

    plt.suptitle(f'{variable} of events at each gauge, split by sampling duration', fontsize=16);    