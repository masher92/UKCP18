##################################################################
# set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)

# Specify catchment name
# catchments = ['Holbeck', 'Mill Beck', 'Wyke Beck', 'Meanwood Beck', 'Fairburn Ings',
# 'GillBeck_Aire', 'LinDyke', 'OilMillBeck', 'GuiseleyBeck']
catchment_name ='Holbeck'

# Read in csv file for one duration in order to extract a list of all the 
# return periods covered
d_1h = pd.read_csv(root_fp +"DataAnalysis/FloodModelling/{}/ReFH2_Data/1h_12mins.csv".format(catchment_name),
                   index_col = False)
rps = d_1h['Return period (yrs)']

# Specify the durations for which there is a csv containing data
durations = ['1h', '3h','5h','7h','9h','11h','13h','15h','17h','19h','21h', '25h','27h', '29h', '31h', '33h', '35h', '37h', '39h']

##################################################################
# Creating dataframe for each return period containing the values 
# for peak flow and direct runoff for each duration (rural and urbanised)
##################################################################
# Create a dictionary to store a dataframe for each return period containing
# the values for each duration
all_rps_all_durations= {}

max_urbrunoff_vals = {}
max_urbflow_vals = {}#
max_rurrunoff_vals ={}
max_rurflow_vals ={}
max_urbrunoff_vals_summer = {}
max_urbflow_vals_summer = {}#
max_rurrunoff_vals_summer ={}
max_rurflow_vals_summer ={}


# Loop through return periods, 
#   Then, loop through durations
for rp in rps:
    if "one_rp_all_durations" in globals():
        del one_rp_all_durations
    print(rp)
    for duration in durations:
        print(duration)
        
        # Read in csv for that duration      
        duration_df = pd.read_csv(root_fp +
                    "DataAnalysis/FloodModelling/IndividualCatchments/{}/ReFH2_Data/{}_12mins.csv".format(catchment_name, duration),
                   index_col = False)
        
        duration_df_summer =  pd.read_csv(root_fp +
                    "DataAnalysis/FloodModelling/IndividualCatchments/{}/ReFH2_Data/Summer/{}_12mins_summer.csv".format(catchment_name, duration),
                   index_col = False)
        
        # Cut the data out for just the return period of this loop
        one_rp_one_duration = duration_df.loc[duration_df['Return period (yrs)'] == rp]
        one_rp_one_duration_summer = duration_df_summer.loc[duration_df_summer['Return period (yrs)'] == rp]

        # rename to summer
        one_rp_one_duration_summer.columns = [str(col) + '_summer' for col in one_rp_one_duration_summer.columns]        
        # join
        one_rp_one_duration = one_rp_one_duration.join(one_rp_one_duration_summer)
        del one_rp_one_duration['Description_summer'], one_rp_one_duration['Return period (yrs)_summer']
        
        # Remove return period variables
        one_rp_one_duration  = one_rp_one_duration.drop(['Return period (yrs)'], axis =1)
        one_rp_one_duration  = one_rp_one_duration.drop(['Description'], axis =1)
        # Set duration as a variable
        one_rp_one_duration ['Duration'] = duration
        
        # If dataframe to store all the durations for the current return period
        # does not exist, then create it using the same column names as the
        # dataframe for one duration
        if 'one_rp_all_durations' not in locals():
            cols = one_rp_one_duration.columns
            one_rp_all_durations = pd.DataFrame(columns=cols)
        
        # Add the values for that duration to the dataframe containing the values
        # for all the durations
        one_rp_all_durations = one_rp_all_durations.append(one_rp_one_duration)

    # Add this dataframe to the dictionary containing the dataframes
    # for each return period
    all_rps_all_durations[rp] = one_rp_all_durations

    ##### Find duration with max values for urban/rural runoff and peak flow
    # Reset index
    one_rp_all_durations.reset_index(drop = True, inplace = True)

    # Use the index of the max values to find the duration at the same index
    max_urbrunoff_vals[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['Urbanised direct runoff (ML)'].argmax()]
    max_urbflow_vals[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['Urbanised peak flow (m^3/s)'].argmax()]
    max_rurrunoff_vals[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['As-rural direct runnof (ML)'].argmax()]
    max_rurflow_vals[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['As-rural peak flow (m^3/s)'].argmax()]
    

    max_urbrunoff_vals_summer[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['Urbanised direct runoff (ML)_summer'].argmax()]
    max_urbflow_vals_summer[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['Urbanised peak flow (m^3/s)_summer'].argmax()]
    max_rurrunoff_vals_summer[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['As-rural direct runnof (ML)_summer'].argmax()]
    max_rurflow_vals_summer[rp] = one_rp_all_durations['Duration'][one_rp_all_durations['As-rural peak flow (m^3/s)_summer'].argmax()]
    


