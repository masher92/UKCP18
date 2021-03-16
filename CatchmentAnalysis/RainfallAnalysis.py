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

RP_10yrs = rainfalls_dict_bymetric['10 year rainfall (mm)']
RP_10yrs_t = RP_10yrs.T  
RP_10yrs_t.rename(columns=RP_10yrs_t.iloc[0], inplace = True)
RP_10yrs_t = RP_10yrs_t[1:22]
      
## Check whether bigger difference between Urban and Rural results in
# Catchmens with greater urban extent
# for i in RP_10yrs_t.columns:
#     plt.scatter(transposed['ALTBAR'], RP_10yrs_t[i])
#     plt.xlabel('SAAR (mm)')
#     plt.ylabel('Rainfall (mm) for 2 hour storm, 10 year return period' )
#     #plt.ylim(0,90)
#     plt.show()
#     plt.close()
    
# Create a figure
fig = plt.figure()

# 5 different marker options
markers = ['.', '^', 'x', '<', '>' ] * 5    

# List of colour values with each catchment a different colour
catchment_colors = ["#"+''.join([random.choice('0123456789ABCDEF') for x in range(6)])
             for y in range(len(catchments))]
# List of colour values with each catchment  the same colour
# catchment_colors = ['lightblue'] * len(catchments)  


df = pd.DataFrame({'x': [25, 12, 15, 14, 19, 23, 25, 29],
                   'y': [5, 7, 7, 9, 12, 9, 9, 4],
                   'z': ['A', 'A', 'B', 'B', 'B', 'C', 'C', 'C']})

#view DataFrame




test_values =['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', 
'#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', 
'#808000', '#ffd8b1', '#000075', '#808080',  '#000000']
mStyles = ["o","v","8", ">","s","p","P","*","h","X","D"] *2

catchment_colors_dict = {catchments[i]: test_values[i] for i in range(len(catchments))} 
catchment_markers_dict = {catchments[i]: mStyles[i] for i in range(len(catchments))} 


fig = plt.figure(figsize=(20, 13))
ax = fig.add_subplot(1,1,1)
for name, group in groups:
    print(name)
    color = catchment_colors_dict[name]
    ax.plot(group.ALTBAR, group.Precipitation, marker=catchment_markers_dict[name], linestyle='',
             markersize=30, label=name, color = color, markeredgecolor = 'black')
    # Axis labels and title formatting
    #ax.xaxis.set_ticks(xaxis_positions) #set the ticks to be a
    #ax.xaxis.set_ticklabels(cd_allcatchments_allrps.columns[1:]) # change the ticks' names to x
    ax.set_xlabel('Altitude (m)', fontsize=25)
    ax.set_ylabel('Precipitation (mm)', fontsize=25)
    #ax.set_title("Critical Durations - {}".format(catchment_name), fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=20)
    
# Set up overall legend
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])
handles, labels = ax.get_legend_handles_labels()
ax.legend(loc='best', bbox_to_anchor=(0.99, -0.072),
          fancybox=True, shadow=True, ncol=5, fontsize = 18, markerscale = 0.8)
# Adjust height between plots
fig.subplots_adjust(top=0.92)
plt.subplots_adjust(hspace=0.35)    


frames = len(RP_10yrs_t.columns)   # Number of frames

