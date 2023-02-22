import rasterio
import rioxarray as rxr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import pyplot
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter
import matplotlib.ticker as mtick
import os
import rasterio.plot
import matplotlib as mpl
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
import pycrs
from pyproj import CRS
from branca.element import Template, MacroElement
import folium
from folium import Map, FeatureGroup, LayerControl
import numpy.ma as ma
from pathlib import Path
from PIL import Image
import re
import itertools
import matplotlib.patches as mpatches
import contextily as cx
import matplotlib as mpl
from scipy import stats

model_directory = '../../../../FloodModelling/Model_ObservedProfiles/'

# Define whether to filter out values <0.1
remove_little_values = True

# Specify catchment area to add to plot
catchment_shp = model_directory + "CatchmentLinDyke_exported.shp"
catchment_gdf = gpd.read_file(catchment_shp)

def create_binned_counts_and_props(fps, variable_name, breaks, labels, remove_little_values):
    # Create dataframes to populate with values
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()        

    # Loop through each rainfall scenario
    # Get the raster containing its values, and count the number of each unique value, and construct into a dataframe
    for fp in fps  :
        # Classify depth/velocity rasters into depth/velocity bins
        raster = prepare_rainfall_scenario_raster(fp.format(variable_name), remove_little_values)[0]
        unique, counts = np.unique(raster, return_counts=True)
        df = pd.DataFrame({'values': unique, 'counts':counts})

        # Add a new column specifying the bin which each value falls within
        df['bins']= pd.cut(unique, bins=breaks, right=False)

        # Create a new dataframe showing the number of cells in each of the bins
        groups = df.groupby(['bins']).sum()
        groups  = groups.reset_index()

        # Find the total number of cells
        total_n_cells = groups ['counts'].sum()
        # Find the number of cells in each group as a proportion of the total
        groups['Proportion'] = round((groups['counts']/total_n_cells) *100,1)

        # Add values to dataframes
        method_name = fp.split("/")[6]
        counts_df[method_name] = groups['counts']
        proportions_df[method_name] = groups['Proportion']

    # Reset index to show the groups
    counts_df.reset_index(inplace=True)
    proportions_df.reset_index(inplace=True)

    # Set index values
    counts_df['index'] = labels
    proportions_df['index'] = labels

    return counts_df, proportions_df

def create_binned_counts_and_props_hazard(fps):

    # Create dataframes to populate with values
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()      

    for fp in fps:
        # Define filepath
        fp = '../../../../FloodModelling/MeganModel_New/{}/hazard_classified.tif'.format(fp.split('New/')[1].split('/{}')[0])
        # Read in data
        hazard = prepare_rainfall_scenario_raster(fp, remove_little_values)[0]
        # Count the number of each value
        unique, counts = np.unique(hazard, return_counts=True)
        df = pd.DataFrame({'values': unique, 'counts':counts})
        # Remove Nan values
        df = df.dropna()

        # Find the total number of cells
        total_n_cells = df ['counts'].sum()
        # Find the number of cells in each group as a proportion of the total
        df['Proportion'] = round((df['counts']/total_n_cells) *100,1)
        
        # Add values to dataframes
        method_name =fp.split("/")[6]
        counts_df[method_name] = df['counts']
        proportions_df[method_name] = df['Proportion']

    # Reset index to show the groups
    counts_df.reset_index(inplace=True)
    proportions_df.reset_index(inplace=True)

    # Set index values
    labels_hazard = ['Low hazard', 'Moderate hazard', 'Significant hazard', 'Extreme hazard']
    counts_df['index'] = labels_hazard
    proportions_df['index'] = labels_hazard
    return counts_df, proportions_df

