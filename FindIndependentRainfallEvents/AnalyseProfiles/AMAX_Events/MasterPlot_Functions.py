import pandas as pd
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
import geopandas as gpd
import matplotlib.pyplot as plt
from statsmodels.graphics.mosaicplot import mosaic
import seaborn as sns
from scipy.stats import gaussian_kde
from scipy.stats import gaussian_kde, linregress
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
from matplotlib.colors import LinearSegmentedColormap
from scipy.stats import ks_2samp
import datetime as dt
import matplotlib.colors as mcolors
from matplotlib.ticker import FixedLocator, FixedFormatter, FormatStrFormatter, PercentFormatter, ScalarFormatter, MaxNLocator, LogLocator

# Filter for Great Britain
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gb_outline = gdf[(gdf.name == "United Kingdom")]

home_dir = '/nfs/a319/gy17m2a/PhD/'

tbo_vals = pd.read_csv(home_dir + 'datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
tbo_vals = tbo_vals[tbo_vals['Lon']!=-999.0]
tbo_vals['gauge_num'] = tbo_vals.index


def make_scatter_plot_onevariable(df_changes_byduration, df_changes_all, variable, label):
    
    durations =[1,6,24]

    df_changes_all_test =df_changes_all.copy()
    df_changes_byduration_test = df_changes_byduration.copy()
    
    df_changes_all_test["D_mean_present"] = df_changes_all_test["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all_test["D_mean_future"] = df_changes_all_test["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey='all', sharex='all', gridspec_kw={'hspace': 0.05, 'wspace':0.14})
    
    for ax_num, (duration, title) in enumerate(zip(durations, durations )):
        this_duration = df_changes_byduration_test[df_changes_byduration_test['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_present', 'D_mean_present']]
        this_duration["D_mean_present"] = this_duration["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
        make_point_density_plot(axes[0, ax_num], this_duration["D_mean_present"], this_duration[f'{variable}_present'], title)
    make_point_density_plot(axes[0, 3], df_changes_all_test["D_mean_present"], df_changes_all_test[f'{variable}_present'], 'All')
    fig.text(0.04, 0.7, 'Present', va='center', ha='center', fontsize=18, rotation='horizontal');
    
    for ax_num, (duration, title) in enumerate(zip(durations, durations)):
        this_duration = df_changes_byduration_test[df_changes_byduration_test['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_future', 'D_mean_future']]
        this_duration["D_mean_future"] = this_duration["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
        make_point_density_plot(axes[1, ax_num], this_duration["D_mean_future"], this_duration[f'{variable}_future'], title)
    make_point_density_plot(axes[1, 3], df_changes_all_test["D_mean_future"], df_changes_all_test[f'{variable}_future'], 'All')
    fig.text(0.04, 0.3, 'Future', va='center', ha='center', fontsize=18, rotation='horizontal');   
    
    
    axes[0, 0].set_ylabel(label, fontsize=12)
    axes[1, 0].set_ylabel(label, fontsize=12)
    
    # After plotting, convert Julian day ticks to calendar dates
    for ax in axes.flatten():
        
        if ax is not None:  # In case of unused subplots
            # Get the current axis limits
            x_min, x_max = ax.get_xlim()

            # Restrict ticks to the visible range
            ticks = ax.get_xticks()
            visible_ticks = [tick for tick in ticks if x_min <= tick <= x_max]

            # Convert the visible ticks to date labels
            tick_labels = [julian_to_date(int(tick)) for tick in visible_ticks]

            # Apply the visible ticks and corresponding labels
            ax.set_xticks(visible_ticks)  # Restrict ticks to the visible range
            ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))  # Set formatted labels
            ax.tick_params(axis='x', rotation=45)  # Rotate labels for better visibility

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # 2 decimal places

def make_point_density_plot(ax, data_x, data_y, title):
    # Calculate point density
    xy = np.vstack([data_x, data_y])
    density = gaussian_kde(xy)(xy)

    # Scatter plot with density-based coloring
    sc = ax.scatter(
        data_x, 
        data_y, 
        c=density, 
        cmap='viridis', 
        s=10, 
        alpha=0.7
    )

    # Linear regression for the line of best fit
    slope, intercept, r_value, p_value, std_err = linregress(data_x, data_y)

    # Generate the best-fit line
    x_line = np.linspace(min(data_x), max(data_x), 500)
    y_line = slope * x_line + intercept
    ax.plot(x_line, y_line, color='black')

    # Annotate with R² and p-value
    r_squared = r_value ** 2
    
    if p_value <0.05:
        p_value ='<0.05'
    else:
        p_value = '> 0.05'
    
    ax.text(
        0.05, 0.95, 
        f"$R^2$ = {r_squared:.2f}, $p$ {p_value}", 
        transform=ax.transAxes, 
        fontsize=10, 
        verticalalignment='top',
        bbox=dict(facecolor='white', alpha=0.6)
    )
    
    ax.set_title(title)


    return sc


def make_scatter_plot(df, duration, timeperiod, loadings, axes, ax_row):
    df["D_mean_present"] = df["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
    df["D_mean_future"] = df["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
    
    for ax_num, (loading, title) in enumerate(zip(loadings, loadings)):
        title = title if ax_row in[0,5] else ''
        
        if duration in [1, 6, 24]:
            this_duration = df[df['sampling_duration'] == float(duration)]
            make_point_density_plot(
                axes[ax_row][ax_num],  # Updated indexing
                this_duration[f"D_mean_{timeperiod}"],
                this_duration[f"{loading}_percentage_{timeperiod}"],
                title
            )
        else:
            make_point_density_plot(
                axes[ax_row][ax_num],  # Updated indexing
                df[f"D_mean_{timeperiod}"],
                df[f"{loading}_percentage_{timeperiod}"],
                title
            )


def julian_to_date(julian_day):
    """Convert Julian day to calendar date."""
    base_date = datetime(2000, 1, 1)  # Use an arbitrary base year for reference
    return (base_date + timedelta(days=julian_day - 1)).strftime('%d %b')  # Format as '1 Feb', '21 Mar', etc.

def plot_contour(fig, ax, data_x, data_y, x_label, y_label, title, cmap='Blues'):
    
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
    contour = ax.contourf(X, Y, Z_normalized, levels=15, cmap=cmap, alpha=0.6, vmin=0, vmax=1)
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
        
def make_scatter_plot_one_duration(df_changes_byduration, df_changes_all, duration):
    
    loadings =['B2', 'B1', 'C', 'F1', 'F2']
    
    if duration in [1,6,24]:
        df = df_changes_byduration.copy()
    else:
        df = df_changes_all.copy()
    
    df["D_mean_present"] = df["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
    df["D_mean_future"] = df["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
    
    fig, axes = plt.subplots(2, 5, figsize=(16, 8), sharey='all', sharex='all', gridspec_kw={'hspace': 0.05, 'wspace':0.14})
    
    for ax_num, (loading, title) in enumerate(zip(loadings, loadings)):
        if duration in [1,6,24]:
            this_duration = df[df['sampling_duration'] == float(duration)][['gauge_num', f'{loading}_percentage_present', 'D_mean_present']]
            make_point_density_plot(axes[0, ax_num], this_duration["D_mean_present"], this_duration[f'{loading}_percentage_present'], title)
        else:
            make_point_density_plot(axes[0, ax_num], df["D_mean_present"], df[f'{loading}_percentage_present'], title)
    fig.text(0.04, 0.7, 'Present', va='center', ha='center', fontsize=18, rotation='horizontal');
    
    for ax_num, (loading, title) in enumerate(zip(loadings, loadings)):
        if duration in [1,6,24]:
            this_duration = df[df['sampling_duration'] == float(duration)][['gauge_num', f'{loading}_percentage_future', 'D_mean_future']]
            make_point_density_plot(axes[1, ax_num], this_duration["D_mean_future"], this_duration[f'{loading}_percentage_future'], '')
        else:
            make_point_density_plot(axes[1, ax_num], df["D_mean_future"], df[f'{loading}_percentage_future'], '')
    fig.text(0.04, 0.3, 'Future', va='center', ha='center', fontsize=18, rotation='horizontal');   
    
    
    # After plotting, convert Julian day ticks to calendar dates
    for ax in axes.flatten():
        if ax is not None:  # In case of unused subplots
            # Get the current axis limits
            x_min, x_max = ax.get_xlim()

            # Restrict ticks to the visible range
            ticks = ax.get_xticks()
            visible_ticks = [tick for tick in ticks if x_min <= tick <= x_max]

            # Convert the visible ticks to date labels
            tick_labels = [julian_to_date(int(tick)) for tick in visible_ticks]

            # Apply the visible ticks and corresponding labels
            ax.set_xticks(visible_ticks)  # Restrict ticks to the visible range
            ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))  # Set formatted labels
            ax.tick_params(axis='x', rotation=45)  # Rotate labels for better visibility

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # 2 decimal places
        
    fig.suptitle(f"{duration} hours", fontsize =20)

def make_contour_plot(df_changes_byduration, df_changes_all, variable):
    
    durations =[1,6,24]

    df_changes_all_test =df_changes_all.copy()
    df_changes_byduration_test = df_changes_byduration.copy()
    
    df_changes_all_test["D_mean_present"] = df_changes_all_test["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all_test["D_mean_future"] = df_changes_all_test["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), sharey=False, sharex=False, gridspec_kw={'hspace': 0.2, 'wspace':0.14})
    
    for ax_num, (duration, title) in enumerate(zip(durations, durations)):
        this_duration = df_changes_byduration_test[df_changes_byduration_test['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_present', 'D_mean_present']]
        this_duration["D_mean_present"] = this_duration["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
        plot_contour(fig, axes[0, ax_num], this_duration['D_mean_present'],this_duration[f'{variable}_present'], "Day of year", f"{variable[:2]} %", f"{duration}hrs" )
    plot_contour(fig, axes[0, 3], df_changes_all_test["D_mean_present"],  df_changes_all_test[f'{variable}_present'],"Day of year", f"{variable[:2]} %", "All"  )
    fig.text(0.04, 0.7, 'Present', va='center', ha='center', fontsize=18, rotation='horizontal');
    
    for ax_num, (duration, title) in enumerate(zip(durations, titles)):
        this_duration = df_changes_byduration_test[df_changes_byduration_test['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_future', 'D_mean_future']]
        this_duration["D_mean_future"] = this_duration["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
        plot_contour(fig, axes[1, ax_num], this_duration['D_mean_future'], this_duration[f'{variable}_future'], "Day of year", f"{variable[:2]} %" , f"{duration}hrs", 'Reds')   
    plot_contour(fig, axes[1, 3], df_changes_all_test['D_mean_future'], df_changes_all_test[f'{variable}_future'],  "Day of year", f"{variable[:2]} %" ,"All" , 'Reds')
    fig.text(0.04, 0.3, 'Future', va='center', ha='center', fontsize=18, rotation='horizontal');   

    # After plotting, convert Julian day ticks to calendar dates
    for ax in axes.flatten():
        if ax is not None:  # In case of unused subplots
            # Get the current axis limits
            x_min, x_max = ax.get_xlim()

            # Restrict ticks to the visible range
            ticks = ax.get_xticks()
            visible_ticks = [tick for tick in ticks if x_min <= tick <= x_max]

            # Convert the visible ticks to date labels
            tick_labels = [julian_to_date(int(tick)) for tick in visible_ticks]

            # Apply the visible ticks and corresponding labels
            ax.set_xticks(visible_ticks)  # Restrict ticks to the visible range
            ax.xaxis.set_major_formatter(FixedFormatter(tick_labels))  # Set formatted labels
            ax.tick_params(axis='x', rotation=45)  # Rotate labels for better visibility

        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # 2 decimal places





# Function to calculate the month from the day of the year
def get_month_from_doy(day_of_year):
    # Special case: if day_of_year < 0.5, round to 365
    if day_of_year < 0.5:
        day_of_year = 365
    else:
        # Otherwise, round to the nearest integer
        day_of_year = int(round(day_of_year))
    
    # Ensure it fits within valid range for day-of-year (1-365)
    if not 1 <= day_of_year <= 365:
        raise ValueError(f"Invalid day-of-year: {day_of_year}")
    
    # Create a date assuming a non-leap year (e.g., 2023)
    date = dt.datetime.strptime(str(day_of_year), '%j')
    return date.month

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
    
    
def plot_values_on_map_withsig(ax, data, title, tbo_vals, value_column, vmin, vmax, cmap='viridis'):
    # Extract location data for plotting
    gauge_locs = data['gauge_num'].copy()
    lon = tbo_vals.loc[gauge_locs, 'Lon']
    lat = tbo_vals.loc[gauge_locs, 'Lat']
    
    # Plot the background outline of Great Britain
    gb_outline.plot(ax=ax, color='darkgrey', edgecolor='black', linewidth=1)
    
    # Identify points with and without significant values
    significant_points = data[data['sig'] == 1]
    nonsignificant_points = data[data['sig'] != 1]
    
    # Plot nonsignificant points without an outline
    ax.scatter(
        tbo_vals.loc[nonsignificant_points['gauge_num'], 'Lon'],
        tbo_vals.loc[nonsignificant_points['gauge_num'], 'Lat'],
        c=nonsignificant_points[value_column], cmap=cmap, edgecolor=None, alpha=0.9, s=10, marker='o',
        vmin=vmin, vmax=vmax
    )
    
    # Plot significant points with a black outline
    scatter = ax.scatter(
        tbo_vals.loc[significant_points['gauge_num'], 'Lon'],
        tbo_vals.loc[significant_points['gauge_num'], 'Lat'],
        c=significant_points[value_column], cmap=cmap, edgecolor='black', linewidth=1, alpha=0.9, s=20, marker='o',
        vmin=vmin, vmax=vmax
    )
    
    # Set title and remove axis tick labels
    if 'present' in value_column:
        ax.set_title(title, fontsize=20)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    return scatter


def plot_values_on_map(ax, data, title, tbo_vals, value_column, vmin, vmax, cmap='viridis'):
    gauge_locs = data['gauge_num'].copy()
    lon = tbo_vals.loc[gauge_locs, 'Lon']
    lat = tbo_vals.loc[gauge_locs, 'Lat']

    # Plot the background outline of Great Britain
    gb_outline.plot(ax=ax, color='darkgrey', edgecolor='black', linewidth=1)

    # Scatter plot for the specified value column
    scatter = ax.scatter(
        lon, lat, c=data[value_column], cmap=cmap, edgecolor=None, alpha=1, s=10, marker='o',
        vmin=vmin, vmax=vmax)
    if 'present' in value_column:
        ax.set_title(title, fontsize=20)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    return scatter
    
def make_plot(df_changes_all, df_changes_byduration, variable, cmap, diffs_dict, low_lim=None, high_lim=None):
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    df_changes_all['sig'] = diffs_dict['All']
    
    fig, axes = plt.subplots(3, 4, figsize=(16, 13))

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
        # low_lim = 45.5

        high_lim = max(df_changes_all[variable_present].max(), df_changes_all[variable_present].max(), 
                      df_changes_byduration[variable_future].max(), df_changes_byduration[variable_future].max())   
        # high_lim=54.5

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    # Using the adjusted `low_lim` and `high_lim`
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_present]]
        plot_values_on_map(axes[0, i], this_duration, f'{duration}h', tbo_vals, variable_present, low_lim, high_lim, cmap)

    # Plot 'All' present values
    scatter = plot_values_on_map(axes[0, 3], df_changes_all[['gauge_num', variable_present]], 'All', tbo_vals, variable_present, low_lim, high_lim, cmap)

    cbar_ax = fig.add_axes([1.005, 0.685, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16) 
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_future]]
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, variable_future, low_lim, high_lim, cmap)

    # Plot 'All' future values
    scatter = plot_values_on_map(axes[1, 3], df_changes_all[['gauge_num', variable_future]], 'All', tbo_vals, variable_future, low_lim, high_lim, cmap)
    cbar_ax = fig.add_axes([1.005, 0.368, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16) 
    
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    #################################################
    # Plot Difference Data if Available
    #################################################
    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()),
                        abs(df_changes_byduration[variable_diff].min()), abs(df_changes_byduration[variable_diff].max()))
    low_lim_diff=-6
    high_lim_diff = -low_lim_diff

    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_diff']]
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        this_duration['sig'] =diffs_dict[duration] 
        scatter = plot_values_on_map_withsig(axes[2, i], this_duration, f'{duration}h', tbo_vals, f'{variable}_diff',
                                             low_lim_diff, high_lim_diff, 'bwr')
    
    # Plot 'All' differences
    scatter = plot_values_on_map_withsig(axes[2, 3], df_changes_all[['gauge_num', variable_diff, 'sig']], 'All', tbo_vals,
                                         variable_diff, low_lim_diff, high_lim_diff, 'bwr')    
    
    # Create the colorbar in this new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16) 
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')
    
    plt.subplots_adjust(hspace=-0.05)
    
    plt.tight_layout()
    
