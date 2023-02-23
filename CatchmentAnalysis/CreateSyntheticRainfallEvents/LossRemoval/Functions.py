import matplotlib.patches as mpatches
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

roberto_profiles_fp = "../RobertoProfiles/"
total_duration_minutes = (60 * 6) + 1 

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

def make_plot(ax, stats,cols, timeperiod, divide_plot_by, include_losses = False, plot_losses=False, legend = True):
    for col_num, string in enumerate(stats):
        data = pd.read_csv('PostLossRemovalData/IdealisedProfiles/6h_sp_fl_0.2/{}/{}_summer_urban.csv'.format(timeperiod, string))
        data['losses'] =round(data['Observed rainfall - 01/08/2022 00:00']/data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model']*100,2)
        the_sum = round(data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:total_duration_minutes].sum(),1)
        as_a_percent_of_original = int(the_sum/59.29 * 100)
        
        if divide_plot_by == 'stat':
            label = "{}: \ntotal rainfall = {}mm \n% of original = {}%".format(string.split('_')[1], the_sum, as_a_percent_of_original)
            title = string.split('_')[0] 
        else:
            label = "{}: \ntotal rainfall = {}mm \n% of original = {}%".format(string.split('_')[0], the_sum, as_a_percent_of_original)
            title = string.split('_')[1] 
            
        # Plot the rainfall after losses removed
        if plot_losses == False:
            ax.plot(range(0,total_duration_minutes), 
                     data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:total_duration_minutes],
                    color = cols[col_num], label = label)
            if include_losses == True:
                pre_loss_removal = pd.read_csv('../IdealisedProfiles/6hr_100yrRP/PreLossRemoval/6h_sp_fl_0.2.csv', names = ['Time', 'Rainfall'])
                pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:total_duration_minutes]
                ax.plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'black', linestyle = 'dashed',
                        label = 'prelossremoval')
        # Plot just the losses
        else:
             ax.plot(range(0,total_duration_minutes), data['losses'][0:total_duration_minutes],
                    color = cols[col_num], label = "{}: \ntotal rainfall = {}mm \n% of original = {}mm".format(string, the_sum, as_a_percent_of_original))
    if legend==True:            
        ax.legend(loc="upper right", fontsize=6)  
        ax.set_title(title)
    
    if plot_losses == True:
        ax.set_ylabel("Losses removed (mm)")
    else:
        ax.set_ylabel("Rainfall (mm)")        
    ax.set_xlabel("Minutes")

def make_comparison_plot(ax, stats,cols, include_losses = False):
    for col_num, string in enumerate(stats):
        data = pd.read_csv('PostLossRemovalData/IdealisedProfiles/6h_sp_fl_0.2/{}_summer_urban.csv'.format(string))
        the_sum = round(data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:total_duration_minutes].sum(),1)
        as_a_percent_of_original = int(the_sum/59.29 * 100)
        ax.plot(range(0,total_duration_minutes), 
                 data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:total_duration_minutes],
                color = cols[col_num],  
                label = "{}: \ntotal rainfall = {}mm \n% of original = {}%".format(string.split('/')[0], the_sum, as_a_percent_of_original) )
    if include_losses == True:
        pre_loss_removal = pd.read_csv('../IdealisedProfiles/6hr_100yrRP/PreLossRemoval/6h_sp_fl_0.2.csv', names = ['Time', 'Rainfall'])
        pre_loss_removal['Time'] = post_loss_removal_df['Time'][0:total_duration_minutes]
        ax.plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'black', linestyle = 'dashed', label = 'prelossremoval')
    
    ax.legend(loc="upper right", fontsize=8)  
    ax.set_title(string.split('/')[1])
    ax.set_xlabel("Minutes")
    ax.set_ylabel("Rainfall (mm)")    
    