def create_binned_counts_and_props_hazard_cat_change(fps):
    # Create dataframes to populate with values
    counts_df = pd.DataFrame(columns = ["values"])
    proportions_df = pd.DataFrame(columns = ["values"]) 

    for fp in fps[1:]:
        # Add values to dataframes
        method_name = fp.split("/")[6]
        # Read in hazard data 
        fp = '../../../../FloodModelling/MeganModel_New/{}/hazard_cat_difference.tif'.format(fp.split('New/')[1].split('/{}')[0])
        hazard = prepare_rainfall_scenario_raster(fp, False)[0]
        unique, counts = np.unique(hazard, return_counts=True)
        df = pd.DataFrame({'values': unique, method_name:counts})
        # Remove NA columns
        df = df.dropna()

        # Add to dataframes
        counts_df= counts_df.merge(df[['values', method_name]], on = 'values', how = 'outer')

        # Find the total number of cells
        total_n_cells = df [method_name].sum()
        # Find the number of cells in each group as a proportion of the total
        df[method_name] = round((df[method_name]/total_n_cells) *100,1)

       # Add to dataframes
        proportions_df= proportions_df.merge(df[['values', method_name]], on = 'values', how = 'outer')

        # Order intoi ascending order
        proportions_df = proportions_df.sort_values(by='values')
        counts_df = counts_df.sort_values(by='values')

    # Join the two dataframes together and reformat
    both_dfs = pd.DataFrame(columns = ["Cluster_num"])  
    for num, df in enumerate([counts_df,proportions_df]):
        df['Cluster_num']= ['Hazard_3CatsLower','Hazard_2CatsLower', 'Hazard_1CatsLower', 'Hazard_SameCat', 'Hazard_1CatsHigher', 'Hazard_2CatsHigher', 'Hazard_3CatsHigher']
        del df['values']
        df = df.set_index('Cluster_num').T
        if num == 0:
            df = df.add_suffix('_countcells')
        else:
            df = df.add_suffix('_propcells')
        df['Cluster_num'] = df.index
        both_dfs = pd.merge(both_dfs, df,  how="outer", on = 'Cluster_num')
    
    return both_dfs


def create_binned_counts_and_props_urban(fps, variable_name, breaks, labels, remove_little_values, landcover_mod):
    # Create dataframes to populate with values
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()        

    # Loop through each rainfall scenario
    # Get the raster containing its values, and count the number of each unique value, and construct into a dataframe
    for fp in fps:

        raster = prepare_rainfall_scenario_raster(fp.format(variable_name), remove_little_values)[0]
        # Create a dataframe with each row relating to a cell and its landcover and depth/velocity value
        raster_and_landcover = pd.DataFrame({'landcovercategory':  landcover_mod.flatten(), 'value': raster.flatten()})
        # Get just the urban rows
        urban_flooding = raster_and_landcover[raster_and_landcover['landcovercategory']==10].copy()  
        # Add a column assigning a bin based on the depth/velocity value
        urban_flooding['bins']= pd.cut(urban_flooding['value'], bins=breaks, right=False)

        # Create a new dataframe showing the number of cells in each of the bins
        groups = urban_flooding.groupby(['bins']).count()
        groups  = groups.reset_index()
        # Find the total number of cells
        total_n_cells = groups['value'].sum()
        # Find the number of cells in each group as a proportion of the total
        groups['Proportion'] = round((groups['value']/total_n_cells) *100,1)

        # Add values to dataframes
        method_name =fp.split("/")[6]
        counts_df[method_name] = groups["value"]
        proportions_df[method_name] = groups['Proportion']

    # Reset index to show the groups
    counts_df.reset_index(inplace=True)
    proportions_df.reset_index(inplace=True)

    # Set index values
    counts_df['index'] = labels
    proportions_df['index'] = labels

    return counts_df, proportions_df    

