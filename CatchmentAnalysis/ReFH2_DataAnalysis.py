import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)
d_1h = pd.read_csv(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/1h_12mins.csv",
                   index_col = False)
rps = d_1h['Return period (yrs)']

durations = ['1h', '3h','5h','7h','9h','11h','13h','15h','17h','19h','21h', '25h',
             '27h', '29h', '31h', '33h', '35h', '37h', '39h']

all_rps_all_durations= {}
for rp in rps:
    if "one_rp_all_durations" in globals():
        del one_rp_all_durations
    print(rp)
    for duration in durations:
        print(duration)
        
        # Read in csv for that duration
        duration_df = pd.read_csv(root_fp +
                    "DataAnalysis/FloodModelling/Holbeck - ReFH2/{}_12mins.csv".format(duration),
                   index_col = False)
        
        # Cut the data out for just the return period of this loop
        one_rp_one_duration = duration_df.loc[duration_df['Return period (yrs)'] == rp]
     
        # Remove return period variables
        one_rp_one_duration  = one_rp_one_duration .drop(['Return period (yrs)'], axis =1)
        one_rp_one_duration  = one_rp_one_duration .drop(['Description'], axis =1)
        # Set duration as a variable
        one_rp_one_duration ['Duration'] = duration
        
        # If dataframe to store all the durations for the current return period
        # does not exist, then create it using the same column names as the
        # dataframe for one duration
        if 'one_rp_all_durations' not in locals():
            cols = one_rp_one_duration.columns
            one_rp_all_durations = pd.DataFrame(columns=cols)
        
        # ddd
        one_rp_all_durations = one_rp_all_durations.append(one_rp_one_duration)

        #
        all_rps_all_durations[rp] = one_rp_all_durations

    ################### PLOT
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    
    #ax1.scatter(all_rps['Duration'], all_rps['Urbanised peak flow (m^3/s)'],
    #            c='r', marker='.')
    #ax1.scatter(all_rps['Duration'], all_rps['As-rural peak flow (m^3/s)'], c='c', marker='.')
    
    plt.xticks(rotation = 45)
    
    # Plot data
    ax1.plot(all_rps['Duration'], all_rps['Urbanised peak flow (m^3/s)'], 'r:^', 
             linewidth=2, markersize=2, label='Urbanised')
    ax1.plot(all_rps['Duration'], all_rps['As-rural peak flow (m^3/s)'], 'g:<', 
             linewidth=2, markersize=2, label='Rural')
    
    # Legend
    ax1.legend()
    
    # Axis labels and title
    ax1.set_xlabel('Duration')
    ax1.set_ylabel('Peak flow ($m^3$/s)')
    ax1.set_title('Peak flow, Holbeck - {}yr RP'.format(rp))
    
    # Save and show plot
    plt.savefig(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/Plots/{}yrRP_peakflow.png".format(rp))
    plt.show()

    ################### PLOT
    fig = plt.figure()
    ax1 = fig.add_subplot(1, 1, 1)
    
    #ax1.scatter(all_rps['Duration'], all_rps['Urbanised peak flow (m^3/s)'],
    #            c='r', marker='.')
    #ax1.scatter(all_rps['Duration'], all_rps['As-rural peak flow (m^3/s)'], c='c', marker='.')
    
    plt.xticks(rotation = 45)
    
    # Plot data
    ax1.plot(all_rps['Duration'], all_rps['Urbanised direct runoff (ML)'], 'r:^', 
             linewidth=2, markersize=2, label='Urbanised')
    ax1.plot(all_rps['Duration'], all_rps['As-rural direct runnof (ML)'], 'g:<', 
             linewidth=2, markersize=2, label='Rural')
    
    # Legend
    ax1.legend()
    
    # Axis labels and title
    ax1.set_xlabel('Duration')
    ax1.set_ylabel('Direct Runoff (ml)')
    ax1.set_title('Direct runoff, Holbeck')

    # Save and show plot
    plt.savefig(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/Plots/{}yrRP_directunoff.png".format(rp))
    plt.show()

####### Ploting together
fig = plt.figure(figsize=(30, 18))

for rp,num in zip(rps, range(1,10)):
    ax = fig.add_subplot(3,3,num)
    ax.plot(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['Urbanised direct runoff (ML)'], 'r:^', linewidth=2, markersize=12, label='Urban')
    ax.plot(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['As-rural direct runnof (ML)'], 'b:^', linewidth=2, markersize=12, label='Rural')

    ax.legend(fontsize=18)
    # Axis labels and title
    ax.set_xlabel('Duration', fontsize=18)
    ax.set_ylabel('Direct Runoff (ml)', fontsize=18)
    ax.set_title("{} Year RP".format(rp), fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=15)

    plt.xticks(rotation = 45)
# Add one title
plt.suptitle("Holbeck, Direct Runoff", fontsize=34)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/Plots/DirectRunoff_AllRPs.png".format(rp))
plt.show()

####### Ploting together
fig = plt.figure(figsize=(30, 18))

for rp,num in zip(rps, range(1,10)):
    ax = fig.add_subplot(3,3,num)
    ax.plot(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['Urbanised peak flow (m^3/s)'], 'r:^', linewidth=2, markersize=12, label='Urban')
    ax.plot(all_rps_all_durations[rp]['Duration'],
         all_rps_all_durations[rp]['As-rural peak flow (m^3/s)'], 'b:^', linewidth=2, markersize=12, label='Rural')

    ax.legend(fontsize=18)
    # Axis labels and title
    ax.set_xlabel('Duration', fontsize=18)
    ax.set_ylabel('Peak flow ($m^3$/s)', fontsize=18)
    ax.set_title("{} Year RP".format(rp), fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=15)

    plt.xticks(rotation = 45)

# Add one title
plt.suptitle("Holbeck, Peak Flow", fontsize=34)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/Plots/PeakFlowf_AllRPs.png".format(rp))
plt.show()