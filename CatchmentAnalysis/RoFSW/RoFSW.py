## 2m grid according to: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/842485/What-is-the-Risk-of-Flooding-from-Surface-Water-Map.pdf

import pandas as pd
import os 
import glob as glob
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt    
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.stats import pearsonr, spearmanr
from scipy import stats
import statsmodels.formula.api as smf

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
 
catchments_info.reset_index(drop = True, inplace = True)

# Extract from catchments info dataframe the variables of interest
cols= ['geometry' ,'name', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting','Northing']
catchments_info_filtered = catchments_info[cols]

#########################################################    
######################################################################################
######################################################################################
# For each return period create a dataframe, with each catchment as a row, and columns
# containing the values for velocity, depth, hazard and extent
# Store each dataframe in a dictionary
######################################################################################
######################################################################################
# List return periods and variables to look at
RPs = [30,100,1000]
#variables = ['Depth', 'Hazard', 'Velocity']
variables = ['Hazard']

# Function to clean the catchment names to match those used in the catchment descriptors
def clean_catchment_names (df):
    # df=df.rename(columns = {'L2_NAME':'name'})
    # df.loc[df.OBJECTID == 13, 'name'] = "GillBeck_Wharfe"
    # df.loc[df.OBJECTID == 14, 'name'] = "GillBeck_Aire"
    # df['name'] = df['name'].str.replace(' ', '')
    # df.replace('CockBeckAberford', 'CockBeck_Aberford', inplace = True)
    # df.replace('StankBeck/Eccup', 'StankBeck', inplace = True)
    # df.replace('LadyBeck', 'MeanwoodBeck', inplace = True)
    # df.replace('HolBeck', 'Holbeck', inplace = True)
    # df.replace('MillDike', 'MillDyke', inplace = True)
    
    # df=df.rename(columns = {'L2_NAME':'name'})
    # df.loc[df.OBJECTID == 13, 'name'] = "GillBeck_Wharfe"
    # df.loc[df.OBJECTID == 14, 'name'] = "GillBeck_Aire"
    # df['name'] = df['name'].str.replace(' ', '')
    
    catchment_names_new = sorted(catchments_info_filtered['name'])
    catchment_names_orig= sorted(df_by_var['name'].unique())
    
    # For correct catchment names    
    for i in range(0,len(catchments_info_filtered['name'])):
        print(i)
        catchment_name_original  = catchment_names_orig[i]
        catchment_name_new =catchment_names_new[i]
        print(catchment_name_original)
        print(catchment_name_new)
        df.replace(catchment_name_original, catchment_name_new, inplace = True) 
    return df

# Create dictionary to store results for each return period
results_dict = {}
# Loop through return periods
for rp in RPs:
    # Crate dataframe to store results for this return period
    all_catchments_all_vars = pd.DataFrame()
    # For each variable, read in the data
    for var in variables:
        print(rp, var)
        # Read in
        df_by_var = pd.read_csv("DataAnalysis/datadir/RoFSW/1in{}_FEHCatchments/{}/{}_ByCatchment_By{}.csv".format(rp, var, var, var))
        # Clean up catchment names to match catchment descriptors
        df_by_var = clean_catchment_names(df_by_var)
        df_by_var =  pd.merge(df_by_var, catchments_info, how= 'left')

        all_catchments = pd.DataFrame()
        for catchment in catchments:
            print(catchment)
            # extract the data for just this catchment
            this_catchment = df_by_var.loc[df_by_var['name'] == catchment]
            # take just columns containing breakdown by varaible values
            this_catchment = this_catchment[[var.lower(), 'sum', 'AREA']]
            # Find sum per area
            this_catchment['Cells_per_Km2'] = this_catchment['sum']/this_catchment['AREA']
            # Transpose
            this_catchment = this_catchment.T
            # Reformat
            this_catchment = this_catchment.rename(columns=this_catchment.iloc[0]).drop(this_catchment.index[0])
            # Add a total column
            this_catchment['Total'] = this_catchment[list(this_catchment)[0:]].sum(axis=1)
            # Add variable name to column names
            this_catchment.columns= [var + '_' + str(col)  for col in this_catchment.columns]
            # Add catchment name as column
            this_catchment.insert(0, 'name', catchment)
            # Keep only SUM column
            #this_catchment=this_catchment.iloc[[2]] #cellsperareacolumn
            this_catchment=this_catchment.iloc[[0]]

            # Add to dataframe containing all the catchments data
            all_catchments = all_catchments.append(this_catchment)
        
        # Join to dataframe containing data for all the variables
        all_catchments_all_vars = pd.concat([all_catchments_all_vars, all_catchments], axis = 1)
    
    # Reset index
    all_catchments_all_vars.reset_index(inplace = True, drop= True)
    # Delete duplicate 'name' columns
    #all_catchments_all_vars=all_catchments_all_vars.T.drop_duplicates().T
            
    # # Read in dataframe containing extent, and join
    # extent = pd.read_csv("DataAnalysis/datadir/RoFSW/1in{}/Extent/Extent_ByCatchment.csv".format(rp, var, var, var))
    # extent = clean_catchment_names(extent)
    # # Join with catchment desciptors
    # extent = pd.merge(catchments_info[['name','AREA']],extent)
    # # Create column which is cells per km2
    # extent['Extent'] = extent['sum']
    # #extent['Extent'] = extent['sum']/extent['AREA']
    # # select columns
    # extent = extent[['name', 'Extent']]
    # Join extent info
    #all_catchments_all_vars =  pd.merge(all_catchments_all_vars, extent)
   
    # Join with catchment desciptors
    all_catchments_all_vars = pd.merge(catchments_info,all_catchments_all_vars)
    # replace na values with 0
    all_catchments_all_vars = all_catchments_all_vars.replace(np.nan, 0)
    # Convert all values to numeric
    all_catchments_all_vars.iloc[:,2:] =all_catchments_all_vars.iloc[:,2:].apply(pd.to_numeric)
    # Add to results dictionary
    results_dict[rp] = all_catchments_all_vars

# filtered['FloodedCellsPerKm2'] = filtered['Velocity_Total']/filtered['AREA']
# # Add a total area column (assuming each square is 4m2)
# filtered['Total_Area_km2'] = (filtered['Velocity_Total'] * 4)/1000000
# # Find flooded area as a propotion of total area
# filtered['Prop_of_area_flooded'] = filtered['Total_Area_km2']/filtered['AREA'] *100
# filtered.iloc[:,2:] =filtered.iloc[:,2:].apply(pd.to_numeric)

######################################################################################
######################################################################################
# Plotting - relationship between extent, velocity and hazard
######################################################################################
######################################################################################
catchment_colors =['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', 
'#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', "#006FA6", '#800000', '#aaffc3', 
'#808000', "#FFA0F2", '#000075', '#000000']
mStyles = ["o","v","8", ">","s","p","P","*","h","X","D"] *2
# Create dictionaries
catchment_colors_dict = {catchments[i]: catchment_colors[i] for i in range(len(catchments))} 
catchment_markers_dict = {catchments[i]: mStyles[i] for i in range(len(catchments))} 
# Create seaborn palette
my_pal = sns.set_palette(sns.color_palette(catchment_colors))
      
# fig, ax = plt.subplots()
# ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Extent'], label="Extent")
# ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Velocity_Total'], label="Speed")
# ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Depth_Total'], label="Depth")
# ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Hazard_Total'], label="Hazard")
# ax.set_ylabel('Number of Cells')
# ax.legend()
# plt.xticks(rotation = 90)

######################################################################################
######################################################################################
# Plotting - Spatial distribution of flooded cells, and cells with severe flooding
######################################################################################
######################################################################################
cols= ['name', 'geometry', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting', 'Northing', 'Hazard_0.75 - 1.25',
       'Hazard_0.50 - 0.75', 'Hazard_1.25 - 2.00', 'Hazard_> 2.00',
       'Hazard_Total']

### FLooded cells per km2
fig = plt.figure(figsize=(28,20)) 
for rp, subplot_num in zip(RPs, range(1,4)):
    all_catchments_all_vars = results_dict[rp]
    filtered = all_catchments_all_vars[cols]
    # Convert to number cells per km2
    filtered.iloc[:,13:]=filtered.iloc[:,13:].div(filtered['AREA'], axis=0) 
    
    print(var, rp)
    ax = fig.add_subplot(1,3,subplot_num)
    divider = make_axes_locatable(ax)
    # create `cax` for the colorbar
    cax = divider.append_axes("right", size="5%", pad=-0.2)
    filtered.plot(ax=ax, cax = cax, column= 'Hazard_Total',cmap='OrRd', 
                        edgecolor = 'black', legend=True)
    # manipulate the colorbar `cax`
    cax.set_ylabel('Flooded cells per km2', rotation=90, size = 20)
    cax.tick_params(labelsize=15)
    ax.axis('off')
    ax.set_title(str(rp) + 'yr RP: ', fontsize=20)
    
    #Append with catchment names
    # filtered.apply(lambda filtered: ax.annotate(s=filtered['name'], 
    #                                                           xy= filtered.geometry.centroid.coords[0],
    #                                                           ha='center', size= 18),axis=1)  

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/RoFSW/Figs/Flooding_AllRPs.png".format(rp),
            bbox_inches='tight')


