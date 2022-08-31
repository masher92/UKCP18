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
mxd = arcpy.mapping.MapDocument(r"MeganModel/Latest.mxd")

# Get list of dataframes
df = arcpy.mapping.ListDataFrames(mxd)[0]

###################################################################################
###################################################################################
# Add catchment boundary layer
###################################################################################
###################################################################################
# Define the boundary of the catchment, and the symbology layer to use for it (no fill and black background)
catchment_bounday_layer = arcpy.mapping.Layer("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/Lin Dyke Catchment.shp")
catchment_boundary_symbology_lyr = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/ArcPy/catchment_symbology.lyr"
# Add the layer to the map at the bottom and apply symbology
arcpy.mapping.AddLayer(df, catchment_bounday_layer,"BOTTOM")
arcpy.ApplySymbologyFromLayer_management(catchment_bounday_layer, catchment_boundary_symbology_lyr)

###################################################################################
###################################################################################
# Add the raster layer to the map
###################################################################################
###################################################################################
result = arcpy.MakeRasterLayer_management("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/velocity_difference_singlepeak_{}.tif".format("dividetime"), "singlepeak")
layer = result.getOutput(0)
arcpy.mapping.AddLayer(df, layer, 'AUTO_ARRANGE')
mxd.save()

###################################################################################
###################################################################################
# Set map extent based on the catchment boundary layer
###################################################################################
###################################################################################
# Get the catchment boundary layer and extract it's extent
lyr = arcpy.mapping.ListLayers(mxd, 'LinDykeCatchment', df)[1]
newExtent = lyr.getExtent()
# Set this extent on the dataframe (not sure what the dataframe means in this context)
df.extent = newExtent
# Refresh the map and save
arcpy.RefreshActiveView()
mxd.save()

###################################################################################
###################################################################################
# Legend + things
###################################################################################
###################################################################################
##map_legend = arcpy.mapping.ListLayoutElements(mxd, 'LEGEND_ELEMENT', 'Map_L*')
##legend.autoAdd = True
##legend = map_legend[0]
##legend.elementPositionX = 0.5
##legend.elementPositionY = 1.33

legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT", 'Map_L*')[0]
#add new items to legend
legend.autoAdd = True

###################################################################################
###################################################################################
# Export to JPEG
###################################################################################
###################################################################################
arcpy.mapping.ExportToJPEG(mxd, 'Z:/test.jpg', resolution = 100)


##
### add layer to arcmap (works from within arcmap
##df = arcpy.mapping.ListDataFrames(mxd, "Layers")[0]
##addLayer = arcpy.mapping.Layer("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/Arcpy/velocity_difference_singlepeak_{}.tif".format("singlepeak"))
##arcpy.mapping.AddLayer(df, addLayer, "BOTTOM")
###arcpy.ApplySymbologyFromLayer_management(basis, yellow)
##

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

