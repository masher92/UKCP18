## 2m grid according to: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/842485/What-is-the-Risk-of-Flooding-from-Surface-Water-Map.pdf

import pandas as pd
import os 
import glob as glob
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt    
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

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
 
######################################################################################
######################################################################################
# For each return period create a dataframe, with each catchment as a row, and columns
# containing the values for velocity, depth, hazard and extent
# Store each dataframe in a dictionary
######################################################################################
######################################################################################
# List return periods and variables to look at
RPs = [30,100,1000]
variables = ['Depth', 'Hazard', 'Velocity']

# Function to clean the catchment names to match those used in the catchment descriptors
def clean_catchment_names (df):
    df=df.rename(columns = {'L2_NAME':'name'})
    df.loc[df.OBJECTID == 13, 'name'] = "GillBeck_Wharfe"
    df.loc[df.OBJECTID == 14, 'name'] = "GillBeck_Aire"
    df['name'] = df['name'].str.replace(' ', '')
    df.replace('CockBeckAberford', 'CockBeck_Aberford', inplace = True)
    df.replace('StankBeck/Eccup', 'StankBeck', inplace = True)
    df.replace('LadyBeck', 'MeanwoodBeck', inplace = True)
    df.replace('HolBeck', 'Holbeck', inplace = True)
    df.replace('MillDike', 'MillDyke', inplace = True)
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
        df_by_var = pd.read_csv("DataAnalysis/datadir/RoFSW/1in{}/{}/{}_ByCatchment_By{}.csv".format(rp, var, var, var))
        # Clean up catchment names to match catchment descriptors
        df_by_var = clean_catchment_names(df_by_var)
        df_by_var =  pd.merge(df_by_var, catchments_info)

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
            this_catchment.columns = this_catchment.iloc[0]
            this_catchment = this_catchment.rename(columns=this_catchment.iloc[0]).drop(this_catchment.index[0])
            # Add a total column
            this_catchment['Total'] = this_catchment[list(this_catchment)[0:]].sum(axis=1)
            # Add variable name to column names
            this_catchment.columns= [var + '_' + str(col)  for col in this_catchment.columns]
            # Add catchment name as column
            this_catchment.insert(0, 'name', catchment)
            # Keep only cells per km2 column
            #this_catchment=this_catchment.iloc[[2]]
            this_catchment=this_catchment.iloc[[0]]

            # Add to dataframe containing all the catchments data
            all_catchments = all_catchments.append(this_catchment)
        
        # Join to dataframe containing data for all the variables
        all_catchments_all_vars = pd.concat([all_catchments_all_vars, all_catchments], axis = 1)
    
    # Reset index
    all_catchments_all_vars.reset_index(inplace = True, drop= True)
    # Delete duplicate 'name' columns
    all_catchments_all_vars=all_catchments_all_vars.T.drop_duplicates().T
            
    # Read in dataframe containing extent, and join
    extent = pd.read_csv("DataAnalysis/datadir/RoFSW/1in{}/Extent/Extent_ByCatchment.csv".format(rp, var, var, var))
    extent = clean_catchment_names(extent)
    # Join with catchment desciptors
    extent = pd.merge(catchments_info[['name','AREA']],extent)
    # Create column which is cells per km2
    extent['Extent'] = extent['sum']
    #extent['Extent'] = extent['sum']/extent['AREA']
    # select columns
    extent = extent[['name', 'Extent']]
    
    # Join extent info
    all_catchments_all_vars =  pd.merge(all_catchments_all_vars, extent)
    
    # Join with catchment desciptors
    all_catchments_all_vars = pd.merge(catchments_info,all_catchments_all_vars)
    
    # replace na values with 0
    all_catchments_all_vars = all_catchments_all_vars.replace(np.nan, 0)
    
    # Convert all values to numeric
    all_catchments_all_vars.iloc[:,2:] =all_catchments_all_vars.iloc[:,2:].apply(pd.to_numeric)
    
    # Add to results dictionary
    results_dict[str(rp)] = all_catchments_all_vars


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
      
fig, ax = plt.subplots()
ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Extent'], label="Extent")
ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Velocity_Total'], label="Speed")
ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Depth_Total'], label="Depth")
ax.plot(all_catchments_all_vars['name'], all_catchments_all_vars['Hazard_Total'], label="Hazard")
ax.set_ylabel('Number of Cells')
ax.legend()
plt.xticks(rotation = 90)


