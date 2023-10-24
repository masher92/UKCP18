import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

def plot_flooded_extent_1catchment(cluster_results_ls, urban_str, profiles_name, profiles_name_short,  ylim, percent_adjust,
                                   label_height_adjuster_x, label_height_adjuster_y):
    
    fig, ax = plt.subplots(ncols= 1, sharey=True,figsize = (4,4), gridspec_kw={'hspace': 0.2, 'wspace': 0.03})
    catchment_name_ls = ['LinDyke','WykeBeck', 'LinDyke','WykeBeck']
    ##############################
    # Plot number of flooded cells
    ##############################
    number=0
    cluster_results =  cluster_results_ls[number]

    y_pos = np.arange(len(cluster_results['Cluster_num']))
    ax.bar(y_pos, cluster_results['{}FloodedArea'.format(urban_str)].values.tolist(), width = 0.9, 
           color = cluster_results['colour'])
    # Create names on the x-axis
    ax.set_xticks(y_pos)
    ax.set_xticklabels(cluster_results['Cluster_num'], fontsize =10, rotation = 75)
    ax.tick_params(axis='both', which='major', labelsize=12.5)
    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]


    if catchment_name_ls[number] == 'LinDyke':
        label_height_adjuster= label_height_adjuster_x
    elif catchment_name_ls[number] == 'WykeBeck':
        label_height_adjuster= label_height_adjuster_y

    for i, v in enumerate(cluster_results['{}FloodedArea'.format(urban_str)].values.tolist()):
        ax.text(xlocs[i] - percent_adjust, v * label_height_adjuster, 
                str(cluster_results["%Diff_{}FloodedArea_fromSP_formatted".format(urban_str)][i]), 
                    fontsize = 12.5, rotation =90)

    if urban_str == '':
        ax.set_ylim(1,ylim)
    else :
        ax.set_ylim(0,ylim)

    ax.set_title(catchment_name_ls[number],fontsize=15)

    # fig.text(0.04, 0.5, 'Flooded area (km2)', fontsize=15, va='center', rotation='vertical')   
    
    if urban_str != '':
        urban_str = '_' + urban_str
    fig.savefig("../ProcessModelResults/Outputs/Figs/{}Profiles/{}_CompareCatchments_Extent1Plot{}.PNG".format(profiles_name,
        profiles_name_short, urban_str), bbox_inches='tight')


    
def plot_flooded_extent_2catchments_2profilesets(cluster_results_ls, urban_str, profiles_name, profiles_name_short,  ylim, 
                                    percent_adjustments,  label_height_adjusters_x, label_height_adjusters_y, set_title= False):
    
    
    # Try@https://stackoverflow.com/questions/40936729/matplotlib-title-spanning-two-or-any-number-of-subplot-columns
    
    fig, axs = plt.subplots(ncols= 4, nrows=1, sharey=True,figsize = (15,4), gridspec_kw={'hspace': 0.2, 'wspace': 0.03})
    catchment_name_ls = ['LinDyke','WykeBeck', 'LinDyke','WykeBeck']
    
    ##############################
    # Plot number of flooded cells
    ##############################
    #for number, ax in enumerate(axs.flatten()):
    #    print(number)
        # Get: (1) idealised results (2) observed results
    number =0
    for number2, cluster_results_one_set_of_profiles in enumerate(cluster_results_ls):
        # Get (1) Lin Dyke (2) Wyke Beck
        for cluster_results_one_catchment in cluster_results_one_set_of_profiles:

            y_pos = np.arange(len(cluster_results_one_catchment['Cluster_num']))
            axs[number].bar(y_pos, cluster_results_one_catchment['{}FloodedArea'.format(urban_str)].values.tolist(), width = 0.9, 
                   color = cluster_results_one_catchment['colour'])
            # Create names on the x-axis
            axs[number].set_xticks(y_pos)
            axs[number].set_xticklabels(cluster_results_one_catchment['Cluster_num'], fontsize =10, rotation = 75)
            axs[number].tick_params(axis='both', which='major', labelsize=12.5)
            xlocs, xlabs = plt.xticks(y_pos)
            xlocs=[i+1 for i in range(0,19)]
            xlabs=[i/2 for i in range(0,19)]
            
            if catchment_name_ls[number] == 'LinDyke':
                label_height_adjuster= label_height_adjusters_x[number2]
            elif catchment_name_ls[number] == 'WykeBeck':
                label_height_adjuster = label_height_adjusters_y[number2]

            for i, v in enumerate(cluster_results_one_catchment['{}FloodedArea'.format(urban_str)].values.tolist()):
                axs[number].text(xlocs[i] - percent_adjustments[number2], v * label_height_adjuster, 
                        str(cluster_results_one_catchment["%Diff_{}FloodedArea_fromSP_formatted".format(urban_str)][i]), 
                            fontsize = 11, rotation =90)

            if urban_str == '':
                axs[number].set_ylim(1,ylim)
            else :
                axs[number].set_ylim(0,ylim)
            
            if set_title == True:
                axs[number].set_title(catchment_name_ls[number],fontsize=15)
            
            number=number+1
            
    fig.text(0.07, 0.5, 'Flooded area (km2)', fontsize=15, va='center', rotation='vertical')   
    if urban_str != '':
        urban_str = '_' + urban_str
    fig.savefig(f"../ProcessModelResults/Outputs/Figs/CompareCatchments_Extent1Plot{urban_str}.PNG", bbox_inches='tight')
    print(f"../ProcessModelResults/Outputs/Figs/CompareCatchments_Extent1Plot{urban_str}.PNG");
        
    
