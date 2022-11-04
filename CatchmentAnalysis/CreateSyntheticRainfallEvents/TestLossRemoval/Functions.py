import matplotlib.patches as mpatches
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

roberto_profiles_fp = "../RobertoProfiles/"
total_duration_minutes = 60 * 6 

def clean_dfs (df):
    # Convert date to datetime
    df['Time'] = pd.to_datetime(df['Time'])
    # Filter to only include those within the first 6 hours
    start_time = df['Time'].loc[0]
    end_time = start_time + timedelta(hours=6) - timedelta(minutes=1)
    df = df[(df['Time'] >= start_time) & (df['Time'] <= end_time)].copy()
    # Dates are flipped between the two, dates are arbitrary anyway, so just make consistent
    df['Time'] =  np.array(range(total_duration_minutes))
    return df

def make_plot (ax, ax_num, cluster_num, options, colors, legend_position, include_pre_losses= True):
    # Create the patches for legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        # Add to patches
        patch = mpatches.Patch(color=colors[number], label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv(roberto_profiles_fp + "PostLossRemoval/6hr_100yrRP/{}/cluster{}_urban_summer.csv".format(option, cluster_num))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df[post_loss_removal_df.columns[5]], color = colors[number])
        
    # Include a line before the losses were removed
    if include_pre_losses == True:
        pre_loss_removal = pd.read_csv(roberto_profiles_fp + "PreLossRemoval/6hr_100yrRP/cluster{}.csv".format(cluster_num), names = ['Time', 'Rainfall'])
        pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:360]
        ax.plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'black', linestyle = 'dashed')
        patch = mpatches.Patch(color='black', label='Pre Loss Removal', linestyle = 'dashed')
        patches.append(patch)
    
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Rainfall (mm)")


def make_plot_old (axs, ax_num, cluster_num, options, colors, legend_position, include_pre_losses= True):
    ax = axs.flatten()[ax_num]
    # Create the patches for legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        # Add to patches
        patch = mpatches.Patch(color=colors[number], label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv(roberto_profiles_fp + "PostLossRemoval/6hr_100yrRP/{}/cluster{}_urban_summer.csv".format(option, cluster_num))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df[post_loss_removal_df.columns[5]], color = colors[number])
        
    # Include a line before the losses were removed
    if include_pre_losses == True:
        pre_loss_removal = pd.read_csv(roberto_profiles_fp + "PreLossRemoval/6hr_100yrRP/cluster{}.csv".format(cluster_num), names = ['Time', 'Rainfall'])
        pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:360]
        ax.plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'black', linestyle = 'dashed')
        patch = mpatches.Patch(color='black', label='Pre Loss Removal', linestyle = 'dashed')
        patches.append(patch)
    
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Rainfall (mm)")
    
    if ax_num == 1:
        ax.legend(handles=patches, loc=legend_position, fontsize= 10)

def make_plot_losses (ax, cluster_num, options, colors, legend_position):
    # Create the patches for legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        # Add to patches
        patch = mpatches.Patch(color=colors[number], label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv(roberto_profiles_fp + "PostLossRemoval/6hr_100yrRP/{}/cluster{}_urban_summer.csv".format(option, cluster_num))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        post_loss_removal_df['losses'] = post_loss_removal_df['Observed rainfall - 01/01/2022 00:00'] - post_loss_removal_df['Total net rain mm (Observed rainfall - 01/01/2022) - urbanised model']
        
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df['losses'], color = colors[number])
        
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Rainfall (mm)")
    
    if ax == axs[0]:
        ax.legend(handles=patches, loc=legend_position, fontsize= 10)        
        
        
def singlepeak_plot(ax, options, colors, include_post_loss_removal = True):
    # List to store patches to make legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        # Add to patches
        patch = mpatches.Patch(color=colors[number], label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv(roberto_profiles_fp + "PostLossRemoval/6hr_100yrRP/SinglePeak_6h1_1min_100yr/{}_urban.csv".format(option))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df[post_loss_removal_df.columns[5]], color = colors[number])
    
    # Include the ReFH2 design rainfall post loss removal
    pre_loss_removal = pd.read_csv(roberto_profiles_fp + "PostLossRemoval/6hr_100yrRP/SinglePeak_6h1_1min_100yr/Urban.csv")
    pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:360]
    ax.plot(pre_loss_removal['Time'], pre_loss_removal['Total net rain mm (100 year) - urbanised model'], color = 'green')
    patch = mpatches.Patch(color='green', label='RefH2 loss removal', linestyle = 'dashed')
    patches.append(patch)
    # Plot the pre-loss removal rainfall
    if include_post_loss_removal == True:
        ax.plot(pre_loss_removal['Time'], pre_loss_removal['100 year design rainfall - FEH 2013 model'], color = 'black', 
               linestyle = 'dashed')
    
        patch = mpatches.Patch(color='black', label='Pre Loss Removal', linestyle = 'dashed')
        patches.append(patch)
    # Format plot    
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Rainfall (mm)")
    plt.legend(handles=patches, loc="upper right", fontsize= 10)