######################################################################################
######################################################################################
# Plotting - Spatial distribution of flooded cells, and cells with severe flooding
######################################################################################
######################################################################################
cols= ['name', 'geometry', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting', 'Northing', 'Depth_0.00 - 0.15', 'Depth_0.15 - 0.30',
       'Depth_0.30 - 0.60', 'Depth_0.60 - 0.90', 'Depth_0.90 - 1.20',
       'Depth_> 1.20', 'Depth_Total', 'Hazard_0.75 - 1.25',
       'Hazard_0.50 - 0.75', 'Hazard_1.25 - 2.00', 'Hazard_> 2.00',
       'Hazard_Total', 'Velocity_0.00 - 0.25', 'Velocity_0.25 - 0.50',
       'Velocity_0.50 - 1.00', 'Velocity_1.00 - 2.00', 'Velocity_> 2.00',
       'Velocity_Total', 'Extent']

severe_vars = ['Depth_> 1.20','Velocity_> 2.00', 'Hazard_> 2.00']
rps = ["30","100","1000"]

# Create figure
fig = plt.figure(figsize=(28,20)) 
# Make subplot for each Return Period
#for var, subplot_num in zip(severe_vars, range(1,13)):
i=1
for rp in rps:
    all_catchments_all_vars = results_dict[rp]
    filtered = all_catchments_all_vars[cols]
    # Convert to number cells per km2
    filtered.iloc[:,13:]=filtered.iloc[:,13:].div(filtered['AREA'], axis=0) 
    
    for var in severe_vars:
         print(var, rp)
         ax = fig.add_subplot(3,3,i)
         divider = make_axes_locatable(ax)
         # create `cax` for the colorbar
         cax = divider.append_axes("right", size="5%", pad=-0.2)
         filtered.plot(ax=ax, cax = cax, column= var,cmap='OrRd', 
                             edgecolor = 'black', legend=True)
         # manipulate the colorbar `cax`
         cax.set_ylabel('Flooded cells per km2', rotation=90, size = 20)
         cax.tick_params(labelsize=15)
         ax.axis('off')
         ax.set_title(rp + 'yr RP: ' + var, fontsize=20)
         
         i = i+1

fig = plt.figure(figsize=(28,20)) 
for rp, subplot_num in zip(rps, range(1,4)):
    all_catchments_all_vars = results_dict[rp]
    filtered = all_catchments_all_vars[cols]
    # Convert to number cells per km2
    filtered.iloc[:,13:]=filtered.iloc[:,13:].div(filtered['AREA'], axis=0) 
    
    print(var, rp)
    ax = fig.add_subplot(1,3,subplot_num)
    divider = make_axes_locatable(ax)
    # create `cax` for the colorbar
    cax = divider.append_axes("right", size="5%", pad=-0.2)
    filtered.plot(ax=ax, cax = cax, column= 'Depth_Total',cmap='OrRd', 
                        edgecolor = 'black', legend=True)
    # manipulate the colorbar `cax`
    cax.set_ylabel('Flooded cells per km2', rotation=90, size = 20)
    cax.tick_params(labelsize=15)
    ax.axis('off')
    ax.set_title(rp + 'yr RP: ', fontsize=20)
    
    # Append with catchment names
    #filtered.apply(lambda filtered: ax.annotate(s=filtered['name'], 
    #                                                          xy= filtered.geometry.centroid.coords[0],
    #                                                          ha='center', size= 18),axis=1)  

# Save and show plot
plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/RoFSW/Figs/Flooding_AllRPs.png".format(rp),
            bbox_inches='tight')


######################################################################################
######################################################################################
# Plotting - relationship between flood extent and catchment descriptors
######################################################################################
######################################################################################

# filter columns
filtered = all_catchments_all_vars.iloc[:, np.r_[0:15, 18:27, 39:41, 47,52,58,59 ]]
filtered = filtered.iloc[:, np.r_[0:4,6,8,9,13:16,22,24,25,28]]
filtered['FloodedCellsPerKm2'] = filtered['Velocity_Total']/filtered['AREA']
# Add a total area column (assuming each square is 4m2)
filtered['Total_Area_km2'] = (filtered['Velocity_Total'] * 4)/1000000
# Find flooded area as a propotion of total area
filtered['Prop_of_area_flooded'] = filtered['Total_Area_km2']/filtered['AREA'] *100