############ Just for Hazard
# Calculating a weighted sum
hazard_vars= ['Hazard_0.50 - 0.75', 'Hazard_0.75 - 1.25','Hazard_1.25 - 2.00', 'Hazard_> 2.00',
       'Hazard_Total']

# Create figure
fig = plt.figure(figsize=(40,25)) 
# Make subplot for each Return Period
#for var, subplot_num in zip(severe_vars, range(1,13)):
i=1
for rp in RPs:
    all_catchments_all_vars = results_dict[rp]
    hazard = all_catchments_all_vars[hazard_vars]
    # Join to catchments info
    hazard = pd.concat([catchments_info_filtered, hazard], axis=1)
    
    # Convert to number cells per km2
    hazard.iloc[:,13:]=hazard.iloc[:,13:].div(hazard['AREA'], axis=0) 

    # Get just the 4 hazard categories
    hazard_cats = hazard.copy().iloc[:,13:17]
    # Define the weights
    weights = pd.Series([0.5, 0.25, 0.75, 1], index=['Hazard_0.75 - 1.25', 'Hazard_0.50 - 0.75',
    #weights = pd.Series([0.25, 0.5, 1, 2], index=['Hazard_0.75 - 1.25', 'Hazard_0.50 - 0.75',
     'Hazard_1.25 - 2.00', 'Hazard_> 2.00'])
    # Add a column to the initial df containing the weighted syms
    hazard['weighted_sum']  = (hazard_cats * weights).sum(1)
        
    for var in hazard_vars + ['weighted_sum']:
         print(var, rp)
         ax = fig.add_subplot(4,6,i)
         divider = make_axes_locatable(ax)
         # create `cax` for the colorbar
         cax = divider.append_axes("left", size="2%", pad=-0.2)
         hazard.plot(ax=ax, cax = cax, column= var,cmap='OrRd', 
                             edgecolor = 'black', legend=True)
         # manipulate the colorbar `cax`
         cax.set_ylabel('Flooded cells per km2', rotation=90, size = 20)
         cax.tick_params(labelsize=15)
         cax.remove()
         ax.axis('off')
         ax.set_title(str(rp) + 'yr RP: ' + var, fontsize=20)

         i = i+1

