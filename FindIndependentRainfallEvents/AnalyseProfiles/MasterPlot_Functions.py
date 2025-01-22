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
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm, Normalize
from scipy.stats import ks_2samp
import datetime as dt
import matplotlib.colors as mcolors
from matplotlib.ticker import FixedLocator, FixedFormatter, FormatStrFormatter, PercentFormatter, ScalarFormatter, MaxNLocator, LogLocator
import matplotlib.cm as cm
from scipy.stats import chi2_contingency

# Filter for Great Britain
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
gb_outline = gdf[(gdf.name == "United Kingdom")]

home_dir = '/nfs/a319/gy17m2a/PhD/'

tbo_vals = pd.read_csv(home_dir + 'datadir/RainGauge/interarrival_thresholds_CDD_noMissing.txt')
tbo_vals = tbo_vals[tbo_vals['Lon']!=-999.0]
tbo_vals['gauge_num'] = tbo_vals.index


##########################################################################################
##########################################################################################
##########################################################################################
################################## DATE ADJUSTING ########################################
##########################################################################################
##########################################################################################
##########################################################################################

def date_to_julian_day(date):
    """Convert a date (YYYY-MM-DD) to its Julian day of the year."""
    date = datetime.strptime(date, "%Y-%m-%d")
    return date.timetuple().tm_yday

def julian_to_date(julian_day):
    """Convert Julian day to calendar date."""
    base_date = datetime(2000, 1, 1)  # Use an arbitrary base year for reference
    return (base_date + timedelta(days=julian_day - 1)).strftime('%d %b')  # Format as '1 Feb', '21 Mar', etc.

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

##########################################################################################
##########################################################################################
##########################################################################################
##################################### COLOUR MAPS ########################################
##########################################################################################
##########################################################################################
##########################################################################################

# Define a function to create a customized colormap with emphasis on the middle
def create_custom_colormap(cmap):
    # Create a colormap using a diverging color palette (like "coolwarm")
    cmap = cm.get_cmap(cmap)

    # Adjust the colormap to emphasize the center (modify the range around the midpoint)
    new_colors = cmap(np.linspace(0, 1, 15))

    # Define the modified colormap
    new_cmap = mcolors.LinearSegmentedColormap.from_list("custom_cmap", new_colors)

    return new_cmap


def reverse_colormap(cmap):
    # Get the original colormap with 256 discrete colors
    colors = cmap(np.linspace(0, 1, 256))
    
    # Reverse the colormap
    reversed_colors = colors[::-1]
    
    # Create a new colormap from the reversed colors
    reversed_cmap = mcolors.LinearSegmentedColormap.from_list("reversed_cmap", reversed_colors)
    
    return reversed_cmap

def modify_colormap(cmap, gamma=2.0):
    # Get the original colormap with 256 discrete colors
    colors = cmap(np.linspace(0, 1, 256))
    
    # Apply a power law transformation to enhance the center
    # For gamma > 1, the mid part of the colormap gets more variation
    # For gamma < 1, the extremes get more variation
    new_colors = np.copy(colors)
    
    # Apply a power transformation to the r, g, b channels separately
    for i in range(3):  # Apply to each RGB channel
        new_colors[:, i] = np.power(colors[:, i], gamma)

    # Create a new colormap from the modified colors
    new_cmap = mcolors.LinearSegmentedColormap.from_list("modified_cmap", new_colors)
    
    return new_cmap       
    
##########################################################################################
##########################################################################################
##########################################################################################
##################################### MISCELLANEOUS ######################################
##########################################################################################
##########################################################################################
##########################################################################################

def test_proportions(present, future, categories, variable):
    results = []
    total_present = len(present)
    total_future = len(future)

    for category in categories:
        # Calculate proportions
        present_count = (present[variable] == category).sum()
        future_count = (future[variable] == category).sum()

        present_prop = present_count / total_present
        future_prop = future_count / total_future

        # Build a contingency table using counts
        contingency_table = np.array([[present_count, future_count],
                                       [total_present - present_count, total_future - future_count]])

        # Perform chi-square test
        chi2, p_value, _, _ = chi2_contingency(contingency_table)

        results.append({
            'category': category,
            'present_count': present_count,
            'future_count': future_count,
            'present_prop': present_prop,
            'future_prop': future_prop,
            'chi2': chi2,
            'p_value': p_value
        })

    return pd.DataFrame(results)