def find_percentage_diff (totals_df, fps):
    percent_diffs_formatted_for_plot = []
    percent_diffs_abs = []
    percent_diffs = []

    sp_value = totals_df.loc[totals_df['short_id'] == '6h_feh_sp']['FloodedArea']

    for fp in fps:
        rainfall_scenario_name = fp.split('/')[6]
        if rainfall_scenario_name!= '6h_feh_sp':
            # FInd value for this scenario
            this_scenario_value = totals_df.loc[totals_df['short_id'] == rainfall_scenario_name]['FloodedArea']
            this_scenario_value.reset_index(drop=True, inplace=True)
            # FInd % difference between single peak and this scenario
            percent_diffs.append(round((this_scenario_value/sp_value-1)*100,2)[0])
            percent_diffs_abs.append(round(abs((this_scenario_value/sp_value-1)[0])*100,2))
            percent_diffs_formatted_for_plot.append(round((this_scenario_value/sp_value-1)*100,2)[0])
    # Convert values to strings, and add a + sign for positive values
    # Include an empty entry for the single peak scenario
    percent_diffs_df = pd.DataFrame({'percent_diff_formatted':[''] +['+' + str(round((list_item),2)) + '%' if list_item > 0 else str(round((list_item),2)) +
     '%'  for list_item in percent_diffs_formatted_for_plot] ,
             'percent_diffs':[0] + percent_diffs, 'percent_diffs_abs':[0] + percent_diffs_abs })
    return percent_diffs_df

def create_totals_df (velocity_counts):
    totals_df =pd.DataFrame(velocity_counts.sum(numeric_only=True)).T
    totals_df = totals_df.iloc[[len(totals_df)-1]]
    # Convert this to the total flooded area for each method
    totals_df_area = (totals_df * 1)/1000000
    totals_df_area = totals_df_area.T
    totals_df_area.reset_index(inplace=True)
    totals_df_area.rename(columns={'index': 'short_id', 0: 'FloodedArea'}, inplace = True)
    return totals_df_area
    
def categorise_difference (raster):
    classified_raster = raster.copy()
    classified_raster[np.where( raster < -0.1 )] = 1
    classified_raster[np.where((-0.1 >= raster) & (raster < 0.1)) ] = 2
    classified_raster[np.where((0.1 >= raster) & (raster < 0.3)) ] = 3
    classified_raster[np.where( raster >= 0.3  )] = 4
    return classified_raster

def save_array_as_raster(raster, fp_to_save, out_meta):
    #src = rasterio.open("MeganModel/6hr_dt_u/6hr_dividetime_velocity.Resampled.Terrain.tif")
    with rasterio.open(
            fp_to_save, "w", **out_meta) as dest_file:
        dest_file.write(raster,1)
    dest_file.close()      

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]

# Opensa raster, trims it to extent of catchment, saves a trimmed version
# and returns an arrat contianing the data, also trimmed
def open_and_clip(input_raster_fp):
    # Read in data as array
    data = rasterio.open(input_raster_fp)
    # Create a bounding box 
    minx, miny = 437000,  426500
    maxx, maxy = 445500, 434300
    bbox = box(minx, miny, maxx, maxy)
    # Insert the bbox into a GeoDataFrame
    geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs=CRS('EPSG:27700'))     
    # Re-project into the same coordinate system as the raster data
    geo = geo.to_crs(crs=CRS('EPSG:27700'))#data.crs.data

    # Next we need to get the coordinates of the geometry in such a format
    # that rasterio wants them. This can be conducted easily with following function
    # Get the geometry coordinates by using the function.
    coords = getFeatures(geo)

    # Clip the raster with the polygon using the coords variable that we just created. Clipping the raster can be done easily 
    # with the mask function and specifying clip=True.
    clipped_array, out_transform = mask(data, shapes=coords, crop=True)

    # # Set -9999 to NA
    if np.isnan(np.sum(clipped_array)) == True:
        clipped_array[clipped_array < -9998] = np.nan
        clipped_array[clipped_array < -9999] = np.nan
    else:
        clipped_array = clipped_array.astype('float') 
        clipped_array[clipped_array ==0] = np.nan

    # Modify the metadata. Let’s start by copying the metadata from the original data file.
    out_meta = data.meta.copy()
    # Parse the EPSG value from the CRS so that we can create a Proj4 string using PyCRS library 
    # (to ensure that the projection information is saved correctly) [this bit didn't work so specified manually]
    #epsg_code = int(data.crs.data['init'][5:])
    # Now we need to update the metadata with new dimensions, transform (affine) and CRS (as Proj4 text)
    out_meta.update({"driver": "GTiff","height": clipped_array.shape[1],"width": clipped_array.shape[2], 
                     "transform": out_transform, "crs": CRS('EPSG:27700')})#pycrs.parser.from_epsg_code(epsg_code).to_proj4()})

    return clipped_array[0,:,:], out_meta

