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
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.cm as cm
import statsmodels.formula.api as smf

# Specify catchment name
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/")
catchments  = glob.glob("*")
catchments.remove("WortleyBeck")

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
cd_values ={}
# Loop through seasonal storm profiles and ruralities
for seasonal_storm_profile in seasonal_storm_profiles:
    for rurality in ['Urban', 'Rural']:
       
        # Create dataframe with catchment names
        # This will be filled with the critical duration values for each RP and each catchment
        cd_allcatchments_allrps = pd.DataFrame({'Catchments':catchments})
        # To store the values
        cdvalues_allcatchments_allrps = pd.DataFrame({'Catchments':catchments})
        
        # Loop through return periods
        #   Loop through catchments
        #       Finding critical duration for each RP
        for rp in rps:    
            # Extract dataframe storing peaks for this return period/rurality/storm profile
            peaks = peaks_all_catchments_allrps[str(rp) + '_' + rurality + '_' + seasonal_storm_profile]
            # Create dataframe to store critical durations for this RP
            cd_allcatchments_onerp = pd.DataFrame()
            cdvalues_allcatchments_onerp = pd.DataFrame()
            # Loop through catchments
            for catchment_name in catchments:
                # Find the critical duration for this catchment at this RP
                peak_val_idx = peaks[catchment_name].argmax()     
                # Create dataframe containing the length of the critical duration
                cd_onecatchment_onerp = pd.DataFrame({'Catchment' : [catchment_name],
                                                  rp: [peaks['Duration'][peak_val_idx]]})
                # Create dataframe containing the value found at this critical duration
                cdvalue_onecatchment_onerp = pd.DataFrame({'Catchment' : [catchment_name],
                                                  rp: [peaks[catchment_name][peak_val_idx]]})
                # Add to dataframe containing results for this RP
                cd_allcatchments_onerp = cd_allcatchments_onerp.append(cd_onecatchment_onerp, ignore_index=True)
                cdvalues_allcatchments_onerp = cdvalues_allcatchments_onerp.append(cdvalue_onecatchment_onerp, ignore_index=True)
                
            # Convert durations to numeric, remove the 'h' from the end 
            cd_allcatchments_onerp[rp] = pd.to_numeric(cd_allcatchments_onerp[rp].str.replace(r'h', ''))
                    
            # Add to dataframe 
            cd_allcatchments_allrps.insert(len(cd_allcatchments_allrps.columns), rp, cd_allcatchments_onerp[rp], True) 
            cdvalues_allcatchments_allrps.insert(len(cdvalues_allcatchments_allrps.columns), rp, cdvalues_allcatchments_onerp[rp], True) 
            
            # delete critical durations df (as a new one is needed next loop)
            del cd_allcatchments_onerp
            del cdvalues_allcatchments_onerp
            
        # Add to dictionary       
        cds[seasonal_storm_profile + '_' + rurality] = cd_allcatchments_allrps
        cd_values[seasonal_storm_profile + '_' + rurality] = cdvalues_allcatchments_allrps
        
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
    catchment_descriptors['Easting'] = concat_shp['geometry'][0].centroid.coords[0][0]
    catchment_descriptors['Northing'] = concat_shp['geometry'][0].centroid.coords[0][1]
    
    ##############################
    # Join together geometry info and catchment descriptors and add to dataframe
    # for all catchments
    ##############################
    catchment_info = pd.concat([concat_shp, catchment_descriptors], axis=1)
    catchment_info['name'] = catchment_name
    catchments_info = pd.concat([catchments_info,catchment_info])

catchments_info.reset_index(drop = True, inplace = True)