def make_comparison_plot_ver2(ax, stats,cols, dict_of_values, include_losses = False, plot_losses=False):
    for col_num, string in enumerate(stats):
        data = pd.read_csv('PostLossRemovalData/IdealisedProfiles/6h_sp_fl_0.2/{}_summer_urban.csv'.format(string))
        data['%_of_rainfall_removed'] =round(100 - data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model']/data['Observed rainfall - 01/08/2022 00:00']*100,2)
        the_sum = round(data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:total_duration_minutes].sum(),1)
        as_a_percent_of_original = int(the_sum/59.29 * 100)
        associated_rainfall = dict_of_values[string.split('_')[0]]

        if plot_losses == True:
            ax.plot(range(0,total_duration_minutes), data['%_of_rainfall_removed'][0:total_duration_minutes],
                color = cols[col_num], label = "{}mm ({}): \ntotal rainfall = {}mm \n% of original = {}%".format(associated_rainfall, string.split('_')[0], the_sum, as_a_percent_of_original))
            ax.set_ylabel("%_of_rainfall_removed") 
        
        else: 
            ax.plot(range(0,total_duration_minutes), 
            data['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:total_duration_minutes],
            color = cols[col_num], 
            label = "{}mm ({}): \ntotal rainfall = {}mm \n% of original = {}%".format(associated_rainfall, string.split('_')[0],the_sum, as_a_percent_of_original))
            ax.legend(loc="upper right", fontsize=8) 
            ax.set_ylabel("Net rainfall (mm)") 

    ax.set_title(string.split('_')[1])
    ax.set_xlabel("Minutes")
    
    

def singlepeak_plot(ax, options, cols, include_post_loss_removal = True, plot_losses=False):

    # Include the ReFH2 design rainfall post loss removal
    pre_loss_removal = pd.read_csv("PostLossRemovalData/ObservedProfiles/SinglePeak_6h1_1min_100yr/Urban.csv")
    pre_loss_removal = pre_loss_removal[0:361]
    the_sum = round(pre_loss_removal['Total net rain mm (100 year) - urbanised model'][0:361].sum(),1)
    as_a_percent_of_original = int(the_sum/59.29 * 100)
    pre_loss_removal['%_of_rainfall_removed'] =round(100 - pre_loss_removal['Total net rain mm (100 year) - urbanised model']/pre_loss_removal['100 year design rainfall - FEH 2013 model']*100,2)

    # Plot each of the antecedent condition options, and add a patch for to patches list for legend
    for number,option in enumerate(options):
        # Read in data, clean it and plot it
        post_loss_removal_df = pd.read_csv("PostLossRemovalData/ReFH2Profiles/6h/{}_summer_urban.csv".format(option))
        post_loss_removal_df =post_loss_removal_df[0:361]
        post_loss_removal_df['%_of_rainfall_removed'] =round(100 - post_loss_removal_df['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model']/post_loss_removal_df['Observed rainfall - 01/08/2022 00:00']*100,2)        
        the_sum = round(post_loss_removal_df['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model'][0:361].sum(),1)
        as_a_percent_of_original = int(the_sum/59.29 * 100)
        
        if plot_losses == True:
            ax.plot(range(0,total_duration_minutes), post_loss_removal_df['%_of_rainfall_removed'][0:total_duration_minutes],
                color = cols[number], label = "{}: \ntotal rainfall = {}mm \n% of original = {}%".format(option, the_sum, as_a_percent_of_original))
            ax.set_ylabel("% of rainfall removed") 
        else:
            ax.plot(range(0,total_duration_minutes),
                    post_loss_removal_df[post_loss_removal_df.columns[5]], color = cols[number],
                       label = "{}: \ntotal rainfall = {}mm \n% of original = {}%".format(option, the_sum, as_a_percent_of_original))
            ax.set_ylabel("Rainfall (mm)")
            
    if plot_losses == True:       
        ax.plot(range(0,total_duration_minutes), pre_loss_removal['%_of_rainfall_removed'][0:total_duration_minutes],
            color = 'black',label = "ReFH2 loss removal: \ntotal rainfall = {}mm \n% of original = {}%".format(the_sum, as_a_percent_of_original))       
    else:
        ax.plot(range(0,total_duration_minutes), pre_loss_removal['Total net rain mm (100 year) - urbanised model'], color = 'black',
            label = "ReFH2 loss removal: \ntotal rainfall = {}mm \n% of original = {}%".format(the_sum, as_a_percent_of_original))
            
    # Include data before losses removed
    if include_post_loss_removal ==True:
        ax.plot(range(0,total_duration_minutes), pre_loss_removal['100 year design rainfall - FEH 2013 model'], color = 'black',
            linestyle = 'dotted', label = 'Pre loss removal')

    # Format plot    
    ax.set_xlabel("Minutes")
    if ax ==axs[2]:
        ax.legend(loc="upper right", fontsize=8)    