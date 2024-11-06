import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
import matplotlib.pyplot as plt
from statsmodels.graphics.mosaicplot import mosaic
import seaborn as sns
from scipy.stats import gaussian_kde
from scipy.stats import gaussian_kde, linregress

# Filter for Great Britain
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gb_outline = gdf[(gdf.name == "United Kingdom")]

home_dir = '/nfs/a319/gy17m2a/PhD/'

tbo_vals = pd.read_csv(home_dir + 'datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
tbo_vals = tbo_vals[tbo_vals['Lon']!=-999.0]
tbo_vals['gauge_num'] = tbo_vals.index


def plot_boxplot(data, ax, color_mapping):
    sns.swarmplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  dodge=True, palette=color_mapping)
    ax.set_xlabel('Quintile classification', fontsize=15)
    ax.set_ylabel("$D_{50}$", fontsize=15)
    
def plot_boxplot_by_season(data, ax):
    season_palette = {"Autumn": "darkorange", "Summer": "yellow", "Winter":"lightskyblue", 'Spring':'lightgreen'}
    sns.boxplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  hue='season', dodge=True, palette = season_palette)       

def plot_boxplot_by_duration(data, duration, ax, color_mapping):
    
        h1 = data[data['dur_for_which_this_is_amax'].apply(
            lambda x: isinstance(x, list) and str(1) in x or x == str(1))] 
        h6 = data[data['dur_for_which_this_is_amax'].apply(
            lambda x: isinstance(x, list) and str(6) in x or x == str(6))] 
        h24 = data[data['dur_for_which_this_is_amax'].apply(
            lambda x: isinstance(x, list) and str(24) in x or x == str(24))]        
        
        test=pd.concat([h1,h6,h24])
        
        print(len(this_duration))
        sns.boxplot(ax=ax, data=test, x='Loading_profile_molly',
            y='D50',  hue='dur_for_which_this_is_amax', dodge=True)   
        
        ax.set_xlabel('Quintile classification', fontsize=15)
        if duration =='1':
            ax.set_ylabel("$D_{50}$", fontsize=15)        
    
    

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
    if split_variable == 'D50_loading': 
        the_ls = [the_ls[0]] + [x * 3 for x in the_ls[1:]]

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
                text.set_fontsize(17)
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
    gb_outline.plot(ax=ax, color='darkgrey', edgecolor='black', linewidth=1)
    
    # Scatter plot for the specified value column
    scatter = ax.scatter(lon, lat, c=data[value_column], cmap=cmap, edgecolor=None, alpha=0.9, s=5, marker='o',
                         vmin =vmin, vmax=vmax)
    ax.set_title(title)
    #ax.set_xlabel('Longitude')
    #ax.set_ylabel('Latitude')
    ax.set_xticklabels([]); ax.set_yticklabels([])
    
    # Create a color bar that is scaled to the size of the plot
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)  # Control the width and padding of the colorbar
    plt.colorbar(scatter, cax=cax)   
     
    
