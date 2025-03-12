import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def plot_raw_data(sample, ax, labels=True, title=False):
    """
    Plot the raw rainfall data.
    """
    # x values: each measurement is taken at a 0.5-hour interval.
    x_values = np.array(range(1, len(sample) + 1)) * 0.5
    ax.bar(x_values, sample, color='royalblue', alpha=0.7, width=0.4)
    
    if labels:
        ax.set_xlabel('Time (hours)', fontsize=15)
        ax.set_ylabel('Rainfall (mm)', fontsize=15)
    if title:
        ax.set_title('Raw rainfall (mm)', fontsize=15)


def plot_dimensionless_cumulative(raw_rainfall, dimensionless_cumulative_rainfall, ax, boundaries_boolean = False, labels=True, title=False):
    """
    Plot the dimensionless cumulative rainfall.
    """
    # Create a percentage scale for the duration.
    time_percentage = (np.arange(0, len(raw_rainfall) + 1) / len(raw_rainfall)) * 100
    
    # Define time intervals
    total_duration = time_percentage[-1]  # e.g., 270 minutes
    boundaries = np.linspace(0, total_duration, 6)  # 6 boundaries -> 5 segments
    
    ax.plot(time_percentage, dimensionless_cumulative_rainfall, 
            label='Cumulative Sum', linewidth=2, marker='o', color='royalblue', markerfacecolor='purple')
    
    if boundaries_boolean ==True:
        for marker in boundaries[1:]:
            ax.axvline(marker, color='red', linestyle='--', label='Fifth Boundary' if marker==boundaries[1] else "")
    
    if labels:
        ax.set_xlabel('Proportion of duration', fontsize=15)
        ax.set_ylabel('Proportion of total rainfall', fontsize=12)
    if title:
        ax.set_title('Dimensionless cumulative rainfall,\nwith linearly interpolated lines', fontsize=15)


def plot_interpolated_cumulative(interpolated_n_cumulative_rainfall, ax, labels=True, title=False):
    """
    Plot the interpolated cumulative rainfall.
    """
    # Convert the time to percentage
    interpolated_n_times = np.linspace(0, 1, len(interpolated_n_cumulative_rainfall))
    interpolated_n_times_percentage = interpolated_n_times * 100 
    ax.plot(interpolated_n_times_percentage, interpolated_n_cumulative_rainfall, label='Cumulative Sum', 
            linewidth=2, marker='o', color='royalblue', markersize=8, markerfacecolor='magenta')
    ax.set_xlim(0, 100)
    
    if labels:
        ax.set_xlabel('Proportion of duration', fontsize=15)
        ax.set_ylabel('Proportion of total rainfall', fontsize=12)
    if title:
        ax.set_title('Dimensionless cumulative rainfall\ninterpolated to len 5', fontsize=15)

def plot_incremental_rainfall(rainfall_array, ax, titles=False, labels=False):
    
    # Define custom labels for the bars
    bar_labels = ['F2', 'F1', 'C', 'B1', 'B2']

    # Define the color mapping
    color_mapping = {
        'F2': (0.0, 0.0, 1.0, 0.6),'F1': (0.0, 0.6902, 1.0, 0.6),'C': (0.5, 0.5, 0.5, 0.6),'B1': (0.8039, 0.0, 0.0, 0.6),   
        'B2': (0.5451, 0.0, 0.0, 0.6) }

    # Find the index of the maximum value
    index_of_max = np.argmax(rainfall_array)
    print(index_of_max)

    # Initialize all bars with a default color (e.g., white or light gray)
    colors = ['white'] * len(rainfall_array)  # Default color for all bars

    # Apply the color from the color_mapping to the bar at index_of_max
    colors[index_of_max] = color_mapping[bar_labels[index_of_max]]

    # Create the bar chart
    time_steps = np.arange(1, len(rainfall_array) + 1)
    ax.bar(time_steps, rainfall_array, label='Incremental Rainfall', color=colors, edgecolor='black')

    # Set custom labels on the x-axis
    ax.set_xticks(time_steps, bar_labels)
    
    ax.set_ylabel('Proportion of total rainfall', fontsize=12)
    if titles == True:
        ax.set_title('Rainfall accumulations (5 bins)', fontsize=15)
    if labels:
        ax.set_xlabel('Quintile class', fontsize=15)
    ax.grid('off');