def plot_flooded_extent_2catchments(cluster_results_ls, urban_str, profiles_name, profiles_name_short,  ylim, percent_adjust,
                                   label_height_adjuster_x, label_height_adjuster_y):
    
    fig, axs = plt.subplots(ncols= 2, nrows=1, sharey=True,figsize = (9,4), gridspec_kw={'hspace': 0.2, 'wspace': 0.03})
    catchment_name_ls = ['LinDyke','WykeBeck', 'LinDyke','WykeBeck']
    ##############################
    # Plot number of flooded cells
    ##############################
    for number, ax in enumerate(axs.flatten()):

        cluster_results =  cluster_results_ls[number]
        
        y_pos = np.arange(len(cluster_results['Cluster_num']))
        ax.bar(y_pos, cluster_results['{}FloodedArea'.format(urban_str)].values.tolist(), width = 0.9, 
               color = cluster_results['colour'])
        # Create names on the x-axis
        ax.set_xticks(y_pos)
        ax.set_xticklabels(cluster_results['Cluster_num'], fontsize =10, rotation = 75)
        ax.tick_params(axis='both', which='major', labelsize=12.5)
        xlocs, xlabs = plt.xticks(y_pos)
        xlocs=[i+1 for i in range(0,19)]
        xlabs=[i/2 for i in range(0,19)]
        
        
        if catchment_name_ls[number] == 'LinDyke':
            label_height_adjuster= label_height_adjuster_x
        elif catchment_name_ls[number] == 'WykeBeck':
            label_height_adjuster= label_height_adjuster_y
            
        for i, v in enumerate(cluster_results['{}FloodedArea'.format(urban_str)].values.tolist()):
            ax.text(xlocs[i] - percent_adjust, v * label_height_adjuster, 
                    str(cluster_results["%Diff_{}FloodedArea_fromSP_formatted".format(urban_str)][i]), 
                        fontsize = 12.5, rotation =90)
        
        if urban_str == '':
            ax.set_ylim(1,ylim)
        else :
            ax.set_ylim(0,ylim)
       
        ax.set_title(catchment_name_ls[number],fontsize=15)

    fig.text(0.04, 0.5, 'Flooded area (km2)', fontsize=15, va='center', rotation='vertical')   
    
    if urban_str != '':
        urban_str = '_' + urban_str
    fig.savefig("../ProcessModelResults/Outputs/Figs/{}Profiles/{}_CompareCatchments_Extent1Plot{}.PNG".format(profiles_name,
        profiles_name_short, urban_str), bbox_inches='tight')
    
    
