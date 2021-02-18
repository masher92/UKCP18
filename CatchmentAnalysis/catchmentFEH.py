import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)
d_1h = pd.read_csv(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/1h_12mins.csv",
                   index_col = False)
d_3h = pd.read_csv(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/3h_12mins.csv",
                   index_col = False)
d_11h = pd.read_csv(root_fp +"DataAnalysis/FloodModelling/Holbeck - ReFH2/11h_12mins.csv",
                   index_col = False)

durations = ['1h', '3h','5h','7h','9h','11h','13h','15h','17h','19h','21h', '25h',
             '27h', '29h', '31h', '33h', '35h', '37h', '39h']

for rp in rps:
    del all_rps
    print(rp)
    for duration in durations:
        print(duration)
        
        # Read in csv for that duration
        duration_df = pd.read_csv(root_fp +
                    "DataAnalysis/FloodModelling/Holbeck - ReFH2/{}_12mins.csv".format(duration),
                   index_col = False)
        
        #
        this_rp = duration_df.loc[duration_df['Return period (yrs)'] == rp]
        this_rp = this_rp.drop(['Return period (yrs)'], axis =1)
        this_rp = this_rp.drop(['Description'], axis =1)
        this_rp['Duration'] = duration
        
        # if dataframe to store all rps does not exist, then create
        if 'all_rps' not in locals():
            cols = this_rp.columns
            all_rps = pd.DataFrame(columns=cols)
        
        # ddd
        all_rps = all_rps.append(this_rp)

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


 
d_11h = pd.DataFrame({'RP': [1,2,5,10,30, 50, 100],
                      'DirectRunoff_rural':[403.38,448.49, 601.05,714.57, 918.80, 1031.19, 1217.73],
                      'TotalFlowVol_rural':[1128.58, 1241.65, 1626.56, 1901.81, 2370.25,2621.34, 3018.25 ],                           
                      'PeakFlow_rural': [11.99, 13.12, 16.91, 19.71, 24.70, 27.43, 31.93],
                       'DirectRunoff_urban':[492.31,546.24, 727.17, 860.48, 1097.80, 1227.19, 1440.22],
                      'TotalFlowVol_urban':[1125.30,1245.24, 1621.84, 1896.24, 2371.29, 2621.86, 3019.10],                        
                      'PeakFlow_urban' :[14.31,15.70,20.35, 23.75, 29.78, 33.04, 38.40] })


# 3h duration, 12sec timestep
d_3h = pd.DataFrame({'RP': [1,2,5,10,30, 50, 100],
                      'DirectRunoff_rural':[195.68,225.80, 328.39, 405.05, 538.96, 611.57, 727.93],
                      'TotalFlowVol_rural':[566.65, 649.25, 927.41, 1129.13, 1469.17, 1648.97, 1927.48],                         
                      'PeakFlow_rural': [7.58, 8.45, 11.39, 13.57, 17.37, 19.42, 22.69],
                       'DirectRunoff_urban':[241.15,277.89, 402.19, 494.32, 653.79, 739.57, 876.10],
                      'TotalFlowVol_urban':[565.08, 648.46, 926.11, 1128.22, 1468.57, 1647.78, 1927.23],                      
                      'PeakFlow_urban' :[8.83,9.93, 13.63, 16.36, 21.07, 23.59, 27.60] })



# 21h duration, 12sec timestep
d_21h = pd.DataFrame({'RP': [1,2,5,10,30, 50, 100],
                      'DirectRunoff_rural':[532.46, 586.71,  ],
                      'TotalFlowVol_rural':[1462.68,1597.11],                         
                      'PeakFlow_rural': [13.18, 14.33],
                       'DirectRunoff_urban':[647.70, 712.01],
                      'TotalFlowVol_urban':[1461.33, 1595.57],                      
                      'PeakFlow_urban' :[15.22,16.58] })


d_3h = pd.DataFrame({'RP': [1,2,5,10,30, 50, 100],
                      'DirectRunoff_rural':[],
                      'TotalFlowVol_rural':[],                         
                      'PeakFlow_rural': [],
                       'DirectRunoff_urban':[],
                      'TotalFlowVol_urban':[],                      
                      'PeakFlow_urban' :[] })





        
