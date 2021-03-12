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

# Specify catchment name
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/")
catchments  = glob.glob("*")

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)

# Get the rainfall metrics
filename = glob.glob(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/BagleyBeck/DesignRainfall/*.csv")[0]
rainfall = pd.read_csv(filename, index_col = False, skiprows = 9)
rainfall_metrics = rainfall.columns[2:]

# Create figure
fig = plt.figure(figsize=(30,20)) 
# Make subplot for each Return Period
for rainfall_metric, subplot_num in zip(rainfall_metrics, range(1,13)):
    ax = fig.add_subplot(4,4,subplot_num)
    rainfalls_dict = {}
    for catchment_name in catchments:
        # rain in rainfall data
        filename = glob.glob(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/{}/DesignRainfall/*.csv".format(catchment_name))[0]
        rainfall = pd.read_csv(filename, index_col = False, skiprows = 9)
        rainfalls_dict[catchment_name] = rainfall
        # Add line to the plot
        ax.plot(rainfall["Duration hours"], rainfall[rainfall_metric], linestyle = ':', markersize=20, label=catchment_name)
    
    ax.set_xlabel('Duration (hours)', fontsize=15)
    ax.set_ylabel(rainfall_metric, fontsize=15)
    ax.set_title(rainfall_metric, fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=12)

# Add one title
plt.suptitle("Rainfalls", fontsize=40)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
# fig.subplots_adjust(right=0.92)
plt.subplots_adjust(hspace=0.25)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/FloodModelling/AllCatchments/Rainfall/Rainfall.png",
            bbox_inches='tight')

###########################################
rainfalls_dict_bymetric = {}
catchments_with_maxs = pd.DataFrame({'Duration hours': rainfalls_dict[catchment_name]['Duration hours']})

for rainfall_metric in rainfall_metrics:
    df = pd.DataFrame({'Duration hours': rainfalls_dict[catchment_name]['Duration hours']})
    for catchment_name in catchments:
            #
            catchment_df = pd.DataFrame({catchment_name: rainfalls_dict[catchment_name][rainfall_metric]})
            #
            df[catchment_name] = catchment_df[catchment_name]
            
    df['Catchment_with_max_val'] = df.iloc[:, 1:].idxmax(axis=1)    
    catchments_with_maxs[rainfall_metric] = df['Catchment_with_max_val']
       
    # Add to dictionary
    rainfalls_dict_bymetric[rainfall_metric] = df
           
       
catchments_with_maxs = catchments_with_maxs.replace('MillDyke' ,1)
catchments_with_maxs = catchments_with_maxs.replace('GillBeck_Wharfe' ,2)
catchments_with_maxs = catchments_with_maxs.replace('GillBeck_Aire' ,3)
catchments_with_maxs = catchments_with_maxs.replace('StankBeck' ,4)
catchments_with_maxs = catchments_with_maxs.replace('CarrBeck' ,5)
catchments_with_maxs = catchments_with_maxs.replace('FairburnIngs' ,6)


catchments_with_maxs_arr = catchments_with_maxs.iloc[:, 1:].to_numpy()


rps = ['2yr', '5yr','10yr', '20yr','30yr', '50yr','75yr', '100yr',
       '150yr', '200yr','500yr', '1000yr','10000yr']

durations = catchments_with_maxs['Duration hours']


##########
fig = plt.figure(figsize=(20, 13))
ax = fig.add_subplot(1,1,1)
#fig.subplots_adjust(bottom=0.25,left=0.25) # make room for labels

# #cmap = cm.get_cmap('PiYG', 6)
# cmap = plt.get_cmap('RdBu', np.max(test2)-np.min(test2)+1)
# heatmap = ax.pcolor(test2, cmap = cmap)
# cbar = plt.colorbar(heatmap, ticks=np.arange(np.min(test2) + 0.5,np.max(test2)+0.5))

cmap = plt.get_cmap('RdBu', np.max(catchments_with_maxs_arr)-np.min(catchments_with_maxs_arr)+1)
# set limits .5 outside true range
heatmap = plt.pcolor(catchments_with_maxs_arr,cmap=cmap,vmin = np.min(catchments_with_maxs_arr)-.5, vmax = np.max(catchments_with_maxs_arr)+.5)
#tell the colorbar to tick at integers
cax = plt.colorbar(heatmap, ticks=np.arange(np.min(catchments_with_maxs_arr),np.max(catchments_with_maxs_arr)+1), pad=0.02)

cax.ax.tick_params(labelsize=25) 

# Set ticks in center of cells
ax.set_xticks(np.arange(catchments_with_maxs_arr.shape[1]) + 0.5, minor=False)
ax.set_yticks(np.arange(0,383, 20)+ 0.5, minor=False)

# Rotate the xlabels. Set both x and y labels to headers[1:]
ax.set_xticklabels(rps,rotation=90)
ax.set_yticklabels(durations[0::20])

ax.set_xlabel('Return period', fontsize=25)
ax.set_ylabel('Duration (hrs)', fontsize=25)

plt.xticks(rotation = 45)

ax.tick_params(axis='both', which='major', labelsize=20)
plt.show()


