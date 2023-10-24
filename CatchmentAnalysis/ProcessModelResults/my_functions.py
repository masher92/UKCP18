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

# Opens a raster, trims it to extent of catchment, saves a trimmed version
# and returns an arrat contianing the data, also trimmed
def open_and_clip(input_raster_fp, bbox):
    # Read in data as array
    data = rasterio.open(input_raster_fp)

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


def open_and_clip_to_catchment (input_fp, catchment_gdf, crop_or_not):
    # Get the results, and mask out values not within the geodataframe
    with rasterio.open(input_fp) as src:
        catchment_gdf=catchment_gdf.to_crs(src.crs)
        out_image, out_transform=mask(src,catchment_gdf.geometry,crop=crop_or_not)
        out_meta=src.meta.copy() # copy the metadata of the source DEM
        raster = out_image[0]
        # Set -9999 to np.nan
        raster = raster.astype('float') 
        raster[raster <= -9999] = np.nan
        raster[raster == 0] = np.nan
        raster[raster ==-2147483648] = np.nan
    # Update to match     
    out_meta.update({"nodata":np.nan,"dtype" :'float64', "driver":"Gtiff", "height":out_image.shape[1], # height starts with shape[1]
        "width":out_image.shape[2], # width starts with shape[2]
        "transform":out_transform})
    
    return raster, out_meta   


def prepare_rainfall_scenario_raster(input_raster_fp, bbox, remove_little_values):
    
    # Clip the raster files to the extent of the catchment boundary
    # Also return out_meta which contains..
    raster, out_meta = open_and_clip(input_raster_fp, bbox) 
    
    # If looking at velocity, then also read in depth raster as this is needed to filter out cells where 
    # the depth is below 0.1m   
    # Set cell values to Null in cells which have a value <0.1 in the depth raster
    if remove_little_values == True:
        if "Depth" in input_raster_fp:
            raster = np.where(raster <0.1, np.nan, raster)    
        else:
            depth_raster = open_and_clip(input_raster_fp.replace('Velocity', 'Depth'), bbox)[0]
            raster = np.where(depth_raster <0.1, np.nan, raster)
    
    return raster, out_meta


def remove_little_values_fxn(raster, fp, catchment_gdf, crop_or_not):
        if "Depth" in fp:
            raster = np.where(raster <0.1, np.nan, raster)    
        else:
            depth_raster, out_meta  = open_and_clip_to_catchment(fp.format('Depth'), catchment_gdf, crop_or_not)
            raster = np.where(depth_raster <0.1, np.nan, raster)      
        return raster

def create_binned_counts_and_props(methods, fps, filter_by_land_cover, variable_name, catchment_gdf, crop_or_not,
                                   landcover_data=False, remove_little_values = True,):
    
    # Set breaks/labels for either velocity and depth
    if variable_name =='Depth':
        breaks = np.array([0, 0.3, 0.6, 1.2, 100])  
        labels = ['<=0.3m', '0.3-0.6m', '0.6-1.2m', '>1.2m']
    elif variable_name =='Velocity':
        breaks = np.array([0,0.25,0.5,2,100])
        labels = ["<=0.25m/s", "0.25-0.5m/s", "0.5-2m/s", ">2m/s"]
        
    # Create dataframes to populate with values
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()        

    # Loop through each rainfall scenario
    # Get the raster containing its values, and count the number of each unique value, and construct into a dataframe
    for num, fp in enumerate(fps) :
        
        # Get the results, and trim to the catchment
        raster, out_meta  = open_and_clip_to_catchment(fp.format(variable_name), catchment_gdf, crop_or_not)
        # Remove values <0.1m
        if remove_little_values == True:
            raster = remove_little_values_fxn(raster, fp, catchment_gdf, crop_or_not)       
                        
        # If analysing all cells
        if filter_by_land_cover == '':
            # Dataframe containing all values
            df=pd.DataFrame({'value':raster.flatten()})
            # Remove NAs
            df = df.dropna()
            # Add a new column specifying the bin which each value falls within
            df['bins']= pd.cut(df['value'], bins=breaks, right=False)

        # If just analysing certain landcover cells
        elif filter_by_land_cover == True:
            raster_and_landcover = pd.DataFrame({'landcovercategory':  landcover_data, 'value': raster.flatten()})
            # Get just the relevant rows
            df = raster_and_landcover[raster_and_landcover['landcovercategory']==10].copy()  
            # Remove na
            df = df.dropna()
            # Add a column assigning a bin based on the depth/velocity value
            df['bins']= pd.cut(df['value'], bins=breaks, right=False)
            
        # Create a new dataframe showing the number of cells in each of the bins
        groups = df.groupby(['bins']).count()
        groups  = groups.reset_index()
        groups.rename(columns={"value": "Count"},inplace=True)

        # Find the total number of cells
        total_n_cells = groups['Count'].sum()
        # Find the number of cells in each group as a proportion of the total
        groups['Proportion'] = round((groups['Count']/total_n_cells) *100,1)

        # Add values to dataframes
        method_name = methods[num]
        counts_df[method_name] = groups['Count']
        proportions_df[method_name] = groups['Proportion']

    # Reset index to show the groups
    counts_df.reset_index(inplace=True)
    proportions_df.reset_index(inplace=True)

    # Set index values
    counts_df['index'] = labels
    proportions_df['index'] = labels
    
    return counts_df,proportions_df

