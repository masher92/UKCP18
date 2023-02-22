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

def plot_results_losses(by_day_or_percentile, cols_dict, lists, titles) :
    
    fig = plt.figure(constrained_layout=True, figsize = (6,8))
    if by_day_or_percentile == 'percentile':
        (subfig1, subfig2, subfig3, subfig4) = fig.subfigures(4,1) 
    else:
        (subfig1, subfig2, subfig3) = fig.subfigures(3,1) 
    (ax1, ax2) = subfig1.subplots(1, 2,sharey=True)      
    (ax3, ax4) = subfig2.subplots(1, 2,sharey=True)    
    (ax5, ax6) = subfig3.subplots(1, 2,sharey=True)    
    if by_day_or_percentile == 'percentile':
        (ax7, ax8) = subfig4.subplots(1, 2,sharey=True)   
    # Plot    
    make_plot_losses(ax1, 1, lists[0],cols_dict, 'upper right')
    make_plot_losses(ax2, 5, lists[0],cols_dict, 'upper left')

    make_plot_losses(ax3, 1, lists[1], cols_dict, 'upper right')
    make_plot_losses(ax4,5,lists[1], cols_dict, 'upper left')

    make_plot_losses(ax5,1, lists[2], cols_dict , 'upper right')
    make_plot_losses(ax6,5, lists[2], cols_dict, 'upper left')
    
    if by_day_or_percentile == 'percentile':
        make_plot_losses(ax7, 1, lists[3], cols_dict, 'upper right')
        make_plot_losses(ax8,5,lists[3], cols_dict, 'upper left')

    # Add subfigure titles
    subfig1.suptitle(titles[0], fontsize = 11)
    subfig2.suptitle(titles[1], fontsize = 11)    
    subfig3.suptitle(titles[2], fontsize = 11)
    
    if by_day_or_percentile == 'percentile':
        subfig3.suptitle(titles[2], fontsize = 11)

def plot_results(by_day_or_percentile, cols_dict, lists, titles) :
    
    fig = plt.figure(constrained_layout=True, figsize = (20,12))
    if by_day_or_percentile == 'percentile':
        (subfig1, subfig2, subfig3, subfig4) = fig.subfigures(4,2) 
    else:
        (subfig1, subfig2, subfig3) = fig.subfigures(3,2) 
    (ax1, ax2) = subfig1[0].subplots(1, 2)      
    (ax3, ax4) = subfig1[1].subplots(1, 2)    
    (ax5, ax6) = subfig2[0].subplots(1, 2)    
    (ax7, ax8) = subfig2[1].subplots(1, 2)    
    (ax9, ax10) = subfig3[0].subplots(1, 2)    
    (ax11, ax12) = subfig3[1].subplots(1, 2)    
    if by_day_or_percentile == 'percentile':
        (ax13, ax14) = subfig4[0].subplots(1, 2)    
        (ax15, ax16) = subfig4[1].subplots(1, 2)    
    # Plot    
    make_plot(ax1, 1, lists[0],cols_dict, 'upper right', False)
    make_plot(ax2, 1, lists[0],cols_dict, 'upper right', True)
    make_plot(ax3, 5, lists[0],cols_dict, 'upper left', False)
    make_plot(ax4, 5, lists[0],cols_dict, 'upper left', True)

    make_plot(ax5, 1, lists[1], cols_dict, 'upper right', False)
    make_plot(ax6, 1, lists[1], cols_dict, 'upper right', True)
    make_plot(ax7,5,lists[1], cols_dict, 'upper left', False)
    make_plot(ax8,5,lists[1], cols_dict,  'upper left', True)   

    make_plot(ax9,1, lists[2], cols_dict , 'upper right', False)
    make_plot(ax10, 1,lists[2], cols_dict,'upper right', True)
    make_plot(ax11,5, lists[2], cols_dict, 'upper left', False)
    make_plot(ax12,5, lists[2], cols_dict, 'upper left', True)
    
    if by_day_or_percentile == 'percentile':
        make_plot(ax13, 1, lists[3], cols_dict, 'upper right', False)
        make_plot(ax14, 1, lists[3], cols_dict, 'upper right', True)
        make_plot(ax15,5,lists[3], cols_dict, 'upper left', False)
        make_plot(ax16,5,lists[3], cols_dict,  'upper left', True)   

    # Add figure titles
    plt.figtext(0.5,1.01, titles[0], ha="center", va="top", fontsize=20)
    
    # Add subfigure titles
    subfig1[0].suptitle('Cluster 1', fontsize = 14)
    subfig1[1].suptitle('Cluster 5', fontsize = 14)
    subfig2[0].suptitle('Cluster 1', fontsize = 14)    
    subfig2[1].suptitle('Cluster 5', fontsize = 14)      
    subfig3[0].suptitle('Cluster 1', fontsize = 14)
    subfig3[1].suptitle('Cluster 5', fontsize = 14)
    
    if by_day_or_percentile == 'percentile':
        plt.figtext(0.5,0.75, titles[1], ha="center", va="top", fontsize=20)
        plt.figtext(0.5,0.50, titles[2], ha="center", va="top", fontsize=20)
        plt.figtext(0.5,0.25, titles[3], ha="center", va="top", fontsize=20)
        subfig4[0].suptitle('Cluster 1', fontsize = 14)
        subfig4[1].suptitle('Cluster 5', fontsize = 14)
    else:
        plt.figtext(0.5,0.67, titles[1], ha="center", va="top", fontsize=20)
        plt.figtext(0.5,0.33, titles[2], ha="center", va="top", fontsize=20)

