import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
import matplotlib.patches as mpatches
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/CreateSyntheticRainfallEvents")

methods=['single-peak','divide-time','max-spread','subpeak-timing']
durations = ['1h', '3h', '6h']

# Set size of x/y tick labels in all subplots
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14

# Create figure
fig, axes = plt.subplots(4, len(methods), figsize=(14,10), sharex =True, sharey = True)

# Set title on columns
for ax, col in zip(axes[0], methods):
    ax.set_title(col, size =16)

# Read in data
for axes_number, method in enumerate(methods):
    
    pre_loss_removal = pd.read_csv("LinDyke_DataAndFigs/SyntheticEvents_preLossRemoval/6h/6h_{}.csv".format(method))
    pre_loss_removal = pre_loss_removal.rename(columns={'2022-04-05 00:00:00': 'Time', '0.0': 'Rainfall'})
    post_loss_removal_urban = pd.read_csv("LinDyke_DataAndFigs/SyntheticEvents_postLossRemoval/6h/6h_{}_urban.csv".format(method))
    post_loss_removal_rural = pd.read_csv("LinDyke_DataAndFigs/SyntheticEvents_postLossRemoval/6h/6h_{}_rural.csv".format(method))
    
    # Convert date to datetime
    pre_loss_removal['Time'] = pd.to_datetime(pre_loss_removal['Time'])
    post_loss_removal_urban['Time'] = pd.to_datetime(post_loss_removal_urban['Time'])
    post_loss_removal_rural['Time'] = pd.to_datetime(post_loss_removal_rural['Time'])
    
    # Filter to only include those within the first 6 hours
    post_loss_removal_urban = post_loss_removal_urban[(post_loss_removal_urban['Time'] >= '2022-05-04 00:00:00') & (post_loss_removal_urban['Time'] < '2022-05-04 06:00:00')]
    post_loss_removal_rural = post_loss_removal_rural[(post_loss_removal_rural['Time'] >= '2022-05-04 00:00:00') & (post_loss_removal_rural['Time'] < '2022-05-04 06:00:00')]
    
    # Dates are flipped between the two, dates are arbitrary anyway, so just make consistent
    pre_loss_removal['Time'] =  post_loss_removal_rural['Time']
    
    # PLot
    axes[0, axes_number].plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'dodgerblue')
    axes[0, axes_number].plot(post_loss_removal_urban['Time'], post_loss_removal_urban['Total net rain mm (Observed rainfall - 05/04/2022) - urbanised model'], color = 'green')
    axes[0, axes_number].plot(post_loss_removal_rural['Time'], post_loss_removal_rural['Total net rain mm (Observed rainfall - 05/04/2022) - as 100% rural model'], color = 'gold')

    axes[1, axes_number].plot(pre_loss_removal['Time'], pre_loss_removal['Rainfall'], color = 'dodgerblue')
    axes[2, axes_number].plot(post_loss_removal_urban['Time'], post_loss_removal_urban['Total net rain mm (Observed rainfall - 05/04/2022) - urbanised model'], color = 'green')
    axes[3, axes_number].plot(post_loss_removal_rural['Time'], post_loss_removal_rural['Total net rain mm (Observed rainfall - 05/04/2022) - as 100% rural model'], color = 'gold')
   
    myFmt = mdates.DateFormatter('%H')
    axes[3, axes_number].xaxis.set_major_formatter(myFmt)
    
fig.text(0.5, 0.05, 'Hour', ha='center', size =16)
fig.text(0.08, 0.5, 'Rainfall (mm)', va='center', rotation='vertical', size = 16)    

green_patch = mpatches.Patch(color='green', label='Losses removed (urban model)')
blue_patch = mpatches.Patch(color='dodgerblue', label='Pre-loss removal')
gold_patch = mpatches.Patch(color='gold', label='Losses removed (rural model)')
plt.legend(handles=[blue_patch, green_patch, gold_patch], loc="lower center", fontsize= 14, bbox_to_anchor=(0.4, -0.95))

plt.savefig("LinDyke_DataAndFigs/4methods_pre-post_loss_removal2.png",dpi=1000,bbox_inches = "tight")