def prepare_rainfall_scenario_raster(input_raster_fp, remove_little_values):
    
    # Clip the raster files to the extent of the catchment boundary
    # Also return out_meta which contains..
    raster, out_meta = open_and_clip(input_raster_fp) 
    
    # If looking at velocity, then also read in depth raster as this is needed to filter out cells where 
    # the depth is below 0.1m   
    # Set cell values to Null in cells which have a value <0.1 in the depth raster
    if remove_little_values == True:
        if "Depth" in input_raster_fp:
            raster = np.where(raster <0.1, np.nan, raster)    
        else:
            depth_raster = open_and_clip(input_raster_fp.replace('Velocity', 'Depth'))[0]
            raster = np.where(depth_raster <0.1, np.nan, raster)
    
    return raster, out_meta

def classify_raster (raster, breaks):
    
    # Classify using the specified breaks
    classified_raster = np.digitize(raster,breaks, right = False)
    # Set values which are classified as category 5 to np.nan
    classified_raster = np.where(classified_raster == len(breaks), np.nan, classified_raster)
    
    return classified_raster

def find_worst_case_method(fps, short_ids, variable_name):
    scenario_ls =[]
    for fp in fps[1:]:
        scenario = prepare_rainfall_scenario_raster(fp.format(variable_name), remove_little_values)[0].flatten()
        scenario_ls.append(scenario)

    #Create a list to store the index for each cell of the scenario that produced the maximum value
    rainfall_scenario_max_producing_numbers = []
    # Assign a number for each of the scenarios (0:singlepeak, 1:dividetime, 2:subpeaktiming, 3:maxspread)
    rainfall_scenario_numbers = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    # Loop through each cell in the array:
    ls = []
    for i, x in enumerate(zip(*scenario_ls)):
        ls.append(i)
        # Find the number related to the scenario which produced the maximum
        index_of_max = np.argmax(x)
        # Check that the max being referrred to is not np.nan
        # if it is, then append np.nan to the list of indexes, to indicate no values were the maximum
        if np.isnan(x[index_of_max]):
              rainfall_scenario_max_producing_numbers.append(np.nan)
        # If it's not np.nan
        else:
            # Check that the maximum value is not equal to any of the other values
            # If there is another equivalent value then add a flag to the list storing whether there are any matching values
            matches = []
            for number in rainfall_scenario_numbers:
                if number != index_of_max:
                    if x[number] == x[index_of_max]:
                        matches.append('yes')
            # If matches is empty (i.e. there are no matching values to the maxium) then give the index of 
            # the scenario which was the maximum 
            if not matches:
                rainfall_scenario_max_producing_numbers.append(short_ids[1:][index_of_max])
            # If matches is not empty (i.e. there are values matching the maximum) then return 4 (no one 
            # scenario can be deemed the worst case)
            elif matches:
                rainfall_scenario_max_producing_numbers.append('multiple matches')      

    # Find the number of counts of each value
    unique, counts = np.unique(rainfall_scenario_max_producing_numbers, return_counts=True)
    worst_case_method_df = pd.DataFrame({'values': unique, 'counts':counts})
    return worst_case_method_df

''' Gets the depth/velocity counts and props data back into the format that the original plotting
function expected it in'''
def reformat_counts_and_props(cluster_results, column_names,short_ids):
    counts  = cluster_results[column_names]
    counts.columns = [col.replace('_{}'.format(column_names[0].split('_')[1]), '') for col in counts.columns]
    if 'urban' in counts.columns[1]:
        counts.columns = [col.replace('_urban', '') for col in counts.columns]
    counts = counts.T
    counts.columns = short_ids
    return counts