######################################################################################
######################################################################################
# Plotting - relationship between flood extent and catchment descriptors
######################################################################################
######################################################################################
rp = "100"
var = 'FloodedCellsPerKm2'
cols =['name', 'geometry', 'AREA', 'ALTBAR', 'BFIHOST', 'DPSBAR', 'FARL',
           'LDP', 'PROPWET', 'SAAR', 'URBEXT2000', 'Easting', 'Northing', 'Depth_Total']

correlations_df = pd.DataFrame()
for rp in ['30', '100', '1000']:
    all_catchments_all_vars = results_dict[rp]
    # filter columns
    filtered = all_catchments_all_vars[cols]
    # Convert to number cells per km2
    filtered['FloodedCellsPerKm2']=filtered['Depth_Total'].div(filtered['AREA'], axis=0) 
    # Find all correlations with total number flooded cells
    corrs = filtered[filtered.columns[2:]].corr()['FloodedCellsPerKm2'][:]
    corrs = corrs.reindex(corrs.abs().sort_values(ascending = False).index)
    df = pd.DataFrame({'Variable': corrs.index, 'Correlation': round(corrs,2)})
    df.reset_index(inplace = True, drop = True)
    correlations_df = pd.concat([correlations_df, df], axis =1)


fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=filtered, x="Depth_Total", y='LDP',
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()




######################################################################################
######################################################################################
# Plotting - relationship between flood extent and FEH13 rainfall
######################################################################################
######################################################################################
correlations_df = pd.DataFrame()
for rp in design_rainfall_by_rp.keys():

    rainfall_10yrrp = design_rainfall_by_rp[rp]
    rainfall_10yrrp = rainfall_10yrrp.T
    # Reformat
    rainfall_10yrrp.columns = rainfall_10yrrp.iloc[0]
    rainfall_10yrrp = rainfall_10yrrp.rename(columns=rainfall_10yrrp.iloc[0]).drop(rainfall_10yrrp.index[0])
    # rainfall_10yrrp = rainfall_10yrrp[[1,10,50,90]]
    rainfall_10yrrp['name'] = rainfall_10yrrp.index
    rainfall_10yrrp.reset_index(inplace = True, drop = True)
    
    rainfall_10yrrp= pd.concat([rainfall_10yrrp, filtered['Velocity_Total']], axis = 1)
    
    corrs = rainfall_10yrrp[rainfall_10yrrp.columns[1:]].corr()['Velocity_Total'][:]
    corrs = corrs.reindex(corrs.abs().sort_values().index)
    rp = [int(i) for i in rp.split() if i.isdigit()][0]
    correlations_df[rp] = corrs


correlations_df = correlations_df.drop(['Velocity_Total'], axis=0)
correlations_df.abs().max()

fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=rainfall_10yrrp, x="Velocity_Total", y=0.5,
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()



######################################################################################
######################################################################################
# Plotting - relationship between flood extent and ReFH2 runoff
######################################################################################
######################################################################################
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
    
    peaks= pd.concat([peaks, filtered['Velocity_Total']], axis = 1)
    
    corrs = peaks[peaks.columns[1:]].corr()['Velocity_Total'][:]
    corrs = corrs.reindex(corrs.abs().sort_values().index)
   
    correlations_df[category] = corrs


fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=peaks, x="Velocity_Total", y='33h',
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()


### Crtitical durations
correlations_df = pd.DataFrame()
for category in cds.keys():

    peaks = cds[category]
    
    
    
    peaks= pd.concat([peaks, filtered['Velocity_Total']], axis = 1)
    
    corrs = peaks[peaks.columns[1:]].corr()['Velocity_Total'][:]
    corrs = corrs.reindex(corrs.abs().sort_values().index)
   
    correlations_df[category] = corrs



fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=peaks, x=75, y='Velocity_Total',
                     style = 'Catchments',  markers = catchment_markers_dict, 
                     hue = 'Catchments', s= 200, palette = my_pal)
ax.legend_.remove()



######################################################################################
######################################################################################
# Plotting 
######################################################################################
######################################################################################
# https://python-for-multivariate-analysis.readthedocs.io/a_little_book_of_python_for_multivariate_analysis.html
corrmat =all_catchments_all_vars_f.corr()
sns.heatmap(corrmat, vmax=1., square=False).xaxis.tick_top()



# Find all correlations with velocity
corrs = all_catchments_all_vars_ff[all_catchments_all_vars_ff.columns[1:]].corr()['Depth_Total'][:]
corrs = corrs.abs().sort_values(kind="quicksort")



