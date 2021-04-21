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
import statsmodels.formula.api as smf
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib as mpl
from matplotlib.pyplot import cm

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
#### Create dataframe containing for each RP/duration combo:
#### The max and min values across all the catchments and the % difference between the 2
######################################################################################
######################################################################################
#### Create dataframe with max, min and % difference for RP/duration combos
masterDf = pd.DataFrame({'Duration (hours)':[0.25, 0.5, 0.75] + list(range(1,101,10))})
for rp in [2,5,20,50]:
    this_rp = design_rainfall_by_rp[str(rp) + " year rainfall (mm)"]
    maxs = []
    mins = []
    diffs = []
    for duration in [0.25, 0.5, 0.75] + list(range(1,101,10)):
        print(duration)
        this_duration =  this_rp.loc[this_rp['Duration hours'] == duration].iloc[:,1:]
        this_max = round(this_duration.max(axis=1).item(),1)
        this_min = round(this_duration.min(axis=1).item(),1)
        maxs.append(this_max)
        mins.append(this_min)
        diffs.append(round((this_max-this_min)/((this_max+this_min)/2) * 100,1))
    this_rp = pd.DataFrame({'Min (' + str(rp) + ')' : mins,
                       'Max (' + str(rp) + ')' : maxs,
                       '% Diff (' + str(rp) + ')' : diffs})   
    masterDf = pd.concat([masterDf, this_rp], axis =1)


######################################################################################
######################################################################################
#### Find the difference between the values for two different RPs
# Find this as the difference between the NORMALISED value at RP
# This should mean that it shows up catchments that have increased in their
# values proportional to other catchments
#### NB: This code can be adapted to plot just the values for one RP
######################################################################################
######################################################################################
# Function for plotting with 0 in the middle of the colorbar
class MidpointNormalize(mpl.colors.Normalize):
    """Normalise the colorbar."""
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        mpl.colors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))

# Create dictionary to store results for each rp
normalised_dfs = {}    
# Define the RPs between which to find the normalised difference
rp1, rp2 = 2, 10
for rp in [rp1, rp2]:    
    # extract data for this rp
    rp ="{} year rainfall (mm)".format(rp)   
    one_rp = design_rainfall_by_rp[rp]   
    
    # Reformat
    one_rp_t = one_rp.T  
    one_rp_t.rename(columns=one_rp_t.iloc[0], inplace = True)
    one_rp_t = one_rp_t[1:]
    one_rp_t.reset_index(inplace =True, drop = True)
   
    # Normalise
    for col in one_rp_t.columns:
        print(col)
        one_rp_t[col] = one_rp_t[col]/one_rp_t[col].max() 
    normalised_dfs[rp] = one_rp_t
    
diff_between_rps = normalised_dfs["{} year rainfall (mm)".format(rp1)]- normalised_dfs["{} year rainfall (mm)".format(rp2)]
diff_between_rps = pd.concat([catchments_info,diff_between_rps], axis =1)

### Plotting
# Define the max and min values across all the durations
the_max = -100000000000
the_min = 1000000000000
for duration in [0.25,0.75, 1,4,6,8, 10, 20,30, 40, 50, 60, 70, 80, 90]:
    if diff_between_rps[duration].max() > the_max:
        the_max = diff_between_rps[duration].max()
    if diff_between_rps[duration].min() < the_min:
        the_min= diff_between_rps[duration].min() 

# Plot for the listed durations
fig = plt.figure(figsize=(35, 20))   
i = 1
for duration in [0.25,0.75, 1,4,6,8, 10, 20,30, 40, 50, 60, 70, 80, 90]:
    ax = fig.add_subplot(4,5,i)
    # Create figure
    divider = make_axes_locatable(ax)
    
    # create `cax` for the colorbar
    cax = divider.append_axes("right", size="5%", pad=-0.2)
    
    # plot the geodataframe specifying the axes `ax` and `cax` 
    diff_between_rps.plot(ax=ax, cax = cax, column= duration,cmap='PRGn', 
                 vmin=the_min, vmax=the_max, 
                norm=MidpointNormalize(the_min, the_max, 0.),
                 edgecolor = 'black',legend=True)
    
    # manipulate the colorbar `cax`
    cax.set_ylabel('Precipitation', rotation=90, size = 20)
    cax.tick_params(labelsize=15) 
    
    ax.axis('off')
    ax.set_title(str(duration) + 'h', fontsize = 25)
    
    i=i+1

# Adjust height between plots
fig.subplots_adjust(top=0.92)

# Add one title
#plt.suptitle(rp, fontsize=40)
plt.suptitle("Difference between {} and {} yr Return Periods".format(rp1, rp2), fontsize=40)


# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/Diff{}and{}RP_Rainfall_spatialplot.png".format(rp1,rp2),
            bbox_inches='tight')
      
######################################################################################
######################################################################################
# Create a heat map plot which shows combination of RPs and durations
# With the cells coloured according to a number (representing a catchment) with the
# max or min value for that combination
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
        cmap = 'BuPu'
        fp_to_save = root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/HeatMap_mins.png"
    else:
        cmap = "BrBG"
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
# Animation of rainfall against catchment descriptors, with each frame showing
# a different duration. One animation per return period
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
variables = ['AREA']
variable_units = ['Area (Km2)']
variable_units_dict = dict(zip(variables, variable_units))

# Loop
for rp in rps:
    rp_rainfalls = design_rainfall_by_rp[str(rp) + ' year rainfall (mm)']
    rp_rainfalls_t = rp_rainfalls.T  
    rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
    rp_rainfalls_t = rp_rainfalls_t[1:22]
    rp_rainfalls_t = rp_rainfalls_t.reset_index(drop = True)
    frames = len(rp_rainfalls_t.columns)   # Number of frames
    #frames = 50
    for variable, variable_unit in variable_units_dict.items():
        fig = plt.figure()
        def draw(frame):
           # Only plot everu 4th duration
            if frame % 5 == 0:
                 # Clear the previous figure
                plt.clf()
                
                #fig = plt.figure()
                df2 = pd.DataFrame({'Catchment':catchments_info['name'],
                                    variable : catchments_info[variable],
                            'Precipitation' :rp_rainfalls_t.iloc[:,frame]})
                df2['Precipitation'] = round(df2['Precipitation'],1)

                # If normalise is 'Yes', then normalise
                # if normalise == 'Yes':
                #     df2['Precipitation'] =  df2['Precipitation']/ df2['Precipitation'].max() 
                # else:
                #     measure_df_thiscatchment =  measure_df[catchment_name]        
                                
                ax = fig.add_subplot(1,1,1)
                ax.clear()
                ax = sns.scatterplot(data=df2, x=variable, y='Precipitation', style = 'Catchment', 
                            markers = catchment_markers_dict, hue = 'Catchment', s= 100, palette = my_pal)
                ax.set_xlabel(variable_unit)
                ax.set_ylabel('Precipitation (mm)')
                ax.tick_params(axis='both', which='major')
                ax.legend_.remove()
                #plt.annotate("R = {:.3f}".format(df2['Precipitation'].corr(df2[variable])), (55, 53))
                
                #ax.set_title("62.25h")
                grid =ax.get_children()[0]

                plt.title(str(rp) + 'yr return period - ' + str(rp_rainfalls_t.columns[frame]) + 'h')
                return grid
            
        def init():
            return draw(0)
        
        def animate(frame):
            return draw(frame)
        
        # Create animation
        ani = animation.FuncAnimation(fig, animate, frames, interval=1, save_count=100, blit=False, init_func=init,repeat=False)
        ani.save(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/{}vs{}yrRPrainfall.mp4".format(variable, rp),
                 writer=animation.FFMpegWriter(fps=10))
        
        # Convert to gif
        fp = root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/{}vs{}yrRPrainfall.mp4".format(variable, rp)
        clip = (VideoFileClip(fp))
        clip.write_gif(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/Rainfall/{}vs{}yrRPrainfall.gif".format(variable, rp))
        # Remove mp4
        os.remove(fp)


####################################################################################
####################################################################################
######## Correlations, using:
# Pearson's Correlation Coefficient
# OLS regression, R2        
####################################################################################
####################################################################################
# Define return period and duration for which to conduct analysis
rp = 2
duration = 0.25

# Extract from catchments info dataframe the variables of interest
cols= ['name', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting','Northing']
catchments_info_filtered = catchments_info[cols]

# Extract dataframe containing rainfall for each duration for that return period
rp_rainfalls = design_rainfall_by_rp[str(rp) + ' year rainfall (mm)']
rp_rainfalls_t = rp_rainfalls.T  
rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
rp_rainfalls_t = rp_rainfalls_t[1:22]
rp_rainfalls_t = rp_rainfalls_t.reset_index(drop = True)

# Add the rainfall values for the defined duration to the dataframe of catchments info
catchments_info_filtered['Precipitation'] = rp_rainfalls_t[duration]

##################### Pearson's R correlation coefficient
### Find correlation between the precipitation variable and all the rest
corrs = catchments_info_filtered[catchments_info_filtered.columns].corr()['Precipitation'][:]

##################### Use OLS regression to find the R2 value for pairs of variables
# and the R2 value for each variable individually 
# Create dataframe to store correlations betweene each variable pair
correlations = pd.DataFrame({"Variable": [x for x in cols if x != 'name']})

# Add to dataframe, so that it contains:
# The diagonal values (e.g. AREA vs AREA) as the R2 value for that variable and precip
# The values between 2 values (e.g. AREA vs ALTBAR) the R2 value for both variables with precipitation
i=0
for var1 in correlations['Variable']:
    corrs = []
    print(var1)
    for var2 in correlations['Variable']:
        print(var2)
        if var1 == var2:
            model = smf.ols("Precipitation~{}".format(var1), data=catchments_info_filtered).fit()
            adj_r2 = round(model.rsquared_adj, 3)
        else:
            model = smf.ols("Precipitation~{}+{}".format(var1,var2), data=catchments_info_filtered).fit()
            adj_r2 = round(model.rsquared_adj, 3)
        print(adj_r2)
        corrs.append(adj_r2)
    df = pd.DataFrame({var1:corrs})
    df.iloc[0:i] = np.nan
    correlations  = pd.concat([correlations,df],axis=1 )
    i=i+1

# Testing whether all relations are significant
# test2 = correlations_df[1:]
# del test2['Correlation']
# test2.reset_index(inplace = True, drop =True)

# i=0
# for var1 in test2['Variable']:
#     corrs = []
#     print(var1)
#     for var2 in test2['Variable']:
#         print(var2)
#         if var1 == var2:
#             model = ols("Precipitation~{}".format(var1), data=filtered).fit()
#             sig = (model.pvalues[1:] < 0.05).any()
#         else:
#             model = ols("Precipitation~{}+{}".format(var1,var2), data=filtered).fit()
#             sig = (model.pvalues[1:] < 0.05).any()
#         corrs.append(sig)
#     df = pd.DataFrame({var1:corrs})
#     df.iloc[0:i] = np.nan
#     test2  = pd.concat([test2,df],axis=1 )
#     i=i+1

####################################################################################
####################################################################################
# Find the variable which is most strongly correlated with the precipitation value 
# at different RP and duration combinations
# Store these in a dataframe, and also store the maximum correlation value
####################################################################################
####################################################################################
max_variables_df = pd.DataFrame()
max_values_df = pd.DataFrame()
correlations_all_durations_all_rps = {}

for rp in rps:    
    ###########################
    # Create dataframe containing the correlation between each variable and 
    # precipitation for each duration 
    ###########################
    # Extract dataframe containing rainfall for each duration for that return period
    rp_rainfalls = design_rainfall_by_rp[rp]
    rp_rainfalls_t = rp_rainfalls.T  
    rp_rainfalls_t.rename(columns=rp_rainfalls_t.iloc[0], inplace = True)
    rp_rainfalls_t = rp_rainfalls_t[1:22]
    rp_rainfalls_t = rp_rainfalls_t.reset_index(drop = True)

    correlations_df_all_durations = pd.DataFrame({'Variable': catchments_info_filtered.columns[1:]})
    for i in range(2,len(rp_rainfalls_t.columns)):
        if i % 4 == 0:
            i=i-1
    
            catchments_info_filtered['Precipitation'] = rp_rainfalls_t.iloc[:,i]
            # Find all correlations with total number flooded cells
            corrs = catchments_info_filtered[catchments_info_filtered.columns[1:]].corr()['Precipitation'][:]
            #corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)
            df = pd.DataFrame({rp_rainfalls_t.columns[i]: round(corrs,3)})
            df.reset_index(inplace = True, drop = True)
            correlations_df_all_durations = pd.concat([correlations_df_all_durations, df], axis =1)
        
    correlations_df_all_durations = correlations_df_all_durations.drop([11])
    correlations_all_durations_all_rps[rp] = correlations_df_all_durations

    ###########################
    # Find the variable with highest correlation with precipitation at each duration
    ###########################
    max_variables  =[]
    max_values = []
    for col in correlations_df_all_durations.columns[1:]:
        print(col)
        max_value = correlations_df_all_durations[col][abs(correlations_df_all_durations[col]). idxmax()]
        
        max_variable = correlations_df_all_durations['Variable'][abs(correlations_df_all_durations[col]). idxmax()]
        
        max_values.append(max_value)
        max_variables.append(max_variable)

    max_variables_df_thisrp = pd.DataFrame({[int(s) for s in rp.split() if s.isdigit()][0]:max_variables})
    max_variables_df= pd.concat([max_variables_df,max_variables_df_thisrp],axis=1)
     
    max_values_df_thisrp = pd.DataFrame({[int(s) for s in rp.split() if s.isdigit()][0]:max_values})
    max_values_df= pd.concat([max_values_df,max_values_df_thisrp],axis=1)

#max_values_df.insert(0, 'Duration', correlations_df_all_durations.columns[1:])
#max_variables_df.insert(0, 'Duration', correlations_df_all_durations.columns[1:])

####################################################################################
####################################################################################
# Create heatmap plot showing the variable (represented by a number) which has the 
# strongest correlation with precipitation for each RP, duration combination
####################################################################################
####################################################################################
# Convert to arrays
maxs_df_arr = max_variables_df.iloc[:, 1:].to_numpy()
x=1
for variable in np.unique(maxs_df_arr) :
    print(variable)
    maxs_df_arr = np.where(maxs_df_arr==variable, x, maxs_df_arr) 
    x = x+1 
maxs_df_arr =maxs_df_arr.astype(int)

# Create figure
fig = plt.figure(figsize=(20, 13))
ax = fig.add_subplot(1,1,1)
cmap = 'rainbow'
cmap = plt.get_cmap(cmap, np.max(maxs_df_arr)-np.min(maxs_df_arr)+1)
# set limits .5 outside true range
heatmap = plt.pcolor(maxs_df_arr,cmap=cmap,vmin = np.min(maxs_df_arr)-.5, vmax = np.max(maxs_df_arr)+.5)
#tell the colorbar to tick at integers
cax = plt.colorbar(heatmap, ticks=np.arange(np.min(maxs_df_arr),np.max(maxs_df_arr)+1), pad=0.02)
cax.ax.tick_params(labelsize=25) 
# Set ticks in center of cells
ax.set_xticks(np.arange(maxs_df_arr.shape[1]) + 0.5, minor=False)
ax.set_yticks(np.arange(0,len(max_variables_df),2), minor=False)
ax.set_yticklabels(max_variables_df['Duration'].values.tolist()[::2])

# Rotate the xlabels. Set both x and y labels to headers[1:]
rp_names = ['2yr', '5yr','10yr', '20yr','30yr', '50yr','75yr', '100yr',
       '150yr', '200yr','500yr', '1000yr','10000yr']
ax.set_xticklabels(rp_names,rotation=90)
durations = max_variables_df['Duration']

ax.set_xlabel('Return period', fontsize=25)
ax.set_ylabel('Duration (hrs)', fontsize=25)

plt.xticks(rotation = 45)

ax.tick_params(axis='both', which='major', labelsize=20)

####################################################################################
####################################################################################
# Plot line plots showing the change in correlation between each variable and precipitation
# over different durations (with a plot for each RP)
####################################################################################
####################################################################################
###### For one RP
rp = "200 year rainfall (mm)"
# Get correlations for this RP
correlations_df_all_durations = correlations_all_durations_all_rps[rp]
# Reformat    
correlations_t = correlations_df_all_durations.T
correlations_t.rename(columns=correlations_t.iloc[0], inplace = True)
correlations_t = correlations_t[1:]

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
for column in ['Northing', 'SAAR', 'URBEXT2000','AREA', 'Easting', 'BFIHOST', 'ALTBAR', 'DPSBAR', 'FARL']:
    plt.plot(correlations_t.index, correlations_t[column], label = column)
    plt.scatter(correlations_t.index, correlations_t[column], label = column, s= 5)    
    plt.xlabel('Duration (hr)')
    plt.ylabel('Correlation with rainfall for this duration')
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

###### For all RPs
subplot_num=1
fig = plt.figure(figsize=(35, 25))     
for rp in rps.tolist()[:-1]:
    print(rp)
    # Get correlations for this RP
    correlations_df_all_durations = correlations_all_durations_all_rps[rp]
    # Reformat    
    correlations_t = correlations_df_all_durations.T
    correlations_t.rename(columns=correlations_t.iloc[0], inplace = True)
    correlations_t = correlations_t[1:]
    
    # Create subplot
    ax = fig.add_subplot(4,3,subplot_num)
    n =  len(['Northing', 'SAAR', 'URBEXT2000','AREA', 'Easting', 'BFIHOST', 'ALTBAR', 'DPSBAR', 'FARL'])
    color=iter(cm.Dark2(np.linspace(0,1,n)))
    
    for column in ['Northing', 'SAAR', 'URBEXT2000','AREA', 'Easting', 'BFIHOST', 'ALTBAR', 'DPSBAR', 'FARL']:
        c=next(color)
        #plt.scatter(correlations_t.index, correlations_t[column], label = column,s= 8)
        plt.plot(correlations_t.index, correlations_t[column], label = column, c=c, linewidth =3)
        plt.xlabel('Duration (hr)', fontsize = '20')
        plt.ylabel('Correlation',  fontsize = '20')
        ax.tick_params(axis='both', which='major', labelsize=20)
        # Shrink current axis by 20%
        #box = ax.get_position()
        #ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        
        # Put a legend to the right of the current axis
        #ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title (str(rp) + ' Year Return Period', fontsize = '22')
       
    # Increase subplot number for next plot
    subplot_num=subplot_num+1

box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.3,
                  box.width, box.height * 0.8])