##################################################################
# Create dataframe containing the critical durations for urban/rural runoff
# and save to file
##################################################################
critical_durations = pd.DataFrame({'Urbanised direct runoff (ML)': max_urbrunoff_vals_summer,
                     'As-rural direct runnof (ML)': max_rurrunoff_vals_summer,
                     'Urbanised peak flow (m^3/s)' : max_urbflow_vals_summer,
                     'As-rural peak flow (m^3/s)':max_rurflow_vals_summer,
                     'Urbanised direct runoff (ML)_summer': max_urbrunoff_vals_summer,
                     'As-rural direct runnof (ML)_summer': max_rurrunoff_vals_summer,
                     'Urbanised peak flow (m^3/s)_summer' : max_urbflow_vals_summer,
                     'As-rural peak flow (m^3/s)_summer':max_rurflow_vals_summer})

# Check if Outputs directory exists, and if not then create
if not os.path.isdir(root_fp +"DataAnalysis/FloodModelling/IndividualCatchments/{}/Outputs/".format(catchment_name)):
    os.mkdir(root_fp +"DataAnalysis/FloodModelling/IndividualCatchments/{}/Outputs/".format(catchment_name))

# Save as CSV   
critical_durations.to_csv(root_fp +"DataAnalysis/FloodModelling/IndividualCatchments/{}/Outputs/CriticalDurations.csv".format(catchment_name))

##################################################################
# Plotting - with subplot for each return period
##################################################################
## Direct runoff
fig = plt.figure(figsize=(30, 18))

for rp,subplot_num in zip(rps, range(1,10)):
    
    # Create colours, where the maximum value is highlighted
    length = len(all_rps_all_durations[rp]['Duration'])
    colors_urban = ['black']  * length  
    colors_urban[all_rps_all_durations[rp]['Urbanised direct runoff (ML)'].argmax()] = 'gold'
    colors_rural = ['teal']  * length  
    colors_rural[all_rps_all_durations[rp]['As-rural direct runnof (ML)'].argmax()] = 'gold'
    
    ax = fig.add_subplot(3,3,subplot_num)
    ax.scatter(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['Urbanised direct runoff (ML)'], c= colors_urban, label='Urban')
    ax.scatter(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['As-rural direct runnof (ML)'], c= colors_rural, label='Rural')
    ax.legend(fontsize=18)
    
    # Add vrtical lines to show what the maximum value's duration is
    plt.axvline(x=all_rps_all_durations[rp]['Duration'][all_rps_all_durations[rp]['Urbanised direct runoff (ML)'].argmax()], c = 'black', linestyle='dashed')
    plt.axvline(x=all_rps_all_durations[rp]['Duration'][all_rps_all_durations[rp]['As-rural direct runnof (ML)'].argmax()], c = 'teal', linestyle='dashed')
    
    # Axis labels and title
    ax.set_xlabel('Duration', fontsize=18)
    ax.set_ylabel('Direct Runoff (ml)', fontsize=18)
    ax.set_title("{} Year RP".format(rp), fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=15)

    plt.xticks(rotation = 45)
    