def create_binned_counts_and_props_hazard(methods, fps, filter_by_land_cover, catchment_name_str, catchment_gdf, crop_or_not, landcover_data=False, remove_little_values = True):

    # Create dataframes to populate with values
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()      

    for num, fp in enumerate(fps):
        # Define filepath
        fp = fp.replace('{} (Max).{}'.format({}, catchment_name_str),'hazard_classified')
        
        ####################################################
        # Open hazard results file and trim to catchment boundary
        ####################################################
        # Get the results, and trim to the catchment
        hazard, out_meta  = open_and_clip_to_catchment(fp, catchment_gdf, crop_or_not)
            
        # Remove values <0.1m
        if remove_little_values == True:
            hazard = remove_little_values_fxn(hazard, fp, catchment_gdf, crop_or_not)                   
                
        ####################################################        
        # If filtering by land cover, then do additional stage of filtering out only cells in that category
        ####################################################
        if filter_by_land_cover != '':
            # Get dataframe of hazard values, alongside land cover class
            hazard_and_landcover = pd.DataFrame({'landcovercategory':  landcover_data.flatten(), 'counts': hazard.flatten()})
            # Keep just the rows in the relevant landcoverclass
            df = hazard_and_landcover[hazard_and_landcover['landcovercategory']==10].copy()  
            # remove the NA values (i.e. where there is no flooding)
            df=df[df.counts.notnull()]
            # Convert the counts back into an array
            hazard = np.array(df['counts'])
            
        ####################################################
        # Count number of cells in each hazard category
        ####################################################
        unique, counts = np.unique(hazard, return_counts=True)
        df = pd.DataFrame({'values': unique, 'counts':counts})
        # Remove Nan values
        df = df.dropna()
        
        # Find the total number of cells
        total_n_cells = df ['counts'].sum()
        # Find the number of cells in each group as a proportion of the total
        df['Proportion'] = round((df['counts']/total_n_cells) *100,1)
        
        # Add values to dataframes
        method_name = methods[num]
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


def find_percentage_diff (methods, reference_method_name, totals_df, fps):
    percent_diffs_formatted_for_plot = []
    percent_diffs_abs = []
    percent_diffs = []

    sp_value = totals_df.loc[totals_df['short_id'] == reference_method_name]['FloodedArea']

    for num, fp in enumerate(fps):
        rainfall_scenario_name = methods[num]
        if rainfall_scenario_name!= reference_method_name:
            # Find value for this scenario
            this_scenario_value = totals_df.loc[totals_df['short_id'] == rainfall_scenario_name]['FloodedArea']
            this_scenario_value.reset_index(drop=True, inplace=True)
            # Find % difference between single peak and this scenario
            percent_diffs.append(round((this_scenario_value/sp_value-1)*100,1)[0])
            percent_diffs_abs.append(round(abs((this_scenario_value/sp_value-1)[0])*100,1))
            percent_diffs_formatted_for_plot.append(round((this_scenario_value/sp_value-1)*100,1)[0])
    # Convert values to strings, and add a + sign for positive values
    # Include an empty entry for the single peak scenario
    percent_diffs_df = pd.DataFrame({'percent_diff_formatted':[''] +['+' + str(round((list_item),2)) + '%' if list_item > 0 else str(round((list_item),2)) +
     '%'  for list_item in percent_diffs_formatted_for_plot] ,
             'percent_diffs':[0] + percent_diffs, 'percent_diffs_abs':[0] + percent_diffs_abs })
    return percent_diffs_df