######################################################################
######################################################################
## Plotting functions
######################################################################
######################################################################
def create_colours_df (short_ids_by_loading, short_ids):
    lst = ['darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    loading_lst = ['F2', 'F1', 'C', 'B1', 'B2']
    colours =['black'] + list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in lst))
    loadings =['FEH'] + list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in loading_lst))
    colours_df = pd.DataFrame({ 'short_id': short_ids_by_loading, "colour": colours, 'loading':loadings})
    colours_df = colours_df.reindex(colours_df['short_id'].map(dict(zip(short_ids, range(len(short_ids))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    return colours_df


def scatter_plot_with_trend_line(ax, short_ids, x,y,xlabel,ylabel,  colors, add_r2 = False):
    ax.scatter(x, y, color = colors)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    m, b, r_value, p_value, std_err = stats.linregress(x,y)
#     ax.plot(x, m*x + b)
    if add_r2 == True:
        ax.annotate('R\N{SUPERSCRIPT TWO} = ' + str("{:.2f}".format(r_value**2))
                    + ', P value = ' + str("{:.2f}".format(p_value**2)) , 
                     xy=(x.min() + (x.min()/150), y.max() - (y.max()/150)),
                   color = 'darkred')
    ax.plot(x,p(x),"k--")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    for i, txt in enumerate(short_ids):
        ax.annotate(txt, (x[i], y[i]))
    ax.set_title("{} against\n {}".format(xlabel, ylabel), fontsize = 8)
        
def make_props_plot (ax, proportions_df, variable, variable_unit, labels):
    
    # reformat the dataframe for stacked plotting
    reformatted_df  =proportions_df.T[1:]
    reformatted_df.columns = labels

    # Plot
    reformatted_df.plot(ax=ax, kind='bar', edgecolor='white', linewidth=3, stacked = True, width =0.8, rot =45,
                         xlabel = 'Flood {} ({})'.format(variable, variable_unit),
                            ylabel = 'Proportion of flooded cells', fontsize = 12)
    plt.rcParams.update({'font.size': 14})
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')

def bar_plot_counts (fig, ax, counts_df, variable_name, short_ids_order, colours_df, title):
    
    labels = counts_df.index
    x = np.arange(len(counts_df.index))
    width = 0.3
        
    counts_df = counts_df[short_ids_order].copy()
    
    colours_df =colours_df.reindex(colours_df['short_id'].map(dict(zip(short_ids_order, range(len(short_ids_order))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    
    # counts_df plotting
    width, DistBetweenBars, Num = 0.05, 0.01, 16 # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num*width + (Num-1)*DistBetweenBars        
        
    # Proportions_df plotting
    for i in range(Num):
        ax.bar(np.arange(len(counts_df))-WithGroupedBars/2 + (width+DistBetweenBars)*i, counts_df.iloc[:,i], width, 
                color = colours_df['colour'][i])
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {}'.format(variable_name), fontsize = 15)
    ax.set_ylabel('Number of cells', fontsize = 15)
    
    # Make legend
    colors = ['black','darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    texts = ['FEH','F2','F1','C', 'B1', 'B2'] 
    patches = [ mpatches.Patch(color=colors[i], label="{:s}".format(texts[i]) ) for i in range(len(texts)) ]
    plt.legend(handles=patches, bbox_to_anchor=(1.15, 0.5), loc='center', ncol=1, prop={'size': 15} )  

    
def bar_plot_props (fig, ax, props_df, variable_name, short_ids_order, colours_df, title):
    
    labels = props_df.index
    x = np.arange(len(props_df.index))
    width = 0.3
        
    props_df = props_df[short_ids_order].copy()
    
    colours_df =colours_df.reindex(colours_df['short_id'].map(dict(zip(short_ids_order, range(len(short_ids_order))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    
    # counts_df plotting
    width, DistBetweenBars, Num = 0.05, 0.01, 16 # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num*width + (Num-1)*DistBetweenBars        
        
    # Proportions_df plotting
    for i in range(Num):
        ax.bar(np.arange(len(props_df))-WithGroupedBars/2 + (width+DistBetweenBars)*i, props_df.iloc[:,i], width, 
                color = colours_df['colour'][i])
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {}'.format(variable_name), fontsize = 15)
    ax.set_ylabel('Proportion of cells', fontsize = 15)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    
    # Make legend
    colors = ['black','darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    texts = ['FEH','F2','F1','C', 'B1', 'B2'] 
    patches = [ mpatches.Patch(color=colors[i], label="{:s}".format(texts[i]) ) for i in range(len(texts)) ]
    plt.legend(handles=patches, bbox_to_anchor=(1.15, 0.5), loc='center', ncol=1, prop={'size': 15} )
    
    fig.suptitle(title, fontsize = 25)     

def plot_totals(cluster_results, short_ids, title):
    colors = cluster_results['colour']
    cluster_results = cluster_results.reindex(cluster_results['Cluster_num'].map(dict(zip(short_ids, range(len(short_ids))))).sort_values().index)
    cluster_results.reset_index(inplace=True, drop=True)
    
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize = (28,7))
    y_pos = np.arange(len(cluster_results['Cluster_num']))

    ##############################
    # Plot number of flooded cells
    ##############################
    axs[0].bar(y_pos, cluster_results['TotalFloodedArea'].values.tolist(), width = 0.9, color = cluster_results['colour'])
    # Create names on the x-axis
    axs[0].set_xticks(y_pos)
    axs[0].set_xticklabels(short_ids, fontsize =20, rotation = 75)
    axs[0].set_ylabel('Number of flooded cells', fontsize =20)
    axs[0].tick_params(axis='both', which='major', labelsize=15)

    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]
    
    for i, v in enumerate(cluster_results['TotalFloodedArea'].values.tolist()):
        axs[0].text(xlocs[i] - 1.2, v * 1.025, str(cluster_results["%Diff_FloodedArea_fromSP_formatted"][i]), fontsize = 19, rotation =90)

    ##############################
    # Plot percent difference from single peak
    ##############################
    axs[1].bar(np.arange(len(cluster_results['%Diff_FloodedArea_fromSP'][1:])), cluster_results['%Diff_FloodedArea_fromSP'][1:], width = 0.9, color = cluster_results['colour'][1:])
    # Create names on the x-axis
    axs[1].set_xticks(y_pos[:-1])
    axs[1].set_xticklabels(short_ids[1:], fontsize =20, rotation = 75)
    axs[1].set_ylabel('% difference from single peak', fontsize =20)
    axs[1].tick_params(axis='both', which='major', labelsize=15)    

    ##############################
    # Plot percent diffference (absoloute)
    ##############################
    axs[2].bar(np.arange(len(cluster_results['Abs%Diff_FloodedArea_fromSP'][1:])), cluster_results['Abs%Diff_FloodedArea_fromSP'][1:], width = 0.9, color = cluster_results['colour'][1:])
    # Create names on the x-axis
    axs[2].set_xticks(y_pos[:-1])
    axs[2].set_xticklabels(short_ids[1:], fontsize =20, rotation = 75)
    axs[2].set_ylabel('Absoloute % difference from single peak', fontsize =20)
    axs[2].tick_params(axis='both', which='major', labelsize=15)
    
    # Make legend
    colors = ['black','darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    texts = ['FEH','F2','F1','C', 'B1', 'B2'] 
    patches = [ mpatches.Patch(color=colors[i], label="{:s}".format(texts[i]) ) for i in range(len(texts)) ]
    plt.legend(handles=patches, bbox_to_anchor=(1.1, 0.5), loc='center', ncol=1, prop={'size': 15} )
    
    fig.suptitle(title, fontsize = 25)   
    
def plot_difference_levels (fp_for_classified_diff_raster, labels, norm = None):

    # Create discrete cmap
    colors_list = [mpl.cm.viridis(0.1), mpl.cm.viridis(0.5), mpl.cm.viridis(0.7), mpl.cm.viridis(0.9)]
    cmap = mpl.colors.ListedColormap(colors_list)
    cmap.set_over('red')
    cmap.set_under('green')

    # Create labels
    if 'depth' in fp_for_classified_diff_raster:
        labels= ['<-0.1m', '-0.1-0.1m', '0.1-0.3m', '0.3m+']
    else:
        labels = ['<-0.1m/s', '-0.1-0.1m/s', '0.1-0.3m/s', '0.3m/s+']
   
   # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  

    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_classified_diff_raster)

    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)
       
    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()
    plt.axis('off')
    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =20)
    
    # Create file path for saving figure to
    method_name = fp_for_classified_diff_raster.split("/")[6]
    figs_dir = 'Figs/{}/'.format(method_name)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_classified_diff_raster).group(1) + ".png"
                                 
    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()   
    
def plot_classified_raster(fp_for_classified_raster, labels, colors_list, norm = None):
    
    # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  
    
    # Create cmap
    cmap = mpl.colors.ListedColormap(colors_list)
    
    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_classified_raster)

    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)

    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()

    plt.axis('off')

    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =20)
    
    # Create file path for saving figure to
    method_name = fp_for_classified_raster.split("/")[6]
    figs_dir = 'Figs/{}/'.format(method_name)
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_classified_raster).group(1) + ".png"

    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()  
      
        
def plot_difference_levels_pos_neg (fp_for_posneg_diff_raster, norm = None):

    # Create discrete cmap
    colors_list = ["red", "grey", "green"]
    cmap = mpl.colors.ListedColormap(colors_list)

    # Create patches for legend
    patches_list = []
    labels= ['{} < single peak'.format(fp_for_posneg_diff_raster.split('/')[1]),
             '{} = single peak'.format(fp_for_posneg_diff_raster.split('/')[1]),
             '{} > single peak'.format(fp_for_posneg_diff_raster.split('/')[1])]
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  

    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_posneg_diff_raster)

    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)

    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()

    plt.axis('off')
    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =15)
    
    # Create file path for saving figure to
    method_name =  fp_for_posneg_diff_raster.split("/")[6]
    figs_dir = 'Figs/{}/'.format(method_name)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_posneg_diff_raster).group(1) + ".png"                                 
    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()  
    
def plot_worst_case_bars (ax, cluster_results, short_ids, col):
    y_pos = np.arange(len(cluster_results['Cluster_num']))
    ax.bar(y_pos, cluster_results[col].values.tolist(), width = 0.9, color = cluster_results['colour'])
    ax.set_xticks(y_pos)
    ax.set_xticklabels(short_ids, fontsize =20, rotation = 75)
    ax.set_ylabel('Number of flooded cells', fontsize =20)
    ax.tick_params(axis='both', which='major', labelsize=15)
    
def make_totals_bar_plot (ax, totals_df, y_name, ls, colors):
    y_pos = np.arange(len(totals_df.columns))
    ax.bar( y_pos, totals_df.iloc[[0]].values.tolist()[0], color=colors,
            width = 0.9)
    # Create names on the x-axis
    ax.set_xticks(y_pos, totals_df_area.columns, fontsize =10, rotation = 45)
    ax.tick_params(axis= 'both', which = 'major', labelsize =10)

    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,10)]
    xlabs=[i/2 for i in range(0,10)]

    for i, v in enumerate(totals_df.iloc[[0]].values.tolist()[0]):
        ax.text(xlocs[i] - 1.12, v * 1.015, str(ls[i]), fontsize = 10)
    
