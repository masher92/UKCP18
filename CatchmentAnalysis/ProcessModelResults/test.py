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

# define the arc map mapping document
mxd = arcpy.mapping.MapDocument(r"MeganModel/ArcMap.mxd")

# Get list of dataframes
df = arcpy.mapping.ListDataFrames(mxd)[0]

# Add the raster layer to the map
result = arcpy.MakeRasterLayer_management("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/velocity_difference_singlepeak_{}.tif".format("dividetime"), "singlepeak")
layer = result.getOutput(0)
arcpy.mapping.AddLayer(df, layer, 'TOP')


arcpy.mapping.ExportToPNG(mxd, "BuffaloNY.png", resolution=50)
print("test")