def hinton(matrix, max_weight=None, ax=None):
    """Draw Hinton diagram for visualizing a weight matrix."""
    ax = ax if ax is not None else plt.gca()

    if not max_weight:
        max_weight = 2**np.ceil(np.log(np.abs(matrix).max())/np.log(2))

    ax.patch.set_facecolor('lightgray')
    ax.set_aspect('equal', 'box')
    ax.xaxis.set_major_locator(plt.NullLocator())
    ax.yaxis.set_major_locator(plt.NullLocator())

    for (x, y), w in np.ndenumerate(matrix):
        color = 'red' if w > 0 else 'blue'
        size = np.sqrt(np.abs(w))
        rect = plt.Rectangle([x - size / 2, y - size / 2], size, size,
                             facecolor=color, edgecolor=color)
        ax.add_patch(rect)

    nticks = matrix.shape[0]
    ax.xaxis.tick_top()
    ax.set_xticks(range(nticks))
    ax.set_xticklabels(list(matrix.columns), rotation=90)
    ax.set_yticks(range(nticks))
    ax.set_yticklabels(matrix.columns)
    ax.grid(False)

    ax.autoscale_view()
    ax.invert_yaxis()

hinton(corrmat)


def mosthighlycorrelated(mydataframe, numtoreport):
    # find the correlations
    cormatrix = mydataframe.corr()
    # set the correlations on the diagonal or lower triangle to zero,
    # so they will not be reported as the highest ones:
    cormatrix *= np.tri(*cormatrix.values.shape, k=-1).T
    # find the top n correlations
    cormatrix = cormatrix.stack()
    cormatrix = cormatrix.reindex(cormatrix.abs().sort_values(ascending=False).index).reset_index()
    # assign human-friendly names
    cormatrix.columns = ["FirstVariable", "SecondVariable", "Correlation"]
    return cormatrix.head(numtoreport)

mosthighlycorrelated(all_catchments_all_vars_f, 10)


correlation_mat = all_catchments_all_vars_f.corr()
corr_pairs = correlation_mat.unstack()
print(corr_pairs)
sorted_pairs = corr_pairs.sort_values(kind="quicksort")
print(sorted_pairs)
strong_pairs = sorted_pairs[abs(sorted_pairs) > 0.5]
print(strong_pairs)


######################################################################################
######################################################################################
# Plotting 
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

      
fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=filtered, x="BFIHOST", y="FC_perKM2",
                     style = 'name',  markers = catchment_markers_dict, hue = 'name', 
                     s= 200, palette = my_pal)
ax.legend_.remove()

#Find the covariance
from scipy.stats import pearsonr, spearmanr
from scipy import stats

covariance = np.cov(inner_merged['FloodedCells_per_Km2'], inner_merged['BFIHOST'])
# calculate Pearson's correlation
corr, _ = pearsonr(inner_merged['FloodedCells_per_Km2'], inner_merged['BFIHOST'])
print('Pearsons correlation: %.3f' % corr)
corr, _ = spearmanr(inner_merged['FloodedCells_per_Km2'], inner_merged['BFIHOST'])
print('Spearmans correlation: %.3f' % corr)

# Check for normality
k2, p = stats.normaltest( inner_merged['FloodedCells_per_Km2'])
alpha = 1e-3
print("p = {:g}".format(p))
p = 3.27207e-11
if p < alpha:  # null hypothesis: x comes from a normal distribution
    print("The null hypothesis can be rejected")
else:
    print("The null hypothesis cannot be rejected")



inner_merged[['FloodedCells_per_Km2','BFIHOST', 'Easting']].corr()
features1=['FloodedCells_per_Km2','BFIHOST','Easting']
inner_merged[features1].corr()



import math
df = pd.DataFrame({
    'IQ':[100,140,90,85,120,110,95], 
    'GPA':[3.2,4.0,2.9,2.5,3.6,3.4,3.0],
    'SALARY':[45e3,150e3,30e3,25e3,75e3,60e3,38e3]
    })

# Get pairwise correlation coefficients
cor = df.corr()

# Independent variables
x = 'IQ'
y = 'GPA'

# Dependent variable
z = 'SALARY'

# Pairings
xz = cor.loc[ x, z ]
yz = cor.loc[ y, z ]
xy = cor.loc[ x, y ]

Rxyz = math.sqrt((abs(xz**2) + abs(yz**2) - 2*xz*yz*xy) / (1-abs(xy**2)) )
R2 = Rxyz**2

# Calculate adjusted R-squared
n = len(df) # Number of rows
k = 2       # Number of independent variables
R2_adj = 1 - ( ((1-R2)*(n-1)) / (n-k-1) )