def create_totals_df (velocity_counts, cell_size_in_m2):
    totals_df =pd.DataFrame(velocity_counts.sum(numeric_only=True)).T
    totals_df = totals_df.iloc[[len(totals_df)-1]]
    # Convert this to the total flooded area for each method
    totals_df_area = (totals_df * cell_size_in_m2)/1000000
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
    with rasterio.open(
            fp_to_save, "w", **out_meta) as dest_file:
        dest_file.write(raster,1)
    dest_file.close()      

def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]


def classify_raster (raster, breaks):
    
    # Classify using the specified breaks
    classified_raster = np.digitize(raster,breaks, right = False)
    # Set values which are classified as category 5 to np.nan
    classified_raster = np.where(classified_raster == len(breaks), np.nan, classified_raster)
    
    return classified_raster


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


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0
   
    
def find_percentage_diff (methods, reference_method_name, totals_df, fps):
    percent_diffs_formatted_for_plot = []
    percent_diffs_abs = []
    percent_diffs = []

    sp_value = totals_df.loc[totals_df['short_id'] == reference_method_name]['FloodedArea'].values[0]

    for num, fp in enumerate(fps):
        rainfall_scenario_name = methods[num]
        if rainfall_scenario_name!= reference_method_name:
            # FInd value for this scenario
            this_scenario_value = totals_df.loc[totals_df['short_id'] == rainfall_scenario_name]['FloodedArea'].values[0]
            # FInd % difference between single peak and this scenario
            #percent_diffs.append(round((this_scenario_value/sp_value-1)*100,1)[0])
            percent_diffs.append(get_change(this_scenario_value, sp_value))
            #percent_diffs.append(round((this_scenario_value/sp_value-1)*100,1))
            percent_diffs_abs.append(round(abs((this_scenario_value/sp_value-1))*100,1))
            percent_diffs_formatted_for_plot.append(round((this_scenario_value/sp_value-1)*100,1))
    # Convert values to strings, and add a + sign for positive values
    # Include an empty entry for the single peak scenario
    percent_diffs_df = pd.DataFrame({'percent_diff_formatted':[''] +['+' + str(round((list_item),2)) + '%' if list_item > 0 else str(round((list_item),2)) +
     '%'  for list_item in percent_diffs_formatted_for_plot] ,
             'percent_diffs':[0] + percent_diffs, 'percent_diffs_abs':[0] + percent_diffs_abs })
    return percent_diffs_df    
    
