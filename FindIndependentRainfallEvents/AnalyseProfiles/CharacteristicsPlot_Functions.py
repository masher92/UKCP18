def plot_histogram_for_duration(df, variable, duration, duration_variable, ax, bins=25, label=None, color=None, alpha=0.5):

    # Filter the DataFrame for the specified duration
    duration_data = df[df[variable] == duration]

    # Plot histogram for the specified duration
    if not duration_data.empty:
#         ax.hist(duration_data[variable], bins=bins, alpha=alpha, label = label, color = color, edgecolor='black')
        n, bins_used, patches = ax.hist(duration_data[variable], bins=bins, alpha=alpha, label=label, color=color, edgecolor='black')
        
        #ax.set_title(f"{variable} Distribution - {duration}", fontsize=12)
        #ax.grid(True)
    else:
        pass
        #ax.set_title(f"{variable} Distribution - {duration} (No Data)", fontsize=12)
        #ax.grid(True)

    # Set y-axis label to the specific duration bin it refers to
    ax.set_ylabel(f"{duration}hrs", fontsize=10, rotation=0)
    # Remove y-tick labels
    ax.set_yticks([])
    

def plot_density_for_duration(event_props_dict, variable, duration, duration_variable, ax, label=None, color=None, alpha=0.5):
    """
    Plots a density plot for a specified variable for a given duration category on a specified axis.

    Parameters:
    - event_props_dict: Dictionary containing event properties.
    - variable: The variable to plot (e.g., 'Volume' or 'Intensity').
    - duration: The specific duration category to plot.
    - ax: The axis to plot on.
    """
    # Step 1: Convert event_props_dict to a pandas DataFrame
    data = []
    for props in event_props_dict:
        data.append({variable: props[variable], 'Duration': props[duration_variable]})

    df = pd.DataFrame(data)

    # Filter the DataFrame for the specified duration
    duration_data = df[df['Duration'] == duration]

    # Plot density plot for the specified duration
    if not duration_data.empty:
        sns.kdeplot(duration_data[variable], ax=ax, shade=True, label=label, color=color, alpha=alpha)
        ax.set_title(f"{variable} Distribution - {duration}", fontsize=12)
        ax.grid(True)
    else:
        pass  # Handle the case where there's no data

    # Set y-axis label to the specific duration bin it refers to
    ax.set_ylabel(f"{duration}hrs", fontsize=10, rotation=0)
    # Remove y-tick labels
    ax.set_yticks([])
    
    