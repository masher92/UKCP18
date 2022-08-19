import arcpy
from arcpy.sa import *
import os
arcpy.CheckOutExtension("spatial")
arcpy.env.overwriteOutput = True

# Check geodatabase works which we are working inside, and if not then create it
if not os.path.exists(os.path.dirname("C:/Users/gy17m2a/mygdb.gdb")):
    arcpy.CreateFileGDB_management(out_folder_path="C:/Users/gy17m2a", out_name="mygdb.gdb", out_version="CURRENT")

os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/")

# Define the names of the methods, and the shorthand versions of the names used in the folder naming conventions
method_names_dict =  {'singlepeak' : 'sp', 'dividetime' : 'dt', 'subpeaktiming' : 'sp-t', 'maxspread': 'ms'}

# Convert Hec-Ras outputs from .vrt to TIFF
for key, value in method_names_dict.items():
    listOfVRT = ["MeganModel/6hr_{}_u/6hr_{}_depth.vrt".format(value,key)]
    print(listOfVRT)
    arcpy.RasterToOtherFormat_conversion(listOfVRT , "MeganModel/6hr_{}_u/".format(value) ,"TIFF") 
    print(key)