def make_plot(df_changes_all, df_changes_byduration, variable, cmap, low_lim=None, high_lim=None):
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    fig, axes = plt.subplots(3, 4, figsize=(16, 11))

    #################################################
    # Shift January Days in Both Present and Future
    #################################################
    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'
    
    #################################################
    # Determine Color Limits Based on Both Datasets
    #################################################
    if high_lim is None:
        low_lim = min(df_changes_all[variable_present].min(), df_changes_all[variable_present].min(), 
                      df_changes_byduration[variable_future].min(), df_changes_byduration[variable_future].min())
        # low_lim = 45

        high_lim = max(df_changes_all[variable_present].max(), df_changes_all[variable_present].max(), 
                      df_changes_byduration[variable_future].max(), df_changes_byduration[variable_future].max())   
        # high_lim=55

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    # Using the adjusted `low_lim` and `high_lim`
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_present]]
        plot_values_on_map(axes[0, i], this_duration, f'{duration}h', tbo_vals, variable_present, low_lim, high_lim, cmap)

    # Plot 'All' present values
    plot_values_on_map(axes[0, 3], df_changes_all[['gauge_num', variable_present]], 'All', tbo_vals, variable_present, low_lim, high_lim, cmap)

    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_future]]
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, variable_future, low_lim, high_lim, cmap)

    # Plot 'All' future values
    plot_values_on_map(axes[1, 3], df_changes_all[['gauge_num', variable_future]], 'All', tbo_vals, variable_future, low_lim, high_lim, cmap)

    #################################################
    # Plot Difference Data if Available
    #################################################
    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()))
    high_lim_diff = max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()))
    
    print(low_lim_diff)
    print(high_lim_diff)

    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_diff]]
        plot_values_on_map(axes[2, i], this_duration, f'{duration}h', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    # Plot 'All' differences
    plot_values_on_map(axes[2, 3], df_changes_all[['gauge_num', variable_diff]], 'All', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    fig.text(0.08, 0.750, 'Present', va='center', ha='center', fontsize=12, rotation='horizontal')
    fig.text(0.08, 0.5, 'Future', va='center', ha='center', fontsize=12, rotation='horizontal')
    fig.text(0.08, 0.22, 'Difference', va='center', ha='center', fontsize=12, rotation='horizontal')


def make_plot_D(df_changes_all, df_changes_byduration, variable, cmap, low_lim=None, high_lim=None):
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    fig, axes = plt.subplots(3, 4, figsize=(16, 11))

    #################################################
    # Shift January Days in Both Present and Future
    #################################################
    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'
    
    #print('All')
    #print(df_changes_all[variable_present].min())
    #print(df_changes_all[variable_present].max())
    
    #print('By duration')
    #print(df_changes_byduration[variable_present].min())
    #print(df_changes_byduration[variable_present].max())
    
    # Apply the transformation to both present and future values
    df_changes_all[variable_present] = df_changes_all[variable_present].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all[variable_future] = df_changes_all[variable_future].apply(lambda x: x + 365 if x < 50 else x)
    
    df_changes_byduration[variable_present] = df_changes_byduration[variable_present].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration[variable_future] = df_changes_byduration[variable_future].apply(lambda x: x + 365 if x < 50 else x)
    
    #print('All')
    #print(df_changes_all[variable_present].min())
    #print(df_changes_all[variable_present].max())    
    
    #print('By duration')
    #print(df_changes_byduration[variable_present].min())
    #print(df_changes_byduration[variable_present].max())
    
    #################################################
    # Determine Color Limits Based on Both Datasets
    #################################################
    if high_lim is None:
        low_lim = min(df_changes_all[variable_present].min(), df_changes_all[variable_present].min(), 
                      df_changes_byduration[variable_future].min(), df_changes_byduration[variable_future].min())

        high_lim = max(df_changes_all[variable_present].max(), df_changes_all[variable_present].max(), 
                      df_changes_byduration[variable_future].max(), df_changes_byduration[variable_future].max())   
        

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    # Using the adjusted `low_lim` and `high_lim`
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_present]]
        plot_values_on_map(axes[0, i], this_duration, f'{duration}h', tbo_vals, variable_present, low_lim, high_lim, cmap)

    # Plot 'All' present values
    plot_values_on_map(axes[0, 3], df_changes_all[['gauge_num', variable_present]], 'All', tbo_vals, variable_present, low_lim, high_lim, cmap)

    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_future]]
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, variable_future, low_lim, high_lim, cmap)

    # Plot 'All' future values
    plot_values_on_map(axes[1, 3], df_changes_all[['gauge_num', variable_future]], 'All', tbo_vals, variable_future, low_lim, high_lim, cmap)

    #################################################
    # Plot Difference Data if Available
    #################################################
    variable_diff = f'{variable}_diff_new'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()))
    high_lim_diff = max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()))

    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_diff]]
        plot_values_on_map(axes[2, i], this_duration, f'{duration}h', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    # Plot 'All' differences
    plot_values_on_map(axes[2, 3], df_changes_all[['gauge_num', variable_diff]], 'All', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    fig.text(0.08, 0.750, 'Present', va='center', ha='center', fontsize=12, rotation='horizontal')
    fig.text(0.08, 0.5, 'Future', va='center', ha='center', fontsize=12, rotation='horizontal')
    fig.text(0.08, 0.22, 'Difference', va='center', ha='center', fontsize=12, rotation='horizontal')



# Define the function to categorize ages
def categorise_D50(D50):
    if D50 > 50:
        return 'B'
    else:
        return 'F'
    
    
def create_heatmap (ax_count, ax_count2, ax_heatmap, df, cmap, color):
    # 1. Define bins for 'D50'
    D50_bins = np.linspace(df['D50_new'].min(), df['D50_new'].max(), 10) 

    # 2. Create a 2D histogram to count events for each D50 vs D combination
    hist, D50_edges, D_edges = np.histogram2d(df['D50_new'].values, df['D'].values, bins=[D50_bins, np.arange(0, 366)])

    # Example histogram creation (already done in previous code)
    D_counts = hist.sum(axis=0)  # Total number of events per day (summed across all D50 bins)
    normalized_hist = np.divide(hist, D_counts, where=D_counts!=0)  # Avoid division by zero

    # 2. Plot the event counts (number of events per day) as a line plot on the first subplot
    ax_count.bar(np.arange(0, 365), D_counts, color=color, linewidth=2, width=1)
    ax_count.set_ylabel('Events count', fontsize=20)
    
    vals, counts = np.unique(df['D'], return_counts=True)
    df=pd.DataFrame({'Day':vals, 'counts':counts})
    ax_count2.bar(np.arange(0, len(df['counts'])), df['counts'], color='red', linewidth=2, width=1)
    
    # 3. Plot the normalized 2D histogram (proportions per day) as a heatmap on the second subplot
    cax = ax_heatmap.imshow(normalized_hist, origin='lower', aspect='auto', extent=[0, 365, D50_bins[0], D50_bins[-1]], 
                            cmap=cmap)

    # Add colorbar to the heatmap
    # cbar = fig.colorbar(cax, ax=ax_heatmap)
    # cbar.set_label('Proportion of Events')

    # 4. Label the heatmap axes
    ax_heatmap.set_xlabel('Day of Year (D)', fontsize=20)
    ax_heatmap.set_ylabel('D50', fontsize=20)
    # ax_heatmap.set_title('Proportion of Events by Day of Year and D50')

    ax_heatmap.tick_params(axis='both', which='major', labelsize=15)  
    ax_count.tick_params(axis='both', which='major', labelsize=15)  

    # Tight layout for better spacing between plots
    plt.tight_layout() 
    
def plot_contour(ax, data_x, data_y, x_label, y_label, title, cmap='Blues'):
    
    if x_label == "Day of year":
        data_x = data_x.apply(lambda x: x + 365 if x < 50 else x)
    
    # Create a grid for the contour plot
    x_grid = np.linspace(data_x.min(), data_x.max(), 100)
    y_grid = np.linspace(data_y.min(), data_y.max(), 100)
    X, Y = np.meshgrid(x_grid, y_grid)

    # Perform Kernel Density Estimation (KDE)
    kde = gaussian_kde([data_x, data_y])
    Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)

    # Normalize the density values to be between 0 and 1
    Z_normalized = (Z - Z.min()) / (Z.max() - Z.min())

    # Create the contour plot with fixed color limits between 0 and 1
    contour = ax.contourf(X, Y, Z_normalized, levels=10, cmap=cmap, alpha=0.6, vmin=0, vmax=1)
    if title =='All':
        cbar = fig.colorbar(contour, ax=ax)
        cbar.set_label('Density (normalized)')

    # Calculate the R^2 value
    slope, intercept, r_value, p_value, std_err = linregress(data_x, data_y)
    r_squared = r_value**2
    
    if p_value <0.05:
        p_value ='<0.05'
    else:
        p_value = '> 0.05'
    
    # Annotate the R^2 value on the plot
    ax.text(0.95, 0.05, f'$R^2 = {r_squared:.2f}$, $P {p_value}$', transform=ax.transAxes,
            ha='right', va='bottom', fontsize=10, bbox=dict(facecolor='white', alpha=0.6))

    # Set labels
    if title =='1hrs':
        ax.set_ylabel(y_label, fontsize=15)
    if cmap == 'Reds':
        ax.set_xlabel(x_label, fontsize=15)
    if cmap == 'Blues':
        ax.set_title(title, fontsize=15)    
    
def plot_contour_all_events(ax, data_x, data_y, title, cmap='Blues'):
    # Create a grid for the contour plot
    x_grid = np.linspace(data_x.min(), data_x.max(), 100)
    y_grid = np.linspace(data_y.min(), data_y.max(), 100)
    X, Y = np.meshgrid(x_grid, y_grid)

    # Perform Kernel Density Estimation (KDE)
    kde = gaussian_kde([data_x, data_y])
    Z = kde(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)

    # Normalize the density values to be between 0 and 1
    Z_normalized = (Z - Z.min()) / (Z.max() - Z.min())

    # Create the contour plot with fixed color limits between 0 and 1
    contour = ax.contourf(X, Y, Z_normalized, levels=10, cmap=cmap, alpha=0.6, vmin=0, vmax=1)
#     cbar = fig.colorbar(contour, ax=ax)
#     cbar.set_label('Density (normalized)')

    # Calculate R^2 and p-value
    slope, intercept, r_value, p_value, std_err = linregress(data_x, data_y)
    r_squared = r_value**2

    # Set labels and title
    # ax.set_xlabel('%' if ax in [axs[1, 0], axs[1, 1]] else '')
    ax.set_ylabel("$D_{50}$",fontsize=18)
    ax.set_xlim(0,366)
    ax.set_ylim(0,6)
    
        