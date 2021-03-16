##################################################################
# Set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob as glob
import matplotlib.animation as animation
import random
import warnings
import seaborn as sns

# Specify catchment name
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/")
catchments  = glob.glob("*")

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)

# Parameters for plotting
plt.rcParams['animation.ffmpeg_path'] = root_fp + 'DataAnalysis/Scripts/ffmpeg-20200225-36451f9-win64-static/bin/ffmpeg'
plt.rcParams['savefig.bbox'] = 'tight' 
warnings.simplefilter(action='ignore', category=FutureWarning)

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
plt.suptitle("Annual maximum rainfall accumulation, by duration and return period", fontsize=40)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
# fig.subplots_adjust(right=0.92)
plt.subplots_adjust(hspace=0.25)    

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/Rainfall.png",
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
            
    df['Catchment_with_max_val'] = df.iloc[:, 1:].idxmin(axis=1)    
    catchments_with_maxs[rainfall_metric] = df['Catchment_with_max_val']
       
    # Add to dictionary
    rainfalls_dict_bymetric[rainfall_metric] = df
           
       
# catchments_with_maxs = catchments_with_maxs.replace('MillDyke' ,1)
# catchments_with_maxs = catchments_with_maxs.replace('GillBeck_Wharfe' ,2)
# catchments_with_maxs = catchments_with_maxs.replace('GillBeck_Aire' ,3)
# catchments_with_maxs = catchments_with_maxs.replace('StankBeck' ,4)
# catchments_with_maxs = catchments_with_maxs.replace('CarrBeck' ,5)
# catchments_with_maxs = catchments_with_maxs.replace('FairburnIngs' ,6)

catchments_with_maxs = catchments_with_maxs.replace('Holbeck' ,1)
catchments_with_maxs = catchments_with_maxs.replace('BalneBeck' ,2)
catchments_with_maxs = catchments_with_maxs.replace('FairburnIngs' ,3)
catchments_with_maxs = catchments_with_maxs.replace('OultonBeck' ,4)
catchments_with_maxs = catchments_with_maxs.replace('BushyBeck' ,5)
catchments_with_maxs = catchments_with_maxs.replace('MeanwoodBeck' ,6)
catchments_with_maxs = catchments_with_maxs.replace('CockBeck_Aberford' ,7)

catchments_with_maxs_arr = catchments_with_maxs.iloc[:, 1:].to_numpy()


rps = ['2yr', '5yr','10yr', '20yr','30yr', '50yr','75yr', '100yr',
       '150yr', '200yr','500yr', '1000yr','10000yr']

durations = catchments_with_maxs['Duration hours']


#########################################################
# Heat map plot
#########################################################
fig = plt.figure(figsize=(20, 13))
ax = fig.add_subplot(1,1,1)
#fig.subplots_adjust(bottom=0.25,left=0.25) # make room for labels

# #cmap = cm.get_cmap('PiYG', 6)
# cmap = plt.get_cmap('RdBu', np.max(test2)-np.min(test2)+1)
# heatmap = ax.pcolor(test2, cmap = cmap)
# cbar = plt.colorbar(heatmap, ticks=np.arange(np.min(test2) + 0.5,np.max(test2)+0.5))

#cmap = plt.get_cmap('RdBu', np.max(catchments_with_maxs_arr)-np.min(catchments_with_maxs_arr)+1)
cmap = plt.get_cmap('PRGn', np.max(catchments_with_maxs_arr)-np.min(catchments_with_maxs_arr)+1)
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


plt.savefig(root_fp +"DataAnalysis/FloodModelling/AllCatchments/Rainfall/HeatMap_mins.png",
                bbox_inches = 'tight')
plt.show()