# Adjust height between plots
fig.subplots_adjust(top=0.92)
# fig.subplots_adjust(right=0.92)
plt.subplots_adjust(hspace=0.05, wspace=0.0)   


# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/RoFSW/Figs/Flooding_AllRPs_weightedsum.png".format(rp),
            bbox_inches='tight')


######################################################################################
######################################################################################
# Plotting - relationship between flood extent and catchment descriptors
######################################################################################
######################################################################################
rp =30
all_catchments_all_vars = results_dict[rp]
# Just keep Hazard
hazard = all_catchments_all_vars[cols]
# Normalise by area
hazard.iloc[:,13:]=hazard.iloc[:,13:].div(hazard['AREA'], axis=0) 

# filtered['FloodedCellsPerKm2'] = filtered['Velocity_Total']/filtered['AREA']
# # Add a total area column (assuming each square is 4m2)
# filtered['Total_Area_km2'] = (filtered['Velocity_Total'] * 4)/1000000
# # Find flooded area as a propotion of total area
# filtered['Prop_of_area_flooded'] = filtered['Total_Area_km2']/filtered['AREA'] *100


############## Find correlations with total hazard cells
# as opposed to different hazard levels
rp = "100"
var = 'FloodedCellsPerKm2'
cols =['name', 'geometry', 'AREA', 'ALTBAR', 'BFIHOST', 'DPSBAR', 'FARL',
           'LDP', 'PROPWET', 'SAAR', 'URBEXT2000', 'Easting', 'Northing', 'Hazard_Total']

correlations_df = pd.DataFrame()
for rp in RPs:
    all_catchments_all_vars = results_dict[rp]
    # filter columns
    # Just keep Hazard
    hazard = all_catchments_all_vars[ cols]
    # Normalise by area
    hazard.iloc[:,13:]=hazard.iloc[:,13:].div(hazard['AREA'], axis=0) 
    # Find all correlations with total number flooded cells
    corrs = hazard[hazard.columns[2:]].corr()['Hazard_Total'][:]
    corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)
    df = pd.DataFrame({'Variable': corrs.index, 'Correlation': round(corrs,2)})
    df.reset_index(inplace = True, drop = True)
    correlations_df = pd.concat([correlations_df, df], axis =1)


fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=hazard, x="Hazard_Total", y='BFIHOST',
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()


# MUltiple lienar regression?
predictor_variables = 'BFIHOST'
model = smf.ols("Hazard_Total~{}".format(predictor_variables) , data=hazard).fit()
model.summary()
round(model.rsquared_adj,2)



