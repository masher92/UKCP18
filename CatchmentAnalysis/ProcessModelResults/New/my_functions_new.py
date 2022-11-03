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
import fiona
import rasterio.plot
import matplotlib as mpl
from rasterio.plot import show
from rasterio.plot import show_hist
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
from fiona.crs import from_epsg
import pycrs
from pyproj import CRS
import matplotlib.patches as mpatches
import contextily as cx
from branca.element import Template, MacroElement
import folium
from folium import Map, FeatureGroup, LayerControl
import numpy.ma as ma
from pathlib import Path

# Define whether to filter out values <0.1
remove_little_values = True

# Specify catchment area to add to plot
os.chdir("../../../../FloodModelling")
catchment_shp = "MeganModel/CatchmentLinDyke_exported.shp"
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
        counts_df[fp.split('/')[1]] = groups['counts']
        proportions_df[fp.split('/')[1]] = groups['Proportion']

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
    
    # Set -9999 to NA
    clipped_array[clipped_array < -9998] = np.nan
    
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
    if 'depth' not in input_raster_fp:
        depth_raster = open_and_clip(input_raster_fp.replace('depth', 'velocity'))[0]

    # Set cell values to Null in cells which have a value <0.1 in the depth raster
    if remove_little_values == True:
        if "depth" in input_raster_fp:
            raster[raster < 0.1] = np.nan
        else:
            raster[depth_raster < 0.1] = np.nan
    
    return raster, out_meta

def classify_raster (raster, breaks):
    
    # Classify using the specified breaks
    classified_raster = np.digitize(raster,breaks, right = False)
    # Set values which are classified as category 5 to np.nan
    classified_raster = np.where(classified_raster == len(breaks), np.nan, classified_raster)
    
    return classified_raster

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
    figs_dir = fp_for_classified_raster.split('/', 3)[0] + '/Figs/' + fp_for_classified_raster.split('/', 3)[1] +'/'
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + fp_for_classified_raster.split('/')[2].replace(".tif", ".png")

    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    
    plt.close()    
    
def find_worst_case_method(variable_name):
    # Read in the datasets
    singlepeak = prepare_rainfall_scenario_raster(sp_fp.format(variable_name), remove_little_values)[0].flatten()
    dividetime = prepare_rainfall_scenario_raster(fps[2].format(variable_name), remove_little_values)[0].flatten()
    subpeaktiming =prepare_rainfall_scenario_raster(fps[1].format(variable_name), remove_little_values)[0].flatten()
    maxspread = prepare_rainfall_scenario_raster(fps[0].format(variable_name), remove_little_values)[0].flatten()

    # Create a list to store the index for each cell of the scenario that produced the maximum value
    rainfall_scenario_max_producing_numbers = []
    # Assign a number for each of the scenarios (0:singlepeak, 1:dividetime, 2:subpeaktiming, 3:maxspread)
    rainfall_scenario_numbers = [0,1,2,3]
    # Loop through each cell in the array:
    ls = []
    for i, x in enumerate(zip(singlepeak,dividetime, subpeaktiming,maxspread)):
        print(i)
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
                rainfall_scenario_max_producing_numbers.append(index_of_max)
            # If matches is not empty (i.e. there are values matching the maximum) then return 4 (no one 
            # scenario can be deemed the worst case)
            elif matches:
                rainfall_scenario_max_producing_numbers.append(4)      
    
    # Find the number of counts of each value
    unique, counts = np.unique(rainfall_scenario_max_producing_numbers, return_counts=True)
    worst_case_method_df = pd.DataFrame({'values': unique, 'counts':counts})
    
    # Store in a dictionary
    return worst_case_method_df   

def plot_difference(variable_name, rainfall_scenario_name, cmap, norm = None):
    
    # plot the new clipped raster      
    clipped = rasterio.open("Arcpy/{}_singlepeak_{}_diff.tif".format(variable_name, rainfall_scenario_name))
    
    fig, ax = plt.subplots(figsize=(20, 15))
    catchment_gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
    cx.add_basemap(ax, crs = gdf.crs.to_string(), url = cx.providers.OpenStreetMap.Mapnik)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)
       
    # use imshow so that we have something to map the colorbar to
    raster = clipped.read(1)
    image_hidden = ax.imshow(raster, cmap=cmap)

    # plot on the same axis with rio.plot.show
    show((clipped, 1),  ax=ax, cmap=cmap) 
    
    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()
    
    # # add colorbar using the now hidden image
    cbar = fig.colorbar(image_hidden, ax=ax, fraction=0.03, pad=0.04)
    cbar.set_label(variable_name, fontsize=16)
    cbar.ax.tick_params(labelsize=15)
    
    # Save the figure
    plt.savefig("Arcpy/Figs/{}_singlepeak_{}_diff.png".format(variable_name, rainfall_scenario_name), dpi=500,bbox_inches='tight')
    plt.close()
    
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
    figs_dir = fp_for_classified_diff_raster.split('/', 3)[0] + '/Figs/' + fp_for_classified_diff_raster.split('/', 3)[1] +'/'
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + fp_for_classified_diff_raster.split('/')[2].replace(".tif", ".png")
    
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
    figs_dir = fp_for_posneg_diff_raster.split('/', 3)[0] + '/Figs/' + fp_for_posneg_diff_raster.split('/', 3)[1] +'/'
    Path(figs_dir).mkdir(parents=True, exist_ok=True)
    plot_fp = figs_dir + fp_for_posneg_diff_raster.split('/')[2].replace(".tif", ".png")
    
    # Save the figure
    plt.savefig(plot_fp, dpi=500,bbox_inches='tight')
    plt.close()  
    
def plot_worst_case_bars (ax, worst_case_method_df):
    # Remove the np.nan values
    worst_case_method_df = worst_case_method_df.iloc[:5,1]
    # Set scenario names as index
    worst_case_method_df.index = ["singlepeak", "dividetime", "subpeaktiming", "maxspread", "no maximum"]
    # Plot
    worst_case_method_df.plot(ax= ax, kind ='bar',width=  0.9, rot =45, ylabel = 'Number of cells')  
    
def make_totals_bar_plot (ax, totals_df, y_name):
    y_pos = np.arange(len(totals_df.columns))
    ax.bar( y_pos, totals_df.iloc[[0]].values.tolist()[0], color=colors,
            width = 0.9)
    # Create names on the x-axis
    ax.set_xticks(y_pos, rainfall_scenario_names.keys(), fontsize =15, rotation = 45)
    ax.set_ylabel(y_name, fontsize =20)

    xlocs, xlabs = plt.xticks()
    xlocs=[i+1 for i in range(0,10)]
    xlabs=[i/2 for i in range(0,10)]

    for i, v in enumerate(totals_df.iloc[[0]].values.tolist()[0]):
        ax.text(xlocs[i] - 1.12, v * 1.015, str(ls[i]), fontsize = 20)
    
def make_bar_plot_by_category (ax, df_to_plot, variable, variable_unit, ylabel):
           
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