def plot_boxplot(data, ax, color_mapping):
    sns.swarmplot(ax=ax, data=data, x='Loading_profile_molly',
            y='D50',  dodge=True, palette=color_mapping)
    ax.set_xlabel('Quintile classification', fontsize=15)
    ax.set_ylabel("$D_{50}$", fontsize=15)
   
     
def find_significance_of_differences (present, future, variable):
    
    diffs_dict={}
    gauge_nums=[]
    
    present['D'] = present['D'].apply(lambda x: x + 365 if x < 50 else x)
    future['D'] = future['D'].apply(lambda x: x + 365 if x < 50 else x)

    for i, dur in enumerate(['<=7hr', '7-16hr','16hr+', 'All']):
        present_data = present[present["duration_category_onemore"] == dur]
        future_data = future[future["duration_category_onemore"] == dur]       
        
        if dur == 'All':
            present_data = present
            future_data = future

        diff = []
        for gauge_num in range(0,1294):
            if gauge_num not in [444,827,888]:
                if dur == '<=7hr':
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
    
    df = pd.DataFrame({'gauge_num':gauge_nums, 'Sig_Diff_1h':np.array(diffs_dict['<=7hr']),
                    'Sig_Diff_6h':np.array(diffs_dict['7-16hr']), 'Sig_Diff_24h':np.array(diffs_dict['16hr+']),
                      'Sig_Diff_All':np.array(diffs_dict['All'])})    
    
    return df, diffs_dict

    
# Custom function to format ticks as percentages
def percent_formatter(x, pos):
    return f"{x:.0f}%"  # Format the tick as an integer percentage (no decimals) 

    
##########################################################################################
##########################################################################################
##########################################################################################
################################## CONTOUR AND SCATTER ###################################
##########################################################################################
##########################################################################################
##########################################################################################  
    
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

    # Calculate R^2 and p-value
    slope, intercept, r_value, p_value, std_err = linregress(data_x, data_y)
    r_squared = r_value**2

    # Set labels and title
    ax.set_ylabel("$D_{50}$",fontsize=18)
    ax.set_xlim(0,366)

def make_scatter_plot_durcats(df, duration, timeperiod, loadings, axes, ax_row):
    df["D_mean_present"] = df["D_mean_present"].apply(lambda x: x + 365 if x < 50 else x)
    df["D_mean_future"] = df["D_mean_future"].apply(lambda x: x + 365 if x < 50 else x)
    
    for ax_num, (loading, title) in enumerate(zip(loadings, loadings)):
        if title != f'D50_mean':
            title = title.split('_')[0]
        else:
            ax_num=ax_num+1
        title = title if ax_row in[0,4] else ''
        
        if duration in ['<=7hr', '7-16hr','16hr+']:
            this_duration = df[df['sampling_duration'] == duration]
            make_point_density_plot(
                axes[ax_row][ax_num],  # Updated indexing
                this_duration[f"D_mean_{timeperiod}"],
                this_duration[f"{loading}_{timeperiod}"],
                title)
        else:
            make_point_density_plot(
                axes[ax_row][ax_num],  # Updated indexing
                df[f"D_mean_{timeperiod}"],
                df[f"{loading}_{timeperiod}"],
                title)           

def make_point_density_plot(ax, data_x, data_y, title):
    # Calculate point density
    xy = np.vstack([data_x, data_y])
    density = gaussian_kde(xy)(xy)

    # Scatter plot with density-based coloring
    sc = ax.scatter( data_x, data_y, c=density,cmap='viridis',  s=10, alpha=0.7)

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
    
    ax.text(0.05, 0.95, f"$R^2$ = {r_squared:.2f}, $p$ {p_value}",  transform=ax.transAxes, fontsize=12, 
        verticalalignment='top', bbox=dict(facecolor='white', alpha=0.7))
    
    ax.set_title(title)
    return sc


##########################################################################################
##########################################################################################
##########################################################################################
############################## SEASONAL HISTOGRAMS #######################################
##########################################################################################
##########################################################################################
##########################################################################################    
    