def boxplot(fig, individual_cell_values_ls, fl_method,bl_method, variable_name, ax, title, outliers = False):
    colors = [ 'darkred','darkblue', 'darkred', 'darkblue']
    catchments = ['LD', 'WB']
    ls =[]
    labels = []
    # For each catchment
    for number in range(0,len(individual_cell_values_ls)):
        # Get the values for this catchment
        vals_1catchment =  individual_cell_values_ls[number]
        # Add to the list the values for the bl/fl method for this catchment
        ls.append(vals_1catchment[vals_1catchment['short_id']==fl_method][variable_name])
        ls.append(vals_1catchment[vals_1catchment['short_id']==bl_method][variable_name])
        # Create labels to correspond to this data
        labels.append("FL ({})".format(catchments[number]))
        labels.append("BL ({})".format(catchments[number]))

    # Plot   
    bplot = ax.boxplot(ls,patch_artist=True,widths=0.9, showfliers=outliers,
                   medianprops=dict(color="black"),labels =labels)
    ax.set_ylabel(variable_name)
    ax.set_title(title)
    if variable_name =='Depth':
        ax.set_ylim(0,1.2)
    plt.setp(bplot['boxes'], color='black')

    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
        
    fig.savefig("../ProcessModelResults/Outputs/Figs/BothProfiles/Boxplot_{}.PNG".format(variable_name), 
                bbox_inches='tight')      
    
    
    
def plot_histogram (individual_cell_values_ls, variable_name, profiles_name, profiles_name_short, smallest_method,
                    largest_method, title = True):
    
    catchments = ['LinDyke', 'WykeBeck']
    
    # Define bins
    bins = np.cumsum([0.1*1.15**i for i in range(10)])
    bins = np.cumsum([0.1*1.14**i for i in np.arange (0.1,10.1,1)])
    #bins = np.cumsum([0.1*1.05**i for i in np.arange (0.1,10,1)])
    
    if variable_name == 'Depth':
        bins = np.cumsum([0.1*1.19**i for i in np.arange (0.1,7,1)])
    elif variable_name =='Velocity':
        bins = np.cumsum([0.1*1.1**i for i in np.arange (0.1,6,1)])
        bins = np.insert(bins,0,0)
       # bins = np.cumsum([0.1*1.14**i for i in np.arange (0.1,10.1,1)])
    
    # Make labels of bin values for dataframe
    if variable_name == 'Depth':
        b = [f'{i}-{j}m' for i, j in zip(np.round(bins,1)[:], np.round(bins,1)[1:])] 
        b = b + ['>1.3m']
    else:
        b = [f'{i}-{j}m/s' for i, j in zip(np.round(bins,1)[:], np.round(bins,1)[1:])] 
        b = b + ['>0.8m/s']
    
    # Dataframe to store change percentages
    df = pd.DataFrame({'Label':b})    
    
    fig, axs = plt.subplots(ncols= 2, nrows=1, sharey=True,figsize = (8,2.5), gridspec_kw={'hspace':1, 'wspace': 0.05})
    
    ##############################
    # Plot number of flooded cells
    ##############################
    for number, ax in enumerate(axs.flatten()):
        individual_cell_values =  individual_cell_values_ls[number]
        
        # Get the 2 most extreme scenario results separately
        extremes = individual_cell_values.loc[individual_cell_values['short_id'].isin([smallest_method, largest_method])].copy()
        # Get so the most/least extreme appear in plots with the colours in same order
        if profiles_name =='SinglePeak_Scaled':
            extremes.sort_values(by=['short_id'],ascending =True, inplace=True)
        else:
            extremes.sort_values(by=['short_id'],ascending=True, inplace=True)

        ls_values = sns.histplot(ax=axs[number], data=extremes, x=variable_name, hue='short_id',stat='count',element = 'step', 
                     linewidth=2, fill =False,log_scale=False,bins=bins, palette = ['darkred','darkblue']).get_lines()
        
        if title == True:
            axs[number].set_title(catchments[number],fontsize=15)
          
        #### Get change percentages
        change_pcs = []
        for num in range(0,len(ls_values[1].get_data()[1][:-1])):
            previous = ls_values[0].get_data()[1][:-1][num]
            current = ls_values[1].get_data()[1][:-1][num]
            change_percent = ((float(current)-previous)/previous)*100
            change_pcs.append(round(change_percent,1))   
            
        # Add ones not in the histogram    
        largest_method_values = individual_cell_values.loc[individual_cell_values['short_id'].isin([largest_method])].copy()
        smallest_method_values = individual_cell_values.loc[individual_cell_values['short_id'].isin([smallest_method])].copy()
        if variable_name == 'Depth':
            previous =len(smallest_method_values[smallest_method_values['Depth']>1.3])
            current = len(largest_method_values[largest_method_values['Depth']>1.3])
        else:
            previous =len(smallest_method_values[smallest_method_values['Velocity']>0.8])
            current = len(largest_method_values[largest_method_values['Velocity']>0.8])            
            
        change_pcs.append(round(((float(current)-previous)/previous)*100,1)) 
        # Add column in dataframe
        df['{} ({})'.format(profiles_name, catchments[number])]=change_pcs
        
    fig.savefig("../ProcessModelResults/Outputs/Figs/{}Profiles/{}_Histograms_{}.PNG".format(profiles_name,profiles_name_short,variable_name), 
                bbox_inches='tight')
    return df   

