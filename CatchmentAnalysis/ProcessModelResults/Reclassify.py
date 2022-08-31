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

# Define the RemapValue Object 
myRemapRange = RemapRange([[0.1, 0.15, 1], [0.15, 0.3, 2], [0.3, 0.6, 3],
                            [0.6, 0.9, 4], [0.9, 1.2, 5], [1.2, 100, 6]])

# Execute Reclassify
#outReclassRR = Reclassify(inRaster, "VALUE", myRemapRange)

# Populate the dictionaries with the depth/velocity rasters
# Filter out values which have a depth of <0.1m
for key, value in method_names_dict.items():
    depth_raster = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_depth.Resampled.Terrain.tif".format(value, key))
    depth_raster = SetNull(depth_raster<0.1, depth_raster)
    #depth_raster =  Reclassify(depth_raster, "VALUE", myRemapRange)
    #depth_raster.save("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/depth_cats_{}.tif".format(raster_name))
    arcpy.gp.Reclassify_sa(depth_raster, "VALUE", myRemapRange, "Arcpy/depth_categories_{}.tif".format(key))
##    depth_rasters_dict[key] = depth_raster
    #velocity_raster = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_velocity.Resampled.Terrain.tif".format(value, key))
    #velocity_rasters_dict[key]  =   SetNull(depth_raster<0.1 , velocity_raster)

### Find the difference between each raster and the singlepeak version,
### and create a reclassified version showing just whether the value is positive or negative
##for raster_name in depth_rasters_dict:
##    # Finding difference with single peak so don't want to include this
##    print(raster_name)
##    # Find difference between depth raster from this method, and the single peak method
##    depth_rasters_dict[raster_name].save("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/depth_cats_{}.tif".format(raster_name))
##
### Replace a layer/table view name with a path to a dataset (which can be a layer file) or create the layer/table view within the script
### The following inputs are layers or table views: "6hr_dividetime_depth.tif"
##raster_input =   arcpy.Raster("MeganModel/6hr_dt_u/6hr_dividetime_depth.Resampled.Terrain.tif")
##raster_output = Reclassify(raster_input, "VALUE", myRemapRange, "DATA")
##
##raster = arcpy.Raster("MeganModel/6hr_dt_u/6hr_dividetime_depth.Resampled.Terrain.tif")
##outreclass1 = Reclassify(raster, "VALUE", "0 0.500000 0;0.500000 1 1")
###format for Reclassify is the same as python snippet from Results of manua
##
##myRemapVal = RemapValue([[-3,9],[0,1],[3,-4],[4,5],[5,6],[6,4],[7,-7]])
### Execute Reclassify
##outReclassRV = Reclassify(raster, "VALUE", myRemapVal, "")
##
### Save the output 
##outReclassRV.save("C:/Users/")


