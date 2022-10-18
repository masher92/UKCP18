'''
This file reads in ASC files which contain topographic data for small areas.
It reads them in and merges them to produce one topographic file for a large Northern region.
This file is then masked to contain only grid cells in either the Northern region
area or the Leeds-at-centre area.
This is thenn plotted and saved to file
'''

import os
import matplotlib.pyplot as plt    
from rasterio import plot as rioplot
import rasterio
import glob, os
from rasterio.merge import merge
from rasterio.plot import show
import sys
#import earthpy.plot as ep
from rasterio.mask import mask

############################################
# Define variables and set up environment
#############################################
#os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/SpatialData/terrain-50-dtm_3566580/")
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/SpatialData/terrain-50-dtm_3613329/")
    
# Change wd
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:27700'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:27700'})

##################################################################
# Load ASC files containing topographic information for small
# areas within the big area required
# Only create if it doesn't already exist
##################################################################
# Define name of file if it exists
out_fp = "datadir/SpatialData/Northern_raster.asc"

# If it doesn't exist, then create
if not os.path.isfile(out_fp):
    # Find filenames of all the asc files
    # This involves going into all of the subdirectories #3613329
    filenames = []
    for file in glob.glob("datadir/SpatialData/terrain-50-dtm_3613329/*/*.asc", recursive = True):
        file = file.replace('\\','/')
        filenames.append(file)
    
    # Create list to store files to merge
    src_files_to_mosaic = []  
    for fp in filenames:
        src = rasterio.open(fp)
        src_files_to_mosaic.append(src)    
        
    # Merge the files into one
    mosaic, out_trans = merge(src_files_to_mosaic)    
    # Check plotting
    show(mosaic, cmap='terrain')   
    # Save an example of one of the original file's transformation structure
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                         "height": mosaic.shape[1],
                         "width": mosaic.shape[2],
                         "transform": out_trans,
                         "crs": {'init' :'epsg:27700'}
                         }
                        )
    # Save the merged file with these properties
    with rasterio.open(out_fp, "w", **out_meta) as dest:
               dest.write(mosaic)
    
###################################################
# Clip to boundary of regional areas
###################################################
## Extract features of geodataframe in the format required by rasterio
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]               


# Reimport file
DSM = rasterio.open(out_fp)
          
regions =  ['leeds-at-centre', 'Northern']
for region in regions:
    if region == 'leeds-at-centre':
        regional_gdf = leeds_at_centre_gdf
        # Filename to save output to
        filename =  "Outputs/Topography/leeds-at-centre.png"
    elif region == 'Northern':
        regional_gdf = northern_gdf
        # Filename to save output to
        filename =  "Outputs/Topography/Northern.png"
    
    ## Extract features of geodataframe in the format required by rasterio
    regional_area_coords = getFeatures(regional_gdf)
    
    # Mask the topographic file withe regional_area_coords
    # This ensures that only grid cells within the region are plotted
    masked, mask_transform = mask(dataset=DSM,shapes=regional_area_coords,crop=True, all_touched = True, filled = False)
    # Check plotting
    show(masked, transform=mask_transform)
    
    ###################################################
    # Plot
    ###################################################    
    ### Plot
    fig, ax = plt.subplots(figsize=(13, 14))
    plot = show(masked, transform=mask_transform, ax=ax,cmap='terrain')
    if region == 'leeds-at-centre':
        leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4) ## alpha is the transparency setting
    elif region == 'Northern':
        leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4) ## alpha is the transparency setting
        northern_gdf.plot(ax=ax, facecolor='none', linewidth = 4, edgecolor='black') ## alpha is the transparency setting
    plt.axis('off')
    
    # Save the figure to file
    fig.savefig(filename,bbox_inches='tight')



