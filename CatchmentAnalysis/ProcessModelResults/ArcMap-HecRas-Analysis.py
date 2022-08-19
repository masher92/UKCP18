import arcpy
from arcpy import env
from arcpy.sa import *

x=1
x
arcpy.env.workspace = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel.gdb"
arcpy.env.scratchWorkspace = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel.gdb"
raster_list = arcpy.ListRasters("*")
print (raster_list)

arcpy.env.scratchWorkspace = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\6hr_dt_u.gdb"
raster_list = arcpy.ListRasters("*")
print (raster_list)

arcpy.env.workspace = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\6hr_dt_u.gdb"
raster_list = arcpy.ListRasters("*")
print (raster_list)

import arcpy
from arcpy.sa import *
f1 = arcpy.Raster("C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\6hr_dt_u\6hr_dividetime_depth.Resampled.Terrain.tif")

import arcpy
from arcpy.sa import *
f1 = arcpy.Raster("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_dt_u/6hr_dividetime_depth.Resampled.Terrain.tif")

f2 = arcpy.Raster("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/6hr_sp_u/6hr_singlepeak_depth.Resampled.Terrain.tif")
f1-2 = f1 - f2
f1-f2
x = 
x = f1-f2
# Set workspace
env.workspace = "C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\Data Analysis\FloodModelling\MeganModel"

x = f1-f2
# Set workspace
out_folder_path= "C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\Data Analysis\FloodModelling\MeganModel"

outname = "mygdb.gdb"
# Execute CreateFileGDB
arcpy.CreateFileGDB_management(out_folder_path, out_name)

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(out_folder_path, outname)

# Set workspace
out_folder_path= "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/Data Analysis/FloodModelling/MeganModel"

# Set workspace
out_folder_path= "C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel"

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(out_folder_path, outname)

x = f1-f2
# Set workspace
env.workspace ="C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\Data Analysis\FloodModelling\MeganModel\mygdb.gdb"

arcpy.env.workspace = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\Data Analysis\FloodModelling\MeganModel\mygdb.gdb"
arcpy.env.scratchWorkspace = r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\Data Analysis\FloodModelling\MeganModel\mygdb.gdb"
x = f1-f2
as
arcpy.env.workspace = r"C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/Data Analysis/FloodModelling/MeganModel/mygdb.gdb"
x = f1-f2
# Set workspace
env.workspace ="C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\Data Analysis\FloodModelling\MeganModel\mygdb.gdb"


# Set workspace
out_folder_path= "C:\Users\gy17m2a\"

# Set workspace
out_folder_path= "C:\Users\gy17m2a"

# Execute CreateFileGDB
arcpy.CreateFileGDB_management(out_folder_path, outname)

# Set workspace
env.workspace ="C:\Users\gy17m2a\mygdb.gdb"

x = f1-f2
# Set workspace
env.scratchWorkspace ="C:\Users\gy17m2a\mygdb.gdb"

x = f1-f2
x
y = f1-f2
arcpy.CreateFileGDB_management(out_folder_path="C:/Users/gy17m2a", out_name="mygdb.gdb", out_version="CURRENT")
f1
f2
z = f2-f1