def draw(frame):
    print(frame)
    plt.clf()
    grid = plt.figure()
    #creating a subplot 
    ax1 = grid.add_subplot(1,1,1)
    # Clear the previous figure
    
    df2 = pd.DataFrame({'Catchment':RP_10yrs_t.index, 
                    'ALTBAR' : transposed['ALTBAR'],
                    'Precipitation' :RP_10yrs_t.iloc[:,frame]})
    #print(df2)
    groups = df2.groupby('Catchment')

    for name, group in groups:
        #print(name)
        color = catchment_colors_dict[name]
        #ax1.clear()
        ax1.plot(group.ALTBAR, group.Precipitation, marker=catchment_markers_dict[name], linestyle='',
                 markersize=30, label=name, color = color, markeredgecolor = 'black')
        # Axis labels and title formatting
        #ax.xaxis.set_ticks(xaxis_positions) #set the ticks to be a
        #ax.xaxis.set_ticklabels(cd_allcatchments_allrps.columns[1:]) # change the ticks' names to x
        #ax.set_xlabel('Altitude (m)', fontsize=25)
        #ax.set_ylabel('Precipitation (mm)', fontsize=25)
        #ax.set_title("Critical Durations - {}".format(catchment_name), fontsize=30)
        #ax.tick_params(axis='both', which='major', labelsize=20)
        
    # Set up overall legend
    #box = ax.get_position()
    #ax.set_position([box.x0, box.y0 + box.height * 0.3,
    #                  box.width, box.height * 0.8])
    #handles, labels = ax.get_legend_handles_labels()
    #ax.legend(loc='best', bbox_to_anchor=(0.99, -0.072),
    #         fancybox=True, shadow=True, ncol=5, fontsize = 18, markerscale = 0.8)
    # Adjust height between plots
    #fig.subplots_adjust(top=0.92)
    #plt.subplots_adjust(hspace=0.35)    
print(grid)
    return grid
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

# Not sure what, if anything, this does
from matplotlib import rc, animation
rc('animation', html='html5')

ani = animation.FuncAnimation(fig, animate, frames, interval=10, save_count=50, blit=False, init_func=init,repeat=False)
ani.save(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/tester2.mp4", writer=animation.FFMpegWriter(fps=8))


frames = len(RP_10yrs_t.columns)   # Number of frames

fig = plt.figure(figsize=(35,25))
def draw(frame):
    # Clear the previous figure
    plt.clf()
    
    df2 = pd.DataFrame({'Catchment':RP_10yrs_t.index, 
                'ALTBAR' : transposed['ALTBAR'],
                'Precipitation' :RP_10yrs_t.iloc[:,frame]})
    
    ax = fig.add_subplot(1,1,1)
    ax.clear()
    ax = sns.scatterplot(data=df2, x='ALTBAR', y='Precipitation', style = 'Catchment', 
                markers = catchment_markers_dict, hue = 'Catchment', s= 1000)
    ax.set_xlabel('Altitude (m)', fontsize=25)
    ax.set_ylabel('Precipitation (mm)', fontsize=25)
    #ax.set_title("Critical Durations - {}".format(catchment_name), fontsize=30)
    ax.tick_params(axis='both', which='major', labelsize=20)
    plt.legend(bbox_to_anchor=(0.5, 0.1), ncol = 5)
    
    grid =ax.get_children()[0]
    
    # Create datetime in human readable format
    plt.xlabel('SAAR (mm)')
    plt.ylabel('Design Rainfall (mm)')
    plt.title(str(RP_10yrs_t.columns[frame]) + 'h')
    return grid
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

# Not sure what, if anything, this does
from matplotlib import rc, animation
rc('animation', html='html5')

ani = animation.FuncAnimation(fig, animate, frames, interval=10, save_count=50, blit=False, init_func=init,repeat=False)
ani.save(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/test3.mp4", writer=animation.FFMpegWriter(fps=8))


####


sns.scatterplot(data=df2, x='ALTBAR', y='Precipitation', style = 'Catchment', 
                markers = catchment_markers_dict, hue = 'Catchment', palette = catchment_colors_dict)

grid = plt.scatter(transposed['SAAR'], RP_10yrs_t.iloc[:,frame])

ax = sns.scatterplot(data=df2, x='ALTBAR', y='Precipitation', style = 'Catchment', 
                markers = catchment_markers_dict, hue = 'Catchment', palette = catchment_colors_dict)
grid =ax.get_children()[0]



# plt.scatter(transposed['SAAR'], RP_10yrs_t[0.25])
# plt.xlabel('SAAR (mm)')
# plt.ylabel('Rainfall (mm) for 2 hour storm, 10 year return period' )

# plt.scatter(transposed['SAAR'], RP_10yrs_t[96.0])
# plt.xlabel('SAAR (mm)')
# plt.ylabel('Rainfall (mm) for 2 hour storm, 10 year return period' )