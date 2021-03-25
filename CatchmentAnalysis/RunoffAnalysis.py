##################################################################
# Data files from ReFH2 contain all the return periods for one duration 
# in one csv file.
# This script reformats so that the values for all durations are in one
# table

# It is currently only set up with the urban values; and
# lots are only for peak flows

##################################################################
# Set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import glob as glob
import random
import geopandas as gpd
from scipy.stats import pearsonr
import matplotlib.animation as animation
import warnings
from moviepy.editor import *

# Specify catchment name
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/")
catchments  = glob.glob("*")
catchments.remove("WortleyBeck")
#catchments = ['CarrBeck', 'GillBeck_Aire', 'GillBeck_Wharfe']
#catchments = ['BalneBeck', 'HowleyBeck', 'BagleyBeck', 'GuiseleyBeck']
#catchments = [ 'CollinghamBeck', 'FairburnIngs','FirgreenBeck', 'CockBeck_Aberford']
#catchments = [ 'BushyBeck','Holbeck','LinDyke', 'MeanwoodBeck', 'MillDyke', 'OilMillBeck',
# 'OultonBeck', 'StankBeck', 'WortleyBeck', 'WykeBeck']

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)

# The return periods of interest
rps =   [1, 2, 5, 10, 30, 50, 75, 100, 200, 1000]

# Specify the durations for which there is a csv containing data
durations = ['1h', '3h','5h','7h','9h','11h','13h','15h','17h','19h','21h', '25h','27h', '29h', '31h', '33h', '35h', '37h', '39h']

# Summer or winter profile
seasonal_storm_profiles = ['Summer', 'Winter']

##################################################################
##################################################################
# Create one dictionary for peaks and one for runoff, with:
#      Keys: return periods, summer profile, rurality
#      Items: Dataframe containing values for flow/runoff for each duration, in each
#             catchment, for the RP/storm profile/rurality combo in the key
##################################################################
##################################################################
# Create dictionaries to store for each RP/storm profile/rurality combo:
# a dataframe containins peaks/runoff values for each duration, for each catchment
peaks_all_catchments_allrps ={}
runoff_all_catchments_allrps = {}

# Loop through summer and winter storm profiles
    # Loop through return periods, 
        # Loop through the catchments
        #   For each catchment, loop through durations
        #      Read in the csv containing the values for each RP for that duration
        #      Cut out the values for just the RP of the current loop
        #      Create a dataframe for that catchment containing the values for each duration
        #      Add the peaks/runoff values to a dataframe to store the values from all catchments

for seasonal_storm_profile in seasonal_storm_profiles:
    print(seasonal_storm_profile)
    for rp in rps:
        # Create dataframes to store the results for this RP
        urbanised_peaks_all_catchments = pd.DataFrame()
        urbanised_runoff_all_catchments = pd.DataFrame()
        rural_peaks_all_catchments = pd.DataFrame()
        rural_runoff_all_catchments = pd.DataFrame()
        
        # Create dataframes to store values for runoff/peaks across all durations and all catchments
        # columns are added to these in the loop
        # Loop through catchments and durations
        for catchment_name in catchments:
            #print(catchment_name)
            if "one_catchment_all_durations" in globals():
                del one_catchment_all_durations
            print(rp)
            for duration in durations:
                # Read in csv for that duration      
                duration_df = pd.read_csv(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/{}/ReFH2_Data/{}/{}_12mins.csv".format(catchment_name,seasonal_storm_profile, duration),
                           index_col = False)
                
                # Cut the data out for just the return period of this loop
                one_catchment_one_duration = duration_df.loc[duration_df['Return period (yrs)'] == rp]
             
                # Remove return period variables
                one_catchment_one_duration  = one_catchment_one_duration.drop(['Return period (yrs)'], axis =1)
                one_catchment_one_duration  = one_catchment_one_duration.drop(['Description'], axis =1)
                # Set duration as a variable
                one_catchment_one_duration ['Duration'] = duration
                
                # If dataframe to store all the durations for the current return period
                # does not exist, then create it using the same column names as the
                # dataframe for one duration
                if 'one_catchment_all_durations' not in locals():
                    cols = one_catchment_one_duration.columns
                    one_catchment_all_durations = pd.DataFrame(columns=cols)
                
                # Add the values for that duration to the dataframe containing the values
                # for all the durations
                one_catchment_all_durations = one_catchment_all_durations.append(one_catchment_one_duration)
                # Reset index
                one_catchment_all_durations.reset_index(drop = True, inplace = True)
            
            # Add to dataframe containing values for peaks/runoff across all durations and all catchments
            urbanised_peaks_all_catchments['Duration'],urbanised_peaks_all_catchments[catchment_name]  =one_catchment_all_durations['Duration'], one_catchment_all_durations['Urbanised peak flow (m^3/s)']
            urbanised_runoff_all_catchments['Duration'],urbanised_runoff_all_catchments[catchment_name]  =one_catchment_all_durations['Duration'], one_catchment_all_durations['Urbanised direct runoff (ML)']
            rural_peaks_all_catchments['Duration'],rural_peaks_all_catchments[catchment_name]  =one_catchment_all_durations['Duration'], one_catchment_all_durations['As-rural peak flow (m^3/s)']
            rural_runoff_all_catchments['Duration'],rural_runoff_all_catchments[catchment_name]  =one_catchment_all_durations['Duration'], one_catchment_all_durations['As-rural direct runnof (ML)']
        
        # Add to dictionary containing values for all RP/storm profile/rurality combos
        peaks_all_catchments_allrps[str(rp) + '_Urban_' + seasonal_storm_profile] = urbanised_peaks_all_catchments
        peaks_all_catchments_allrps[str(rp) + '_Rural_' + seasonal_storm_profile] = rural_peaks_all_catchments        
        runoff_all_catchments_allrps[str(rp) + '_Urban_' + seasonal_storm_profile] = urbanised_runoff_all_catchments
        runoff_all_catchments_allrps[str(rp) + '_Rural_' + seasonal_storm_profile] = rural_runoff_all_catchments    
 