handles, labels = ax.get_legend_handles_labels()
ax.legend(loc='best', bbox_to_anchor=(0.5, -0.2),
          fancybox=True, shadow=True, ncol=5,  fontsize = 30, markerscale = 10)

# Adjust height between plots
fig.subplots_adjust(top=0.92)
# fig.subplots_adjust(right=0.92)
plt.subplots_adjust(hspace=0.3)    

####################################################################################
####################################################################################
# Plot line plots showing the change in correlation between each variable and precipitation
# over different durations (with a plot for each variable, and line on each for each RP)
# REVERSE of above
####################################################################################
####################################################################################
# subplot_num=0
# fig = plt.figure(figsize=(35, 25)) 
# for var in correlations_t.columns:
#     print(var)
#     subplot_num=subplot_num+1
#     ax = fig.add_subplot(4,3,subplot_num)
#     for rp in rps:
#         # Get correlations for this RP
#         correlations_df_all_durations = correlations_all_durations_all_rps[rp]
#         # Reformat    
#         correlations_t = correlations_df_all_durations.T
#         correlations_t.rename(columns=correlations_t.iloc[0], inplace = True)
#         correlations_t = correlations_t[1:]
        
#         plt.plot(correlations_t.index, correlations_t[var], label = rp, linewidth = 2)
    