def plot_histogram_weighted (individual_cell_values_dict, profiles_name, profiles_name_short, smallest_method,
                    largest_method, filter_out_water, title = True):
    
    catchments = ['LinDyke', 'WykeBeck', 'LinDyke', 'WykeBeck']
    variables = ['Depth', 'Depth', 'Velocity', 'Velocity']
    
    # Set up figure
    fig, axs = plt.subplots(ncols= 2, nrows=2, sharey=False,figsize =(11,5), gridspec_kw={'hspace':0.5, 'wspace': 0.3})
    dfs=[]
    
    for ax_number, ax in enumerate(axs.flatten()):
        variable_name = variables[ax_number]
        catchment_name = catchments[ax_number]
        
        # Get data
        individual_cell_values =  individual_cell_values_dict[catchment_name]

        # Filter out cells which are water
        if filter_out_water == True:
            individual_cell_values = individual_cell_values[individual_cell_values['Water_class']==10]
        
        # Define bins
        if variable_name == 'Depth':
            bins = [0.1,0.3,0.6,1.2, 3]
            b = [f'{i}-{j}m' for i, j in zip(np.round(bins,1)[:], np.round(bins,1)[1:])] 
            b = [f'{i}-{j}m' for i, j in zip(bins[:], bins[1:])] 
            b = b + ['>3m']
            label = 'Depth (m)'
            
        elif variable_name =='Velocity':
            bins =[0, 0.25, 0.5, 1, 2, 3]
            b = [f'{i}-{j}m/s' for i, j in zip(np.round(bins,2)[:], np.round(bins,2)[1:])] 
            b = b + ['>3m/s']
            label = 'Velocity (m/s)'

        # Set weights differently to account for different cell sizes 
        if catchment_name =='WykeBeck':
            weight = 4 * 0.000001 
        elif catchment_name == 'LinDyke':
            weight = 0.000001 

        # Get the 2 most extreme scenario results separately
        extremes = individual_cell_values.loc[individual_cell_values['short_id'].isin([smallest_method, largest_method])].copy()
        # Get so the most/least extreme appear in plots with the colours in same order
        if profiles_name =='SinglePeak_Scaled':
            extremes.sort_values(by=['short_id'],ascending =True, inplace=True)
        else:
            extremes.sort_values(by=['short_id'],ascending=True, inplace=True)

        # Plot
        ls_values = sns.histplot(ax=ax, data=extremes, x=variable_name, hue='short_id',stat='count',
                                 element = 'step', weights=weight,linewidth=2, fill =False,log_scale=False,
                                 bins=bins, palette = ['darkred','darkblue']).get_lines()
        ax.set_ylabel('Area (km2)')
        ax.set_xticks(bins)
        ax.tick_params(axis='x', rotation=55)
        ax.yaxis.set_major_locator(plt.MaxNLocator(5))
        ax.set_xlabel (label)
        
        # Set title
        if variable_name == 'Depth':
            ax.set_title(catchment_name, fontsize=15)

        #### Get change percentages
        most_extreme_ls = []
        least_extreme_ls = []
        diff_ls=[]
        for num in range(0,len(ls_values[1].get_data()[1][:-1])):
            least_extreme = ls_values[0].get_data()[1][:-1][num]
            least_extreme_ls.append(round(least_extreme,2))
            most_extreme = ls_values[1].get_data()[1][:-1][num]
            most_extreme_ls.append(round(most_extreme,2))
            diff=most_extreme-least_extreme
            diff_ls.append(round(diff,3))

        # Add ones not in the histogram    
        largest_method_values = individual_cell_values.loc[individual_cell_values['short_id'].isin([largest_method])].copy()
        smallest_method_values = individual_cell_values.loc[individual_cell_values['short_id'].isin([smallest_method])].copy()

        if variable_name == 'Depth':
            least_extreme_abovehist =len(smallest_method_values[smallest_method_values['Depth']>=bins[-1]])
            least_extreme_ls.append(round((least_extreme_abovehist/1000000),2))
            most_extreme_abovehist = len(largest_method_values[largest_method_values['Depth']>=bins[-1]])
            most_extreme_ls.append(round((most_extreme_abovehist/1000000),2))
        else:
            least_extreme_abovehist =len(smallest_method_values[smallest_method_values['Velocity']>=bins[-1]])
            least_extreme_ls.append(round((least_extreme_abovehist/1000000),2))
            most_extreme_abovehist = len(largest_method_values[largest_method_values['Velocity']>=bins[-1]])      
            most_extreme_ls.append(round((most_extreme_abovehist/1000000),2))
        
        # Difference
        diff_abovehist = most_extreme_abovehist - least_extreme_abovehist
        diff_ls.append(round((diff_abovehist/1000000),4))

        # Add column in dataframe
        df = pd.DataFrame({'label':b, 'LeastExtreme': least_extreme_ls, 'MostExtreme':most_extreme_ls, 'Difference': diff_ls})
        dfs.append(df)
    
    if filter_out_water == False:
        fp_to_save = "../ProcessModelResults/Outputs/Figs/{}Profiles/{}_Histograms.PNG".format(profiles_name, profiles_name_short)
        fig.savefig(fp_to_save, bbox_inches='tight')
    else:
        fp_to_save = "../ProcessModelResults/Outputs/Figs/{}Profiles/{}_Histograms_withoutwater.PNG".format(profiles_name, profiles_name_short)
        fig.savefig(fp_to_save, bbox_inches='tight')
    print(fp_to_save)
    return dfs