##################################################################       
##################################################################
# Find critical durations for peak using both winter and summer seasonal storm
# profiles, and urban and rural model
##################################################################
##################################################################
# Create a dictionary to store results
cds = {}
# Loop through seasonal storm profiles and ruralities
for seasonal_storm_profile in seasonal_storm_profiles:
    for rurality in ['Urban', 'Rural']:
       
        # Create dataframe with catchment names
        # This will be filled with the critical duration values for each RP and each catchment
        cd_allcatchments_allrps = pd.DataFrame({'Catchments':catchments})
        
        # Loop through return periods
        #   Loop through catchments
        #       Finding critical duration for each RP
        for rp in rps:    
            # Extract dataframe storing peaks for this return period/rurality/storm profile
            peaks = peaks_all_catchments_allrps[str(rp) + '_' + rurality + '_' + seasonal_storm_profile]
            # Create dataframe to store critical durations for this RP
            cd_allcatchments_onerp = pd.DataFrame()
            # Loop through catchments
            for catchment_name in catchments:
                # Find the critical duration for this catchment at this RP
                peak_val_idx = peaks[catchment_name].argmax()        
                cd_onecatchment_onerp = pd.DataFrame({'Catchment' : [catchment_name],
                                                  rp: [peaks['Duration'][peak_val_idx]]})
                # Add to dataframe containing results for this RP
                cd_allcatchments_onerp = cd_allcatchments_onerp.append(cd_onecatchment_onerp, ignore_index=True)
                
            # Convert durations to numeric, remove the 'h' from the end 
            cd_allcatchments_onerp[rp] = pd.to_numeric(cd_allcatchments_onerp[rp].str.replace(r'h', ''))
                    
            # Add to dataframe 
            cd_allcatchments_allrps.insert(len(cd_allcatchments_allrps.columns), rp, cd_allcatchments_onerp[rp], True) 
            
            # delete critical durations df (as a new one is needed next loop)
            del cd_allcatchments_onerp
            
        # Add to dictionary       
        cds[seasonal_storm_profile + '_' + rurality] = cd_allcatchments_allrps
    
######################################################################################
######################################################################################
# Create a dataframe containing a row for each catchment, with the catchment's values
# for various catchment descriptors and geometry values
######################################################################################
######################################################################################
# Create a dataframe to populate with rows containing data for each catchment
catchments_info = pd.DataFrame()   