def plot_polar_months_plot(df, ax, title_on, title, rmax, name_variable_to_plot, original_D_mean, R):
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
    colors = ['#C2DFFF', '#C2DFFF', '#A8E6CF', '#A8E6CF', '#A8E6CF', '#FFD3B6', '#FFD3B6', '#FFD3B6', '#FFABAB', '#FFABAB', 
              '#FFABAB', '#C2DFFF']      
    colors.reverse()
    
    # Plot bars
    ax.bar(circular_plot_position, variable_to_plot.iloc[::-1], width=width, color=colors)
    
    # --- Add season separators (black dashed lines) ---
    season_boundaries = [circular_plot_position[0]+5, circular_plot_position[3]+5, circular_plot_position[6]+5, circular_plot_position[9]+5]
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
        fontsize=12, fontweight='bold' )

    # Format plot
    if title_on:
        ax.set_title(title, fontsize=20, pad=50, fontweight='bold')
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
    

##########################################################################################
##########################################################################################
##########################################################################################
############################## DENSITY DISTRIBUTIONS #####################################
##########################################################################################
##########################################################################################
##########################################################################################    
    
def plot_proportion_histogram_with_overlap(ax, present, future, bins):
    # Calculate the histogram counts and bin edges for both distributions
    present_counts, present_bin_edges = np.histogram(present, bins=bins, density=True)
    future_counts, future_bin_edges = np.histogram(future, bins=bins, density=True)
    
    # Normalize counts to get proportions (i.e., counts / total count)
    present_proportions = present_counts / np.sum(present_counts)
    future_proportions = future_counts / np.sum(future_counts)
    
    # If no axes are passed, create a new plot
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
    
    # Plot the histograms as bar charts showing the proportions
    ax.bar(present_bin_edges[:-1], present_proportions, width=np.diff(present_bin_edges), color='royalblue', edgecolor='black', alpha=1, label='Present', align='edge')
    ax.bar(future_bin_edges[:-1], future_proportions, width=np.diff(future_bin_edges), color='indianred', edgecolor='black', alpha=1, label='Future', align='edge')
    
    # Prepare data for shading the overlap region
    overlap_props = np.minimum(present_proportions, future_proportions)
    # Shade the overlap area
    ax.bar(future_bin_edges[:-1], overlap_props, width=np.diff(future_bin_edges), color='lightgrey', edgecolor='black', alpha=1, label='Both', align='edge',
          linewidth=0.5)
    # Format the y-axis to show percentages
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x*100:.0f}%'))
    
    # Show legend
    ax.legend(loc='upper right')
    # Display the plot
    plt.tight_layout()     
    
    
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
    
    if variable == 'Volume':
        ax.set_xlabel('Volume (mm)')  
    elif variable == 'max_intensity':
        ax.set_xlabel("Max Intensity (mm/hr)")     
    
    
    # Reduce the number of ticks by manually setting tick positions
    ticks = [1, 2, 5, 10, 20, 50, 100, int(max(present_data[variable]))]  # Example ticks
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

#     # Reduce the number of ticks by manually setting tick positions
    ticks = [1, 2, 5, 10, 20, 50, 100, int(max(present_duration_data[variable]))]  # Example ticks
    ax.set_xticks(ticks)
    if variable == 'Volume':
        ax.set_xlabel('Volume (mm)')  
    elif variable == 'max_intensity':
        ax.set_xlabel("Max Intensity (mm/hr)")     
    
    # Format the x-axis labels with normal numbers (no scientific notation)
    ax.xaxis.set_major_formatter(ScalarFormatter())

    # Rotate tick labels if necessary
    ax.tick_params(axis='x', rotation=90)
    
    # Optional: Adjust tick parameters to ensure the labels fit
    ax.tick_params(axis='x', which='both', labelbottom=True)
    
       
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
     
        
        
##########################################################################################
##########################################################################################
##########################################################################################
################################### SPATIAL PLOTTING #####################################
################################### HELPER FUNCTIONS #####################################
##########################################################################################
##########################################################################################          
  