##################################################################  
# Read in catchment descriptors
##################################################################
for catchment_name in catchments:
    print(catchment_name)
    filename = glob.glob(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/{}/CatchmentDescriptors/*.csv".format(catchment_name))[0]
    catchment_descriptors = pd.read_csv(filename)
    catchment_descriptors =catchment_descriptors[2:]     
    catchment_descriptors = catchment_descriptors[catchment_descriptors.columns[0:2]]
        
    if "catchment_descriptors_all_catchments" not in globals():
        print("True")
        catchment_descriptors_all_catchments = catchment_descriptors

    catchment_descriptors_all_catchments[catchment_name]=catchment_descriptors[' "FEH CD-ROM"']    
    # Convert column to numeric
    catchment_descriptors_all_catchments[catchment_name] =pd.to_numeric(catchment_descriptors_all_catchments[catchment_name])    
    
# Rename columns
catchment_descriptors_all_catchments.rename(columns={"VERSION": "Catchment Descriptor"}, inplace = True)
# Delete extra column
del catchment_descriptors_all_catchments[' "FEH CD-ROM"']  

# Reformat
transposed = catchment_descriptors_all_catchments.transpose()
transposed.rename(columns=transposed.iloc[0], inplace = True)
transposed = transposed[1:]

# Create dictionary liking catchment names to a marker and color
catchment_colors =['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', 
'#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', 
'#808000', '#ffd8b1', '#000075', '#808080',  '#000000']
mStyles = ["o","v","8", ">","s","p","P","*","h","X","D"] *2
# Create dictionaries
catchment_colors_dict = {catchments[i]: catchment_colors[i] for i in range(len(catchments))} 
catchment_markers_dict = {catchments[i]: mStyles[i] for i in range(len(catchments))} 


# Create dataframe with....
rp = 100
rp_rainfalls = rainfalls_dict_bymetric[str(rp) + ' year rainfall (mm)']
rp_rainfalls_t = rp_rainfalls.T  
rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
rp_rainfalls_t = rp_rainfalls_t[1:22]

# Create the figure

# define number of frames
frames = len(rp_rainfalls_t.columns)   # Number of frames
frames = 10

fig = plt.figure(figsize=(5,2))
def draw(frame):
    # Clear the previous figure
    plt.clf()
    
    df2 = pd.DataFrame({'Catchment':rp_rainfalls_t.index, 
                'SAAR' : transposed['SAAR'],
                'Precipitation' :rp_rainfalls_t.iloc[:,frame]})
    
    ax = fig.add_subplot(1,1,1)
    ax.clear()
    ax = sns.scatterplot(data=df2, x='SAAR', y='Precipitation', style = 'Catchment', 
                markers = catchment_markers_dict, hue = 'Catchment', s= 100)
    ax.set_xlabel('SAAR (mm)')
    ax.set_ylabel('Precipitation (mm)')
    ax.tick_params(axis='both', which='major')
    ax._legend.remove()
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.3,
    #                   box.width, box.height * 0.8])
    # handles, labels = ax.get_legend_handles_labels()
    # ax.legend(handles[1:],labels[1:], loc='best', bbox_to_anchor=(1.05, -0.122),
    #         fancybox=True, shadow=True, ncol=4)
    #Adjust height between plots
    #fig.subplots_adjust(top=1.22)
    #fig.subplots_adjust(bottom=0.1)    
    #plt.subplots_adjust(hspace=0.85)    
    
    grid =ax.get_children()[0]
    
    # Create datetime in human readable format
    plt.xlabel('SAAR (mm)')
    plt.ylabel('Design Rainfall (mm)')
    plt.title(str(rp_rainfalls_t.columns[frame]) + 'h')
    return grid
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

# Not sure what, if anything, this does
# from matplotlib import rc, animation
# rc('animation', html='html5')

ani = animation.FuncAnimation(fig, animate, frames, interval=10, save_count=50, blit=False, init_func=init,repeat=False)
ani.save(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/SAARvs{}yrRPrainfall.mp4".format(rp),
         writer=animation.FFMpegWriter(fps=8))