def make_bar_plot_by_category (ax, df_to_plot, variable, variable_unit, ylabel, colors):
           
    # Setting up plotting
    width, DistBetweenBars, Num = 0.2, 0.01, 4 # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num* width + (Num-1)*DistBetweenBars

    for i in range(Num):
        ax.bar(np.arange(len(df_to_plot))-WithGroupedBars/2 + (width+DistBetweenBars)*i, df_to_plot.iloc[:,i+1], width, 
                color = colors[i])
    ax.set_xticks(np.arange(len(df_to_plot['index'])), df_to_plot['index'], rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {} ({})'.format(variable,variable_unit), fontsize = 15)
    ax.set_ylabel(ylabel, fontsize = 15)
    
    # Put legend on top left plot
    if ax == axs[0,0]:
        plt.legend(df_to_plot.columns[1:], fontsize=15, frameon = True)    
    
    
def make_props_plot (ax, proportions_df, variable, variable_unit, labels):
    
    # reformat the dataframe for stacked plotting
    reformatted_df  =proportions_df.T[1:]
    
    if variable  == 'Velocity':
        reformatted_df.columns = labels_velocity
    else:
        reformatted_df.columns = labels_depth

    # Plot
    reformatted_df.plot(ax=ax, kind='bar', edgecolor='white', linewidth=3, stacked = True, width =0.8, rot =45,
                         xlabel = 'Flood {} ({})'.format(variable, variable_unit),
                            ylabel = 'Proportion of flooded cells', fontsize = 12)
    plt.rcParams.update({'font.size': 14})
    ax.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
       
def make_spatial_plot(ax, fp):
    img = Image.open(fp)
    ax.imshow(img)
    ax.axis('off')   
    
def prep_for_folium_plotting(input_raster_fp):
    # Open dataset using rioxarray
    xarray_dataarray = rxr.open_rasterio(input_raster_fp).squeeze()
    # reproject
    xarray_dataarray.rio.set_crs("EPSG:27700")
    xarray_dataarray = xarray_dataarray.rio.reproject("EPSG:4326", nodata = np.nan)
    return xarray_dataarray

def colorize(array, cmap):
    normed_data = (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array)) 
    #normed_data = (array - array.min()) / (array.max() - array.min()) 
    cm = plt.cm.get_cmap(cmap)    
    return np.uint8(cm(normed_data)  * 255)