######################################################################################
######################################################################################
# Plotting - relationship between flood extent and FEH13 rainfall
######################################################################################
######################################################################################
rp = 30
all_catchments_all_vars = results_dict[rp]
# filter columns
# Just keep Hazard
hazard = all_catchments_all_vars[ cols]
# Normalise by area
hazard.iloc[:,13:]=hazard.iloc[:,13:].div(hazard['AREA'], axis=0) 

# Import FEH13 rainfall
# (Code from RainfallAnalysis.py)
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
design_rainfall_by_rp = {}


for rp in rps:
    df = pd.DataFrame({'Duration hours': design_rainfall_by_catchment[catchment_name]['Duration hours']})
    for catchment_name in catchments:
            catchment_df = pd.DataFrame({catchment_name: design_rainfall_by_catchment[catchment_name][rp]})
            df[catchment_name] = catchment_df[catchment_name]
     
    # Add to dictionary
    design_rainfall_by_rp[rp] = df

# Create dataframe to store correlation for each RP/duration combination 
# between precipitation for that combination and the number of flooded cells
correlations_df = pd.DataFrame()
for rainfall_rp in design_rainfall_by_rp.keys():
    
    # Create dataframe containing rainfall for this rp and the RoFSW flooded cells
    rainfall_10yrrp = design_rainfall_by_rp[rainfall_rp]
    rainfall_10yrrp = rainfall_10yrrp.T
    # Reformat
    rainfall_10yrrp.columns = rainfall_10yrrp.iloc[0]
    rainfall_10yrrp = rainfall_10yrrp.rename(columns=rainfall_10yrrp.iloc[0]).drop(rainfall_10yrrp.index[0])
    # rainfall_10yrrp = rainfall_10yrrp[[1,10,50,90]]
    rainfall_10yrrp['name'] = rainfall_10yrrp.index
    rainfall_10yrrp.reset_index(inplace = True, drop = True)
    rainfall_10yrrp= pd.concat([rainfall_10yrrp, hazard['Hazard_Total']], axis = 1)
    
    # Find correlations between rainfall and the number of flooded cells
    corrs = rainfall_10yrrp[rainfall_10yrrp.columns].corr()['Hazard_Total'][:]
    #corrs = corrs.reindex(corrs.abs().sort_values().index)
    
    # Add to dataframe
    correlations_df[[int(i) for i in rainfall_rp.split() if i.isdigit()][0]] = corrs

# Remove row containing Depth
correlations_df = correlations_df.drop(['Hazard_Total'], axis=0)
# Find the max correlation for each return period
correlations_df.abs().max()

# plot relationship between number of flooded cells and one duration for each catchment
fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=rainfall_10yrrp, x="Hazard_Total", y=96.0,
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()


######################################################################################
######################################################################################
# Plotting - relationship between flood extent and ReFH2 runoff
######################################################################################
######################################################################################
# Load peaks_all_catchments_allrps from RunoffAnalysis.py script 
correlations_df = pd.DataFrame()
for category in peaks_all_catchments_allrps.keys():

    peaks = peaks_all_catchments_allrps[category]
    peaks = peaks.T
    # Reformat
    peaks.columns = peaks.iloc[0]
    peaks = peaks.rename(columns=peaks.iloc[0]).drop(peaks.index[0])
    
    peaks =peaks.apply(pd.to_numeric)
    peaks.insert(0,'name', peaks.index)
    peaks.reset_index(inplace = True, drop = True)
    peaks= pd.concat([peaks, filtered['Depth_Total']], axis = 1)
    corrs = peaks[peaks.columns[1:]].corr()['Depth_Total'][:]
    corrs = corrs.reindex(corrs.abs().sort_values().index)
    correlations_df[category] = corrs

fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=peaks, x="Depth_Total", y='33h',
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()


### Crtitical durations
correlations_df = pd.DataFrame()
for category in cds.keys():

    peaks = cds[category]
    peaks= pd.concat([peaks, filtered['Depth_Total']], axis = 1)
    corrs = peaks[peaks.columns[1:]].corr()['Depth_Total'][:]
    corrs = corrs.reindex(corrs.abs().sort_values().index)
    correlations_df[category] = corrs


fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=peaks, x=75, y='Depth_Total',
                     style = 'Catchments',  markers = catchment_markers_dict, 
                     hue = 'Catchments', s= 200, palette = my_pal)
ax.legend_.remove()



######################################################################################
######################################################################################
# Check for normality 
######################################################################################
######################################################################################
# 
k2, p = stats.normaltest( filtered['FloodedCellsPerKm2'])
alpha = 1e-3
print("p = {:g}".format(p))
p = 3.27207e-11
if p < alpha:  # null hypothesis: x comes from a normal distribution
    print("The null hypothesis can be rejected")
else:
    print("The null hypothesis cannot be rejected")