def plot_values_on_map(
    ax, data, title_off_or_on, title, tbo_vals, value_column, 
    low_lim=None, high_lim=None, norm=None, cmap='coolwarm', 
    highlight_sig=False
):
    """
    Plots values on a map with optional customization for normalization and significance.

    Parameters:
        ax: Matplotlib axis object.
        data: DataFrame containing the data to plot.
        title: Title of the plot.
        tbo_vals: DataFrame containing longitude and latitude values for gauges.
        value_column: Column name in `data` containing values to plot.
        low_lim: Minimum value for color scale (used if `norm` is not provided).
        high_lim: Maximum value for color scale (used if `norm` is not provided).
        norm: Matplotlib normalization object (e.g., LogNorm) for custom color scaling.
        cmap: Colormap to use for scatter plot.
        highlight_sig: Boolean, whether to highlight significant points with an outline.

    Returns:
    """
    gauge_locs = data['gauge_num'].copy()
    lon = tbo_vals.loc[gauge_locs, 'Lon']
    lat = tbo_vals.loc[gauge_locs, 'Lat']
    
    mean_val = data[value_column].mean()
    min_val = data[value_column].min()
    max_val = data[value_column].max()    

    # Plot the background outline of Great Britain
    gb_outline.plot(ax=ax, color='darkgrey', edgecolor='black', linewidth=1)

    # Define base scatter plot arguments
    scatter_kwargs = {'cmap': cmap,  'marker': 'o'}
    if norm:
        scatter_kwargs['norm'] = norm
    else:
        scatter_kwargs['vmin'] = low_lim
        scatter_kwargs['vmax'] = high_lim

    if highlight_sig:
        # Identify points with and without significant values
        significant_points = data[data['sig'] == 1]
        nonsignificant_points = data[data['sig'] != 1]

        ax.scatter(
            tbo_vals.loc[nonsignificant_points['gauge_num'], 'Lon'],
            tbo_vals.loc[nonsignificant_points['gauge_num'], 'Lat'],
            c=nonsignificant_points[value_column],
            alpha=1, s=12, linewidth=0.1, **scatter_kwargs)

        # Plot significant points with a black outline
        scatter = ax.scatter(
            tbo_vals.loc[significant_points['gauge_num'], 'Lon'],
            tbo_vals.loc[significant_points['gauge_num'], 'Lat'],
            c=significant_points[value_column], 
            edgecolor='black', linewidth=0.2, s=15, **scatter_kwargs)
    else:
        # Simple scatter plot without significance distinction
        scatter = ax.scatter(lon, lat, c=data[value_column], edgecolor=None,s=10, **scatter_kwargs)

    # Set title
    if title_off_or_on == True:
        ax.set_title(title, fontsize=20, fontweight='bold')
    
    ax.text(
            0.98, 0.98, 
            f"Mean: {mean_val:.1f} \nMin: {min_val:.1f} \nMax: {max_val:.1f}",
            ha='right', va='top', transform=ax.transAxes, fontsize=15, color='black'
        )
    
    # Remove axis labels
    ax.set_xticklabels([])  
    ax.set_yticklabels([])  

    return scatter
  
        
        
##########################################################################################
##########################################################################################
##########################################################################################
################################### SPATIAL PLOTTING #####################################
##########################################################################################
##########################################################################################
##########################################################################################        
        