def plot_with_folium(dict_of_fps_and_names, cmap, template):
    
    # Set up figure
    f = folium.Figure(width=800, height=700)
    
    # Create base map - location figures were from clat, clon, but wanted to create map before loop
    mapa = folium.Map(location=[53.768306874761016, -1.3756056884868098],zoom_start=13).add_to(f)
    folium.TileLayer(
        tiles = 'https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}',
        attr="No Base Map",
        name="No Base Map",
        show=True
    ).add_to(mapa)
   
    # Add to map
    catchment_boundary_feature_group = FeatureGroup(name='Catchment boundary')
    catchment_boundary_feature_group.add_child(folium.GeoJson(data=catchment_gdf["geometry"], style_function=lambda x, 
                                                              fillColor='#00000000', color='Black': {
            "fillColor": '#00000000',"color": 'Black',}))
        
    # Add raster data
    for name,fp in dict_of_fps_and_names.items():
        # read in with xarray and convert projection
        xarray_dataarray = prep_for_folium_plotting(fp)
        # Get coordinates needed in plotting
        clat, clon = xarray_dataarray.y.values.mean(), xarray_dataarray.x.values.mean()
        mlat, mlon = xarray_dataarray.y.values.min(), xarray_dataarray.x.values.min()
        xlat, xlon = xarray_dataarray.y.values.max(), xarray_dataarray.x.values.max()
        # Apply colormap
        data  = ma.masked_invalid(xarray_dataarray.values)
        colored_data = colorize(data.data, cmap=cmap)
        # Add to map
        feature_group1 = FeatureGroup(name=name)
        feature_group1.add_child(folium.raster_layers.ImageOverlay(colored_data,
                                  [[mlat, mlon], [xlat, xlon]],
                                  opacity=1,interactive=True, popup=name))
        mapa.add_child(feature_group1)
    
    # Add legend
    macro = MacroElement()
    macro._template = Template(template)
    mapa.get_root().add_child(macro)
    
    # Add layer control button
    mapa.add_child(catchment_boundary_feature_group)
    mapa.add_child(LayerControl("topright", collapsed = False))
    display(mapa)    
    
def plot_diff_hazard_cats( fp_for_diff_raster, labels, colors_list, norm = None):

    # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  

    # Create cmap
    cmap = mpl.colors.ListedColormap(colors_list)

    # plot the new clipped raster      
    clipped = rasterio.open(fp_for_diff_raster)

    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = catchment_gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)

    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()

    plt.axis('off')

    plt.legend(handles=patches_list, handleheight=3, handlelength=3, fontsize =20)

    # Create file path for saving figure to
    method_name = fp_for_diff_raster.split("/")[6]
    figs_dir = 'Figs/{}/'.format(method_name)
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_diff_raster).group(1) + ".png"

    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()   