def hazard_plot(individual_cell_values_dict,  profiles_name, profiles_name_short, smallest_method_str,
                    largest_method_str,filter_out_water, title = True):
    
    fig, axs = plt.subplots(ncols= 2, nrows=1, sharey=False,figsize = (12,3), gridspec_kw={'hspace':1, 'wspace': 0.2})
    catchments = ['LinDyke', 'WykeBeck']

    ##############################
    # Plot number of flooded cells
    ##############################
    for ax_number, ax in enumerate(axs.flatten()):
        catchment_name = catchments[ax_number]
        if catchment_name == "LinDyke":
            cell_size_in_m2 = 1
        elif catchment_name == "WykeBeck":
            cell_size_in_m2 = 4
        
        # Get data
        individual_cell_values =  individual_cell_values_dict[catchment_name]
        # Filter out cells which are water
        if filter_out_water == True:
            individual_cell_values = individual_cell_values[individual_cell_values['Water_class']==10]
        
        # Get biggest/smallest method data
        largest_method = individual_cell_values[individual_cell_values['short_id'] == largest_method_str]
        smallest_method = individual_cell_values[individual_cell_values['short_id'] == smallest_method_str]
        
        largest_method_val = np.unique(largest_method['Hazard'],return_counts=True)[1]
        smallest_method_val = np.unique(smallest_method['Hazard'],return_counts=True)[1]
        
        largest_method_val =  largest_method_val * (cell_size_in_m2/1000000)
        smallest_method_val =  smallest_method_val* (cell_size_in_m2/1000000)
        
        # make dataframe
        hazard_cats =pd.DataFrame({'Hazard_cat':['Low', 'Moderate', 'Significant', 'Extreme'],
                                  smallest_method_str: smallest_method_val,
                                   largest_method_str:largest_method_val})
        
        hazard_cats.set_index('Hazard_cat').plot.bar(ax=axs[ax_number], rot = 0,  width=0.8, color=['darkblue', 'darkred'])
        
        if title == True:
            axs[ax_number].set_title(catchment_name_ls[ax_number],fontsize=15)      
        
        ax.set_ylabel("Area (km2)")
        ax.set_xlabel('')
        
    if filter_out_water == False:
        fp_to_save =  "../ProcessModelResults/Outputs/Figs/{}Profiles/{}_HazardCats.PNG".format(profiles_name,profiles_name_short)
        fig.savefig(fp_to_save, bbox_inches='tight')
    elif filter_out_water == True:
        fp_to_save = "../ProcessModelResults/Outputs/Figs/{}Profiles/{}_HazardCats_withoutwater.PNG".format(profiles_name,profiles_name_short)
        fig.savefig(fp_to_save, bbox_inches='tight')
    print(fp_to_save)