# Extract from catchments info dataframe the variables of interest
cols= ['name', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting','Northing']
catchments_info_filtered = catchments_info[cols]

##################################################################
##################################################################
#  Create a dataframe containing mean differences between summer and winter values
# (with urban and rural models) and urban and rural values (with summer and winter storms)
##################################################################
##################################################################
# Find the differences between summer values and winter values, and urban values and rural values
mean_differences = pd.DataFrame()
summer_winter_differences_urban =pd.DataFrame()

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
        var1= cds_thiscatchment[cds_thiscatchment["Combo"] == list[0]].iloc[:, 1:]
        var2=cds_thiscatchment[cds_thiscatchment["Combo"] == list[1]].iloc[:, 1:]
        differences = var1- var2
        percent_differences = round(((var1-var2)/var1) *100,2)
        differences.insert(0,'Combo',list[2])
        percent_differences.insert(0,'Combo',list[2] + '_%')
        cds_thiscatchment = cds_thiscatchment.append(differences)
        cds_thiscatchment = cds_thiscatchment.append(percent_differences)
        
    # Mean differences for this catchment
    mean_differences_catchment = pd.DataFrame({'Catchment': catchment,
                                         "UvR_Diff_Winter": cds_thiscatchment[cds_thiscatchment["Combo"] == 'UvR_Diff_Winter'].iloc[:, 1:].mean(axis=1).values[0],
                                         "UvR_Diff_Summer" : cds_thiscatchment[cds_thiscatchment["Combo"] == 'UvR_Diff_Summer'].iloc[:, 1:].mean(axis=1).values[0],
                                         "SvW_Diff_Urban": cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Urban'].iloc[:, 1:].mean(axis=1).values[0],
                                         "SvW_Diff_Rural" : cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Rural'].iloc[:, 1:].mean(axis=1).values[0],
                                         "UvR_%Diff_Winter": cds_thiscatchment[cds_thiscatchment["Combo"] == 'UvR_Diff_Winter_%'].iloc[:, 1:].mean(axis=1).values[0],
                                         "UvR_%Diff_Summer" : cds_thiscatchment[cds_thiscatchment["Combo"] == 'UvR_Diff_Summer_%'].iloc[:, 1:].mean(axis=1).values[0],
                                         "SvW_%Diff_Urban": cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Urban_%'].iloc[:, 1:].mean(axis=1).values[0],
                                         "SvW_%Diff_Rural" : cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Rural_%'].iloc[:, 1:].mean(axis=1).values[0]}, index=[0])
    # Add to dataframe conttaining values for all catchments
    mean_differences = mean_differences.append(mean_differences_catchment)
    mean_differences = mean_differences.reset_index(drop = True)

    #
    catch_summer_winter_differences_urban = cds_thiscatchment[cds_thiscatchment["Combo"] == 'SvW_Diff_Urban'].iloc[:, 1:]
    catch_summer_winter_differences_urban['name']=catchment
    summer_winter_differences_urban = pd.concat([summer_winter_differences_urban, catch_summer_winter_differences_urban],axis=0)

# Find Pearson's R correlations with catchment descriptors
mean_differences = pd.concat([catchments_info_filtered, mean_differences], axis =1)
corrs = mean_differences[mean_differences.columns].corr()["SvW_%Diff_Urban"][:]
corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)
print(corrs)

summer_winter_differences_urban = pd.concat([catchments_info_filtered, summer_winter_differences_urban], axis =1)
corrs = summer_winter_differences_urban[summer_winter_differences_urban.columns].corr()[5][:11]
corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)
print(corrs)

##################################################################
##################################################################
# Plot a spatial plot showing the critical duration for each catchment
# At each RP
##################################################################
##################################################################
cds_summer_urban = cds['Summer_Urban']
rps = cds_summer_urban.columns[1:]
cds_summer_urban = pd.concat([catchments_info, cds_summer_urban], axis =1)

fig = plt.figure(figsize=(35, 10))   
#fig = plt.figure(figsize=(11, 20))   
i = 1
for rp in rps:
    ax = fig.add_subplot(2,5,i)    
    # Create figure
    divider = make_axes_locatable(ax)
    # create `cax` for the colorbar
    cax = divider.append_axes("right", size="5%", pad=-0.2)
    # plot the geodataframe specifying the axes `ax` and `cax` 
    cds_summer_urban.plot(ax=ax, cax=cax, column= rp,cmap=plt.cm.get_cmap('Greens', 10), 
                 edgecolor = 'black',legend=True)
    cax.tick_params(labelsize=15) 
    ax.axis('off')
    ax.set_title(str(rp)+'yr' , fontsize = 25)
    i=i+1
    
#plt.suptitle("Critical Durations", fontsize=40)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
#plt.subplots_adjust(hspace=0.15)    
    
##################################################################
##################################################################
# Plot a spatial plot showing the peak flow at the critical duration
##################################################################
##################################################################
cdvalues_summer_urban = cd_values['Summer_Urban']
rps = cdvalues_summer_urban.columns[1:]
cdvalues_summer_urban = pd.concat([catchments_info, cdvalues_summer_urban], axis =1)

fig = plt.figure(figsize=(35, 10))   
#fig = plt.figure(figsize=(11, 20))   
i = 1
for rp in rps:
    ax = fig.add_subplot(2,5,i)    
    # Create figure
    divider = make_axes_locatable(ax)
    # create `cax` for the colorbar
    cax = divider.append_axes("right", size="5%", pad=-0.2)
    # plot the geodataframe specifying the axes `ax` and `cax` 
    cdvalues_summer_urban.plot(ax=ax, cax=cax, column= rp,cmap=plt.cm.get_cmap('Greens', 10), 
                 edgecolor = 'black',legend=True)
    cax.tick_params(labelsize=15) 
    ax.axis('off')
    ax.set_title(str(rp)+'yr' , fontsize = 25)
    i=i+1
    
#plt.suptitle("Critical Durations", fontsize=40)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
#plt.subplots_adjust(hspace=0.15)    

############ Find correlations

# FInd adjusted R2 values from multiple regression
r2s_df = pd.DataFrame({'RPs' : cdvalues_summer_urban.columns[42:53]})
pos_or_neg_df = pd.DataFrame({'RPs' : cdvalues_summer_urban.columns[42:53]})
for predictor_variable in catchments_info_filtered.columns[1:]:
    print(predictor_variable)
    values = []
    pos_or_neg = []
    for response_variable in cdvalues_summer_urban.columns[42:53]:
        print(response_variable)
        model = smf.ols('Q({})~{}'.format(response_variable, predictor_variable) , data=cdvalues_summer_urban).fit()
        values.append(round(model.rsquared_adj, 2))
        pos_or_neg.append(['Positive' if model.params[1] >0 else 'Negative'])
    r2s_df =pd.concat([r2s_df,pd.DataFrame({predictor_variable : values})], axis=1)
    pos_or_neg_df =pd.concat([pos_or_neg_df,pd.DataFrame({predictor_variable : pos_or_neg})], axis=1)    

r2s_df_t = r2s_df.iloc[:,1:].transpose()
r2s_df_t.columns= r2s_df.iloc[:,0]

# tsting multiple variables
model = smf.ols('Q(75)~LDP+AREA+URBEXT2000+BFIHOST+SAAR' , data=cdvalues_summer_urban).fit()
model.rsquared_adj
model.summary()


### Boxplot
# Define colors so negative correlations are red and positive green
colors = []
for col in pos_or_neg_df.columns[1:]:
    if pos_or_neg_df[col][9] == ['Positive']:
        colors.append('green')
    else:
        colors.append('red')

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
box = plt.boxplot(r2s_df_t, patch_artist=True)
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
ax.set_xticklabels(r2s_df_t.index.values.tolist())
ax.set_ylabel('Adjusted R2', fontsize=10)
plt.xticks(rotation = 90)


fig = plt.figure()
ax = fig.add_subplot(1,1,1)
for i in range(0,len(catchments)):
    # Find the catchment name
    catchment_name = catchments[i]
    cdvalues_summer_urban_thiscatchment = cdvalues_summer_urban[cdvalues_summer_urban['name'] == catchment_name]
    ax.scatter(cdvalues_summer_urban_thiscatchment['AREA'],
               cdvalues_summer_urban_thiscatchment[1000], 
            marker = catchment_markers_dict[catchment_name], s =50, 
            c= catchment_colors_dict[catchment_name],label=catchment_name)

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
catchment_groups['medhigh'] = [ 'BushyBeck','Holbeck','LinDyke', 'MeanwoodBeck', 'MillDyke',
                            'OilMillBeck','OultonBeck', 'StankBeck', 'WykeBeck']
catchment_groups['high'] = [ 'CollinghamBeck', 'FairburnIngs','FirgreenBeck', 'CockBeck_Aberford']

subplot_num = 1
# For each RP
fig = plt.figure(figsize=(35, 10)) 
for rp in rps[:1]:
    # fig = plt.figure(figsize=(35, 20)) 
    ### Creating plot
    
    for group, catchment_names in zip(catchment_groups.keys(), catchment_groups.values()):
        print(group, catchment_names, subplot_num)
        
        # Make subplot for each Return Period
        measure_df = peaks_all_catchments_allrps[str(rp) + '_Urban_Summer']
            
        # Set up the subplot
        ax = fig.add_subplot(1,4,subplot_num)
        # Add lines to that subplot from each catchment
        for i in range(0,len(catchment_names)):
            # Find the catchment name
            catchment_name = catchment_names[i]
            
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
             measure_df_thiscatchment, marker = catchment_markers_dict[catchment_name], s =150, c= point_colors,
             label=catchment_name)
            
        # Axis labels and title
        if subplot_num in [1,5,9,13,17,21,25]:
            ax.set_ylabel('Peak Flow ($m^3$/s) ', fontsize=25)
            #ax.title.set_text(rp)
            #ax.set_title(str(rp) + 'yr', fontsize = 35)
            ax.tick_params(axis='y', which='major', labelsize=25)
        else:
            plt.yticks([], [])
        #if subplot_num in [25,26,27,28]:
        if subplot_num in [1,2,3,4]:
            ax.set_xlabel('Duration', fontsize = 25)
            ax.tick_params(axis='x', which='major', labelsize=25)
        else: 
            plt.xticks([], [])
        ax.legend(fontsize = 20, markerscale = 2)
        #ax.legend_.remove()
        plt.xticks(rotation = 45)
        
        subplot_num=subplot_num+1 
    
    # Add one title
    #plt.suptitle("Urban Peak Flow, $m^3$/s (Summer)", fontsize=40)
    
    # # Adjust height between plots
    fig.subplots_adjust(top=0.85)
    plt.subplots_adjust(hspace=0.25, wspace = 0.05)    
    
# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/RunoffAnalysis/UrbanSummerPeaks_grouped/UrbanSummerPeaks_grouped_1yrRp.PNG",
            bbox_inches='tight')
plt.show()


##################################################################
##################################################################
# Plotting:
    # Critical duration values
    # One subplot for each catchment
    # One line for summer and one line for winter
    # NB: Edit this code to get plot for just urban/summer
##################################################################
##################################################################
# Set up figure    
# Loop through catchments
critical_durations_allcatchments_sum_urb = cds['Summer_Urban']
critical_durations_allcatchments_wint_urb = cds['Winter_Urban']
# critical_durations_allcatchments_sum_rur = cds['Summer_Rural']
# critical_durations_allcatchments_wint_rur = cds['Winter_Rural']

fig = plt.figure(figsize=(20, 13))
for i in range(0,len(catchments)):
    ax = fig.add_subplot(5,4,i+1)
    # Define catchment name and colour
    catchment_name = catchments[i]
    
    # define critical durations for this return period
    critical_durations = pd.DataFrame({'Sum_urb' : critical_durations_allcatchments_sum_urb.values[i],
                                      'Wint_urb':critical_durations_allcatchments_wint_urb.values[i],
                                      #'Sum_rur':critical_durations_allcatchments_sum_rur.values[i],
                                      #'Wint_rur':critical_durations_allcatchments_wint_rur.values[i]
                                      })
    critical_durations = critical_durations[1:] #take the data less the header row

    percent_diff = ((critical_durations['Sum_urb'] -critical_durations['Wint_urb'])/critical_durations['Sum_urb'] ) *100

    # Create positions to plot on the x-axis
    xaxis_positions =np.arange(len(critical_durations))
    
    for n in range(0,len(critical_durations.columns)):
        
        if 'Wint' in critical_durations.columns[n] :
            color = 'teal' 
        else:
            color= 'black'
        if 'rur' in critical_durations.columns[n] :
            linestyle = 'dotted'
        else:
            linestyle= 'solid'
        
        # Add line to the plot
        ax.plot(xaxis_positions, critical_durations.iloc[:,n], linestyle = linestyle, color =color,
                markersize=10,  label = critical_durations.columns[n])
        
    ax.set_title(catchment_name, fontsize = 20)
    ax.set_ylim(0,35)
    # Format the plot
    ax.xaxis.set_ticks(xaxis_positions) #set the ticks to be a
    ax.xaxis.set_ticklabels(cd_allcatchments_allrps.columns[1:]) # change the ticks' names to x
    if i in [16,17,18,19]:
        ax.set_xlabel('Return Period', fontsize=15)
    if i in [0,4,8,12,16]:
        ax.set_ylabel('Hours', fontsize=15)
   # ax.tick_params(axis='both', which='major', labelsize=15)