######################################################################
######################################################################
## Plotting functions
######################################################################
######################################################################
def create_colours_df_idealised (short_ids_by_loading, short_ids):
    colours =  ['darkblue']*2 + ['paleturquoise']*2 + ['grey']+  ['indianred']*2 + ['darkred']*2
    loadings = ['F2']*2 + ['F1']*2 + ['C']+  ['B1']*2 + ['B2']*2
    colours_df = pd.DataFrame({ 'short_id': short_ids_by_loading, "colour": colours, 'loading':loadings})
    colours_df = colours_df.reindex(colours_df['short_id'].map(dict(zip(short_ids, range(len(short_ids))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    return colours_df

def create_colours_df_observed (short_ids_by_loading, methods):
    # remove the feh profile from list (because want to order by loading)
    short_ids_by_loading_nofeh=short_ids_by_loading.copy()
    short_ids_by_loading_nofeh.remove('6h_feh_singlepeak')
    colours =list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x
                                                in ['darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']))
    loadings =list(itertools.chain.from_iterable(itertools.repeat(x, 3) for x in ['F2', 'F1', 'C', 'B1', 'B2']))
    colours_df = pd.DataFrame({ 'short_id': short_ids_by_loading_nofeh, "colour": colours, 'loading':loadings})
    feh_row = pd.DataFrame({'short_id':'6h_feh_singlepeak', "colour": "black", "loading":"FEH"}, index=[0])
    colours_df = pd.concat([feh_row,colours_df.loc[:]]).reset_index(drop=True)
    colours_df = colours_df.reindex(colours_df['short_id'].map(dict(zip(methods, range(len(methods))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    return colours_df

def create_colours_df_sp (short_ids_by_loading, short_ids):
    colours_lst = ['black'] + ['#82a2cf', '#566cb8', '#2b36a2', '#00008b']
    colours_df = pd.DataFrame({ 'short_id': short_ids_by_loading, "colour": colours_lst})
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
    
    colours_df =colours_df.reindex(colours_df['Cluster_num'].map(dict(zip(short_ids_order, range(len(short_ids_order))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    
    # counts_df plotting
    width, DistBetweenBars, Num = 0.05, 0.01, len(counts_df.columns) # width of each bar, distance between bars, number of bars in a group
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
    
    colours_df =colours_df.reindex(colours_df['Cluster_num'].map(dict(zip(short_ids_order, range(len(short_ids_order))))).sort_values().index)
    colours_df.reset_index(inplace=True, drop=True)
    
    # counts_df plotting
    width, DistBetweenBars, Num = 0.05, 0.01, len(props_df.columns) # width of each bar, distance between bars, number of bars in a group
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

    
def bar_plot_props_by_loading_cat(fig, ax, props_df, variable_name, short_ids_order, colours_df, title):
    test_df = pd.DataFrame()
    for loading in ['FEH','F2', 'F1', 'B1', 'B2']:
        ls_names = []
        for short_id in colours_df[colours_df['loading']==loading]['short_id']:
            ls_names.append(short_id)
            test_df[loading] = props_df[ls_names].mean(axis=1)

    # counts_df plotting
    width, DistBetweenBars, Num = 0.15, 0.01, len(test_df.columns) # width of each bar, distance between bars, number of bars in a group
    # calculate the width of the grouped bars (including the distance between the individual bars)
    WithGroupedBars = Num*width + (Num-1)*DistBetweenBars        

    # Proportions_df plotting
    for i in range(Num):
        ax.bar(np.arange(len(test_df))-WithGroupedBars/2 + (width+DistBetweenBars)*i, test_df.iloc[:,i], width, 
                color = ['black','darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred'][i])

    ax.set_xticks(np.arange(len(test_df.index)))
    ax.set_xticklabels(test_df.index, rotation=30, fontsize = 12)
    ax.set_xlabel('Flood {}'.format(variable_name), fontsize = 15)
    ax.set_ylabel('Proportion of cells', fontsize = 15)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter())   
    
def plot_totals_1plot(cluster_results, urban_str, title, save_dir):

    fig, axs = plt.subplots(figsize = (5,4))
    y_pos = np.arange(len(cluster_results['Cluster_num']))

    ##############################
    # Plot number of flooded cells
    ##############################
    axs.bar(y_pos, cluster_results['{}FloodedArea'.format(urban_str)].values.tolist(), width = 0.9, 
               color = cluster_results['colour'])
    # Create names on the x-axis
    axs.set_xticks(y_pos)
    axs.set_xticklabels(cluster_results['Cluster_num'], fontsize =10, rotation = 75)
    axs.set_ylabel('Flooded area (km2)', fontsize =15)
    axs.tick_params(axis='both', which='major', labelsize=12.5)
    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]

    for i, v in enumerate(cluster_results['{}FloodedArea'.format(urban_str)].values.tolist()):
        axs.text(xlocs[i] - 1.2, v * 1.025, str(cluster_results["%Diff_{}FloodedArea_fromSP_formatted".format(urban_str)][i]), 
                    fontsize = 12.5, rotation =90)
        
    fig.savefig("{}/FloodedExtent{}_1Plot.PNG".format(save_dir, urban_str), bbox_inches='tight')


def plot_totals_3plots(cluster_results, urban_str, title, save_dir):

    fig, axs = plt.subplots(nrows=1, ncols=3, figsize = (28,7))
    y_pos = np.arange(len(cluster_results['Cluster_num']))

    ##############################
    # Plot number of flooded cells
    ##############################
    axs[0].bar(y_pos, cluster_results['{}FloodedArea'.format(urban_str)].values.tolist(), width = 0.9, 
               color = cluster_results['colour'])
    # Create names on the x-axis
    axs[0].set_xticks(y_pos)
    axs[0].set_xticklabels(cluster_results['Cluster_num'], fontsize =20, rotation = 75)
    axs[0].set_ylabel('Flooded area (km2)', fontsize =30)
    axs[0].tick_params(axis='both', which='major', labelsize=25)
    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]

    for i, v in enumerate(cluster_results['{}FloodedArea'.format(urban_str)].values.tolist()):
        axs[0].text(xlocs[i] - 1.2, v * 1.025, str(cluster_results["%Diff_FloodedArea_fromSP_formatted"][i]), 
                    fontsize = 25, rotation =90)
        
    ##############################
    # Plot percent difference from single peak
    ##############################
    axs[1].bar(np.arange(len(cluster_results['%Diff_{}FloodedArea_fromSP'.format(urban_str)])), 
               cluster_results['%Diff_{}FloodedArea_fromSP'.format(urban_str)], width = 0.9, color = cluster_results['colour'])
    # Create names on the x-axis
    axs[1].set_xticks(y_pos)
    axs[1].set_xticklabels(cluster_results['Cluster_num'], fontsize =10, rotation = 75)
    axs[1].set_ylabel('Percent difference from baseline', fontsize =20)
    axs[1].tick_params(axis='both', which='major', labelsize=15)    

    for i, v in enumerate(cluster_results['{}FloodedArea'.format(urban_str)].values.tolist()):
        if i >4:
            v_multiplier = -0.9
        else:
            v_multiplier= 0.06
        axs[1].text(xlocs[i] -1.2, v * v_multiplier, str(round(cluster_results["{}FloodedArea".format(urban_str)][i],3))+'km2', 
                    fontsize = 20, rotation =90)
    
    ##############################
    # Version without centred profile    
    ##############################
    cluster_results_no_C =  cluster_results.copy()
    cluster_results_no_C = cluster_results_no_C.iloc[[0,1,2,3,5,6,7,8]]
    cluster_results_no_C.reset_index(drop=True, inplace=True)      
    
    ##############################
    # Plot percent diffference (absoloute)
    ##############################
    y_pos = np.arange(len(cluster_results_no_C['Cluster_num']))
    axs[2].bar(np.arange(len(cluster_results_no_C['Abs%Diff_{}FloodedArea_fromSP'.format(urban_str)])), 
               cluster_results_no_C['Abs%Diff_{}FloodedArea_fromSP'.format(urban_str)], 
               width = 0.9, color = cluster_results_no_C['colour'])
    # Create names on the x-axis
    axs[2].set_xticks(y_pos)
    labels = cluster_results_no_C['Cluster_num']
    labels.reset_index(drop=True, inplace=True)
    axs[2].set_xticklabels(labels, fontsize =20, rotation = 75)
    axs[2].set_ylabel('Absoloute % difference from baseline', fontsize =20)
    axs[2].tick_params(axis='both', which='major', labelsize=15)
    
    # Make legend
    colors = ['black','darkblue', 'paleturquoise', 'grey', 'indianred', 'darkred']
    texts = ['F2','F1','C', 'B1', 'B2'] 
    patches = [ mpatches.Patch(color=colors[i], label="{:s}".format(texts[i]) ) for i in range(len(texts)) ]
    plt.legend(handles=patches, bbox_to_anchor=(1.18, 0.55), loc='center', ncol=1, prop={'size': 19} )  
    fig.suptitle(title, fontsize = 25)      
    fig.savefig("{}/FloodedExtent{}_3Plots.PNG".format(save_dir, urban_str), bbox_inches='tight')
    
def plot_difference_levels (fp_for_classified_diff_raster, labels, catchment_gdf,catchment_name, methods_key, norm = None):

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
    figs_dir = 'Outputs/Figs/{}Profiles/{}/SpatialPlots/{}/'.format(methods_key, catchment_name, method_name)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_classified_diff_raster).group(1) + ".png"
                                 
    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()   
        
def plot_classified_raster(fp_for_classified_raster, labels, colors_list, catchment_gdf,catchment_name, methods_key, norm = None):
    
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
    figs_dir = 'Outputs/Figs/{}Profiles/{}/SpatialPlots/{}/'.format(methods_key, catchment_name, method_name)
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_classified_raster).group(1) + ".png"

    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()  
      
        
def plot_difference_levels_pos_neg (fp_for_posneg_diff_raster, catchment_gdf, catchment_name, methods_key, norm = None):

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
    method_name = fp_for_posneg_diff_raster.split("/")[6]
    figs_dir = 'Outputs/Figs/{}Profiles/{}/SpatialPlots/{}/'.format(methods_key, catchment_name, method_name)
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
    cm = plt.cm.get_cmap(cmap)    
    if np.nanmin(array) == np.nanmax(array):
        return np.uint8(cm(array)  * 255)
    else:
        normed_data = (array - np.nanmin(array)) / (np.nanmax(array) - np.nanmin(array)) 
        return np.uint8(cm(normed_data)  * 255)

def plot_with_folium(dict_of_fps_and_names, cmap, template, catchment_gdf):
    
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
    
def plot_diff_hazard_cats( fp_for_diff_raster, labels, colors_list,catchment_gdf, catchment_name, methods_key, norm = None):

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
    figs_dir = 'Outputs/Figs/{}Profiles/{}/SpatialPlots/{}/'.format(methods_key, catchment_name, methods_key)
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + re.search('6h_.*/(.*).tif', fp_for_diff_raster).group(1) + ".png"

    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()   
    
def produce_df_of_cell_by_cell_values(model_directory, catchment_gdf, catchment_name_str, methods, landcover_notwater_flat,
                                      landcover_urban_flat, crop_or_not, remove_little_values = True,):
    all_methods_df = pd.DataFrame()
    variables=['Depth', 'Velocity','Hazard']
    for method_num, short_id in enumerate(methods):
        # Filepath
        fp = model_directory + "{}/{} (Max).{}.tif".format(short_id,'{}',catchment_name_str)
        if '6h_feh_singlepeak' in fp:
            fp = fp.replace("Model_ObservedProfiles", "Model_FEHProfiles")
        # Dataframe where results for this method will be stored
        one_method_df = pd.DataFrame({"short_id" :methods[method_num], 'Water_class':landcover_notwater_flat, 
                                      "urban_class":landcover_urban_flat})
        #print(one_method_df)
        # Read raster, round to three decimal places
        for variable_name in variables:
            this_fp = fp
            if variable_name == 'Hazard':
                this_fp = this_fp.replace('{} (Max).{}'.format('{}', catchment_name_str),'hazard_classified')
            else:
                this_fp = this_fp.format(variable_name)

            raster, out_meta  = open_and_clip_to_catchment(this_fp.format(variable_name), catchment_gdf, crop_or_not)
            #print(len(raster))
            # Remove values <0.1m
            if remove_little_values == True:
                raster = remove_little_values_fxn(raster, fp, catchment_gdf, crop_or_not)       
            
            raster_rounded = np.around(raster, decimals=3)
            
            one_method_df[variable_name]=raster_rounded.flatten()
            # Removes columns that don't have a value for depth/velocity/hazard
        one_method_df = one_method_df.dropna(subset=variables)
        # Join results for this method with results for all methods  
        all_methods_df = pd.concat([all_methods_df, one_method_df], axis =0)   
    return all_methods_df

def plot_totals_area_comparisons(cluster_results_dict, short_ids, title, patches, urban = True):

    fig, axs = plt.subplots(nrows=2, ncols=5, figsize = (28,15))
    y_pos = np.arange(len(cluster_results_dict['All']['Cluster_num']))

    xlocs, xlabs = plt.xticks(y_pos)
    xlocs=[i+1 for i in range(0,19)]
    xlabs=[i/2 for i in range(0,19)]
    
    if urban == True:
        column_to_plot = 'UrbanFloodedArea'
        column_to_text = '%Diff_UrbanFloodedArea_fromSP_formatted'
    else:
        column_to_plot = 'TotalFloodedArea'
        column_to_text = '%Diff_FloodedArea_fromSP_formatted'
        
    for ax_num, (key, cluster_results_df) in enumerate(cluster_results_dict.items()):

        ##############################
        # Plot number of flooded cells
        ##############################
        if urban== True:
            fig.get_axes()[ax_num].bar(y_pos, cluster_results_df[column_to_plot].values.tolist(), width = 0.9, color = cluster_results_df['colour'])
        else:
            fig.get_axes()[ax_num].bar(y_pos, cluster_results_df[column_to_plot].values.tolist(), width = 0.9, color = cluster_results_df['colour'])

        # Create names on the x-axis
        fig.get_axes()[ax_num].set_xticks(y_pos)
        fig.get_axes()[ax_num].set_xticklabels(short_ids, fontsize =10, rotation = 75)
        if ax_num==0:
            fig.get_axes()[ax_num].set_ylabel('Flooded area (km2)', fontsize =20)
        fig.get_axes()[ax_num].tick_params(axis='both', which='major', labelsize=15)
        fig.get_axes()[ax_num].set_title(key, fontsize = 20, x=0.5, y=1.17)

        # Add text with percentages
        for i, v in enumerate(cluster_results_df[column_to_plot].values.tolist()):
            fig.get_axes()[ax_num].text(xlocs[i] - 1.2, v * 1.025, str(cluster_results_df[column_to_text][i]), 
                        fontsize = 20, rotation =90)

        # Make legend
        plt.legend(handles=patches, bbox_to_anchor=(1.18, 0.55), loc='center', ncol=1, prop={'size': 19} )  
        
    fig.get_axes()[ax_num+1].axis('off')
    
    fig.suptitle(title, fontsize = 35,y=1)
    fig.tight_layout(h_pad=3)
  