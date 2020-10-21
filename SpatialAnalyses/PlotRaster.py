import os
import matplotlib.pyplot as plt    
from rasterio import plot as rioplot
import rasterio
import glob, os
from rasterio.merge import merge
from rasterio.plot import show
import sys
import earthpy.plot as ep


# Find filenames of all the asc files
#os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/SpatialData/terrain-50-dtm_3566580/")
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/SpatialData/terrain-50-dtm_3566671/")
filenames = []
for file in glob.glob("**/*.asc", recursive = True):
    file = file.replace('\\','/')
    filenames.append("datadir/SpatialData/terrain-50-dtm_3566671/" + file)
    
# Change wd
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})
wy_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
wy_gdf = wy_gdf.to_crs({'init' :'epsg:27700'}) 

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
out_fp2 = "datadir/SpatialData/WY_raster2.asc"
# with rasterio.open(out_fp, "w", **out_meta) as dest:
#           dest.write(mosaic)
    
# Reimport
DSM = rasterio.open(out_fp2)

import rasterio as rio
fig, ax = plt.subplots(figsize=(15, 15))
rio.plot.show(DSM, ax=ax, cmap='terrain')
wy_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4);
leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 4);    

################### Other method
with rio.open("datadir/SpatialData/WY_raster2.asc") as src:
    # Convert / read the data into a numpy array:
    lidar_dem_im = src.read()
    # Create a spatial extent object using rio.plot.plotting
    spatial_extent = rio.plot.plotting_extent(src)
    # Get bounds of object
    bounds = src.bounds
    
print("spatial extent:", spatial_extent)
# This is the format that rasterio provides with the bounds attribute
print("rasterio bounds:", bounds)

with rio.open("datadir/SpatialData/WY_raster2.asc") as src:
    # Convert / read the data into a numpy array
    # masked = True turns `nodata` values to nan
    lidar_dem_im = src.read(1, masked=True)
    
    # Create a spatial extent object using rio.plot.plotting
    spatial_extent = rio.plot.plotting_extent(src)

print("object shape:", lidar_dem_im.shape)
print("object type:", type(lidar_dem_im))


with rio.open("datadir/SpatialData/WY_raster2.asc") as src:
    
    # Convert / read the data into a numpy array:
    lidar_dem_im2 = src.read(1)

with rio.open("datadir/SpatialData/WY_raster2.asc") as src:
    
    # Convert / read the data into a numpy array:
    lidar_dem_im3 = src.read()

print("Array Shape Using read(1):", lidar_dem_im2.shape)

# Notice that without the (1), your numpy array has a third dimension
print("Array Shape Using read():", lidar_dem_im3.shape)



fig, ax = plt.subplots(figsize=(12, 10))
ep.plot_bands(lidar_dem_im,
              cmap='terrain_r',
              #extent=spatial_extent,
              extent = (384411.0,458800.0 , 399892.0, 456892.0),
              scale=False,
              ax=ax)
#ax.set_title("Lidar Digital Elevation Model \n Pre 2013 Boulder Flood | Lee Hill Road", 
#             fontsize=24)
wy_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 3);
leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='red', linewidth = 3);  
#ax.plot(lcc_lon, lcc_lat, "bo", markersize =10)
plt.show()



polygon_wm = polygon_wm.to_crs({'init' :'epsg:27700'}) 
fig, ax = plt.subplots(figsize=(12, 10))
ep.plot_bands(lidar_dem_im,
              cmap='terrain_r',
              #extent=spatial_extent,
              extent = (412342.104,449124.745178642  , 421129.001, 421368.8352653855),
              scale=False,
              ax=ax)
#ax.set_title("Lidar Digital Elevation Model \n Pre 2013 Boulder Flood | Lee Hill Road", 
#             fontsize=24)
#wy_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 3);
ax.plot(lcc_lon, lcc_lat, "bo", markersize =10)
leeds_gdf.plot(ax=ax, facecolor='none', edgecolor='black', linewidth = 3);  
plt.show()


lcc_lon = -1.548567
lcc_lat = 	53.801277

