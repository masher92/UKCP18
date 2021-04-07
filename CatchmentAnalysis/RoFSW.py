## 2m grid according to: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/842485/What-is-the-Risk-of-Flooding-from-Surface-Water-Map.pdf

import pandas as pd
import os 
import glob as glob
import geopandas as gpd
import seaborn as sns
import matplotlib.pyplot as plt    
import numpy as np

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
#
#
######################################################################################
######################################################################################
RPs = [30,100,1000]
variables = ['Depth', 'Hazard', 'Velocity']

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

for rp in RPs:
    for var in variables:
        print(rp, var)
        df = pd.read_csv("DataAnalysis/datadir/RoFSW/1in{}/{}/{}_ByCatchment.csv".format(rp, var, var))
        df_by_var = pd.read_csv("DataAnalysis/datadir/RoFSW/1in{}/{}/{}_ByCatchment_By{}.csv".format(rp, var, var, var))
        # Clean up catchment names to match catchment descriptors
        df = clean_catchment_names(df)
        df_by_var = clean_catchment_names(df_by_var)
   
       # Join with catchment desciptors
        df_descriptors = pd.merge(catchments_info,df)
        df_descriptors['FloodedCells_per_Km2'] = df_descriptors['count']/df_descriptors['AREA']
        
        df_by_var_descriptors = pd.merge(catchments_info,df_by_var)
        df_by_var_descriptors['FloodedCells_per_Km2'] = df_by_var_descriptors['sum']/df_by_var_descriptors['AREA']

        #### Keep only columns needed
        # (Sum = each area value x count)
        # Test this by summarising by area category, but including area as a variable 
        # to summarise by. This shows that the total sum is the sum of the count for each area
        # x that area 
        #df = 

        filtered =df_descriptors.iloc[:, np.r_[0, 2:13, 18:27, 39:41, 56]]
        filtered = filtered.rename(columns={"FloodedCells_per_Km2": "FC_perKM2"})






# https://python-for-multivariate-analysis.readthedocs.io/a_little_book_of_python_for_multivariate_analysis.html
corrmat =filtered.corr()
sns.heatmap(corrmat, vmax=1., square=False).xaxis.tick_top()
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

mosthighlycorrelated(filtered, 10)

from sklearn.preprocessing import scale
standardisedX = scale(filtered)
standardisedX = pd.DataFrame(standardisedX, index=filtered.index, columns=filtered.columns)


correlation_mat = filtered.corr()
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

