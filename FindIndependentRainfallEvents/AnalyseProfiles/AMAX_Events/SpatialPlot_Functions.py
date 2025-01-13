def make_plot_durcats_quintiles(df_changes_all, df_changes_byduration, variable, cmap, diff_cmap, diffs_dict,category_num, low_lim=None, high_lim=None):
    df_changes_all = df_changes_all.copy()
    df_changes_byduration = df_changes_byduration.copy()
    
    df_changes_all['sig'] = results_dict['All'][category_num].copy()
    
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
        
        scatter = plot_values_on_map_norm(
            axes[0, i], this_duration, f'{duration}', tbo_vals, variable_present,
            low_lim, high_lim, norm, cmap )
        
        # Add the mean value to the top-right corner of the plot
        axes[0, i].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[0, i].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )
             
    # Plot 'All' present values
    scatter = plot_values_on_map_norm(axes[0, 3], df_changes_all, 'All', tbo_vals,
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
        
        scatter = plot_values_on_map_norm(
            axes[1, i], this_duration, f'{duration}', tbo_vals, variable_future,
            low_lim, high_lim, norm, cmap )
        # Add the mean value to the top-right corner of the plot
        axes[1, i].text(
            0.98, 0.98,  # Position (98% along x, 98% along y in axis coordinates)
            f"Mean: {mean:.1f} \n Min: {this_min:.1f} \n Max: {this_max:.1f}",  # Format the mean value with 1 decimal place
            ha='right', va='top',  # Align text to the top-right
            transform=axes[1, i].transAxes,  # Use axis coordinates
            fontsize=15, color='black' )
             
        
    # Plot 'All' future values
    scatter = plot_values_on_map_norm(axes[1, 3], df_changes_all, 'All', tbo_vals,
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
#     low_lim_diff=-6
    high_lim_diff = -low_lim_diff

    for i, duration in enumerate(['<=7hr', '7-16hr','16hr+']):
        this_duration = df_changes_byduration[df_changes_byduration["sampling_duration"] == duration].copy()
        this_duration['sig'] = results_dict[duration][category_num].copy()
        this_duration[f'{variable}_diff'] = this_duration[f'{variable}_diff'].clip(lower=-80, upper=80)
        if variable =='R':
            scatter = plot_values_on_map(axes[2, i], this_duration, f'{duration}', tbo_vals,
                                         variable_diff, low_lim_diff, high_lim_diff, diff_cmap)                
        else:
            scatter = plot_values_on_map_withsig(axes[2, i], this_duration, f'{duration}', tbo_vals, variable_diff,
                                                 low_lim_diff, high_lim_diff, diff_cmap)
        
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
    if variable =='R':
        scatter = plot_values_on_map(axes[2, 3], df_changes_all, 'All', tbo_vals,
                                         variable_diff, low_lim_diff, high_lim_diff, diff_cmap)           
    else:   
        scatter = plot_values_on_map_withsig(axes[2, 3], df_changes_all, 'All', tbo_vals,
                                             variable_diff, low_lim_diff, high_lim_diff, diff_cmap)    
    
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
    