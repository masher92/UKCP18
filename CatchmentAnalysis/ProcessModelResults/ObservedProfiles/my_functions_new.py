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
# import fiona
import rasterio.plot
import matplotlib as mpl
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
# from fiona.crs import from_epsg
import pycrs
from pyproj import CRS
from branca.element import Template, MacroElement
import folium
from folium import Map, FeatureGroup, LayerControl
import numpy.ma as ma
from pathlib import Path
from PIL import Image
import re

model_directory = '../../../../FloodModelling/MeganModel_New/'

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
        method_name = re.search('{}(.*)/'.format(model_directory), fp).group(1)
        counts_df[method_name] = groups['counts']
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

    sp_value = totals_df.loc[totals_df['short_id'] == '6h_sp']['FloodedArea']

    for fp in fps:
        rainfall_scenario_name = fp.split('/')[6]
        if rainfall_scenario_name!= '6h_sp':
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
    totals_df_area = (totals_df * 25)/1000000
    totals_df_area = totals_df_area.T
    totals_df_area.reset_index(inplace=True)
    totals_df_area.rename(columns={'index': 'short_id', 0: 'FloodedArea'}, inplace = True)
    return totals_df_area


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
        method_name = re.search('{}(.*)/'.format(model_directory), fp).group(1)
        counts_df[method_name] = groups["value"]
        proportions_df[method_name] = groups['Proportion']

    # Reset index to show the groups
    counts_df.reset_index(inplace=True)
    proportions_df.reset_index(inplace=True)

    # Set index values
    counts_df['index'] = labels
    proportions_df['index'] = labels

    return counts_df, proportions_df    
    
    
def categorise_difference (raster):
    classified_raster = raster.copy()
    classified_raster[np.where( raster < -0.1 )] = 1
    classified_raster[np.where((-0.1 >= raster) & (raster < 0.1)) ] = 2
    classified_raster[np.where((0.1 >= raster) & (raster < 0.3)) ] = 3
    classified_raster[np.where( raster >= 0.3  )] = 4
    return classified_raster

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

def save_array_as_raster(raster, fp_to_save, out_meta):
    #src = rasterio.open("MeganModel/6hr_dt_u/6hr_dividetime_velocity.Resampled.Terrain.tif")
    with rasterio.open(
            fp_to_save, "w", **out_meta) as dest_file:
        dest_file.write(raster,1)
    dest_file.close()      
    
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
    def getFeatures(gdf):
        """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
        import json
        return [json.loads(gdf.to_json())['features'][0]['geometry']]
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
    
# def find_worst_case_method(fps, sp_fp, variable_name):
#     # Read in the datasets
#     singlepeak = prepare_rainfall_scenario_raster(sp_fp.format(variable_name), remove_little_values)[0].flatten()
#     dividetime = prepare_rainfall_scenario_raster(fps[2].format(variable_name), remove_little_values)[0].flatten()
#     subpeaktiming =prepare_rainfall_scenario_raster(fps[1].format(variable_name), remove_little_values)[0].flatten()
#     maxspread = prepare_rainfall_scenario_raster(fps[0].format(variable_name), remove_little_values)[0].flatten()

#     # Create a list to store the index for each cell of the scenario that produced the maximum value
#     rainfall_scenario_max_producing_numbers = []
#     # Assign a number for each of the scenarios (0:singlepeak, 1:dividetime, 2:subpeaktiming, 3:maxspread)
#     rainfall_scenario_numbers = [0,1,2,3]
#     # Loop through each cell in the array:
#     ls = []
#     for i, x in enumerate(zip(singlepeak,dividetime, subpeaktiming,maxspread)):
#         ls.append(i)
#         # Find the number related to the scenario which produced the maximum
#         index_of_max = np.argmax(x)
#         # Check that the max being referrred to is not np.nan
#         # if it is, then append np.nan to the list of indexes, to indicate no values were the maximum
#         if np.isnan(x[index_of_max]):
#               rainfall_scenario_max_producing_numbers.append(np.nan)
#         # If it's not np.nan
#         else:
#             # Check that the maximum value is not equal to any of the other values
#             # If there is another equivalent value then add a flag to the list storing whether there are any matching values
#             matches = []
#             for number in rainfall_scenario_numbers:
#                 if number != index_of_max:
#                     if x[number] == x[index_of_max]:
#                         matches.append('yes')
#             # If matches is empty (i.e. there are no matching values to the maxium) then give the index of 
#             # the scenario which was the maximum 
#             if not matches:
#                 rainfall_scenario_max_producing_numbers.append(index_of_max)
#             # If matches is not empty (i.e. there are values matching the maximum) then return 4 (no one 
#             # scenario can be deemed the worst case)
#             elif matches:
#                 rainfall_scenario_max_producing_numbers.append(4)      
    
#     # Find the number of counts of each value
#     unique, counts = np.unique(rainfall_scenario_max_producing_numbers, return_counts=True)
#     worst_case_method_df = pd.DataFrame({'values': unique, 'counts':counts})
    
#     # Store in a dictionary
#     return worst_case_method_df   

template_depth_cats = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            left: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>
 
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 20px;'>

<div class='legend-title'> Depth (m) </div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:#d0e1f2;opacity:1;'></span><=0.3m</li>
    <li><span style='background:#6aaed6;opacity:1;'></span>0.3-0.6m</li>
    <li><span style='background:#2e7ebc;opacity:1;'></span>0.6-1.2m</li>
    <li><span style='background:#000080;opacity:1;'></span>>1.2m</li>

  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""


# matplotlib.colors.to_hex(matplotlib.cm.cool(0.3))
template_velocity_cats = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            left: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>
 
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 20px;'>

<div class='legend-title'> Velocity (m/s) </div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:#4cb3ff;opacity:1;'></span><=0.25m/s</li>
    <li><span style='background:#807fff;opacity:1;'></span>0.25-0.5m/s</li>
    <li><span style='background:#b34cff;opacity:1;'></span>0.5-2m</li>
    <li><span style='background:#e619ff;opacity:1;'></span>>2m</li>

  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""


# mpl.colors.to_hex(matplotlib.cm.cool(0.3))
template_pos_neg = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            left: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>
 
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 20px;'>

<div class='legend-title'> Difference </div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:#ff0000;opacity:1;'></span> Method < Single peak' </li>
    <li><span style='background:#808080;opacity:1;'></span> Method = Single peak'/li>
    <li><span style='background:#008000;opacity:1;'></span> Method > Single peak' </li>
  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""


# mpl.colors.to_hex(matplotlib.cm.cool(0.3))
template_difference = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            left: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>
 
<div id='maplegend' class='maplegend' 
    style='position: fixed; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; left: 20px; bottom: 20px;'>

<div class='legend-title'> Difference </div>
<div class='legend-scale'>
  <ul class='legend-labels'>
     <li><span style='background:#482475;opacity:1;'></span><=0.3m' </li>
    <li><span style='background:#21918c;opacity:1;'></span>0.3-0.6m' </li>
    <li><span style='background:#44bf70;opacity:1;'></span>0.6-1.2m' </li>
    <li><span style='background:#bddf26;opacity:1;'></span>>1.2m' </li>
    </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""