def make_plot_durcats(
    df_changes_all, df_changes_byduration, variable, cmap, diff_cmap, diffs_dict, plot_diffs, low_lim_diff, high_lim_diff, figname, 
    low_lim=None, high_lim=None):
    # Copy the dataframes to avoid modifying the originals
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    df_changes_all['sig'] = diffs_dict['All'].copy()

    # Define subplots
    fig, axes = plt.subplots(3, 4, figsize=(16, 13))

    # Set variable names for present, future, and difference
    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'
    variable_diff = f'{variable}_diff'

    # Determine color limits if not provided
    if high_lim is None or low_lim is None:
        all_values = pd.concat([ 
            df_changes_all[variable_present], 
            df_changes_all[variable_future], 
            df_changes_byduration[variable_present], 
            df_changes_byduration[variable_future]
        ])
        low_lim = all_values.min() if low_lim is None else low_lim
        high_lim = all_values.max() if high_lim is None else high_lim

    # Set color normalization
    norm = TwoSlopeNorm(vmin=low_lim, vcenter=50, vmax=high_lim) if variable == 'D50_new' else Normalize(vmin=low_lim, vmax=high_lim)
    
    # Plot present, future, and difference data
    for row, (value_col, title, colormap, norm_func, highlight_sig) in enumerate([
        (variable_present, 'Present', cmap, norm, False),
        (variable_future, 'Future', cmap, norm, False),
        (variable_diff, 'Change', diff_cmap, Normalize(vmin=low_lim_diff, vmax=high_lim_diff), plot_diffs)  # Use plot_diffs for highlighting
    ]):
        if title == 'Present':
            title_off_or_on = True
        else:
            title_off_or_on = False      
            
        if title == 'Change':
            low_lim = low_lim_diff
            high_lim = high_lim_diff
        for i, duration in enumerate(['<=7hr', '7-16hr', '16hr+']):
            duration_data = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
            duration_data['sig'] = diffs_dict[duration].copy()

            if row == 2:  # Clip values for the difference plots
                duration_data[variable_diff] = duration_data[variable_diff].clip(lower=low_lim_diff, upper=high_lim_diff)

            # Use the plot_values_on_map function
            scatter = plot_values_on_map(
                axes[row, i], duration_data, title_off_or_on, duration, tbo_vals, value_col, 
                low_lim, high_lim, norm_func, colormap, highlight_sig=highlight_sig
            )

        # Plot 'All' values for each row
        scatter = plot_values_on_map(
            axes[row, 3], df_changes_all,title_off_or_on, 'All', tbo_vals, value_col, 
            low_lim, high_lim, norm_func, colormap, highlight_sig=highlight_sig
        )

        # Add colorbars for the row
        cbar_ax = fig.add_axes([1.005, 0.68 - 0.31 * row, 0.01, 0.26])
        cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
        cbar.ax.tick_params(labelsize=16)

        # Adjust colorbar ticks based on the row type
        if variable == 'D50_new' and row < 2:
            cbar.set_ticks([low_lim, 50, high_lim])
            cbar.ax.set_yticklabels([f'{low_lim:.1f}', '50', f'{high_lim:.1f}'], fontsize=16)
        elif row == 2:  # Difference row
            ticks = np.linspace(low_lim, high_lim, 5)  # Custom ticks for the difference plot
            cbar.set_ticks(ticks)
            cbar.set_ticklabels([f'{tick:.0f}' if variable != 'R' else f'{tick:.1f}' for tick in ticks], fontsize=16)

    # Add row labels
    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')

    plt.subplots_adjust(hspace=-0.1)
    plt.tight_layout()    
    fig.savefig(figname, dpi=500, bbox_inches='tight')