# Set up overall legend
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])
handles, labels = ax.get_legend_handles_labels()
labels = ['Summer', 'Winter']
ax.legend(handles, labels, loc='best', bbox_to_anchor=(-0.5, -0.42),
          fancybox=True, shadow=True, ncol=8, fontsize = 23, markerscale = 1.5)

# Adjust height between plots
plt.subplots_adjust(hspace=0.55)    
   
# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/RunoffAnalysis/CriticalDuration/CritDuration_eachCatchment_summerAndWinter.png")
plt.show()


##################################################################
##################################################################
# Plotting:
# Boxplot of critical duration values at different return periods
##################################################################
##################################################################   
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
critical_durations_allcatchments_sum_urb.plot(ax=ax,kind='box')
ax.set_xlabel('Return Period', fontsize=10)
ax.set_ylabel('Critical Duration (Hours)', fontsize=10)
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/RunoffAnalysis/CriticalDuration/CritDuration_boxplot.png")
plt.show()

##################################################################
##################################################################
# Plotting
# One subplot for each catchment
# Peak flow over durations, one line for each return period. 
##################################################################
##################################################################   
# Create figure
fig = plt.figure(figsize=(35, 20)) 
# Loop through catchments, creating a plot for each catchment        
for catchment_num, subplot_num in zip(range(0,len(catchments)+1), range(1,len(catchments)+1)):
    print(catchment_num, subplot_num)
   
    # Define catchment
    catchment_name = catchments[catchment_num]
    print(catchment_name)
    
    label = 'Peak flow ($m^3$/s)'

    evenly_spaced_interval = np.linspace(0, 1, len(rps)+1)
    colors = [cm.winter(x) for x in evenly_spaced_interval]

    # Set up plot
    ax = fig.add_subplot(4,5,subplot_num)
    i=0
    for rp in rps:
        values = peaks_all_catchments_allrps[str(rp) + '_Urban_Summer'].copy()
        # Normalise
        values[catchment_name] =  values[catchment_name]/ values[catchment_name].max() 
        
        # set the maximum value to gold
        plt.plot(values['Duration'], values[catchment_name],linewidth =.5, c = colors[i])
        plt.scatter(values['Duration'], values[catchment_name],s = 20, c = colors[i], label = rp)
    
        i=i+1
    
    if subplot_num in [16,17,18,19,20]:
        # Axis labels and title formatting
        ax.set_xlabel('Duration', fontsize=18)
    if subplot_num in [1,6,11,16]:
        ax.set_ylabel(label, fontsize=18)
    ax.set_title(catchment_name, fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=15)
    # Rotate X ticks
    plt.xticks(rotation = 45)
  
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles,labels, loc='best', bbox_to_anchor=(0.7, -0.3),
          fancybox=True, shadow=True, ncol=10,  fontsize = 30, markerscale = 6)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    
            
# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/RunoffAnalysis/UrbanSummerPeaks_byRP/UrbanSummerPeaks_byRP.png",
            bbox_inches = 'tight')
plt.show()  
    
##################################################################
##################################################################
# Plotting:
# Each subfigure is a catchment
# SHowing flow values for different durations
# One line for each urban/rural and summer/winter combo
##################################################################
##################################################################   
rp = 200

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
        for rurality in ['Urban']:
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
                    values = peaks_all_catchments_allrps[str(rp) + '_' + rurality+ '_' + seasonal_storm_profile].copy()
                    #for this_catchment_name in catchments:
                    #    values[this_catchment_name] = values[this_catchment_name]/values[this_catchment_name].max()
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
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/RunoffAnalysis/UrbanPeaks_bySeason/UrbanPeaks_bySeason_{}yrRP.png".format(rp),
            bbox_inches = 'tight')
plt.show()  

##################################################################
##################################################################
# Plotting:
# Each subfigure is a catchment
# Plot difference between summer and winter values at different return periods
##################################################################
##################################################################   
# Create figure
fig = plt.figure(figsize=(35, 20)) 

for catchment_num, subplot_num in zip(range(0,len(catchments)+1), range(1,len(catchments)+1)):
    print(catchment_num, subplot_num)
   
    # Define catchment
    catchment_name = catchments[catchment_num]
    print(catchment_name)
    
    evenly_spaced_interval = np.linspace(0, 1, len(rps)+1)
    colors = [cm.winter(x) for x in evenly_spaced_interval]
    
    #fig = plt.figure(figsize=(35, 20)) 
    ax = fig.add_subplot(4,5,subplot_num)
    i=0
    for rp in rps:
        i=i+1
        #
        summer_values =  peaks_all_catchments_allrps[str(rp) + '_Urban_Summer'].copy()               
        winter_values =  peaks_all_catchments_allrps[str(rp) + '_Urban_Winter'].copy() 
        percent_diff = (summer_values.iloc[:,1:] -winter_values.iloc[:,1:])/((summer_values.iloc[:,1:]+ winter_values.iloc[:,1:])/2) *100
        percent_diff.max()
        percent_diff['Duration'] = summer_values['Duration']

        #Checking correlations
        # percent_diff_t = percent_diff.iloc[:,:-1].T
        # percent_diff_t.columns = percent_diff['Duration']
        # # percent_diff_t['name'] = percent_diff_t.index
        # percent_diff_t.reset_index(inplace=True, drop = True)
        # percent_diff_t = pd.concat([percent_diff_t, catchments_info_filtered], axis=1)
        # corrs = percent_diff_t[percent_diff_t.columns].corr()['7h'][:]
        # corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)
                                                                   
        # Create a copy of the current color scheme being used (depending on urban or rural)
        current_colors = colors.copy()
        # set the maximum value to gold
        current_colors[values[catchment_name].argmax()] = 'gold'  
        
        # Add line to plot
        ax.plot(percent_diff['Duration'], percent_diff[catchment_name], color = colors[i])
        ax.scatter(percent_diff['Duration'], percent_diff[catchment_name], color = colors[i], label = rp)
        
        if subplot_num in [16,17,18,19,20]:
            # Axis labels and title formatting
            ax.set_xlabel('Duration', fontsize=18)
        if subplot_num in [1,6,11,16]:
            ax.set_ylabel('Percentage difference', fontsize=18)
        ax.set_title(catchment_name, fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=15)
        # Rotate X ticks
        plt.xticks(rotation = 45)
  
   # Set up overall legend
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles,labels, loc='best', bbox_to_anchor=(0.8, -0.3),
          fancybox=True, shadow=True, ncol=10,  fontsize = 30, markerscale = 3)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    
            
# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/RunoffAnalysis/UrbanPeaks_bySeason/UrbanPeaks_PercentDiffbySeason.png",
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


corr, _ = pearsonr(catchments_info['ALTBAR'], mean_differences['SvW_Diff_Urban'])
print('Pearsons correlation: %.3f' % corr)

##################################################################
##################################################################
# Find adjusted R2 values between Catchment descriptors and runoff
# Plot a boxplot
##################################################################
### Catchment Descriptors
critical_durations_allcatchments_sum_urb = pd.concat([critical_durations_allcatchments_sum_urb, catchments_info_filtered], axis =1)

# FInd adjusted R2 values from multiple regression
r2s_df = pd.DataFrame({'RPs' : critical_durations_allcatchments_sum_urb.columns[1:11]})
pos_or_neg_df = pd.DataFrame({'RPs' : critical_durations_allcatchments_sum_urb.columns[1:11]})
for predictor_variable in catchments_info_filtered.columns[1:]:
    print(predictor_variable)
    values = []
    pos_or_neg = []
    for response_variable in critical_durations_allcatchments_sum_urb.columns[1:11]:
        print(response_variable)
        model = smf.ols('Q({})~{}'.format(response_variable, predictor_variable) , data=critical_durations_allcatchments_sum_urb).fit()
        values.append(round(model.rsquared_adj, 2))
        pos_or_neg.append(['Positive' if model.params[1] >0 else 'Negative'])
    r2s_df =pd.concat([r2s_df,pd.DataFrame({predictor_variable : values})], axis=1)
    pos_or_neg_df =pd.concat([pos_or_neg_df,pd.DataFrame({predictor_variable : pos_or_neg})], axis=1)    