def find_significance_of_differences (present, future, variable):
    
    diffs_dict={}
    gauge_nums=[]
    
    present['D'] = present['D'].apply(lambda x: x + 365 if x < 50 else x)
    future['D'] = future['D'].apply(lambda x: x + 365 if x < 50 else x)

    for dur in ['All', 1,6,24]:
        # print(dur)
        present_data = present[present['dur_for_which_this_is_amax'].apply(
            lambda x: isinstance(x, list) and str(dur) in x or x == str(dur))]
        future_data = future[future['dur_for_which_this_is_amax'].apply(
            lambda x: isinstance(x, list) and str(dur) in x or x == str(dur))]

        if dur == 'All':
            present_data = present
            future_data = future

        diff = []
        for gauge_num in range(0,1294):
            if gauge_num not in [444,827,888]:
                if dur == 1:
                    gauge_nums.append(gauge_num)

                this_g_present = present_data[present_data['gauge_num'] == gauge_num]
                this_g_future = future_data[future_data['gauge_num'] == gauge_num]

                # Perform KS test
                ks_stat, p_value = ks_2samp(this_g_present[variable], this_g_future[variable])

                if p_value < 0.05:
                    diff.append(1)
                else:
                    diff.append(0) 
        diffs_dict[dur]=diff
    
    df = pd.DataFrame({'gauge_num':gauge_nums, 'Sig_Diff_1h':np.array(diffs_dict[1]),
                    'Sig_Diff_6h':np.array(diffs_dict[6]), 'Sig_Diff_24h':np.array(diffs_dict[24]),
                      'Sig_Diff_All':np.array(diffs_dict['All'])})    
    
    return df, diffs_dict

