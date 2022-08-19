import arcpy
from arcpy.sa import *
import os
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = False

# Check geodatabase works which we are working inside, and if not then create it
if not os.path.exists(os.path.dirname(r"Z:\mygdb.gdb")):
    arcpy.CreateFileGDB_management(out_folder_path=r"Z:/", out_name="mygdb.gdb", out_version="CURRENT")

#os.chdir(r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling")

# Define the names of the methods, and the shorthand versions of the names used in the folder naming conventions
method_names_dict =  {'singlepeak' : 'sp', 'dividetime' : 'dt', 'subpeaktiming' : 'sp-t', 'maxspread': 'ms'}

# define the arc map mapping document
mxd = arcpy.mapping.MapDocument(r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\ArcMap.mxd")

# Get list of dataframes
df = arcpy.mapping.ListDataFrames(mxd)[0]

# add layer to arcmap (works from within arcmap
##df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
##print(df)
##addLayer = arcpy.mapping.Layer("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/velocity_difference_singlepeak_{}.tif".format("singlepeak"))
##arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
###arcpy.ApplySymbologyFromLayer_management(basis, yellow)

# Add catchment boundary
#newlayer = arcpy.mapping.Layer(r"Z:\LinDykeCatchment.shp")
# add the layer to the map at the bottom of the TOC in data frame 0
#arcpy.mapping.AddLayer(df, newlayer, "TOP")
#arcpy.RefreshActiveView()
#mxd.save()

#### Set extent 
##lyr = arcpy.mapping.ListLayers(mxd, '', df)[1]
##newExtent = lyr.getExtent()
##df.extent = newExtent
### Define manually as the coordinates above are too wide
##newExtent.XMin, newExtent.YMin = 437400, 426445
##newExtent.XMax, newExtent.YMax =  445508, 433918
##df.extent = newExtent

print("AboveSave")
project = "N:/test5.jpg"
arcpy.mapping.ExportToJPEG(mxd, project, resolution = 200)
#arcpy.mapping.ExportToJPEG(mxd, project, "", "", "", resolution = 200)
print("Here")