#     plt.xlabel('Duration (hr)', fontsize = '25')
#     plt.ylabel('Correlation', fontsize = '25')
#     ax.tick_params(axis='both', which='major', labelsize=25)
#     ax.set_title (var, fontsize = 25)

# box = ax.get_position()
# ax.set_position([box.x0, box.y0 + box.height * 0.3,
#                   box.width, box.height * 0.8])
# handles, labels = ax.get_legend_handles_labels()
# ax.legend(loc='best', bbox_to_anchor=(2.6, -0.2),
#           fancybox=True, shadow=True, ncol=5,  fontsize = 30, markerscale = 3)

# # Adjust height between plots
# fig.subplots_adjust(top=0.92)
# # fig.subplots_adjust(right=0.92)
# plt.subplots_adjust(hspace=0.35)    
       
####################################################################################
####################################################################################
#
####################################################################################
####################################################################################
# Define RP
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
    
### Create column to define whether the 96h rainfall is smaller or larger than 1h rainfall
normalised_rainfalls['Group']= np.where(normalised_rainfalls[96.0] > normalised_rainfalls[1.0], 'Group1', 'Group2')

# Trim to just the required columns
trim = normalised_rainfalls[["Catchments", "Group"]]
trim['Diff_normalised'] = normalised_rainfalls[96.0] - normalised_rainfalls[1.0]
trim['Diff'] = rp_rainfalls_t[96.0] - rp_rainfalls_t[1.0]

# Join to the catchments info
merged =pd.concat([trim, catchments_info], axis =1)

# Plot to show relationship between difference in normalised 1h and 96h rainfall
# and catchment descriptors
# AREA
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=merged, x="Diff_normalised", y='AREA', style = 'Catchments', 
            markers = catchment_markers_dict, hue = 'Catchments', s= 100, palette = my_pal)
ax.set_xlabel('Difference between normalised 1h and 96h precipitation')
#ax.set_ylabel('Precipitation (mm)')
ax.tick_params(axis='both', which='major')
plt.annotate("R = {:.3f}".format(merged['AREA'].corr(merged['Diff_normalised'])), (-0.12, 60))
ax.legend_.remove()

## Northing
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=merged, x="Diff_normalised", y='Northing', style = 'Catchments', 
            markers = catchment_markers_dict, hue = 'Catchments', s= 100, palette = my_pal)
ax.set_xlabel('Difference between normalised 1h and 96h precipitation')
#ax.set_ylabel('Precipitation (mm)')
ax.tick_params(axis='both', which='major')
plt.annotate("R = {:.3f}".format(merged['Northing'].corr(merged['Diff_normalised'])), (-0.12, 442500))
ax.legend_.remove()