r2s_df_t = r2s_df.transpose()[1:]

### Boxplot
# Define colors so negative correlations are red and positive green
colors = []
for col in pos_or_neg_df.columns[1:]:
    if pos_or_neg_df[col][9] == ['Positive']:
        colors.append('green')
    else:
        colors.append('red')

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
box = plt.boxplot(r2s_df_t, patch_artist=True)
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
ax.set_xticklabels(r2s_df_t.index.values.tolist())
ax.set_ylabel('Adjusted R2', fontsize=10)
plt.xticks(rotation = 90)


### FEH rainfall
critical_durations_allcatchments_sum_urb = pd.concat([critical_durations_allcatchments_sum_urb, catchments_info_filtered], axis =1)

r2s_df = pd.DataFrame({'RPs' : critical_durations_allcatchments_sum_urb.columns[1:11]})
pos_or_neg_df = pd.DataFrame({'RPs' : critical_durations_allcatchments_sum_urb.columns[1:11]})
for predictor_variable in catchments_info_filtered.columns[1:]:
    print(predictor_variable)
    values = []
    pos_or_neg = []
    for response_variable in critical_durations_allcatchments_sum_urb.columns[1:11]:
        print(response_variable)
        model = smf.ols('Q({})~{}'.format(response_variable, predictor_variable) , data=critical_durations_allcatchments_sum_urb).fit()
        values.append(round(model.rsquared_adj, 2))
        pos_or_neg.append(['Positive' if model.params[1] >0 else 'Negative'])
    r2s_df =pd.concat([r2s_df,pd.DataFrame({predictor_variable : values})], axis=1)
    pos_or_neg_df =pd.concat([pos_or_neg_df,pd.DataFrame({predictor_variable : pos_or_neg})], axis=1)    

r2s_df_t = r2s_df.transpose()[1:]

############################################
# For FEH rainfall have not yet updates to use adjsuted R2 rather than correlation coefficient
###########################################
# Boxplot  
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
box = plt.boxplot(r2s_df_t, patch_artist=True)
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
ax.set_xticklabels(correlations_df.index, fontsize = 8)
ax.set_ylabel('Correlation', fontsize=8)
plt.xticks(rotation = 90)

# INdividual PLot
correlations_df_t["RP"]= correlations_df_t.index
test = correlations_df_t.melt(id_vars=["RP"], value_vars=['0.25h', '1.0h', '3.0h', '5.0h', '10.0h', '15.0h', '50.0h'])
                                    
sns.catplot(x="variable", y="value", hue="RP",jitter=False, data=test)
plt.xticks(rotation = 90)

##################################################################
##################################################################
# Plotting:
# Difference between critical duration at different return periods against catchment descriptors
# ANd finding correlations
##################################################################
cds_urban_summer = cds['Summer_Urban']
cds_urban_summer['Diff1_1000']  = round(((cds_urban_summer[1]-cds_urban_summer[1000])/cds_urban_summer[1]) *100,2)
cds_urban_summer = pd.concat([cds_urban_summer,catchments_info_filtered], axis = 1)
cds_urban_summer = cds_urban_summer.iloc[:,11:]

corrs = cds_urban_summer[cds_urban_summer.columns].corr()["Diff1_1000"][:]
corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)

# Scatter plot
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
sns.scatterplot(data=cds_urban_summer, x='Diff1_1000', y='LDP', style = 'name', 
                    markers = catchment_markers_dict, hue = 'name', s= 100)
ax.legend_.remove()

###################################################
###################################################
#
###################################################
###################################################        
# Define return period of the peak flow
peakflow_rp =1
# Extract peak flows for this return period
summer_values = peaks_all_catchments_allrps[str(peakflow_rp) + '_Urban_Summer'].copy()               

