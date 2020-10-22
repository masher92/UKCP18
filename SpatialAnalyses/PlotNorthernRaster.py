import os
import matplotlib.pyplot as plt    
from rasterio import plot as rioplot
import rasterio
import glob, os
from rasterio.merge import merge
from rasterio.plot import show
import sys
import earthpy.plot as ep
from rasterio.mask import mask

# Find filenames of all the asc files
#os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/SpatialData/terrain-50-dtm_3566580/")
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/SpatialData/terrain-50-dtm_3613329/")
filenames = []
for file in glob.glob("**/*.asc", recursive = True):
    file = file.replace('\\','/')
    filenames.append("datadir/SpatialData/terrain-50-dtm_3613329/" + file)
    
# Change wd
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outline of the coast of the UK
uk_gdf = create_uk_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
#uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  

# Create list to store files to merge
# Add al files to list
src_files_to_mosaic = []  
for fp in filenames:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)    
    
# merge them, save their transformations tructure?
mosaic, out_trans = merge(src_files_to_mosaic)    
show(mosaic, cmap='terrain')    
out_meta = src.meta.copy()
out_meta.update({"driver": "GTiff",
                     "height": mosaic.shape[1],
                     "width": mosaic.shape[2],
                     "transform": out_trans,
                     "crs": {'init' :'epsg:27700'}
                     }
                    )
# Save with the properties
out_fp = "datadir/SpatialData/Northern_raster.asc"
with rasterio.open(out_fp, "w", **out_meta) as dest:
           dest.write(mosaic)
    
###################################################
# Clip to boundary
###################################################
# Reimport
DSM = rasterio.open(out_fp)
#show(DSM.read(), transform=DSM.transform)

# Plot with the GDF
fig, ax = plt.subplots(figsize=(13, 14))
show(DSM,  ax=ax)
regional_gdf.plot(ax=ax, color='white', alpha=.75) ## alpha is the transparency setting
plt.show()

## Function to extract features in correct formt
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]
coords = getFeatures(regional_gdf)

# Mask the raster
masked, mask_transform = mask(dataset=DSM,shapes=coords,crop=True, all_touched = True, filled = False)
show(masked, transform=mask_transform)

### Plot
fig, ax = plt.subplots(figsize=(13, 14))
plot = show(masked, transform=mask_transform, ax=ax,cmap='terrain')
regional_gdf.plot(ax=ax, facecolor='none', linewidth = 4) ## alpha is the transparency setting
leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4) ## alpha is the transparency setting
plt.axis('off')

filename =  "Outputs/Topography/leeds-at-centre.png"
fig.savefig(filename,bbox_inches='tight')

# import rasterio as rio
# fig, ax = plt.subplots(figsize=(15, 15))
# plot = rio.plot.show(masked,  transform=mask_transform, ax=ax, cmap='terrain')
# plot = regional_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4);
# plot = leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='red', linewidth = 4);    
# cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
# cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 

    
###################################################
# Clip to boundary of Leeds at centre
###################################################
# Reimport
DSM = rasterio.open(out_fp)
#show(DSM.read(), transform=DSM.transform)

# Plot with the GDF
fig, ax = plt.subplots(figsize=(12, 10))
show(DSM,  ax=ax)
regional_gdf.plot(ax=ax, color='white', alpha=.75) ## alpha is the transparency setting
plt.show()

## Function to extract features in correct formt
def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json
    return [json.loads(gdf.to_json())['features'][0]['geometry']]
coords = getFeatures(regional_gdf)

# Mask the raster
masked, mask_transform = mask(dataset=DSM,shapes=coords,crop=True, all_touched = True, filled = False)
show(masked, transform=mask_transform)

### Plot
fig, ax = plt.subplots(figsize=(12, 10))
plot = show(masked, transform=mask_transform, ax=ax,cmap='terrain')
regional_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4) ## alpha is the transparency setting
leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4) ## alpha is the transparency setting


# import rasterio as rio
fig, ax = plt.subplots(figsize=(15, 15))
plot = show(masked,  transform=mask_transform, ax=ax, cmap='terrain')
plot = regional_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4);
plot = leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='red', linewidth = 4);    
cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 


