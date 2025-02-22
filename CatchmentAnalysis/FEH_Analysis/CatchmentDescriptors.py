##################################################################
# Set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import glob
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
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
# Plot catchment boundaries provided by LCC
######################################################################################
######################################################################################
# Read in shapefiles
shapefile = gpd.read_file("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/LeedsCatchments/LeedsCatchments.shp")
shapefile['PLAN_AREA_km2'] = shapefile['PLAN_AREA']/1000000
print(shapefile)

# Plot
fig, ax = plt.subplots(1, 1)
shapefile.plot(column='PLAN_AREA_km2',   cmap='OrRd',
             legend=True,legend_kwds={'label': "Area (km2)",
                                      'orientation': "vertical"})

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

catchments_info['Tp'] =  [3.495, 3.541, 4.323, 1.875,6.97, 5.86,5.308,6.221,1.955, 1.873,
                              3.487, 6.713,3.151,6.129, 6.552,4.196,4.783, 7.115,4.961,6.07]
catchments_info['CritDur'] = [6.30,5.30,7.30,3.15, 11,11, 9 , 11 , 3.45, 3.15,
                              6.30,11,5.30,11,11,6.30 ,8.30,11 ,8.30,11]


fig = plt.figure(figsize = (9,6))
ax = fig.add_subplot(1,1,1)
ax.clear()
ax = sns.scatterplot(data=catchments_info, x='Tp', y='URBEXT2000', style = 'name', 
            markers = catchment_markers_dict, hue = 'name', s= 200, palette = my_pal)
#ax.set_xlabel('{} ({})'.format(variable1, variable1_unit), fontsize = 12)
#ax.set_ylabel('{} ({})'.format(variable2, ("m")), fontsize = 12)
ax.tick_params(axis='both', which='major')
ax.legend_.remove()


######################################################################################
######################################################################################
# Correlations - Multiple regression
######################################################################################
######################################################################################
cols= ['name', 'AREA', 'ALTBAR', 'BFIHOST','DPSBAR', 'FARL', 'LDP',
       'PROPWET', 'SAAR','URBEXT2000', 'Easting','Northing']
catchments_info_filtered = catchments_info[cols]

# Create dataframe to store the adjusted R2 values
r2s_df = pd.DataFrame({'Variables' : catchments_info_filtered.columns[1:-2]})
pos_or_neg_df = pd.DataFrame({'RPs' : catchments_info_filtered.columns[1:-2]})
for predictor_variable in ['Easting', 'Northing', 'Easting + Northing']:
    print(predictor_variable)
    values = []
    pos_or_neg = []
    for response_variable in catchments_info_filtered.columns[1:-2]:
        print(response_variable)
        model = smf.ols("{}~{}".format(response_variable, predictor_variable) , data=catchments_info).fit()
        values.append(round(model.rsquared_adj, 3))
    r2s_df =pd.concat([r2s_df,pd.DataFrame({predictor_variable : values})], axis=1)
    pos_or_neg_df =pd.concat([pos_or_neg_df,pd.DataFrame({predictor_variable : pos_or_neg})], axis=1)    

r2s_df 

######################################################################################
######################################################################################
# Plotting - spatial plots
######################################################################################
######################################################################################
# Create dictionary mapping variables to their units
variables = ['ALTBAR', 'BFIHOST', 'DPSBAR', 'LDP', 'SAAR', 'URBEXT2000']
variable_units = ['m above sea level', 'BFIHOST', 'm per km', 'km', 'mm', '%']
variable_units_dict = dict(zip(variables, variable_units))
print(variable_units_dict) # {'a': 1, 'b': 2, 'c': 3}

# Create a spatial plot for each variables
for variable, variable_unit in variable_units_dict.items():
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14,12))
    divider = make_axes_locatable(ax)
    
    # create `cax` for the colorbar
    cax = divider.append_axes("right", size="5%", pad=-0.2)
    
    # plot the geodataframe specifying the axes `ax` and `cax` 
    catchments_info.plot(ax=ax, cax = cax, column= variable,cmap='OrRd', edgecolor = 'black',
                 legend=True)
    
    # manipulate the colorbar `cax`
    cax.set_ylabel(variable, rotation=90, size = 20)
    # set `fontsize` on the colorbar `cax`
    maxv, minv = max(catchments_info[variable]), min(catchments_info[variable])
    if minv <1 :
        cax.set_yticklabels(np.around(np.linspace(minv, maxv, 10),2), {'fontsize': 15})
    else:
        cax.set_yticklabels(np.linspace(minv, maxv, 10, dtype=np.dtype(np.uint64)), {'fontsize': 15})
    ax.axis('off')

    # Append with catchment names
    catchments_info.apply(lambda catchments_info: ax.annotate(s=catchments_info['name'], 
                                                              xy= catchments_info.geometry.centroid.coords[0],
                                                              ha='center', size= 18),axis=1)  
    # save figure
    plt.savefig("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/AllCatchments/CatchmentDescriptors/{}_spatial.PNG".format(variable),
                bbox_inches='tight')
    plt.show()


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


##############################     
# Scatter plots
##############################
variable1 = 'SAAR'
variable1_unit  = 'mm'
variable2 = 'ALTBAR'
variable2_unit  = 'm'


##############################     
# Histograms
##############################
variables = ['ALTBAR', 'AREA', 'BFIHOST', 'DPSBAR', 'LDP', 'SAAR', 'URBEXT2000']
variable_units = ['Mean Catchment Altitude (m above sea level', 'Catchment area (km2)', 'BFIHOST', 'm per km', 
                  'Longest drainage path (km)', 'Standard Average Areal Rainfall (mm)', 'Urban Extent (2000)']
variable_units_dict = dict(zip(variables, variable_units))
print(variable_units_dict) # {'a': 1, 'b': 2, 'c': 3}

for variable, variable_unit in variable_units_dict.items():
    plt.hist(catchments_info[variable], bins =15, color='darkblue', edgecolor='black')
    plt.xlabel(variable_unit)
    plt.ylabel('Number of catchments')
    plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Allcatchments/CatchmentDescriptors/{}.PNG".format(variable))
    plt.close()

##############################     
# Scatter plots
##############################
variables2s = ["Easting", "Northing", 'ALTBAR']
for variable2 in variables2s:
    for variable1, variable1_unit in variable_units_dict.items():
        if variable1 != variable2:
            df2 = pd.DataFrame({'Catchment':catchments_info['name'], 
                        variable1 : catchments_info[variable1],
                        variable2 :catchments_info[variable2]})
            
            fig = plt.figure(figsize = (9,6))
            ax = fig.add_subplot(1,1,1)
            ax.clear()
            ax = sns.scatterplot(data=df2, x=variable1, y=variable2, style = 'Catchment', 
                        markers = catchment_markers_dict, hue = 'Catchment', s= 200, palette = my_pal)
            ax.set_xlabel('{} ({})'.format(variable1, variable1_unit), fontsize = 12)
            ax.set_ylabel('{} ({})'.format(variable2, ("m")), fontsize = 12)
            ax.tick_params(axis='both', which='major')
            ax.legend_.remove()
            plt.savefig(root_fp +"DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/Figs/Allcatchments/CatchmentDescriptors/{}vs{}.PNG".format(variable1, variable2))
            
###############################################
lin_dyke_shpfile = shapefile.loc[shapefile['CATCHNAME'] == 'Aire - Lin Dyke Catchment']

# Plot
fig, ax = plt.subplots(1, 1)
lin_dyke_shpfile.plot()