def make_plot_D_seasonal_durcats(df_changes_all, df_changes_byduration, variable, diff_cmap, diffs_dict):

    colors = ["#005f99", "#0072b2", "#009e73", "#56b356", 
        "#99d44f", "#d4e22f", "#ffc20a", "#ff7f00", 
        "#e31a1c", "#a70021", "#6a3d9a", "#440154" ]  
    # Create a ListedColormap with these colors
    month_cmap = mcolors.ListedColormap(colors, name="month_cmap")
    month_cmap = LinearSegmentedColormap.from_list("month_cmap", colors, N=12)
    cmap = month_cmap 
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    # Add sifnificance of changes
    df_changes_all['sig'] = diffs_dict['All']

    fig, axes = plt.subplots(3, 4, figsize=(16, 13))

    variable_present = f'{variable}_present'
    variable_future = f'{variable}_future'

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    for i, duration in enumerate(['<=7hr', '7-16hr', '16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        this_duration['month_present'] = this_duration['D_mean_present'].apply(get_month_from_doy)
        plot_values_on_map(axes[0, i], this_duration,True, f'{duration}', tbo_vals, 'month_present', 1, 12, None, cmap)

    # Plot 'All' present values
    df_changes_all['month_present'] = df_changes_all['D_mean_present'].apply(get_month_from_doy)
    scatter = plot_values_on_map(axes[0, 3], df_changes_all, True, 'All', tbo_vals, 'month_present', 1, 12, None, cmap)

    # Define month names
    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

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
    for i, duration in enumerate(['<=7hr', '7-16hr', '16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        this_duration['month_future'] = this_duration['D_mean_future'].apply(get_month_from_doy)
        plot_values_on_map(axes[1, i], this_duration, False, f'{duration}', tbo_vals, 'month_future', 1, 12,  None, cmap)

    # Plot 'All' future values
    df_changes_all['month_future'] = df_changes_all['D_mean_future'].apply(get_month_from_doy)
    scatter = plot_values_on_map(axes[1, 3], df_changes_all,False, 'All', tbo_vals, 'month_future', 1, 12, None, cmap)
    
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
    low_lim_diff = -90
    high_lim_diff = -low_lim_diff
    norm = Normalize(vmin=low_lim_diff, vmax=high_lim_diff)        

    # Plot Difference Data if Available
    for i, duration in enumerate(['<=7hr', '7-16hr', '16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        this_duration['sig'] =diffs_dict[duration].copy() 
        scatter = plot_values_on_map(axes[2, i], this_duration, False, f'{duration}', tbo_vals, variable_diff, low_lim_diff, 
                                     high_lim_diff, None, cmap_diff, False)

    # Plot 'All' differences
    scatter = plot_values_on_map(axes[2, 3], df_changes_all, False, 'All', tbo_vals,  variable_diff, low_lim_diff,
                                         high_lim_diff, None, cmap_diff, False)

    # Create the colorbar in thisa new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    
    # Customize colorbar ticks and labels
    ticks = np.linspace(low_lim_diff, high_lim_diff, 5)  # Define 11 tick positions (e.g., from 0 to 1)
    cbar.set_ticks(ticks)  # Set the tick positions
    if variable == 'R':
        cbar.set_ticklabels([f'{tick:.1f}' for tick in ticks])  # Optional: set the labels with formatting
    else:
        cbar.set_ticklabels([f'{tick:.0f}' for tick in ticks])  # Optional: set the labels with formatting        

    # Adjust label size and display colorbar
    cbar.ax.tick_params(labelsize=16)  # Set the font size for labels
    
    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')

    plt.subplots_adjust(hspace=-0.15)

    plt.tight_layout()
    fig.savefig("Figs/day_of_year_seasonal_durcats.jpg", dpi=500, bbox_inches='tight')
         
def make_plot_durcats_quintiles(df_changes_all, df_changes_byduration, variable, cmap, diff_cmap, diffs_dict,
                                category_num, figname, low_lim=None, high_lim=None):
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    # df_changes_all['sig'] = diffs_dict['All'][category_num].copy()
    
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
        high_lim = max(df_changes_all[variable_present].max(), df_changes_all[variable_present].max(), 
                      df_changes_byduration[variable_future].max(), df_changes_byduration[variable_future].max())   
    
    # Use a `TwoSlopeNorm` to focus on the middle (50 in this case)
    high_lim= high_lim
    low_lim = low_lim
    
    if variable == 'D50_new':
        norm = TwoSlopeNorm(vmin=low_lim, vcenter=50, vmax=high_lim)
    else:
        norm = Normalize(vmin=low_lim, vmax=high_lim)

    #################################################
    # Plot Present Data for Each Duration
    #################################################
    for i, duration in enumerate(['<=7hr', '7-16hr','16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        mean = this_duration[variable_present].mean()
        this_min = this_duration[variable_present].min()
        this_max= this_duration[variable_present].max()
        
        scatter = plot_values_on_map(
            axes[0, i], this_duration, True, f'{duration}', tbo_vals, variable_present,
            low_lim, high_lim, norm, cmap )
        
        # Add the mean value to the top-right corner of the plot
        axes[0, i].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[0, i].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )
             
    # Plot 'All' present values
    scatter = plot_values_on_map(axes[0, 3], df_changes_all, True, 'All', tbo_vals,
                                 variable_present, low_lim, high_lim, norm, cmap)
    mean = df_changes_all[variable_present].mean()
    this_min = df_changes_all[variable_present].min()
    this_max= df_changes_all[variable_present].max()

    # Add the mean value to the top-right corner of the plot
    axes[0, 3].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[0, 3].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )

    cbar_ax = fig.add_axes([1.005, 0.68, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical', norm=norm)
    cbar.ax.tick_params(labelsize=16) 
    
    # Set ticks at the bottom, middle, and top
    if variable =='D50_new':
        cbar.set_ticks([low_lim, 50, high_lim])
        # Set custom labels for the ticks
        cbar.ax.set_yticklabels([f'{low_lim:.1f}', '50', f'{high_lim:.1f}'], fontsize=16)

    #################################################
    # Plot Future Data for Each Duration
    #################################################
    for i, duration in enumerate(['<=7hr', '7-16hr','16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        mean = this_duration[variable_future].mean()
        this_min = this_duration[variable_future].min()
        this_max= this_duration[variable_future].max()
        
        scatter = plot_values_on_map(
            axes[1, i], this_duration, False, f'{duration}', tbo_vals, variable_future,
            low_lim, high_lim, norm, cmap )
        
        # Add the mean value to the top-right corner of the plot
        axes[1, i].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[1, i].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )
             
        
    # Plot 'All' future values
    scatter = plot_values_on_map(axes[1, 3], df_changes_all, False, 'All', tbo_vals,
                                 variable_future, low_lim, high_lim, norm, cmap)

    
    mean = df_changes_all[variable_future].mean()
    this_min = df_changes_all[variable_future].min()
    this_max= df_changes_all[variable_future].max()
    # Add the mean value to the top-right corner of the plot
    axes[1, 3].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[1, 3].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )
    
    #################################################
    # Add Colorbar for Future Data
    #################################################
    cbar_ax = fig.add_axes([1.005, 0.38, 0.01, 0.24])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    cbar.ax.tick_params(labelsize=16)

    # Set ticks at the bottom, middle, and top
    if variable =='D50_new':
        cbar.set_ticks([low_lim, 50, high_lim])
        # Set custom labels for the ticks
        cbar.ax.set_yticklabels([f'{low_lim:.1f}', '50', f'{high_lim:.1f}'], fontsize=16)
    
    #################################################
    # Plot Difference Data if Available
    #################################################
    variable_diff = f'{variable}_diff'

    # Calculate and apply color limits centered around 0 for the difference
    low_lim_diff = -max(abs(df_changes_all[variable_diff].min()), abs(df_changes_all[variable_diff].max()),
                        abs(df_changes_byduration[variable_diff].min()), abs(df_changes_byduration[variable_diff].max()))
    #  low_lim_diff=-6
    high_lim_diff = -low_lim_diff

    for i, duration in enumerate(['<=7hr', '7-16hr','16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        
        scatter = plot_values_on_map(axes[2, i], this_duration, False, f'{duration}', tbo_vals,
                                         variable_diff, low_lim_diff, high_lim_diff, None, diff_cmap)     
        
        mean = this_duration[variable_diff].mean()
        this_min = this_duration[variable_diff].min()
        this_max= this_duration[variable_diff].max()
        
        # Add the mean value to the top-right corner of the plot
        axes[2, i].text(
                0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
                f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
                ha='right', va='top',  # Align text to the top-right
                transform=axes[2, i].transAxes,  # Use axis coordinates
                fontsize=15, color='black' )

        
    # Plot 'All' differences
    scatter = plot_values_on_map(axes[2, 3], df_changes_all, False, 'All', tbo_vals,
                                     variable_diff, low_lim_diff, high_lim_diff,norm=None,cmap =  diff_cmap)   
    
    mean = df_changes_all[variable_diff].mean()
    this_min = df_changes_all[variable_diff].min()
    this_max= df_changes_all[variable_diff].max()
    
    # Add the mean value to the top-right corner of the plot
    axes[2, 3].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[2, 3].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )
    
    # Create the colorbar in this new axis
    cbar_ax = fig.add_axes([1.007, 0.054, 0.01, 0.26])  # [left, bottom, width, height]
    cbar = fig.colorbar(scatter, cax=cbar_ax, orientation='vertical')
    
    # Customize colorbar ticks and labels
    ticks = np.linspace(low_lim_diff, high_lim_diff, 5)  # Define 11 tick positions (e.g., from 0 to 1)
    cbar.set_ticks(ticks)  # Set the tick positions
    
    if variable == 'R':
        cbar.set_ticklabels([f'{tick:.1f}' for tick in ticks])  # Optional: set the labels with formatting
    else:
        cbar.set_ticklabels([f'{tick:.0f}' for tick in ticks])  # Optional: set the labels with formatting        

    # Adjust label size and display colorbar
    cbar.ax.tick_params(labelsize=16)  # Set the font size for labels
    
    if 'percentage' in variable:
        cbar.ax.yaxis.set_major_formatter(FuncFormatter(percent_formatter))
    
    fig.text(-0.035, 0.82, 'Present', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.48, 'Future', va='center', ha='center', fontsize=17, rotation='horizontal')
    fig.text(-0.035, 0.18, 'Change', va='center', ha='center', fontsize=17, rotation='horizontal')
    
    plt.subplots_adjust(hspace=-0.1)
    plt.tight_layout()  
    fig.savefig(figname, dpi=500, bbox_inches='tight')
    
