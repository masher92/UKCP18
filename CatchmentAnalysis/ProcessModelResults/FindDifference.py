import arcpy
from arcpy.sa import *
import os
from arcpy import env
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True

# Set working directory
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/")

# Check geodatabase works which we are working inside, and if not then create it
if not os.path.exists(os.path.dirname("ArcPy/mygdb.gdb")):
    arcpy.CreateFileGDB_management(out_folder_path="ArcPy", out_name="mygdb.gdb", out_version="CURRENT")


# Set scratch workspace
arcpy.env.scratchWorkspace = "Arcpy/ScratchWorkspace"


### Define the names of the methods, and the shorthand versions of the names used in the folder naming conventions
method_names_dict =  {'singlepeak' : 'sp', 'dividetime' : 'dt', 'subpeaktiming' : 'sp-t', 'maxspread': 'ms'}

# Define the RemapValue Object 
myRemapRange_depth = "0 0.1 0; 0.1 0.15 1;0.15 0.3 2; 0.3 0.6 3; 0.6 0.9 4; 0.9 1.2 5; 1.2 100 6"
myRemapRange_velocity = "0 0.25 1;0.25 0.5 2; 0.5 2 3; 2 100 4"

# Define whether to filter out values <0.1
remove_little_values = True

# Create dictionaries to store the rasters for both depth and velocity
depth_rasters_dict = {}
velocity_rasters_dict = {}

# Populate the dictionaries with the depth/velocity rasters
# Filter out values which have a depth of <0.1m
for key, value in method_names_dict.items():
    # Read in the raster files
    velocity_raster = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_velocity.Resampled.Terrain.tif".format(value, key))
    depth_raster = arcpy.Raster("MeganModel/6hr_{}_u/6hr_{}_depth.Resampled.Terrain.tif".format(value, key))
    # Set cell values to Null in cells which have a value <0.1 in the depth raster
    if remove_little_values == True:
            depth_raster = SetNull(depth_raster<0.1, depth_raster)
            velocity_raster = SetNull(depth_raster<0.1 , velocity_raster)
    # Save to dictionary 
    depth_rasters_dict[key] = depth_raster
    velocity_rasters_dict[key] = velocity_raster
  
### Find the difference between each raster and the singlepeak version,
### and create a reclassified version showing just whether the value is positive or negative
##for raster_name in depth_rasters_dict:
##    # Finding difference with single peak so don't want to include this
##    if raster_name != 'singlepeak':
##        print(raster_name)
##
##        ######################################################################################
##        ######################################################################################
##        # Reclassify depth/velocity rasters into categories from Megan report
##        ######################################################################################
##        ######################################################################################
##        # Depth
##        arcpy.gp.Reclassify_sa(depth_rasters_dict[raster_name], "VALUE", myRemapRange_depth, "Arcpy/depth_categories_{}.tif".format(raster_name))
##        # Velocity
##        arcpy.gp.Reclassify_sa(velocity_rasters_dict[raster_name], "VALUE", myRemapRange_velocity, "Arcpy/velocity_categories_{}.tif".format(raster_name))
##
##        ######################################################################################
##        ######################################################################################
##        # Find difference between depth/velocity rasters from this method, and the single peak method
##        ######################################################################################
##        ######################################################################################
##        # Depth
##        depth_difference_raster = depth_rasters_dict['singlepeak'] - depth_rasters_dict[raster_name]
##        depth_difference_raster.save("Arcpy/depth_difference_singlepeak_{}.tif".format(raster_name))
##        # Velocity
##        velocity_difference_raster = velocity_rasters_dict['singlepeak'] - velocity_rasters_dict[raster_name]
##        velocity_difference_raster.save("Arcpy/velocity_difference_singlepeak_{}.tif".format(raster_name))
##
##        ######################################################################################
##        ######################################################################################
##        # Reclassify the difference rasters to represent whether value is positive or negative 
##        ######################################################################################
##        ######################################################################################
##        # Depth
##        arcpy.gp.Reclassify_sa(depth_difference_raster, "VALUE", "-100000 0 1;0 100000 2", "Arcpy/depth_difference_singlepeak_{}_reclassified.tif".format(raster_name))
##        # Velocity
##        arcpy.gp.Reclassify_sa(velocity_difference_raster, "VALUE", "-1000000 0 1;0 100000 2", "Arcpy/velocity_difference_singlepeak_{}_reclassified.tif".format(raster_name)) 
##


######################################################################################
######################################################################################
# Find the worst depth and velocity value in each grid cell (across all 4 methods)
######################################################################################
######################################################################################         
##arcpy.gp.CellStatistics_sa(['C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp-t_u/6hr_subpeaktiming_depth.Resampled.Terrain.tif',
##                               'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_ms_u/6hr_maxspread_depth.Resampled.Terrain.tif',
##                               'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp_u/6hr_singlepeak_depth.Resampled.Terrain.tif',
##                               'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_dt_u/6hr_dividetime_depth.Resampled.Terrain.tif'],
##                               "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/ArcPy/depth_worstcase_values.tif", "MAXIMUM", "DATA")
##
##   
##arcpy.gp.CellStatistics_sa(['C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp-t_u/6hr_subpeaktiming_velocity.Resampled.Terrain.tif',
##                               'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_ms_u/6hr_maxspread_velocity.Resampled.Terrain.tif',
##                               'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp_u/6hr_singlepeak_velocity.Resampled.Terrain.tif',
##                               'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_dt_u/6hr_dividetime_velocity.Resampled.Terrain.tif'],
##                               "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/ArcPy/velocity_worstcase_values.tif", "MAXIMUM", "DATA")

######################################################################################
######################################################################################
# Find the method leading to the worst case depth/velocity
######################################################################################
######################################################################################
InRas1 =  arcpy.Raster('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_ms_u/6hr_maxspread_depth.Resampled.Terrain.tif')
InRas2 =  arcpy.Raster('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp-t_u/6hr_subpeaktiming_depth.Resampled.Terrain.tif')
InRas3 =  arcpy.Raster('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp_u/6hr_singlepeak_depth.Resampled.Terrain.tif')
InRas4 =  arcpy.Raster('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_dt_u/6hr_dividetime_depth.Resampled.Terrain.tif')
 

 
OutRas = Con(InRas1 > InRas2, 0, 1)
OutRas.save("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/ArcPy/depth_worstcase_method.tif")

print("End")



        