# Loop through catchments reading in spatial information and catchment descriptors
for catchment_name in catchments:
    print(catchment_name)   
    ##############################
    # Shapefiles
    ##############################
    # Define shapefile name
    shpfile_name = glob.glob("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/{}/Shapefile/*.shp".format(catchment_name))
 
    # Read in shapefile 
    concat_shp = gpd.read_file(shpfile_name[0])
    
    ##############################
    # Catchment Descriptors
    ##############################
    # Define catchment descriptors csv file
    filename = glob.glob(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/{}/CatchmentDescriptors/*.csv".format(catchment_name))[0]
    # Read in catchment descriptors 
    catchment_descriptors = pd.read_csv(filename)
    catchment_descriptors =catchment_descriptors[2:]     
    catchment_descriptors = catchment_descriptors[catchment_descriptors.columns[0:2]]

    # Reformat 
    catchment_descriptors = catchment_descriptors.transpose()
    catchment_descriptors.rename(columns=catchment_descriptors.iloc[0], inplace = True)
    catchment_descriptors = catchment_descriptors[1:]
    # Convert values to numeric
    catchment_descriptors[catchment_descriptors.columns] =  catchment_descriptors[catchment_descriptors.columns].apply(pd.to_numeric, errors='coerce')
    catchment_descriptors =  catchment_descriptors.reset_index(drop = True)
    
    ##############################
    # Add easting and northing of centroid
    ##############################
    catchment_descriptors['easting'] = concat_shp['geometry'][0].centroid.coords[0][0]
    catchment_descriptors['northing'] = concat_shp['geometry'][0].centroid.coords[0][1]
    
    ##############################
    # Join together geometry info and catchment descriptors and add to dataframe
    # for all catchments
    ##############################
    catchment_info = pd.concat([concat_shp, catchment_descriptors], axis=1)
    catchment_info['name'] = catchment_name
    catchments_info = pd.concat([catchments_info,catchment_info])

catchments_info = catchments_info.reset_index(drop = True)

##################################################################
##################################################################
#  Create a dataframe containing mean differences between summer and winter values
# (with urban and rural models) and urban and rural values (with summer and winter storms)
##################################################################
##################################################################
# Find the differences between summer values and winter values, and urban values and rural values
mean_differences = pd.DataFrame()

for catchment in catchments:
    print(catchment)
    cds_thiscatchment = pd.DataFrame({})
    for combo in ['Summer_Urban', 'Summer_Rural', 'Winter_Urban', 'Winter_Rural']:
        # Extract the critical durations for this combination
        cds_thiscombo  = cds[combo]
        # Extract the critical durations for this combination, for this catchment
        cds_thiscombo_thiscatchment = cds_thiscombo[cds_thiscombo['Catchments'] == catchment]
        # Rename the catchment column value to the combination stored in this dataframe
        cds_thiscombo_thiscatchment['Catchments'] = combo
        # Add to dataframe storing critical duration values for each combo for this catchment
        cds_thiscatchment = cds_thiscatchment.append(cds_thiscombo_thiscatchment)
    # Rename the Catchments column to Combo    
    cds_thiscatchment = cds_thiscatchment.rename(columns={"Catchments": "Combo"})   
    
    ### Add rows to dataframe containing differences between various combinations
    combo_lists = [['Summer_Rural', "Summer_Urban", "UvR_Diff_Summer"],
             ['Winter_Rural', "Winter_Urban", "UvR_Diff_Winter"],
             ['Summer_Urban', "Winter_Urban", "SvW_Diff_Urban"],
             ['Summer_Rural', "Winter_Rural", "SvW_Diff_Rural"]]
             
    for list in combo_lists:
        print(list)
        differences = cds_thiscatchment[cds_thiscatchment["Combo"] == list[0]].iloc[:, 1:] - cds_thiscatchment[cds_thiscatchment["Combo"] == list[1]].iloc[:, 1:]
        differences.insert(0,'Combo',list[2])
        cds_thiscatchment = cds_thiscatchment.append(differences)
        
    # Mean differences for this catchment
    mean_differences_catchment = pd.DataFrame({'Catchment': catchment,
                                         "UvR_Diff_Winter": cds_thiscatchment[cds_thiscatchment["Combo"] == 'UvR_Diff_Winter'].iloc[:, 1:].mean(axis=1).values[0],
                                         "UvR_Diff_Summer" : cds_thiscatchment[cds_thiscatchment["Combo"] == 'UvR_Diff_Summer'].iloc[:, 1:].mean(axis=1).values[0],
                                         "SvW_Diff_Urban": cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Urban'].iloc[:, 1:].mean(axis=1).values[0],
                                         "SvW_Diff_Rural" : cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Rural'].iloc[:, 1:].mean(axis=1).values[0]}, index=[0])
    # Add to dataframe conttaining values for all catchments
    mean_differences = mean_differences.append(mean_differences_catchment)
    
    mean_differences = mean_differences.reset_index(drop = True)
    
##################################################################
##################################################################
# Plotting:
    # Peaks/runoff values
    # All catchments, one plot
    # One subplot for each RP
    # With each subplot containing a line for each catchment
    # Displaying their values at each duration
##################################################################
##################################################################
catchment_colors =['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', 
'#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', "#006FA6", '#800000', '#aaffc3', 
'#808000', "#FFA0F2", '#000075', '#000000']
mStyles = ["o","v","8", ">","s","p","P","*","h","X","D"] *2
# Create dictionaries
catchment_colors_dict = {catchments[i]: catchment_colors[i] for i in range(len(catchments))} 
catchment_markers_dict = {catchments[i]: mStyles[i] for i in range(len(catchments))} 
# Create seaborn palette
my_pal = sns.set_palette(sns.color_palette(catchment_colors))

# Normalise: 'Yes' or 'No'
normalise = 'Yes'

### Creating plot
for rurality in ['Urban', 'Rural']:
    for seasonal_storm_profile in seasonal_storm_profiles:
        for measure in ['Peaks (m^3/s)', 'Direct Runoff (ml)' ]:
            # Create figure
            fig = plt.figure(figsize=(35, 20)) 
            # Make subplot for each Return Period
            for rp, subplot_num in zip(rps, range(1,10)):
                
                # Extract dataframe storing peaks and runoff for this return period
                if measure == 'Peaks (m^3/s)':
                    measure_title = 'Peaks'
                    measure_df = peaks_all_catchments_allrps[str(rp) + '_' + rurality + '_' + seasonal_storm_profile]
                elif measure == 'Direct Runoff (ml)':
                    measure_df = runoff_all_catchments_allrps[str(rp) + '_' + rurality + '_' + seasonal_storm_profile]
                    measure_title = 'DirectRunoff'
                    
                # Set up the subplot
                ax = fig.add_subplot(3,3,subplot_num)
                # Add lines to that subplot from each catchment
                for i in range(0,len(catchments)):
                    # Find the catchment name
                    catchment_name = catchments[i]
                    
                    #### Make the maximum value for this catchment a different colour
                    # Find the number of points
                    num_durations= len(measure_df)
                    # Find the color for this catchment
                    point_color = catchment_colors_dict[catchment_name]
                    # Repeat the colour the number of times as there is points
                    point_colors = [point_color]  * num_durations  
    
                    # Set the peak value to a different color (gold)
                    peak_val_idx = measure_df[catchment_name].argmax()        
                    critical_duration = measure_df['Duration'][peak_val_idx]
                    point_colors[peak_val_idx] = 'darkblue'
        
                    # If normalise is 'Yes', then normalise
                    if normalise == 'Yes':
                        measure_df_thiscatchment =  measure_df[catchment_name]/ measure_df[catchment_name].max() 
                    else:
                        measure_df_thiscatchment =  measure_df[catchment_name]            
                        
                    #### Plot (df lines and points)
                    ax.plot(measure_df['Duration'],
                     measure_df_thiscatchment,  linestyle = ':', color = point_color )     
                    ax.scatter(measure_df['Duration'],
                     measure_df_thiscatchment, marker = catchment_markers_dict[catchment_name], s =50, c= point_colors,
                     label=catchment_name)
                            
                # Axis labels and title
                ax.set_xlabel('Duration', fontsize=18)
                ax.set_ylabel(measure, fontsize=18)
                ax.set_title("{} Year RP".format(rp), fontsize=20)
                ax.tick_params(axis='both', which='major', labelsize=15)

                plt.xticks(rotation = 45)

            # Put a legend below current axis
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(loc='right', bbox_to_anchor=(0.9, -0.4),
                      fancybox=True, shadow=True, ncol = 8, fontsize = 20, markerscale = 3)
            
            # Add one title
            plt.suptitle("{} {} ({})".format(rurality, measure, seasonal_storm_profile), fontsize=40)
            
            # Adjust height between plots
            fig.subplots_adjust(top=0.92)
            # fig.subplots_adjust(right=0.92)
            plt.subplots_adjust(hspace=0.25)    
            
            # Save and show plot
            plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Runoff/{}_{}_{}.png".format(measure_title, rurality, seasonal_storm_profile),
                        bbox_inches='tight')
            plt.show()

##################################################################
##################################################################
# Plotting:
    # Peaks/runoff values
    # All catchments, one plot
    # One subplot for each RP
    # With each subplot containing a line for each catchment
    # Displaying their values at each duration
##################################################################
##################################################################
# Normalise: 'Yes' or 'No'
normalise = 'Yes'

catchment_groups = {}
catchment_groups["low"] = ['CarrBeck', 'GillBeck_Aire', 'GillBeck_Wharfe']
catchment_groups['med'] = ['BalneBeck', 'HowleyBeck', 'BagleyBeck', 'GuiseleyBeck']
catchment_groups['medhigh'] = [ 'CollinghamBeck', 'FairburnIngs','FirgreenBeck', 'CockBeck_Aberford']
catchment_groups['high'] = [ 'BushyBeck','Holbeck','LinDyke', 'MeanwoodBeck', 'MillDyke',
                            'OilMillBeck','OultonBeck', 'StankBeck', 'WykeBeck']

rp =10
fig = plt.figure(figsize=(35, 20)) 
### Creating plot

for group, catchments, subplot_num in zip(catchment_groups.keys(), catchment_groups.values(), range(1,5)):
    print(group, catchments, subplot_num)
    
    # Make subplot for each Return Period
    measure_df = peaks_all_catchments_allrps[str(rp) + '_Urban_Summer']
        
    # Set up the subplot
    ax = fig.add_subplot(2,2,subplot_num)
    # Add lines to that subplot from each catchment
    for i in range(0,len(catchments)):
        # Find the catchment name
        catchment_name = catchments[i]
        
        #### Make the maximum value for this catchment a different colour
        # Find the number of points
        num_durations= len(measure_df)
        # Find the color for this catchment
        point_color = catchment_colors_dict[catchment_name]
        # Repeat the colour the number of times as there is points
        point_colors = [point_color]  * num_durations  

        # Set the peak value to a different color (gold)
        peak_val_idx = measure_df[catchment_name].argmax()        
        critical_duration = measure_df['Duration'][peak_val_idx]
        point_colors[peak_val_idx] = 'darkblue'

        # If normalise is 'Yes', then normalise
        if normalise == 'Yes':
            measure_df_thiscatchment =  measure_df[catchment_name]/ measure_df[catchment_name].max() 
        else:
            measure_df_thiscatchment =  measure_df[catchment_name]            
            
        #### Plot (df lines and points)
        ax.plot(measure_df['Duration'],
         measure_df_thiscatchment,  linestyle = ':', color = point_color )     
        ax.scatter(measure_df['Duration'],
         measure_df_thiscatchment, marker = catchment_markers_dict[catchment_name], s =200, c= point_colors,
         label=catchment_name)
                
    # Axis labels and title
    ax.set_xlabel('Duration', fontsize=30)
    ax.set_ylabel('Peak Flow ($m^3$/s) ', fontsize=30)
    #ax.set_title("{} Year RP".format(rp), fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=25)
    ax.legend(fontsize = 20, markerscale = 2)

    plt.xticks(rotation = 45)

# Add one title
plt.suptitle("Urban Peak Flow, $m^3$/s (Summer)", fontsize=40)

# # Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.25)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Runoff/UrbanSummerPeaks_grouped.PNG",
            bbox_inches='tight')
plt.show()

catchments_info['group_num'] = [2, 2, 4, 1, 3, 3, 3,3,1,1,2,4,4,4,4,4,4,4,4,4]
plt.scatter(catchments_info['group_num'], catchments_info['ALTBAR'])

            
##################################################################
##################################################################
# Plotting:
    # Critical duration values
    # All catchments, one plot
    # Plot contains a line for each catchment
    # Displaying their critical duration at each return period
##################################################################
##################################################################
# Set up figure    
# Loop through catchments
for seasonal_storm_profile in seasonal_storm_profiles:
    for rurality in ['Urban', 'Rural']:
        # Set up figure
        fig = plt.figure(figsize=(20, 13))
        ax = fig.add_subplot(1,1,1)
        
        critical_durations_allcatchments = cds[seasonal_storm_profile + '_' + rurality]
        
        for i in range(0,len(catchments)):
            # Define catchment name and colour
            catchment_name = catchments[i]
            colour = catchment_colors_dict[catchment_name]
            
            # define critical durations for this return period
            critical_durations = pd.DataFrame(critical_durations_allcatchments.values[i])
            # Reformat
            new_header = critical_durations.iloc[0] #grab the first row for the header
            critical_durations = critical_durations[1:] #take the data less the header row
            critical_durations.columns = new_header #set the header row as the df header
        
            # Create positions to plot on the x-axis
            xaxis_positions =np.arange(len(critical_durations))
            
            # Add line to the plot
            ax.plot(xaxis_positions, critical_durations, color = colour,
                    marker = catchment_markers_dict[catchment_name], linestyle = ':', markersize=20, label=catchment_name)
        
        # Format the plot
        ax.xaxis.set_ticks(xaxis_positions) #set the ticks to be a
        ax.xaxis.set_ticklabels(cd_allcatchments_allrps.columns[1:]) # change the ticks' names to x
        ax.set_xlabel('Return Period', fontsize=20)
        ax.set_ylabel('Critical Duration (Hours)', fontsize=20)
        ax.set_title("Critical Durations - {} Peaks (m^3/s) ({})".format(rurality, seasonal_storm_profile), fontsize=25)
        ax.tick_params(axis='both', which='major', labelsize=15)
        
        # Format the legend
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1,
                          box.width, box.height * 0.9])
        # Put a legend below current axis
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(loc='best', bbox_to_anchor=(1, -0.09),
                  fancybox=True, shadow=True, ncol=8, fontsize = 12, markerscale = 0.6)
           
        # Save and show plot
        plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Runoff/Peaks_criticaldurations_{}_{}.png".format(rurality, seasonal_storm_profile))
        plt.show()

##################################################################
##################################################################
# Plotting:
    # Critical duration values
    # Individual plots each catchment
    # Plot contains a line for each summer/winter and urbna/rural combination
    # Displaying their critical duration at each return period
##################################################################
##################################################################
# Loop through catchments, creating a plot for each catchment        
for i in range(0,len(catchments)):
    # Define catchment
    catchment_name = catchments[i]
    print(catchment_name)
    
    # Set up plot
    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(1,1,1)
    
    # Loop through ruralities and seasonal storm profiles
    for rurality in ['Urban', 'Rural']:
        # Define different base colors for each ruraliy
        if rurality == 'Urban':
            colour = '#000000'
        elif rurality == 'Rural':
            colour = '#008080'          
        for seasonal_storm_profile in seasonal_storm_profiles:
            # Define different marker styles for summer and winter
            if seasonal_storm_profile == 'Summer':
                marker = '^'
            else:
                marker= 'x'
             
            # Get the critical durations for this rurality/storm profile comvbination
            critical_durations_allcatchments = cds[seasonal_storm_profile + '_' + rurality]
            # Extract critical durations for this catchment
            critical_durations = pd.DataFrame(critical_durations_allcatchments.values[i])

            # Create positions to plot on the x-axis
            xaxis_positions =np.arange(len(critical_durations[1:]))
            
            # Add line to the plot
            ax.plot(xaxis_positions, critical_durations[1:], marker = marker, linestyle = ':', 
                    markersize=20, label= rurality + ' (' + seasonal_storm_profile + ')', color = colour)
    
    # Axis labels and title formatting
    ax.xaxis.set_ticks(xaxis_positions) #set the ticks to be a
    ax.xaxis.set_ticklabels(cd_allcatchments_allrps.columns[1:]) # change the ticks' names to x
    ax.set_xlabel('Return period', fontsize=20)
    ax.set_ylabel('Critical Duration (Hours)', fontsize=20)
    ax.set_title("Critical Durations - {}".format(catchment_name), fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=15)
    ax.set_ylim(2,40)
    # Rotate X ticks

    # Set up overall legend
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.3,
                      box.width, box.height * 0.8])
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(loc='best', bbox_to_anchor=(1, -0.072),
              fancybox=True, shadow=True, ncol=8, fontsize = 23, markerscale = 1.5)
    # Adjust height between plots
    fig.subplots_adjust(top=0.92)
    plt.subplots_adjust(hspace=0.35)    
    
    # Save and show plot
    # Individual catchment folders
    plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/IndividualCatchments/CriticalDurations/{}_CriticalDurations.png".format(catchment_name),
                bbox_inches = 'tight')
    plt.show()  
    
    
##################################################################
##################################################################
# Plotting:

##################################################################
##################################################################   
rp = 10

# Create figure
fig = plt.figure(figsize=(35, 20)) 
# Loop through catchments, creating a plot for each catchment        
for catchment_num, subplot_num in zip(range(0,len(catchments)+1), range(1,len(catchments)+1)):
    print(catchment_num, subplot_num)
   
    # Define catchment
    catchment_name = catchments[catchment_num]
    print(catchment_name)
    
    # Loop through measures
    for measure in ['Peaks']:
        # Loop through ruralities
        for rurality in ['Urban', 'Rural']:
            # Define different base colors for each ruraliy
            if rurality == 'Urban':
                colors = ['black']  * len(durations)   
            elif rurality == 'Rural':
                colors = ['teal']  * len(durations)    
            # Loop through seasonal storm profiles
            for seasonal_storm_profile in seasonal_storm_profiles:
                # Define different marker styles for summer and winter
                if seasonal_storm_profile == 'Summer':
                    marker = '^'
                else:
                    marker= 'x'
                ## Extract correct data (according to whether on peak loop or runoff loop)                 
                if measure == 'Peaks':
                    label = 'Peak flow ($m^3$/s)'
                    values = peaks_all_catchments_allrps[str(rp) + '_' + rurality+ '_' + seasonal_storm_profile] 
                elif measure == 'Runoff':
                    label = 'Direct Runoff (ml)'
                    values = runoff_all_catchments_allrps[str(rp) + '_' + rurality+ '_' + seasonal_storm_profile] 
                # Create a copy of the current color scheme being used (depending on urban or rural)
                current_colors = colors.copy()
                # set the maximum value to gold
                current_colors[values[catchment_name].argmax()] = 'gold'    
                    # Set up plot
                ax = fig.add_subplot(4,5,subplot_num)
                # Add line to plot
                ax.scatter(values['Duration'], values[catchment_name], marker = marker, label= rurality  + ' (' + seasonal_storm_profile + ')',
                           color = current_colors, s= 70)
                
                if subplot_num in [16,17,18,19,20]:
                    # Axis labels and title formatting
                    ax.set_xlabel('Duration', fontsize=18)
                if subplot_num in [1,6,11,16]:
                    ax.set_ylabel(label, fontsize=18)
                ax.set_title(catchment_name, fontsize=20)
                ax.tick_params(axis='both', which='major', labelsize=15)
                # Rotate X ticks
                plt.xticks(rotation = 45)
      
        # Add overall figure title
        plt.suptitle("{} year RP".format(rp), fontsize=34)
        
    # # Set up overall legend
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])
handles, labels = ax.get_legend_handles_labels()
labels= ['Model with urban component (Summer)', 'Model with urban component (Winter)',
         'Model without urban component (Summer)', 'Model without urban component (Winter)']
ax.legend(handles,labels, loc='best', bbox_to_anchor=(0.4, -0.3),
          fancybox=True, shadow=True, ncol=2,  fontsize = 30, markerscale = 3)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    
            
# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/{}RP_comparingseason_rurality.png".format(rp),
            bbox_inches = 'tight')
plt.show()  
        

##################################################################
##################################################################
# Plotting:
    # Plots for peaks/runoff
    # Individual plots each catchment
    # One subplot for each RP
    # Plot contains a line for each summer/winter and urbna/rural combination
    # Displaying their value at each duration
##################################################################
##################################################################        
# Loop through catchments
    # Loop through measures
        # Create a figure
            # Loop through return periods
                # for each RP, create a subplot on the figure
                    # Loop through storm profile and ruralities
for catchment_name in catchments:
    print(catchment_name)
    # Loop through measures
    for measure in ['Peaks', 'Runoff']:
        # Set up the figure
        fig = plt.figure(figsize=(30, 18))
        # Loop through RPs and for each work on a subplot
        for rp,subplot_num in zip(rps, range(1,10)):
            # Set up the subplot
            ax = fig.add_subplot(3,3,subplot_num)
            # Loop through ruralities
            for rurality in ['Urban', 'Rural']:
                # Define different base colors for each ruraliy
                if rurality == 'Urban':
                    colors = ['black']  * len(durations)   
                elif rurality == 'Rural':
                    colors = ['teal']  * len(durations)    
                # Loop through seasonal storm profiles
                for seasonal_storm_profile in seasonal_storm_profiles:
                    # Define different marker styles for summer and winter
                    if seasonal_storm_profile == 'Summer':
                        marker = '^'
                    else:
                        marker= 'x'
                    ## Extract correct data (according to whether on peak loop or runoff loop)                 
                    if measure == 'Peaks':
                        label = 'Peak flow ($m^3$/s)'
                        values = peaks_all_catchments_allrps[str(rp) + '_' + rurality+ '_' + seasonal_storm_profile] 
                    elif measure == 'Runoff':
                        label = 'Direct Runoff (ml)'
                        values = runoff_all_catchments_allrps[str(rp) + '_' + rurality+ '_' + seasonal_storm_profile] 
                    # Create a copy of the current color scheme being used (depending on urban or rural)
                    current_colors = colors.copy()
                    # set the maximum value to gold
                    current_colors[values[catchment_name].argmax()] = 'gold'    
                    
                    # Add line to plot
                    ax.scatter(values['Duration'], values[catchment_name], marker = marker, label= rurality  + ' (' + seasonal_storm_profile + ')',
                               color = current_colors, s= 70)
            
            # Axis labels and title formatting
            ax.set_xlabel('Duration', fontsize=18)
            ax.set_ylabel(label, fontsize=18)
            ax.set_title("{} Year RP".format(rp), fontsize=20)
            ax.tick_params(axis='both', which='major', labelsize=15)
            # Rotate X ticks
            plt.xticks(rotation = 45)
          
        # Add overall figure title
        plt.suptitle("{}, {}".format(catchment_name, label), fontsize=34)
        
        # Set up overall legend
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.3,
                          box.width, box.height * 0.8])
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(loc='best', bbox_to_anchor=(0.72, -0.2),
                  fancybox=True, shadow=True, ncol=5,  fontsize = 30, markerscale = 3)
        # Adjust height between plots
        fig.subplots_adjust(top=0.92)
        plt.subplots_adjust(hspace=0.35)    
        
        # Save and show plot
        plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/IndividualCatchments/{}/{}s.png".format(measure, catchment_name),
                    bbox_inches = 'tight')
        plt.show()  
    
##################################################################
##################################################################
# Plotting:
    # Differences between summer and winter
        # and urban and rural
    # Plotted against catchment descriptors
##################################################################
##################################################################     
variable1s = ['AREA', 'DPSBAR', 'URBEXT2000', 'ALTBAR', 'BFIHOST', 'SAAR']
variabl1_units =['Area (km)','Catchment Steepness (m per km)', 'Urban extent (%)', 'Altitude (m above sea level)', 
                 'BFIHOST', 'SAAR (mm)']
variable2s = ['UvR_Diff_Winter', 'UvR_Diff_Summer', 'SvW_Diff_Urban', 'SvW_Diff_Rural']
variable2_units = ['Urban Rural Difference (Winter)', 'Urban Rural Difference (Summer)', 'Summer Winter Difference (Urban)', 
                  'Summer Winter Difference (Rural)']

variable1_units_dict = dict(zip(variable1s, variabl1_units))
variable2_units_dict = dict(zip(variable2s, variable2_units))

for variable1, variable1_unit in variable1_units_dict.items():
    print(variable1)
    for variable2, variable2_unit in variable2_units_dict.items():
        print(variable2)
        
        df2 = pd.DataFrame({'Catchment':catchments_info['name'], 
            variable1 : catchments_info[variable1],
            variable2 :mean_differences[variable2]})
        df2['colo']

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.clear()
        ax = sns.scatterplot(data=df2, x=variable1, y=variable2, style = 'Catchment', 
                    markers = catchment_markers_dict, hue = 'Catchment', s= 100)
        
        ax.set_xlabel(variable1_unit)
        ax.set_ylabel(variable2_unit)
        ax.tick_params(axis='both', which='major')
        ax.legend_.remove()
        plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Allcatchments/Runoff/VsCatchmentDescriptors/{}vs{}.PNG".format(variable1, variable2))

##################################################################
##################################################################
# Plotting:
####### Area vs critical duration
##################################################################
##################################################################         
# Parameters for plotting
plt.rcParams['animation.ffmpeg_path'] = root_fp + 'DataAnalysis/Scripts/ffmpeg-20200225-36451f9-win64-static/bin/ffmpeg'
plt.rcParams['savefig.bbox'] = 'tight' 
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define variable names to use
variable1s = ['Summer_Rural']
variables2s =  ['AREA', 'BFIHOST', 'URBEXT2000', 'LDP', 'DPSBAR', 'ALTBAR']
variable2_units = ['Area (km)', 'BFIHOST', 'Urban Extent (%)', 'Longest drainage path (km)', 
                   'Catchment Steepness (m per km)', 'ALtitude (m)']

for variable1 in variable1s:
    for variable2, variable2_unit in zip(variables2s, variable2_units):
        print(variable1, variable2, variable2_unit)
    
        # Define number of frames
        frames = len(cds[variable1].iloc[:, 1:].columns)
        
        # Set up figure
        fig = plt.figure()
        def draw(frame):
                # clear the previous figure
                plt.clf()
                # Get the critical durations for this summer/winter urban/rural combination
                cds_seasonal = cds[variable1]    
                
                # find return period being useed in this frame
                rp = cds_seasonal.iloc[:, 1:].columns[frame]
                print(rp)
                df2 = pd.DataFrame({'Catchment':catchments_info['name'],
                     'CriticalDuration' : cds_seasonal[rp],
                     variable2 :catchments_info[variable2]})
                
                ax = fig.add_subplot(1,1,1)
                ax.clear()
                ax = sns.scatterplot(data=df2, x='CriticalDuration', y=variable2, style = 'Catchment', 
                            markers = catchment_markers_dict, hue = 'Catchment', s= 100,
                            palette = my_pal)
                ax.set_xlabel('Critical Duration (hrs)')
                ax.set_ylabel(variable2_unit)
                ax.tick_params(axis='both', which='major')
                ax.legend_.remove()
                
                grid =ax.get_children()[0]
                
                plt.title(str(variable1) + ': ' + str(rp) + 'yr return period')
                return grid
            
        def init():
            return draw(0)
        
        def animate(frame):
            return draw(frame)
        
        # Create animation
        ani = animation.FuncAnimation(fig, animate, frames, interval=1, save_count=100, blit=False, init_func=init,repeat=False)
        fp = root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Runoff/CDsVsCatchmentDescriptors/{}vs{}_CriticalDurations".format(variable1,variable2, rp)
        ani.save(fp + '.mp4',writer=animation.FFMpegWriter(fps=1))
        
        # Convert to gif
        clip = (VideoFileClip(fp + '.mp4'))
        clip.write_gif(fp + '.gif')
        # Remove mp4
        os.remove(fp + '.mp4')
        
