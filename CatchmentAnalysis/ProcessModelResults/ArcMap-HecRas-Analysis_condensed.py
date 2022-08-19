import arcpy
from arcpy.sa import *
import os
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = False

# Check geodatabase works which we are working inside, and if not then create it
if not os.path.exists(os.path.dirname(r"Z:\mygdb.gdb")):
    arcpy.CreateFileGDB_management(out_folder_path=r"Z:/", out_name="mygdb.gdb", out_version="CURRENT")

os.chdir(r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling")

# Define the names of the methods, and the shorthand versions of the names used in the folder naming conventions
method_names_dict =  {'singlepeak' : 'sp', 'dividetime' : 'dt', 'subpeaktiming' : 'sp-t', 'maxspread': 'ms'}

# define the arc map mapping document
mxd = arcpy.mapping.MapDocument(r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\Latest.mxd")

# Get list of dataframes
df = arcpy.mapping.ListDataFrames(mxd)[0]

# add layer to arcmap (works from within arcmap
df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
addLayer = arcpy.mapping.Layer("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/velocity_difference_singlepeak_{}.tif".format("singlepeak"))
arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
#arcpy.ApplySymbologyFromLayer_management(basis, yellow)

# Add catchment boundary
newlayer = arcpy.mapping.Layer(r"Z:\LinDykeCatchment.shp")
#  add the layer to the map at the bottom of the TOC in data frame 0
arcpy.mapping.AddLayer(df, newlayer, "TOP")
arcpy.RefreshActiveView()
mxd.save()

## Set extent 
lyr = arcpy.mapping.ListLayers(mxd, '', df)[1]
newExtent = lyr.getExtent()
df.extent = newExtent
#  Define manually as the coordinates above are too wide
newExtent.XMin, newExtent.YMin = 437400, 426445
newExtent.XMax, newExtent.YMax =  445508, 433918
df.extent = newExtent

mxd.save()
print("AboveSave")
project = "Z:/test5.jpg"
arcpy.mapping.ExportToJPEG(mxd, project, resolution = 200)
#arcpy.mapping.ExportToJPEG(mxd, project, "", "", "", resolution = 200)
print("Here")

## List the layers
##for lyr in arcpy.mapping.ListLayers(mxd):
##    if lyr.supports("DATASOURCE"):
##        print "Layer: " + lyr.name + "  Source: " + lyr.dataSource
##
## add layer to arcmap (works from within arcmap -- or adds a layer if the .mxd document is closed when you reopen)
##mxd = arcpy.mapping.MapDocument(r"MeganModel/ArcMap.mxd") or "CURRENT"
##df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
##addLayer = arcpy.mapping.Layer(r"C:\Users\gy17m2a\OneDrive - University of Leeds\PhD\DataAnalysis\FloodModelling\MeganModel\6hr_dt_u\6hr_dividetime_depth.Resampled.Terrain.tif")
##arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
##arcpy.ApplySymbologyFromLayer_management(basis, yellow)
##
##arcpy.RefreshActiveView()
##
##map_legend = arcpy.mapping.ListLayoutElements(mxd, 'LEGEND_ELEMENT', 'Map_L*')
##legend = map_legend[0]
##legend.elementPositionX = 0.5
##legend.elementPositionY = 1.33
##
##test="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/ArcPy/layer_symbology.lyr"
##addSym = arcpy.mapping.Layer(test)
##arcpy.mapping.AddLayer(df,addSym,"TOP")
##
## Find the new layer in the MXD
##newlayer = arcpy.mapping.ListLayers(mxd, addLayer.name)[0]
##
## Apply the symbology to the layer in the MXD
##arcpy.ApplySymbologyFromLayer_management(newlayer, addSym)
##
## Set extent 
##lyr = arcpy.mapping.ListLayers(mxd, '', df)[1]
##newExtent = lyr.getExtent()
##df.extent = newExtent
## Define manually as the coordinates above are too wide
##newExtent.XMin, newExtent.YMin = 437400, 426445
##newExtent.XMax, newExtent.YMax =  445508, 433918
##df.extent = newExtent
##
##arcpy.mapping.ExportToPDF(mxd, 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/ArcPy/test2.pdf')
