##################################################################
# Set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)

# Specify catchment name
catchments = ['Holbeck', 'MillDyke', 'WykeBeck', 'MeanwoodBeck', "FairburnIngs" , 
              "GillBeck_Aire", "LinDyke", 'OilMillBeck', 'GuiseleyBeck', 'FirgreenBeck']

# The return period of interest
rp = 1

# Specify the durations for which there is a csv containing data
durations = ['1h', '3h','5h','7h','9h','11h','13h','15h','17h','19h','21h', '25h','27h', '29h', '31h', '33h', '35h', '37h', '39h']

# Read in csv file for one duration in order to extract a list of all the 
# return periods covered
d_1h = pd.read_csv(root_fp +"DataAnalysis/FloodModelling/FairburnIngs/ReFH2_Data/1h_12mins.csv",
                   index_col = False)
rps = d_1h['Return period (yrs)']

# ['Urbanised peak flow (m^3/s)', 'Urbanised direct runoff (ML)', 'As-rural peak flow (m^3/s)', 'As-rural direct runoff (ML)']
measure  = 'As-rural peak flow (m^3/s)'
# [ 'RualPeakFlow', 'UrbanPeakFlow]
measure_title ="RuralPeakFlow"

# Create a colour palette
palette = sns.color_palette(None, len(catchments))

##################################################################
# Creating dataframe for each return period containing the values 
# for peak flow and direct runoff for each duration (rural and urbanised)
##################################################################
# Create Figure
fig = plt.figure(figsize=(35, 20))

# Loop through return periods, creating a plot for each
for rp,subplot_num in zip(rps, range(1,10)):
    # Create a dictionary to store a dataframe for each return period containing
    # the values for each duration
    all_catchments_all_durations= {}
    
    # Loop through return periods, 
    #   Then, loop through durations
    for catchment_name in catchments:
        if "one_catchment_all_durations" in globals():
            del one_catchment_all_durations
        print(rp)
        for duration in durations:
            print(duration)
            
            # Read in csv for that duration      
            duration_df = pd.read_csv(root_fp + "DataAnalysis/FloodModelling/{}/ReFH2_Data/{}_12mins.csv".format(catchment_name, duration),
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
        
        ##### Find duration with max values for urban/rural runoff and peak flow
        # Reset index
        one_catchment_all_durations.reset_index(drop = True, inplace = True)
        
        # Add this dataframe to the dictionary containing the dataframes
        # for each return period
        all_catchments_all_durations[catchment_name] = one_catchment_all_durations
        
    ##################################################################
    # Plotting - with subplot for each return period
    ##################################################################
    ax = fig.add_subplot(3,3,subplot_num)
    for i in range(0,len(catchments)):
        catchment_name = catchments[i]
        color = palette[i]
        print(i)
        ax.plot(all_catchments_all_durations[catchment_name]['Duration'],
             all_catchments_all_durations[catchment_name][measure], 
             color = palette[i], marker = '^', linestyle = ':', linewidth=2, markersize=8, 
             label= catchment_name)
              
        plt.axvline(x=all_catchments_all_durations[catchment_name]['Duration'][all_catchments_all_durations[catchment_name][measure].argmax()]
                        , c = color, linestyle='dashed')
    
    # Axis labels and title
    ax.set_xlabel('Duration', fontsize=18)
    ax.set_ylabel(measure, fontsize=18)
    ax.set_title("{} Year RP".format(rp), fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=15)
    
    plt.xticks(rotation = 45)

# box = ax.get_position()
# ax.set_position([box.x0, box.y0 + box.height * 0.1,
#                  box.width, box.height * 0.9])

# Put a legend below current axis
handles, labels = ax.get_legend_handles_labels()
ax.legend(loc='right', bbox_to_anchor=(0.65, -0.35),
          fancybox=True, shadow=True, ncol=5, fontsize = 30)

# Add one title
plt.suptitle("{}, by duration".format(measure), fontsize=34)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
# fig.subplots_adjust(right=0.92)
plt.subplots_adjust(hspace=0.35)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/AllCatchments/{}_byduration.png".format(measure_title))
plt.show()

##################################################################
# Plotting - with subplot for each return period
##################################################################
fig = plt.figure(figsize=(20, 13))
ax = fig.add_subplot(1,1,1)

for i in range(0,len(catchments)):
    catchment_name = catchments[i]
    colour = palette[i]
    
    critical_durations = pd.read_csv("DataAnalysis/FloodModelling/{}/Outputs/CriticalDurations.csv".format(catchment_name))
    critical_durations[measure] = pd.to_numeric(critical_durations[measure].str.replace(r'h', ''))
    catchment_critical_durations[catchment_name] = critical_durations

    # ?
    a=np.arange(len(critical_durations['Unnamed: 0']))
    
    # Add line to the plot
    ax.plot(a, critical_durations[measure], color = colour,
            marker = markers[i], linestyle = ':', markersize=20, label=catchment_name)

    
ax.xaxis.set_ticks(a) #set the ticks to be a
ax.xaxis.set_ticklabels(critical_durations['Unnamed: 0']) # change the ticks' names to x

ax.set_xlabel('Return Period', fontsize=20)
ax.set_ylabel('Critical Duration (Hours)', fontsize=20)
ax.set_title("Critical Durations - {}".format(measure), fontsize=25)
ax.tick_params(axis='both', which='major', labelsize=15)

box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                  box.width, box.height * 0.9])

# Put a legend below current axis
handles, labels = ax.get_legend_handles_labels()
ax.legend(loc='left', bbox_to_anchor=(0.96, -0.1),
          fancybox=True, shadow=True, ncol=5, fontsize = 20)
    
# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/AllCatchments/{}_criticalduration.png".format(measure_title))
plt.show()