#Checking correlations
# OLS regression
r2s_df = pd.DataFrame({'Duration' : summer_values_t.columns[:-12]})
pos_or_neg_df =  pd.DataFrame({'Duration' : summer_values_t.columns[:-12]})
for predictor_variable in catchments_info_filtered.columns[1:]:
    print(predictor_variable)
    values = []
    pos_or_neg = []
    for response_variable in summer_values_t.columns[:-12]:
        print(response_variable)
        model = smf.ols('Q("{}")~{}'.format(response_variable, predictor_variable) , data=summer_values_t).fit()
        values.append(round(model.rsquared_adj, 2))
        pos_or_neg.append(['Positive' if model.params[1] >0 else 'Negative'])
    r2s_df =pd.concat([r2s_df, pd.DataFrame({predictor_variable : values})], axis=1)
    pos_or_neg_df =pd.concat([pos_or_neg_df,pd.DataFrame({predictor_variable : pos_or_neg})], axis=1) 

r2s_df_t = r2s_df.T[1:]


### Boxplot
colors = []
for col in pos_or_neg_df.columns[1:]:
    if pos_or_neg_df[col][9] == ['Positive']:
        colors.append('green')
    else:
        colors.append('red')
        
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
box = plt.boxplot(r2s_df, patch_artist=True)
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
ax.set_xticklabels(r2s_df_t.index)
ax.set_ylabel('Absoloute Correlation', fontsize=10)
plt.xticks(rotation = 90)

# Indidivudal plot
correlations_df_t["Duration"]= correlations_df_t.index
test = r2s_df.melt(id_vars=["Duration"], value_vars=['AREA', 'ALTBAR', 'BFIHOST', 'DPSBAR', 'FARL', 'LDP', 'PROPWET', 'SAAR',
       'URBEXT2000', 'Easting', 'Northing'])

fig, ax = plt.subplots()                                    
ax  = sns.catplot(x="variable", y="value", hue="Duration",jitter=True, data=test,
            palette=sns.color_palette("viridis", 20))
plt.xticks(rotation = 90)
ax.set_ylabels("Pearson's R correlation coefficient", fontsize=10)
ax.set_xlabels("")


### FEH rainfall
rainfall_rp ='500 year rainfall (mm)'
rp_rainfalls = design_rainfall_by_rp[str(rainfall_rp)]
rp_rainfalls =rp_rainfalls.add_suffix('h')

correlations_df = pd.DataFrame()
for duration in summer_values_t.columns[0:19]:
    print(duration)
    summer_values_t_thisdur= pd.concat([summer_values_t[duration],
                                                      rp_rainfalls_t], axis = 1)
   
    corrs = summer_values_t_thisdur[summer_values_t_thisdur.columns].corr()[duration][:]

    correlations_df[duration]= corrs[1:]
   
correlations_df = correlations_df.iloc[::20, :]

correlations_df_t = correlations_df.transpose()
correlations_df_t_abs = abs(correlations_df_t)
correlations_df_abs = abs(correlations_df)

# Boxplot  
# fig = plt.figure()
# ax = fig.add_subplot(1,1,1)
# box = plt.boxplot(correlations_df, patch_artist=True)
# for patch, color in zip(box['boxes'], colors):
#     patch.set_facecolor(color)
# ax.set_xticklabels(correlations_df.index, fontsize = 8)
# ax.set_ylabel('Correlation', fontsize=8)
# plt.xticks(rotation = 90)

# INdividual PLot
correlations_df_t["Duration"]= correlations_df_t.index
test = correlations_df_t.melt(id_vars=["Duration"], 
                              value_vars=correlations_df_t.columns.tolist()[:-1])
test.rename(columns={'Duration': 'Peak Flow Duration'}, inplace=True)                                

fig, ax = plt.subplots()                                    
ax  =sns.catplot(x="variable", y="value", hue="Peak Flow Duration",jitter=True, data=test,
            palette=sns.color_palette("viridis", 20))
plt.xticks(rotation = 90)
ax.set_ylabels("Pearson's R correlation coefficient", fontsize=10)
ax.set_xlabels("FEH13 Rainfall Duration")