# Add one title
plt.suptitle("{}, Direct Runoff".format(catchment_name), fontsize=34)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/{}/Outputs/DirectRunoff_AllRPs.png".format(catchment_name))
plt.show()

######## Peak flow
fig = plt.figure(figsize=(30, 18))

for rp,subplot_num in zip(rps, range(1,10)):
    
    # Create colours, where the maximum value is highlighted
    length = len(all_rps_all_durations[rp]['Duration'])
    colors_urban = ['black']  * length  
    colors_urban[all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)'].argmax()] = 'gold'
    sizes_urban = [50] * length
    sizes_urban[all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)'].argmax()] = 50
    
    colors_urban_summer = ['black']  * length  
    colors_urban_summer[all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)_summer'].argmax()] = 'gold'
    sizes_urban_summer = [50] * length
    sizes_urban_summer[all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)_summer'].argmax()] = 50
    
    colors_rural = ['teal']  * length  
    colors_rural[all_rps_all_durations[rp]['As-rural peak flow (m^3/s)'].argmax()] = 'gold'    
    sizes_rural = [50] * length
    sizes_rural[all_rps_all_durations[rp]['As-rural peak flow (m^3/s)'].argmax()] = 50 
    
    colors_rural_summer = ['teal']  * length  
    colors_rural_summer[all_rps_all_durations[rp]['As-rural peak flow (m^3/s)_summer'].argmax()] = 'gold'
    sizes_rural_summer = [50] * length
    sizes_rural_summer[all_rps_all_durations[rp]['As-rural peak flow (m^3/s)_summer'].argmax()] = 50 

    # plot
    ax = fig.add_subplot(3,3,subplot_num)
    ax.scatter(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)'], marker = '^', c= colors_urban, s = sizes_urban, label='Urban')
    ax.scatter(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['As-rural peak flow (m^3/s)'], marker = '^', c= colors_rural, s = sizes_rural, label='Rural')
    ax.scatter(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)_summer'],marker = '.', 
         c= colors_urban_summer,s = sizes_urban_summer,  label='Urban_Summer')
    ax.scatter(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['As-rural peak flow (m^3/s)_summer'], marker = '.', c= colors_rural_summer,
         s = sizes_rural_summer, label='Rural_Summer')

    # plt.axvline(x=all_rps_all_durations[rp]['Duration'][all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)'].argmax()], c = 'black', 
    #             linestyle='dashed', label = 'Urban')
    # plt.axvline(x=all_rps_all_durations[rp]['Duration'][all_rps_all_durations[rp]['As-rural peak flow (m^3/s)'].argmax()], c = 'teal',
    #             linestyle='dashed', label = 'Rural')
    # plt.axvline(x=all_rps_all_durations[rp]['Duration'][all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)_summer'].argmax()],
    #             c = 'black', linestyle='solid', label = 'Urban (summer)')
    # plt.axvline(x=all_rps_all_durations[rp]['Duration'][all_rps_all_durations[rp]['As-rural peak flow (m^3/s)_summer'].argmax()], 
    #             c = 'teal', linestyle='solid', label = 'Rural (summer')

   # ax.legend(fontsize=10)
    # Axis labels and title
    ax.set_xlabel('Duration', fontsize=18)
    ax.set_ylabel('Peak flow ($m^3$/s)', fontsize=18)
    ax.set_title("{} Year RP".format(rp), fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=15)

    plt.xticks(rotation = 45)

# Add one title
plt.suptitle("{}, Peak Flow".format(catchment_name), fontsize=34)

box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])

# Put a legend below current axis
handles, labels = ax.get_legend_handles_labels()
ax.legend(loc='best', bbox_to_anchor=(0.6, -0.2),
          fancybox=True, shadow=True, ncol=5, fontsize = 30)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/IndividualCatchments/{}/Outputs/PeakFlowf_AllRPs_summer.png".format(catchment_name),
            bbox_inches = 'tight')
plt.show()