def day_to_date(day_of_year):
    # Handle days from 1 to 365 (current year)
    if day_of_year <= 365:
        # Convert to current year's date
        start_date = datetime(datetime.now().year, 1, 1)  # Start of the current year
        date = start_date + timedelta(days=day_of_year - 1)  # Subtract 1 to get correct date
    else:
        # Handle days beyond 365 (next year's January)
        day_of_year -= 365  # Adjust to start from 1 (for next January)
        start_date = datetime(datetime.now().year + 1, 1, 1)  # Start of the next year
        date = start_date + timedelta(days=day_of_year - 1)  # Subtract 1 to get correct date
    
    return date.strftime('%d %b')  # Format the date as "01 February"

def make_plot_durcats(df_changes_all, df_changes_byduration, variable, cmap, diffs_dict, low_lim=None, high_lim=None):
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    df_changes_all['sig'] = diffs_dict['All']
    
    fig, axes = plt.subplots(3, 5, figsize=(16, 10))

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

        high_lim = max(df_changes_all[variable_present].max(), df_changes_all[variable_present].max(), 
                      df_changes_byduration[variable_future].max(), df_changes_byduration[variable_future].max())   

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    # Using the adjusted `low_lim` and `high_lim`
    for i, duration in enumerate(['0.25-2.10 hr','2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration][['gauge_num', variable_present]]        
        plot_values_on_map(axes[0, i], this_duration, f'{duration}h', tbo_vals, variable_present, low_lim, high_lim, cmap)

    # Plot 'All' present values
    scatter = plot_values_on_map(axes[0, 4], df_changes_all[['gauge_num', variable_present]], 'All', tbo_vals, variable_present, low_lim, high_lim, cmap)

    cbar_ax = fig.add_axes([1.005, 0.685, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16) 
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate(['0.25-2.10 hr','2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration][['gauge_num', variable_future]]
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, variable_future, low_lim, high_lim, cmap)

    # Plot 'All' future values
    scatter = plot_values_on_map(axes[1, 4], df_changes_all[['gauge_num', variable_future]], 'All', tbo_vals, variable_future, low_lim, high_lim, cmap)
    cbar_ax = fig.add_axes([1.005, 0.368, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16) 
    
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    #################################################
    # Plot Difference Data if Available
    #################################################
    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()),
                        abs(df_changes_byduration[variable_diff].min()), abs(df_changes_byduration[variable_diff].max()))
    # low_lim_diff=-6
    high_lim_diff = -low_lim_diff

    for i, duration in enumerate(['0.25-2.10 hr','2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration][['gauge_num',  f'{variable}_diff']]
        
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        scatter = plot_values_on_map(axes[2, i], this_duration, f'{duration}h', tbo_vals, f'{variable}_diff',
                                             low_lim_diff, high_lim_diff, 'bwr')
    
    # Plot 'All' differences
    scatter = plot_values_on_map(axes[2, 4], df_changes_all[['gauge_num', variable_diff, 'sig']], 'All', tbo_vals,
                                         variable_diff, low_lim_diff, high_lim_diff, 'bwr')    
    
    # Create the colorbar in this new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16) 
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')
    
    plt.subplots_adjust(hspace=-0.05)
    
    plt.tight_layout()
    

def make_plot_D_seasonal_durcats(df_changes_all, df_changes_byduration, variable, diffs_dict):

    colors = [
        "#00adc9",   # January
        "#00a987",   # February
        "#02ae4c",   # March
        "#e3c700",   # April (compressed yellow)
        "#f2a800",   # May (compressed orange)
        "#f97c00",   # June (orange-red)
        "#e93e26",   # July (strong red-orange)
        "#d5005c",   # August (vivid pink)
        "#9a007f",   # September (deep magenta)
        "#323294",   # October
        "#0166b5",   # November
        "#0099df"    # December
    ]
    # Create a ListedColormap with these colors
    month_cmap = mcolors.ListedColormap(colors, name="month_cmap")
    month_cmap = LinearSegmentedColormap.from_list("month_cmap", colors, N=12)

    cmap = month_cmap  # This will give a smoother gradient between June and July
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    # Add sifnificance of changes
    df_changes_all['sig'] = diffs_dict['All']

    fig, axes = plt.subplots(3, 5, figsize=(16, 10))

    #################################################
    # Shift January Days in Both Present and Future
    #################################################
    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    # Using the adjusted `low_lim` and `high_lim`
    
    for i, duration in enumerate(['0.25-2.10 hr','2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration][['gauge_num', variable_present]]
        this_duration['month_present'] = this_duration['D_mean_present'].apply(get_month_from_doy)
        plot_values_on_map(axes[0, i], this_duration, f'{duration}h', tbo_vals, 'month_present', 1, 12, cmap)

    # Plot 'All' present values
    df_changes_all['month_present'] = df_changes_all['D_mean_present'].apply(get_month_from_doy)
    scatter = plot_values_on_map(axes[0, 4], df_changes_all[['gauge_num', variable_present, 'month_present', 'sig']], 'All', tbo_vals,
                                 'month_present', 1, 12, cmap)


    # Define month names
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


    cbar_ax = fig.add_axes([1.005, 0.685, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')

    # Set ticks at the center of each color block
    tick_positions = np.arange(1, 13)  # Values 1 through 12
    cbar.set_ticks(tick_positions)

    # Label each tick with the corresponding month name
    cbar.set_ticklabels(month_labels)

    # Reverse the tick direction to match reversed colorbar
    cbar.ax.invert_yaxis()

    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate(['0.25-2.10 hr','2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration][['gauge_num', variable_future]]
        this_duration['month_future'] = this_duration['D_mean_future'].apply(get_month_from_doy)
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, 'month_future', 1, 12, cmap)

    # Plot 'All' future values
    df_changes_all['month_future'] = df_changes_all['D_mean_future'].apply(get_month_from_doy)
    scatter = plot_values_on_map(axes[1, 4], df_changes_all[['gauge_num', variable_future, 'month_future']], 'All', tbo_vals, 
                                 'month_future', 1, 12, cmap)


    cbar_ax = fig.add_axes([1.005, 0.368, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')

    # Set ticks at the center of each color block
    tick_positions = np.arange(1, 13)  # Values 1 through 12
    cbar.set_ticks(tick_positions)

    # Label each tick with the corresponding month name
    cbar.set_ticklabels(month_labels)

    # Reverse the tick direction to match reversed colorbar
    cbar.ax.invert_yaxis()

    #################################################
    # Plot Difference Data if Available
    #################################################
    # Apply the transformation to both present and future values
    df_changes_all['D_mean_present'] = df_changes_all['D_mean_present'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all['D_mean_future'] = df_changes_all['D_mean_future'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all['D_mean_diff'] = df_changes_all['D_mean_future'] - df_changes_all['D_mean_present']   
    
    df_changes_byduration['D_mean_present'] = df_changes_byduration['D_mean_present'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration['D_mean_future'] = df_changes_byduration['D_mean_future'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration['D_mean_diff'] = df_changes_byduration['D_mean_future'] - df_changes_byduration['D_mean_present']   
    
    # Color map setup for difference plot
    colors = [(0, "blue"), (0.35, "lightblue"), (0.5, "white"), (0.7, "lightcoral"), (1, "red")]
    cmap_diff = LinearSegmentedColormap.from_list("custom_cmap", colors)    

    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()),
                        abs(df_changes_byduration[variable_diff].min()), abs(df_changes_byduration[variable_diff].max()))
    low_lim_diff = -50
    high_lim_diff = -low_lim_diff

    # Plot Difference Data if Available
    for i, duration in enumerate(['0.25-2.10 hr','2.10-6.45 hr', '6.45-19.25 hr', '19.25+ hr']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration][['gauge_num',  f'{variable}_diff']]
        
    #for i, duration in enumerate([1, 6, 24]):
    #    this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_diff']]
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        #this_duration['sig'] =diffs_dict[duration] 
        scatter = plot_values_on_map(axes[2, i], this_duration, f'{duration}h', tbo_vals, f'{variable}_diff', low_lim_diff, high_lim_diff, cmap_diff)

    # Plot 'All' differences
    scatter = plot_values_on_map(axes[2, 4], df_changes_all[['gauge_num', variable_diff, 'sig']], 'All', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    # Create the colorbar in this new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    #cbar.set_label('Difference', fontsize=15)
    cbar.ax.tick_params(labelsize=16) 

    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')

    plt.subplots_adjust(hspace=-0.15)

    plt.tight_layout()
    
    



def make_plot_D_seasonal(df_changes_all, df_changes_byduration, variable, diffs_dict):

    colors = [
        "#00adc9",   # January
        "#00a987",   # February
        "#02ae4c",   # March
        "#e3c700",   # April (compressed yellow)
        "#f2a800",   # May (compressed orange)
        "#f97c00",   # June (orange-red)
        "#e93e26",   # July (strong red-orange)
        "#d5005c",   # August (vivid pink)
        "#9a007f",   # September (deep magenta)
        "#323294",   # October
        "#0166b5",   # November
        "#0099df"    # December
    ]
    # Create a ListedColormap with these colors
    month_cmap = mcolors.ListedColormap(colors, name="month_cmap")
    month_cmap = LinearSegmentedColormap.from_list("month_cmap", colors, N=12)

    cmap = month_cmap  # This will give a smoother gradient between June and July
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    # Add sifnificance of changes
    df_changes_all['sig'] = diffs_dict['All']

    fig, axes = plt.subplots(3, 4, figsize=(16, 13))

    #################################################
    # Shift January Days in Both Present and Future
    #################################################
    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    # Using the adjusted `low_lim` and `high_lim`
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_present]]
        this_duration['month_present'] = this_duration['D_mean_present'].apply(get_month_from_doy)
        plot_values_on_map(axes[0, i], this_duration, f'{duration}h', tbo_vals, 'month_present', 1, 12, cmap)

    # Plot 'All' present values
    df_changes_all['month_present'] = df_changes_all['D_mean_present'].apply(get_month_from_doy)
    scatter = plot_values_on_map(axes[0, 3], df_changes_all[['gauge_num', variable_present, 'month_present', 'sig']], 'All', tbo_vals,
                                 'month_present', 1, 12, cmap)


    # Define month names
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


    cbar_ax = fig.add_axes([1.005, 0.685, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')

    # Set ticks at the center of each color block
    tick_positions = np.arange(1, 13)  # Values 1 through 12
    cbar.set_ticks(tick_positions)

    # Label each tick with the corresponding month name
    cbar.set_ticklabels(month_labels)

    # Reverse the tick direction to match reversed colorbar
    cbar.ax.invert_yaxis()

    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_future]]
        this_duration['month_future'] = this_duration['D_mean_future'].apply(get_month_from_doy)
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, 'month_future', 1, 12, cmap)

    # Plot 'All' future values
    df_changes_all['month_future'] = df_changes_all['D_mean_future'].apply(get_month_from_doy)
    scatter = plot_values_on_map(axes[1, 3], df_changes_all[['gauge_num', variable_future, 'month_future']], 'All', tbo_vals, 
                                 'month_future', 1, 12, cmap)


    cbar_ax = fig.add_axes([1.005, 0.368, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')

    # Set ticks at the center of each color block
    tick_positions = np.arange(1, 13)  # Values 1 through 12
    cbar.set_ticks(tick_positions)

    # Label each tick with the corresponding month name
    cbar.set_ticklabels(month_labels)

    # Reverse the tick direction to match reversed colorbar
    cbar.ax.invert_yaxis()

    #################################################
    # Plot Difference Data if Available
    #################################################
    # Apply the transformation to both present and future values
    df_changes_all['D_mean_present'] = df_changes_all['D_mean_present'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all['D_mean_future'] = df_changes_all['D_mean_future'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all['D_mean_diff'] = df_changes_all['D_mean_future'] - df_changes_all['D_mean_present']   
    
    df_changes_byduration['D_mean_present'] = df_changes_byduration['D_mean_present'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration['D_mean_future'] = df_changes_byduration['D_mean_future'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration['D_mean_diff'] = df_changes_byduration['D_mean_future'] - df_changes_byduration['D_mean_present']   
    
    # Color map setup for difference plot
    colors = [(0, "blue"), (0.35, "lightblue"), (0.5, "white"), (0.7, "lightcoral"), (1, "red")]
    cmap_diff = LinearSegmentedColormap.from_list("custom_cmap", colors)    

    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()),
                        abs(df_changes_byduration[variable_diff].min()), abs(df_changes_byduration[variable_diff].max()))
    low_lim_diff = -50
    high_lim_diff = -low_lim_diff

    # Plot Difference Data if Available
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_diff']]
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        this_duration['sig'] =diffs_dict[duration] 
        scatter = plot_values_on_map_withsig(axes[2, i], this_duration, f'{duration}h', tbo_vals, f'{variable}_diff', low_lim_diff, high_lim_diff, cmap_diff)

    # Plot 'All' differences
    scatter = plot_values_on_map_withsig(axes[2, 3], df_changes_all[['gauge_num', variable_diff, 'sig']], 'All', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    # Create the colorbar in this new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    #cbar.set_label('Difference', fontsize=15)
    cbar.ax.tick_params(labelsize=16) 

    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')

    plt.subplots_adjust(hspace=-0.05)

    plt.tight_layout()
    
    
def plot_quintile_hist_with_overlap_shading(ax, present_data, future_data, bins, color_present='royalblue', color_future='indianred', overlap_color='lightgray'):
    # Calculate histogram counts and bin edges
    present_counts, bin_edges = np.histogram(present_data, bins=bins)
    future_counts, _ = np.histogram(future_data, bins=bin_edges)  # Use the same bin edges

    # Normalize counts to get proportions
    present_props = present_counts / np.sum(present_counts)
    print(present_props)
    future_props = future_counts / np.sum(future_counts)

    # Plot the histograms for Present and Future with proportions
    ax.hist(present_data, bins=bin_edges, color=color_present, alpha=0.3, edgecolor='black', label="Present", weights=np.ones_like(present_data) / len(present_data))
    ax.hist(future_data, bins=bin_edges, color=color_future, alpha=0.3, edgecolor='black', label="Future", weights=np.ones_like(future_data) / len(future_data))

    # Prepare data for shading by repeating proportions to span full bin widths
    x_values = np.repeat(bin_edges, 2)[1:-1]
    present_props_extended = np.repeat(present_props, 2)
    future_props_extended = np.repeat(future_props, 2)
    overlap_props_extended = np.minimum(present_props_extended, future_props_extended)

    # Shade overlap and non-overlap regions
    ax.fill_between(x_values, 0, overlap_props_extended, color=overlap_color, label="Overlap", alpha=1)
    ax.fill_between(x_values, overlap_props_extended, present_props_extended, where=(present_props_extended > future_props_extended), color=color_present, alpha=1)
    ax.fill_between(x_values, overlap_props_extended, future_props_extended, where=(future_props_extended > present_props_extended), color=color_future, alpha=1)

    
def make_plot_D(df_changes_all, df_changes_byduration, variable, cmap, diffs_dict, low_lim=None, high_lim=None):
    
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    df_changes_all['sig'] = diffs_dict['All']
    
    fig, axes = plt.subplots(3, 4, figsize=(16, 13))

    #################################################
    # Shift January Days in Both Present and Future
    #################################################
    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'
    
    # Apply the transformation to both present and future values
    df_changes_all[variable_present] = df_changes_all[variable_present].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all[variable_future] = df_changes_all[variable_future].apply(lambda x: x + 365 if x < 50 else x)
    
    df_changes_byduration[variable_present] = df_changes_byduration[variable_present].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration[variable_future] = df_changes_byduration[variable_future].apply(lambda x: x + 365 if x < 50 else x)

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
    scatter = plot_values_on_map(axes[0, 3], df_changes_all[['gauge_num', variable_present, 'sig']], 'All', tbo_vals, variable_present, low_lim, high_lim, cmap)

    cbar_ax = fig.add_axes([1.005, 0.685, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    # cbar.set_label('Day of year', fontsize=15)
    
    # Use FuncFormatter to apply the custom date format to the colorbar
    ticks = np.linspace(200, 375, num=6)  # Define ticks, covering both normal days and over 365
    cbar.set_ticks(ticks)  # Set ticks for the colorbar
    cbar.ax.tick_params(labelsize=16) 
    cbar.set_ticklabels([day_to_date(day) for day in ticks])  # Apply custom date formatting
    
#     cbar.set_ticks(np.linspace(190, 365, num=6))  # Set specific ticks
#     cbar.set_ticklabels([day_to_date(day) for day in np.linspace(190, 365, num=6)])  # Apply formatting    
    
    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', variable_future]]
        plot_values_on_map(axes[1, i], this_duration, f'{duration}h', tbo_vals, variable_future, low_lim, high_lim, cmap)

    # Plot 'All' future values
    scatter = plot_values_on_map(axes[1, 3], df_changes_all[['gauge_num', variable_future]], 'All', tbo_vals, variable_future, low_lim, high_lim, cmap)
    
    cbar_ax = fig.add_axes([1.005, 0.368, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    # cbar.set_label('Day of year', fontsize=15)
    
    # Use FuncFormatter to apply the custom date format to the colorbar
    ticks = np.linspace(200, 375, num=6)  # Define ticks, covering both normal days and over 365
    cbar.set_ticks(ticks)  # Set ticks for the colorbar
    cbar.ax.tick_params(labelsize=16) 
    cbar.set_ticklabels([day_to_date(day) for day in ticks])  # Apply custom date formatting
    
    #################################################
    # Plot Difference Data if Available
    #################################################
    # Apply the transformation to both present and future values
    df_changes_all['D_mean_present'] = df_changes_all['D_mean_present'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all['D_mean_future'] = df_changes_all['D_mean_future'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_all['D_mean_diff'] = df_changes_all['D_mean_future'] - df_changes_all['D_mean_present']   
    
    df_changes_byduration['D_mean_present'] = df_changes_byduration['D_mean_present'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration['D_mean_future'] = df_changes_byduration['D_mean_future'].apply(lambda x: x + 365 if x < 50 else x)
    df_changes_byduration['D_mean_diff'] = df_changes_byduration['D_mean_future'] - df_changes_byduration['D_mean_present']   
    
    # Color map setup for difference plot
    colors = [(0, "blue"), (0.35, "lightblue"), (0.5, "white"), (0.7, "lightcoral"), (1, "red")]
    cmap_diff = LinearSegmentedColormap.from_list("custom_cmap", colors)    

    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()),
                        abs(df_changes_byduration[variable_diff].min()), abs(df_changes_byduration[variable_diff].max()))
    low_lim_diff = -80
    high_lim_diff = -low_lim_diff

    # Plot Difference Data if Available
    for i, duration in enumerate([1, 6, 24]):
        this_duration = df_changes_byduration[df_changes_byduration['sampling_duration'] == float(duration)][['gauge_num', f'{variable}_diff']]
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        this_duration['sig'] =diffs_dict[duration] 
        scatter = plot_values_on_map_withsig(axes[2, i], this_duration, f'{duration}h', tbo_vals, f'{variable}_diff', low_lim_diff, high_lim_diff, cmap_diff)

    # Plot 'All' differences
    scatter = plot_values_on_map_withsig(axes[2, 3], df_changes_all[['gauge_num', variable_diff, 'sig']], 'All', tbo_vals, variable_diff, low_lim_diff, high_lim_diff, 'bwr')

    # Create the colorbar in this new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    #cbar.set_label('Difference', fontsize=15)
    cbar.ax.tick_params(labelsize=16) 

    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')

    plt.subplots_adjust(hspace=-0.05)
    
    plt.tight_layout()



# Custom function to format ticks as percentages
def percent_formatter(x, pos):
    return f"{x:.0f}%"  # Format the tick as an integer percentage (no decimals) 

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
    
def plot_contour(fig, ax, data_x, data_y, x_label, y_label, title, cmap='Blues'):
    
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
    
def plot_contour_all_events(ax, data_x, data_y,cmap):
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
#     ax.set_ylim(0,6)
    
def plot_polar_months_plot(df, ax, title_on, title, rmax, name_variable_to_plot, original_D_mean, R):
    """
    Plots a polar bar chart showing monthly data, with an added red line indicating the mean day of the year and its seasonal concentration.
    
    Parameters:
    - df: DataFrame containing the month column to be plotted.
    - ax: Axis object for the plot.
    - title_on: Boolean to toggle the title display.
    - title: Title text for the plot.
    - rmax: Maximum radius of the polar plot.
    - name_variable_to_plot: 'Percentage' or 'Count' to determine the plotted variable.
    - D_mean: Mean day of the year (1-365).
    - R: Seasonal concentration (0 to 1).
    """
    D_mean = 365  - round(original_D_mean,0)
    N = 12
    width = (2 * np.pi) / N
    
    # Define bins and their positions
    circular_bins = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    circular_bins = np.append(circular_bins, 2 * np.pi)
    circular_plot_position = circular_bins + 0.5 * np.diff(circular_bins)[0]
    circular_plot_position = circular_plot_position[:-1]
    circular_plot_position = circular_plot_position + 0.5 * np.pi  # Align to start at March
    
    # Count numbers in each month
    count = df['month'].value_counts().sort_index()
    count = count.reindex(list(range(1, 13)), fill_value=0)  # Ensure all months included

    # Calculate percentage
    total_events = count.sum()
    percentage = (count / total_events) * 100
    
    if name_variable_to_plot == 'Percentage':
        variable_to_plot = percentage
    elif name_variable_to_plot == 'Count':
        variable_to_plot = count
    
    # Define colors for each month (reversed order for clockwise plot)
    colors = [
              '#C2DFFF',  # Jan (Light Blue)
              '#C2DFFF',  # Feb (Very Light Blue)
              '#A8E6CF',  # Mar (Purple)
              '#A8E6CF',  # Apr (Medium Purple)
              '#A8E6CF',  # May (Bright Yellow)
              '#FFD3B6',  # Jun (Red-Orange)
              '#FFD3B6',  # Jul (Tomato Red)
              '#FFD3B6',  # Aug (Dark Orange)
              '#FFABAB',  # Sep (Saddle Brown)
              '#FFABAB',  # Oct (Orange)
              '#FFABAB',# Nov (Dark Goldenrod)
              '#C2DFFF',  # Dec (Dark Blue)
    ]  
#         colors = [
#         "#00adc9",   # January
#         "#00a987",    # February
#         "#02ae4c",    # March
#         "#f6ec08",    # April
#         "#fec20c",    # May
#         "#f46c21",    # June
#         "#ef154a",    # July
#         "#ef0c6a",    # August
#         "#e00882",    # September
#         "#323294",    # October
#         "#0166b5",    # November
#         "#0099df"     # December
#     ]
    
    
    colors.reverse()
    
    # Plot bars
    ax.bar(circular_plot_position, variable_to_plot.iloc[::-1], width=width, color=colors)
    
    # --- Add season separators (black dashed lines) ---
    season_boundaries = [circular_plot_position[0]+5, circular_plot_position[3]+5, circular_plot_position[6]+5, circular_plot_position[9]+5]
#     for boundary in season_boundaries:
#         ax.plot([boundary, boundary], [0, rmax], color='black', linewidth=1, linestyle='--')
    
    # --- Add red line for mean day of the year (D_mean) with length proportional to R ---
    mean_angle = (D_mean / 365) * 2 * np.pi + 0.5 * np.pi  # Convert D_mean to radians
    line_length = R * rmax  # Scaled length based on R value
    
    ax.annotate('', xy=(mean_angle, line_length), xytext=(mean_angle, 0),
            arrowprops=dict(facecolor='black', edgecolor='black', arrowstyle='-|>', linewidth=4))
    
    ax.text(
        0.8, 0.35, 
        f'D: {int(original_D_mean)} \n R: {round(R,2)}',  # D with a line over it and R on a new line
        ha='center', va='center', 
        transform=ax.transAxes, 
        fontsize=12, fontweight='bold'
    )

    # Format plot
    if title_on:
        ax.set_title(title, fontsize=20, pad=50)
    ax.set_rlabel_position(90)
    ax.xaxis.grid(False)
    
    if name_variable_to_plot == 'Percentage':
        ax.set_ylim(0, rmax)
    
    # Set custom labels for months
    ax.set_xticks(circular_plot_position - 0.5 * np.pi)
    ax.set_xticklabels(['Mar', 'Feb', 'Jan', 'Dec', 'Nov', 'Oct', 'Sep', 'Aug', 'Jul', 'Jun', 'May', 'Apr'])

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
    
    # Calculate overlap and exclusive percentages
    overlap_percentage = np.minimum(percentage_present, percentage_future)
    present_only_percentage = percentage_present - overlap_percentage
    future_only_percentage = percentage_future - overlap_percentage

    # Plot the overlapping regions in gray
    
    # Define colors for each dataset
    colors_present = 'royalblue'  # Yellow for present
    colors_future = 'indianred'    # Blue for future

    # Plot percentage for present and future datasets
    ax.bar(circular_plot_position, percentage_present.iloc[::-1], width=width, color=colors_present, alpha=1, label='Present')
    ax.bar(circular_plot_position, percentage_future.iloc[::-1], width=width, color=colors_future, alpha=1, label='Future')
    ax.bar(circular_plot_position, overlap_percentage.iloc[::-1], width=width, color='lightgrey', alpha=1, label='Overlap')
    
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
    
    
def plot_histogram_for_duration(df, variable, duration, duration_variable, ax, bins=25, label=None, color=None, alpha=0.5, density=True):
    # Filter the DataFrame for the specified duration
    duration_data = df[df[duration_variable].apply(
        lambda x: isinstance(x, list) and str(duration) in x or x == str(duration))]
    # Plot histogram for the specified duration with density normalization
    if not duration_data.empty:
        n, bins_used, patches = ax.hist(duration_data[variable], bins=bins, alpha=alpha, label=label, color=color, edgecolor='black', density=density)
    else:
        pass

    # Set y-axis label to the specific duration bin it refers to
    ax.set_ylabel(f"{duration}hrs", fontsize=10, rotation=0)
    # Remove y-tick labels
    # ax.set_yticks([])
    
def plot_histogram(df, variable, duration, duration_variable, ax, bins=25, label=None, color=None, alpha=0.5, density=True):
    # Plot histogram for the specified duration with density normalization
    n, bins_used, patches = ax.hist(df[variable], bins=bins, alpha=alpha, label=label, color=color, edgecolor='black', density=density)

    # Set y-axis label to the specific duration bin it refers to
#     ax.set_ylabel(f"{duration}hrs", fontsize=10, rotation=0)
    # Remove y-tick labels
    # ax.set_yticks([])
        
def plot_histogram_with_shaded_difference_all(present_data, future_data, variable, ax, bins, alpha=0.5):
    # Use logarithmic binning for the x-axis to focus on smaller values
    log_bins = np.logspace(np.log10(min(present_data[variable])), np.log10(max(present_data[variable])), bins)
    
    if variable =='duration':
        # Round each bin to the nearest multiple of 0.5
        log_bins = np.round(log_bins * 2) / 2  # Multiply by 2, round, then divide by 2 to ensure multiples of 0.5

        # Ensure that the bins are sorted correctly (rounding may cause misordering)
        log_bins = np.sort(log_bins)
        log_bins = np.unique(log_bins)
    
    # Calculate histogram bin counts without plotting, to ensure matching shapes
    present_counts, bins_used = np.histogram(present_data[variable], bins=log_bins, density=True)
    future_counts, _ = np.histogram(future_data[variable], bins=log_bins, density=True)
    
    # Plot the histograms for each dataset as step lines (no fill initially)
    ax.hist(present_data[variable], bins=log_bins, alpha=0.3, label="Present", color='grey', edgecolor='black', density=True)
    ax.hist(future_data[variable], bins=log_bins, alpha=0.3, label="Future", color='grey', edgecolor='black', density=True)
    
    # Calculate the bin centers for plotting
    bin_centers = (bins_used[:-1] + bins_used[1:]) / 2

    # Fill the regions where `present` is greater than `future`
    ax.fill_between(bin_centers, present_counts, future_counts, where=(present_counts > future_counts),
                    color='royalblue', alpha=alpha, step='mid', label="Present > Future")
    
    # Optional: fill where `future` is greater than `present` in a different color
    ax.fill_between(bin_centers, present_counts, future_counts, where=(future_counts > present_counts),
                   color="indianred", alpha=alpha, step='mid', label="Future > Present")
    
    # Set the x-axis to logarithmic scale to match the binning
    ax.set_xscale('log')

    # Reduce the number of ticks by manually setting tick positions
    ticks = [1, 2, 5, 10, 20, 50, 100, 200]  # Example ticks
    ax.set_xticks(ticks)

    # Format the x-axis labels with normal numbers (no scientific notation)
    ax.xaxis.set_major_formatter(ScalarFormatter())

    # Rotate tick labels to 45 degrees using tick_params
    ax.tick_params(axis='x', rotation=90)

def plot_histogram_with_shaded_difference(present_data, future_data, variable, duration, duration_variable, ax, bins, alpha=0.5):
    # Filter the DataFrame for the specified duration for each dataset
    present_duration_data = present_data[present_data[duration_variable].apply(
        lambda x: isinstance(x, list) and str(duration) in x or x == str(duration))]
    future_duration_data = future_data[future_data[duration_variable].apply(
        lambda x: isinstance(x, list) and str(duration) in x or x == str(duration))]
    
    # Use logarithmic binning for the x-axis to focus on smaller values
    log_bins = np.logspace(np.log10(min(present_duration_data[variable])), np.log10(max(present_duration_data[variable])), bins)
    
    if variable =='duration':
        # Round each bin to the nearest multiple of 0.5
        log_bins = np.round(log_bins * 2) / 2  # Multiply by 2, round, then divide by 2 to ensure multiples of 0.5

        # Ensure that the bins are sorted correctly (rounding may cause misordering)
        log_bins = np.sort(log_bins)
        log_bins = np.unique(log_bins)
    
    # Calculate histogram bin counts without plotting, to ensure matching shapes
    present_counts, bins_used = np.histogram(present_duration_data[variable], bins=log_bins, density=True)
    future_counts, _ = np.histogram(future_duration_data[variable], bins=log_bins, density=True)
    
    # Plot the histograms for each dataset as step lines (no fill initially)
    ax.hist(present_duration_data[variable], bins=log_bins, alpha=0.3, label="Present", color='grey', edgecolor='black', density=True)
    ax.hist(future_duration_data[variable], bins=log_bins, alpha=0.3, label="Future", color='grey', edgecolor='black', density=True)
    
    # Calculate the bin centers for plotting
    bin_centers = (bins_used[:-1] + bins_used[1:]) / 2

    # Fill the regions where `present` is greater than `future`
    ax.fill_between(bin_centers, present_counts, future_counts, where=(present_counts > future_counts),
                    color='royalblue', alpha=alpha, step='mid', label="Present > Future")
    
    # Optional: fill where `future` is greater than `present` in a different color
    ax.fill_between(bin_centers, present_counts, future_counts, where=(future_counts > present_counts),
                    color="indianred", alpha=alpha, step='mid', label="Future > Present")
    
    # Set the x-axis to logarithmic scale to match the binning
    ax.set_xscale('log')

    # Reduce the number of ticks by manually setting tick positions
    ticks = [1, 2, 5, 10, 20, 50, 100, 200]  # Example ticks
    ax.set_xticks(ticks)

    # Format the x-axis labels with normal numbers (no scientific notation)
    ax.xaxis.set_major_formatter(ScalarFormatter())

    # Rotate tick labels if necessary
    ax.tick_params(axis='x', rotation=90)
    
    # Optional: Adjust tick parameters to ensure the labels fit
    ax.tick_params(axis='x', which='both', labelbottom=True)
    
    
   # Function to plot with shaded overlapping regions
def plot_hist_with_overlap(ax, present_data, future_data, bins=100, color_present='RoyalBlue', color_future='orange', overlap_color='gray'):
    # Calculate histogram counts and bin edges for each dataset
    present_counts, bin_edges = np.histogram(present_data, bins=bins, density=False)
    future_counts, _ = np.histogram(future_data, bins=bin_edges, density=False)  # Use same bin edges

    # Calculate bin centers for `fill_between`
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Plot the individual histograms as steps for visibility
    ax.hist(present_data, bins=bin_edges, color=color_present, alpha=1, label="Present", edgecolor=None, histtype='stepfilled')
    ax.hist(future_data, bins=bin_edges, color=color_future, alpha=1, label="Future", edgecolor=None, histtype='stepfilled')

    # Fill overlapping regions with the overlap color (gray)
    overlap = np.minimum(present_counts, future_counts)
    ax.fill_between(bin_centers, overlap, color=overlap_color, step='mid', label="Overlap")

    # Fill the remaining regions with original colors for areas without overlap
    ax.fill_between(bin_centers, present_counts, overlap, where=(present_counts > future_counts), 
                    color=color_present, alpha=1, step='mid')
    ax.fill_between(bin_centers, future_counts, overlap, where=(future_counts > present_counts), 
                    color=color_future, alpha=1, step='mid')

    # Add labels and legend
    ax.set_xlabel('Mean day of year', fontsize=15)
    
    
def plot_hist_with_overlap_shading(ax, present_data, future_data, bins, color_present='royalblue', color_future='indianred', overlap_color='lightgray'):
    # Calculate histogram counts and bin edges
    present_counts, bin_edges = np.histogram(present_data, bins=bins)
    future_counts, _ = np.histogram(future_data, bins=bin_edges)  # Use the same bin edges

    # Plot the histograms for Present and Future without overlap
    ax.hist(present_data, bins=bin_edges, color=color_present, alpha=0.3, edgecolor='black', histtype='stepfilled', label="Present")
    ax.hist(future_data, bins=bin_edges, color=color_future, alpha=0.3, edgecolor='black', histtype='stepfilled', label="Future")

    # Prepare data for shading by repeating counts to span full bin widths
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    x_values = np.repeat(bin_edges, 2)[1:-1]
    present_counts_extended = np.repeat(present_counts, 2)
    future_counts_extended = np.repeat(future_counts, 2)
    overlap_counts_extended = np.minimum(present_counts_extended, future_counts_extended)

    # Shade overlap and non-overlap regions
    ax.fill_between(x_values, 0, overlap_counts_extended, color=overlap_color, label="Overlap", alpha=1, step='mid')
    ax.fill_between(x_values, overlap_counts_extended, present_counts_extended, where=(present_counts_extended > future_counts_extended), color=color_present, alpha=1, step='mid')
    ax.fill_between(x_values, overlap_counts_extended, future_counts_extended, where=(future_counts_extended > present_counts_extended), color=color_future, alpha=1, step='mid')
     
def plot_circular_colorbar(colors, month_labels):
    # colors = colors[::-1]
    # Create a ListedColormap with the provided colors
    cmap = ListedColormap(colors, name="month_cmap")

    # Generate polar coordinates for the circular colorbar
    theta = np.linspace(0, 2 * np.pi, 1000)  # 1000 points for smooth gradient
    r = np.linspace(0.9, 1, 2)  # Narrow ring

    # Create a meshgrid for plotting
    theta, r = np.meshgrid(theta, r)
    z = theta  # Use theta to map colors

    # Plot the circular colorbar
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'})
    c = ax.pcolormesh(theta, r, z, cmap=cmap, shading='auto')

    # Adjust angles to center labels in each color segment
    label_angles = np.linspace(0, 2 * np.pi, len(month_labels), endpoint=False) + (np.pi / 12)

    # Add labels for each month at the centered positions
    for angle, label in zip(label_angles, month_labels):
        ax.text(angle, 1.08, label, ha='center', va='center', fontsize=12)

    # Hide gridlines and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['polar'].set_visible(False)

    # Display the plot
    plt.show()        
 
def plot_2d_heatmap(ax, x, y, z, cmap="Blues", xlabel="Day of Year", ylabel="$D_{50}$", colorbar_label="Value"):
    """
    Plots a 2D heatmap on the given axes.

    Parameters:
        ax: Matplotlib Axes object where the heatmap will be plotted.
        x: 1D array-like. Data for the x-axis (e.g., day of the year).
        y: 1D array-like. Data for the y-axis (e.g., $D_{50}$ values).
        z: 1D array-like. Data for the color intensity (e.g., percentages or values to represent in heatmap).
        cmap: Colormap for the heatmap.
        xlabel: Label for the x-axis.
        ylabel: Label for the y-axis.
        colorbar_label: Label for the colorbar.
    """
    # Create a grid for the heatmap
    heatmap_data, xedges, yedges = np.histogram2d(x, y, bins=[100, 100], weights=z, density=False)
    
    # Normalize the grid to remove empty spaces
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    
    # Plot heatmap
    cax = ax.imshow(
        heatmap_data.T,
        origin='lower',
        extent=extent,
        aspect='auto',
        cmap=cmap,
        interpolation='nearest',
    )
    
    # Add a colorbar
    cbar = plt.colorbar(cax, ax=ax, pad=0.01)
    cbar.set_label(colorbar_label, fontsize=14)
    
    # Set axis labels
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
