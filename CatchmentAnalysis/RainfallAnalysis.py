##################################################################
# Set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob as glob
import matplotlib.animation as animation
import warnings
import seaborn as sns
from moviepy.editor import *
import geopandas as gpd

# Specify catchment name
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/")
catchments  = glob.glob("*")
catchments.remove("WortleyBeck")

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/"
os.chdir(root_fp)

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

catchments_info = catchments_info.reset_index(drop = True)

######################################################################################
######################################################################################
# Create a dictionary containing:
#    Keys: catchment names
#    items: A dataframe containing rainfalls for duration/return period combinations
######################################################################################
######################################################################################
# Get the rainfall metrics
filename = glob.glob(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/BagleyBeck/DesignRainfall/*.csv")[0]
rainfall = pd.read_csv(filename, index_col = False, skiprows = 9)
rps = rainfall.columns[2:]

# Make subplot for each Return Period
for rp in rps:
    design_rainfall_by_catchment = {}
    for catchment_name in catchments:
        # rain in rainfall data
        filename = glob.glob(root_fp + "DataAnalysis/FloodModelling/IndividualCatchments/{}/DesignRainfall/*.csv".format(catchment_name))[0]
        rainfall = pd.read_csv(filename, index_col = False, skiprows = 9)
        design_rainfall_by_catchment[catchment_name] = rainfall

######################################################################################
######################################################################################
# Create a dictionary containing:
#    Keys: Return periods
#    items: A dataframe containing rainfalls for duration/return period combinations
        
# And a dataframe containing the catchment with maximum value for each return period/duration
# And a dataframe containing the catchment with minimum value for each return period/duration        
######################################################################################
######################################################################################
design_rainfall_by_rp = {}
catchments_with_maxs = pd.DataFrame({'Duration hours': design_rainfall_by_catchment[catchment_name]['Duration hours']})
catchments_with_mins = pd.DataFrame({'Duration hours': design_rainfall_by_catchment[catchment_name]['Duration hours']})

for rp in rps:
    df = pd.DataFrame({'Duration hours': design_rainfall_by_catchment[catchment_name]['Duration hours']})
    for catchment_name in catchments:
            catchment_df = pd.DataFrame({catchment_name: design_rainfall_by_catchment[catchment_name][rp]})
            df[catchment_name] = catchment_df[catchment_name]
    
    # Add values to max/min dataframes
    #df['Catchment_with_max_val'] = df.iloc[:, 1:].idxmax(axis=1)   
    #df['Catchment_with_min_val'] = df.iloc[:, 1:].idxmin(axis=1)    
    # Add value to dictionary
    catchments_with_maxs[rp] = df.iloc[:, 1:].idxmax(axis=1)   
    catchments_with_mins[rp] = df.iloc[:, 1:].idxmin(axis=1)   
      
    # Add to dictionary
    design_rainfall_by_rp[rp] = df

######################################################################################
######################################################################################
# Heat map plot     
######################################################################################
######################################################################################
# convert catchment names to numbers for plotting
x= 1
for catchment_name in ['MillDyke', 'GillBeck_Wharfe', 'GillBeck_Aire', 'StankBeck',
                       'CarrBeck', 'FairburnIngs'] :
    print(catchment_name)
    catchments_with_maxs = catchments_with_maxs.replace(catchment_name ,x)
    x = x+1
x=1
for catchment_name in ['Holbeck', 'BalneBeck', 'FairburnIngs', 'OultonBeck',
                       'BushyBeck', 'MeanwoodBeck', 'CockBeck_Aberford'] :
    print(catchment_name)
    catchments_with_mins = catchments_with_mins.replace(catchment_name ,x)
    x = x+1    

# Convert to arrays
catchments_with_maxs_arr = catchments_with_maxs.iloc[:, 1:].to_numpy()
catchments_with_mins_arr = catchments_with_mins.iloc[:, 1:].to_numpy()

##########
# Plot
##########
for array in catchments_with_maxs_arr, catchments_with_mins_arr:
    print(array)
    
    if 7 in array:
        cmap = 'RGn'
        fp_to_save = root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/HeatMap_mins.png"
    else:
        cmap = "RdBuP"
        fp_to_save=root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/HeatMap_maxs.png"
    
    # Create figure
    fig = plt.figure(figsize=(20, 13))
    ax = fig.add_subplot(1,1,1)
    
    cmap = plt.get_cmap(cmap, np.max(array)-np.min(array)+1)
    # set limits .5 outside true range
    heatmap = plt.pcolor(array,cmap=cmap,vmin = np.min(array)-.5, vmax = np.max(catchments_with_maxs_arr)+.5)
    #tell the colorbar to tick at integers
    cax = plt.colorbar(heatmap, ticks=np.arange(np.min(array),np.max(array)+1), pad=0.02)
    cax.ax.tick_params(labelsize=25) 
    # Set ticks in center of cells
    ax.set_xticks(np.arange(array.shape[1]) + 0.5, minor=False)
    ax.set_yticks(np.arange(0,383, 20)+ 0.5, minor=False)
    
    # Rotate the xlabels. Set both x and y labels to headers[1:]
    rp_names = ['2yr', '5yr','10yr', '20yr','30yr', '50yr','75yr', '100yr',
           '150yr', '200yr','500yr', '1000yr','10000yr']
    ax.set_xticklabels(rp_names,rotation=90)
    durations = catchments_with_maxs['Duration hours']
    ax.set_yticklabels(durations[0::20])
    
    ax.set_xlabel('Return period', fontsize=25)
    ax.set_ylabel('Duration (hrs)', fontsize=25)
    
    plt.xticks(rotation = 45)
    
    ax.tick_params(axis='both', which='major', labelsize=20)
    
    #plt.savefig(fp_to_save,bbox_inches = 'tight')
    plt.show()
    
    
######################################################################################
######################################################################################
# Plot of rainfall amounts over different durations, with one subplot for each return period
######################################################################################
######################################################################################
# Create figure
fig = plt.figure(figsize=(30,20)) 
# Make subplot for each Return Period
for rp, subplot_num in zip(rps, range(1,13)):
    ax = fig.add_subplot(4,4,subplot_num)
    rainfalls_dict = {}
    for catchment_name in catchments:
        rainfall = design_rainfall_by_catchment[catchment_name]
        # Add line to the plot
        ax.plot(rainfall["Duration hours"], rainfall[rp], linestyle = ':', markersize=20, label=catchment_name)
    
    ax.set_xlabel('Duration (hours)', fontsize=15)
    ax.set_ylabel(rp, fontsize=15)
    ax.set_title(rp, fontsize=20)
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
    
###############################################################################
###############################################################################
# Animation
###############################################################################
###############################################################################
# Create dictionary liking catchment names to a marker and color
catchment_colors =['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', 
'#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', "#006FA6", '#800000', '#aaffc3', 
'#808000', "#FFA0F2", '#000075', '#000000']
mStyles = ["o","v","8", ">","s","p","P","*","h","X","D"] *2
# Create dictionaries
catchment_colors_dict = {catchments[i]: catchment_colors[i] for i in range(len(catchments))} 
catchment_markers_dict = {catchments[i]: mStyles[i] for i in range(len(catchments))} 
# Create seaborn palette
my_pal = sns.set_palette(sns.color_palette(catchment_colors))

# Parameters for plotting
plt.rcParams['animation.ffmpeg_path'] = root_fp + 'DataAnalysis/Scripts/ffmpeg-20200225-36451f9-win64-static/bin/ffmpeg'
plt.rcParams['savefig.bbox'] = 'tight' 
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define variables
rps = [2,10,100]
variables = ['ALTBAR', 'SAAR', 'Easting', 'Northing']
variable_units = ['Mean Catchment Altitude (m above sea level)', 'Standard Average Areal Rainfall (mm)'
                  , 'Easting(m)', 'Northing (m)']
variable_units_dict = dict(zip(variables, variable_units))

# Loop
for rp in rps:
    
    rp_rainfalls = design_rainfall_by_rp[str(rp) + ' year rainfall (mm)']
    rp_rainfalls_t = rp_rainfalls.T  
    rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
    rp_rainfalls_t = rp_rainfalls_t[1:22]
    rp_rainfalls_t = rp_rainfalls_t.reset_index(drop = True)
    frames = len(rp_rainfalls_t.columns)   # Number of frames
    frames = 50
    for variable, variable_unit in variable_units_dict.items():
        fig = plt.figure()
        def draw(frame):
           # Only plot everu 4th duration
            if frame % 1 == 0:
                 # Clear the previous figure
                plt.clf()
                
               # fig = plt.figure(figsize = (35,25))
                df2 = pd.DataFrame({'Catchment':catchments_info['name'],
                                    variable : catchments_info[variable],
                            'Precipitation' :rp_rainfalls_t.iloc[:,frame]})
                df2['Precipitation'] = round(df2['Precipitation'],1)
            
                # # If normalise is 'Yes', then normalise
                # if normalise == 'Yes':
                #     df2['Normalised'] =  df2['Precipitation']/ df2['Precipitation'].max() 
                # else:
                #     measure_df_thiscatchment =  measure_df[catchment_name]        
                
                # ax = fig.add_subplot(1,1,1)
                # ax.clear()
                # ax = sns.scatterplot(data=df2, x=variable, y='Normalised', style = 'Catchment', 
                #             markers = catchment_markers_dict, hue = 'Catchment', s= 100, palette = my_pal)
                # ax.set_xlabel(variable_unit)
                # ax.set_ylabel('Precipitation (mm)')
                # ax.tick_params(axis='both', which='major')
                # ax.legend_.remove()
                
                
                ax = fig.add_subplot(1,1,1)
                ax.clear()
                ax = sns.scatterplot(data=df2, x=variable, y='Precipitation', style = 'Catchment', 
                            markers = catchment_markers_dict, hue = 'Catchment', s= 100, palette = my_pal)
                ax.set_xlabel(variable_unit)
                ax.set_ylabel('Precipitation (mm)')
                ax.tick_params(axis='both', which='major')
                ax.legend_.remove()
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
                #plt.xlabel('{} ({})'.format(variable, variable_unit))
                #plt.ylabel('Design Rainfall (mm)')
                plt.title(str(rp) + 'yr return period - ' + str(rp_rainfalls_t.columns[frame]) + 'h')
                return grid
            
        def init():
            return draw(0)
        
        def animate(frame):
            return draw(frame)
        
        # Create animation
        ani = animation.FuncAnimation(fig, animate, frames, interval=1, save_count=100, blit=False, init_func=init,repeat=False)
        ani.save(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/{}vs{}yrRPrainfall_start.mp4".format(variable, rp),
                 writer=animation.FFMpegWriter(fps=2))
        
        # Convert to gif
        fp = root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/{}vs{}yrRPrainfall_start.mp4".format(variable, rp)
        clip = (VideoFileClip(fp))
        clip.write_gif(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/{}vs{}yrRPrainfall_start.gif".format(variable, rp))
        # Remove mp4
        os.remove(fp)


frame =50
fig = plt.figure()
df2 = pd.DataFrame({'Catchment':catchments_info['name'],
                    variable : catchments_info[variable],
            'Precipitation' :rp_rainfalls_t.iloc[:,frame]})
df2['Precipitation'] = round(df2['Precipitation'],1)

   
ax = fig.add_subplot(1,1,1)
ax = sns.scatterplot(data=df2, x=variable, y='Precipitation', style = 'Catchment', 
            markers = catchment_markers_dict, hue = 'Catchment', s= 100, palette = my_pal)
ax.set_xlabel(variable_unit)
ax.set_ylabel('Precipitation (mm)')
ax.tick_params(axis='both', which='major')
ax.legend_.remove()
plt.title(str(rp) + 'yr return period - ' + str(rp_rainfalls_t.columns[frame]) + 'h')


################### Test
rps = rainfall.columns[2:]

rp = '10 year rainfall (mm)'

# Create a dataframe containing rainfall for each duration
rp_rainfalls = design_rainfall_by_rp[str(rp) ]
rp_rainfalls_t = rp_rainfalls.T  
rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
rp_rainfalls_t = rp_rainfalls_t[1:22]
rp_rainfalls_t = rp_rainfalls_t.reset_index(drop = True)

# Normalise these rainfall amounts
frames = len(rp_rainfalls_t.columns) 
normalised_rainfalls = pd.DataFrame({'Catchments' :catchments_info['name']})
for frame in range(0,frames):
    print(frame)
    # Normalise rainfalls for this duration
    normalised_rainfalls_thisduration = pd.DataFrame({rp_rainfalls_t.columns[frame]:rp_rainfalls_t.iloc[:,frame]/ rp_rainfalls_t.iloc[:,frame].max()})
    # Join to dataframe of normalised precipitations
    normalised_rainfalls  = pd.concat([normalised_rainfalls , normalised_rainfalls_thisduration], axis =1)
    
### Create column to define whether the 96h rainfall 
normalised_rainfalls['hmm']= np.where(normalised_rainfalls[96.0] > normalised_rainfalls[1.0], 'Group1', 'Group2')

trim = normalised_rainfalls[["Catchments", "hmm"]]
trim['Diff_normalised'] = test[96.0] - test[1.0]
trim['Diff'] = rp_rainfalls_t[96.0] - rp_rainfalls_t[1.0]

merged =pd.concat([trim, catchments_info], axis =1)


fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=merged, x="Diff", y='BFIHOST', style = 'Catchments', 
            markers = catchment_markers_dict, hue = 'Catchments', s= 100, palette = my_pal)
ax.set_xlabel('Precipitation (mm)')
#ax.set_ylabel('Precipitation (mm)')
ax.tick_params(axis='both', which='major')
ax.legend_.remove()


fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=merged, x="Diff", y='SAAR', style = 'Catchments', 
            markers = catchment_markers_dict, hue = 'Catchments', s= 100, palette = my_pal)
ax.set_xlabel('Precipitation (mm)')
#ax.set_ylabel('Precipitation (mm)')
ax.tick_params(axis='both', which='major')
ax.legend_.remove()