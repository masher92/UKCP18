import rasterio
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

def save_array_as_raster(raster, fp_to_save, out_meta):
    src = rasterio.open("MeganModel/6hr_dt_u/6hr_dividetime_velocity.Resampled.Terrain.tif")
#     # Save the clipped raster to disk with following command.
#     with rasterio.open(
#             fp_to_save, 'w', driver='GTiff', height=raster.shape[0], width=raster.shape[1],
#                             count=1, dtype=raster.dtype,crs=src.crs, nodata=np.nan, transform=src.transform) as dest_file:
#         dest_file.write(raster,1)
#     dest_file.close()     
    
    with rasterio.open(
            fp_to_save, "w", **out_meta) as dest_file:
        dest_file.write(raster,1)
    dest_file.close()    
    

# Opensa raster, trims it to extent of catchment, saves a trimmed version
# and returns an arrat contianing the data, also trimmed
def open_and_clip(input_raster_fp, output_raster_fp):

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
    
    # Modify the metadata. Let’s start by copying the metadata from the original data file.
    out_meta = data.meta.copy()
    # Parse the EPSG value from the CRS so that we can create a Proj4 string using PyCRS library 
    # (to ensure that the projection information is saved correctly) [this bit didn't work so specified manually]
    epsg_code = int(data.crs.data['init'][5:])
    # Now we need to update the metadata with new dimensions, transform (affine) and CRS (as Proj4 text)
    out_meta.update({"driver": "GTiff","height": clipped_array.shape[1],"width": clipped_array.shape[2], 
                     "transform": out_transform, "crs": CRS('EPSG:27700')})#pycrs.parser.from_epsg_code(epsg_code).to_proj4()})

    # Save the clipped raster to disk with following command.
    with rasterio.open(
            output_raster_fp, "w", **out_meta
    ) as dest_file:
        dest_file.write(clipped_array)
    dest_file.close()
    
    return clipped_array[0,:,:], out_meta

def plot(input_raster_fp, output_png_fp, variable_name, cmap):
    
    # Specify catchment area to add to plot
    my_shp = "MeganModel/CatchmentLinDyke_exported.shp"
    gdf = gpd.read_file(my_shp)

    # plot the new clipped raster      
    clipped = rasterio.open(input_raster_fp)
    
    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    ax = mpl.pyplot.gca()
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap)
    gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
       
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
    plt.savefig(output_png_fp, dpi=500,bbox_inches='tight')
    plt.close()
    # os.remove(out_tif)  
    
def plot_classified_velocity(input_raster_fp, output_png_fp, labels_velocity, norm = None):
    
    # Specify catchment area to add to plot
    my_shp = "MeganModel/CatchmentLinDyke_exported.shp"
    gdf = gpd.read_file(my_shp)

    # Create discrete cmap
    colors_list = [mpl.cm.cool(0.3), mpl.cm.cool(0.5), mpl.cm.cool(0.7), mpl.cm.cool(0.9)]
    cmap = mpl.colors.ListedColormap(colors_list)
    cmap.set_over('red')
    cmap.set_under('green')

    # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels_velocity[i])
        patches_list.append(patch)  
    
    # plot the new clipped raster      
    clipped = rasterio.open(input_raster_fp)
    
    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    ax = mpl.pyplot.gca()
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)
    gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
       
    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()
    
    plt.axis('off')
    
    plt.legend(handles=patches_list, handleheight=3, handlelength=4, fontsize =25)
    # Save the figure
    plt.savefig(output_png_fp, dpi=500,bbox_inches='tight')
    plt.close()


def plot_classified_depth(input_raster_fp, output_png_fp, labels_depth, norm = None):
    
    # Specify catchment area to add to plot
    my_shp = "MeganModel/CatchmentLinDyke_exported.shp"
    gdf = gpd.read_file(my_shp)

    # Create discrete cmap
    colors_list = [mpl.cm.Blues(0.2), mpl.cm.Blues(0.5), mpl.cm.Blues(0.7),"navy"]
    #colors_list = ['turquoise','teal', 'blue', 'navy']
    cmap = mpl.colors.ListedColormap(colors_list)
    cmap.set_over('red')
    cmap.set_under('green')

    # Create patches for legend
    patches_list = []
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels_depth[i])
        patches_list.append(patch)  
    
    # plot the new clipped raster      
    clipped = rasterio.open(input_raster_fp)
    
    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    ax = mpl.pyplot.gca()
    ax.tick_params(axis='both', which='major', labelsize=20)
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap, norm = norm)
    gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)
       
    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()
    
    plt.axis('off')
    
    plt.legend(handles=patches_list, handleheight=3, handlelength=4, fontsize =25)
    # Save the figure
    plt.savefig(output_png_fp, dpi=500,bbox_inches='tight')
    plt.close()
    
def plot_difference_levels (input_raster_fp, output_png_fp):

    # Specify catchment area to add to plot
    my_shp = "MeganModel/CatchmentLinDyke_exported.shp"
    gdf = gpd.read_file(my_shp)

    # Create discrete cmap
    colors_list = [mpl.cm.viridis(0.1), mpl.cm.viridis(0.5), mpl.cm.viridis(0.7), mpl.cm.viridis(0.9)]
    cmap = mpl.colors.ListedColormap(colors_list)
    cmap.set_over('red')
    cmap.set_under('green')

    # Create patches for legend
    patches_list = []
    labels= ['<-0.1', '-0.1-0.1', '0.1-0.3', '0.3+']
    for i, color in  enumerate(colors_list):
        patch =  mpatches.Patch(color=color, label=labels[i])
        patches_list.append(patch)  

    # plot the new clipped raster      
    clipped = rasterio.open("Arcpy/classified_depth_singlepeak_{}_diff.tif".format(key))

    # Set up plot instance
    fig, ax = plt.subplots(figsize=(20, 15))
    ax = mpl.pyplot.gca()
    rasterio.plot.show((clipped, 1), ax= ax, cmap = cmap)
    gdf.plot(ax=ax, facecolor = 'None', edgecolor = 'black', linewidth = 4)

    # Close file (otherwise can't delete it, as ref to it is open)
    clipped.close()

    plt.axis('off')

    plt.legend(handles=patches_list, handleheight=4, handlelength=5, fontsize =30)
    
    # Save the figure
    plt.savefig(output_png_fp, dpi=500,bbox_inches='tight')
    plt.close()    