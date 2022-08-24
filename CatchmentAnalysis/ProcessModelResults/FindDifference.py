import arcpy
from arcpy.sa import *
import os
from arcpy import env
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True

# Check geodatabase works which we are working inside, and if not then create it
if not os.path.exists(os.path.dirname("C:/Users/gy17m2a/mygdb.gdb")):
    arcpy.CreateFileGDB_management(out_folder_path="C:/Users/gy17m2a", out_name="mygdb.gdb", out_version="CURRENT")

# Set scratch workspace
arcpy.env.scratchWorkspace = "C:/Users/gy17m2a/mygdb.gdb"
# Set working directory
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/")

### Define the names of the methods, and the shorthand versions of the names used in the folder naming conventions
method_names_dict =  {'singlepeak' : 'sp', 'dividetime' : 'dt', 'subpeaktiming' : 'sp-t', 'maxspread': 'ms'}

# Create dictionaries to store the rasters for both depth and velocity
depth_rasters_dict = {}
velocity_rasters_dict = {}

# Populate the dictionaries with the depth/velocity rasters
# Filter out values which have a depth of <0.1m
for key, value in method_names_dict.items():
    depth_raster = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_depth.Resampled.Terrain.tif".format(value, key))
    depth_rasters_dict[key] = SetNull(depth_raster<0.1, depth_raster)
    velocity_raster = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_velocity.Resampled.Terrain.tif".format(value, key))
    velocity_rasters_dict[key]  =   SetNull(depth_raster<0.1 , velocity_raster)

# Populate the dictionaries with the depth/velocity rasters
# Filter out values which have a depth of <0.1m
for key, value in method_names_dict.items():
    depth_rasters_dict[key]  = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_depth.Resampled.Terrain.tif".format(value, key))
    velocity_rasters_dict[key]  = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_velocity.Resampled.Terrain.tif".format(value, key))

# Find the difference between each raster and the singlepeak version,
# and create a reclassified version showing just whether the value is positive or negative
for raster_name in depth_rasters_dict:
    # Finding difference with single peak so don't want to include this
    if raster_name != 'singlepeak':
        print(raster_name)
        # Find difference between depth raster from this method, and the single peak method
        depth_difference_raster = depth_rasters_dict['singlepeak'] - depth_rasters_dict[raster_name]
        depth_difference_raster.save("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/depth_difference_singlepeak_{}.tif".format(raster_name))
        # Reclassify to 1/2 for negative/positive values
        arcpy.gp.Reclassify_sa(depth_difference_raster, "VALUE", "-100000 0 1;0 100000 2", "Arcpy/depth_difference_singlepeak_{}_reclassified.tif".format(raster_name))
        # Find difference between velocity raster from this method, and the single peak method
        velocity_difference_raster = velocity_rasters_dict['singlepeak'] - velocity_rasters_dict[raster_name]
        velocity_difference_raster.save("Arcpy/velocity_difference_singlepeak_{}.tif".format(raster_name))
        # Reclassify to 1/2 for negative/positive values
        arcpy.gp.Reclassify_sa(velocity_difference_raster, "VALUE", "-1000000 0 1;0 100000 2", "Arcpy/velocity_difference_singlepeak_{}_reclassified.tif".format(raster_name)) 