def make_plot (ax, cluster_num, options, colors_dict, legend_position, include_pre_losses= True):
    # Create the patches for legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        if 'days' in list(colors_dict.keys())[0]:
            color = colors_dict[option.split('_')[1]]
        else: 
            color = colors_dict[option.split('_')[0]]
        
        # Add to patches
        patch = mpatches.Patch(color=color, label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv("PostLossRemoval/{}/cluster{}_urban_summer.csv".format(option, cluster_num))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df[post_loss_removal_df.columns[5]], color = color)
        
    # Include a line before the losses were removed
    if include_pre_losses == True:
        pre_loss_removal = pd.read_csv(roberto_profiles_fp + "PreLossRemoval/6hr_100yrRP/cluster{}.csv".format(cluster_num), names = ['Time', 'Rainfall'])
        pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:360]
        ax.plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'black', linestyle = 'dashed')
        patch = mpatches.Patch(color='black', label='Pre Loss Removal', linestyle = 'dashed')
        patches.append(patch)
    
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Rainfall (mm)")
    
    if cluster_num == 5 and include_pre_losses == True:
        ax.legend(handles=patches, loc=legend_position, fontsize= 10)
        
def make_plot_losses (ax, cluster_num, options, colors_dict, legend_position):
    # Create the patches for legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        if 'days' in list(colors_dict.keys())[0]:
            color = colors_dict[option.split('_')[1]]
        else: 
            color = colors_dict[option.split('_')[0]]
        # Add to patches
        patch = mpatches.Patch(color=color, label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv("PostLossRemoval/{}/cluster{}_urban_summer.csv".format(option, cluster_num))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        post_loss_removal_df['losses'] =round(post_loss_removal_df['Total net rain mm (Observed rainfall - 01/01/2022) - urbanised model']/post_loss_removal_df['Observed rainfall - 01/01/2022 00:00']*100,2)
        
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df['losses'], color = color)
    ax.set_title("Cluster {}".format(cluster_num))    
    ax.set_xlabel("Minutes", fontsize = 7)
    ax.set_ylabel("Proportion of rainfall lost", fontsize = 7)
        
    if cluster_num == 5 :
        ax.legend(handles=patches, loc=legend_position, fontsize= 7)  
        
def singlepeak_plot(ax, options, cols_dict, include_post_loss_removal = True):
    # List to store patches to make legend
    patches = []
    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        # Add to patches
        patch = mpatches.Patch(color= cols_dict[option.split('_')[0]], label=options[number])
        patches.append(patch)
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv("PostLossRemoval/{}/singlepeak_urban_summer.csv".format(option))
        post_loss_removal_df = clean_dfs(post_loss_removal_df)
        ax.plot(post_loss_removal_df['Time'], post_loss_removal_df[post_loss_removal_df.columns[5]], color = cols_dict[option.split('_')[0]])
    
    # Include the ReFH2 design rainfall post loss removal
    pre_loss_removal = pd.read_csv("PostLossRemoval/SinglePeak_6h1_1min_100yr/Urban.csv")
    pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:360]
    ax.plot(pre_loss_removal['Time'], pre_loss_removal['Total net rain mm (100 year) - urbanised model'], color = 'dodgerblue')
    
    patch = mpatches.Patch(color='dodgerblue', label='RefH2 loss removal', linestyle = 'dashed')
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