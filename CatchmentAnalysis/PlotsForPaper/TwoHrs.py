print("setting up environment")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import seaborn as sns
import geopandas as gpd
import contextily as cx
from PIL import Image
import time

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import sys
sys.path.append("../ProcessModelResults/")
from my_functions import *

from PlotsForPaper_Functions import *

def open_and_clip_to_catchment (input_fp, catchment_gdf, crop_or_not):
    # Get the results, and mask out values not within the geodataframe
    with rasterio.open(input_fp) as src:
        catchment_gdf=catchment_gdf.to_crs(src.crs)
        out_image, out_transform=mask(src,catchment_gdf.geometry,crop=crop_or_not)
        out_meta=src.meta.copy() # copy the metadata of the source DEM
        raster = out_image[0]
    return raster, out_meta   

####################################
# Variables
####################################
methods_key = sys.argv[1]
catchment_name = sys.argv[2]
model_directory = '/nfs/a319/gy17m2a/PhD/FloodModelling/{}Models/Model_{}Profiles_export/'.format(catchment_name, methods_key)
feh_directory = '/nfs/a319/gy17m2a/PhD/FloodModelling/{}Models/Model_FEHProfiles_export/'.format(catchment_name)

if catchment_name == 'LinDyke':
    garforth_gdf =  gpd.read_file(os.path.join(model_directory, '../SubCatchmentBoundaries/Garforth_manual.shp'))
    kippax_gdf = gpd.read_file(os.path.join(model_directory, '../SubCatchmentBoundaries/Kippax_manual2.shp'))
    cutting_off_wetlands_gdf =  gpd.read_file(os.path.join(model_directory, '../SubCatchmentBoundaries/ManualTrimAboveWetlands.shp'))
    
####################################
# Catchment properties
####################################
if catchment_name == 'LinDyke':
    catchment_name_str = "Resampled.Terrain" 
    catchment_shpfilename = 'CatchmentLinDyke_exported'
    minx, miny, maxx, maxy  = 437000,  426500,  445500, 434300
    catchment_gdf = gpd.read_file(model_directory + 'CatchmentLinDyke_exported.shp')
    filename_ending = "Resampled.Terrain"
    crop_or_not = True
    
elif catchment_name == 'WykeBeck':
    catchment_name_str = "Terrain.wykeDEM" 
    catchment_shpfilename = 'WykeBeckCatchment'
    minx, miny, maxx, maxy = 430004,  429978, 438660, 440996
    catchment_gdf = gpd.read_file(model_directory + 'WykeBeckCatchment.shp')
    filename_ending = "Terrain.wykeDEM"
    crop_or_not = False
    
# Create a bounding box (this is used in preparing the rasters)
bbox = box(minx, miny, maxx, maxy)

####################################
# Rainfall profile names
####################################
methods_dict = {'Idealised': ['6h_sp_fl_0.1', '6h_sp_fl_0.2', '6h_sp_fl_0.3', '6h_sp_fl_0.4','6h_sp_c_0.5',
          '6h_sp_bl_0.6','6h_sp_bl_0.7','6h_sp_bl_0.8','6h_sp_bl_0.9'],
                'Observed':['6h_feh_singlepeak', '6h_c1','6h_c2','6h_c3','6h_c4', '6h_c5', '6h_c6','6h_c7',
             '6h_c8','6h_c9','6h_c10', '6h_c11', '6h_c12','6h_c13','6h_c14','6h_c15'], 
               'SinglePeak_Scaled':['6h_sp_+0%','6h_sp_+5%','6h_sp_+10%','6h_sp_+15%','6h_sp_+20%']}

####################################
# Landcover data
####################################
landcover_directory = '../../../FloodModelling/{}Models/LandCoverData/'.format(catchment_name)
# Water landcover classification - 10 is water, 11 is eveyrthing else
with rasterio.open(landcover_directory + 'LandCover_notwater_classification.tif', 'r') as ds:
    landcover_notwater = ds.read()[0]
    out_meta = ds.meta

# Urban areas classification - 10 is urban, 11 is eveyrthing else
with rasterio.open(landcover_directory + 'LandCover_urban_and_suburban_classification.tif', 'r') as ds:
    landcover_urban = ds.read()[0]
    out_meta = ds.meta
        
    
####################################
# Run processing
####################################    
# Create dictionaries to store results for each method
n_flooded_cells_dict = {}
n_flooded_cells_dict_over10cm = {}
n_flooded_cells_dict_notwater = {}
n_flooded_cells_dict_urban = {}
if catchment_name == 'LinDyke':
    n_flooded_cells_dict_garforth = {}
    n_flooded_cells_dict_garforth_over10 = {}
    n_flooded_cells_dict_kippax = {}
    n_flooded_cells_dict_kippax_over10 = {}
    n_flooded_cells_dict_nowetlands = {}
    n_flooded_cells_dict_nowetlands_over10 = {}
    
# List of all the Hours and Minutes that we need
Hs=range(12,24)
Ms= range(0,60,10)

Hs_dict = {1:range(20,24,2), 2: range(0,24,2), 3: range(0,24,2), 4: range(0,12,2)}

# Loop through methods
for method in methods_dict[methods_key]:
    
    # Create lists to store the values for each timeslice for this method
    n_flooded_cells = []
    n_flooded_cells_over10cm = []
    n_flooded_cells_notwater = []
    n_flooded_cells_urban = []
    if catchment_name == 'LinDyke':
        n_flooded_cells_garforth = []
        n_flooded_cells_garforth_over10 = []
        n_flooded_cells_kippax = []
        n_flooded_cells_kippax_over10 = []    
        n_flooded_cells_nowetlands = []
        n_flooded_cells_nowetlands_over10 = []

    start = time.time()
    print(method)
    
    # Loop through each timeslice
    for D in range(1,5,1):
        Hs = Hs_dict[D]
        for H in Hs:
            H = str(H).zfill(2)
                
            if methods_key == 'Observed' and method == '6h_feh_singlepeak':
                fp = feh_directory + '/{}/Depth (0{}AUG2022 {} 00 00).{}.tif'.format(method, D, H, filename_ending)
                if H == "12" and D ==1 :
                    fp = feh_directory + '{}/Depth (0{}AUG2022 {} 01 00).{}.tif'.format(method, D, H, filename_ending)
                    
            else:
                fp = model_directory + '{}/Depth (0{}AUG2022 {} 00 00).{}.tif'.format(method, D, H, filename_ending)
                if H == "12" and D ==1 :
                    fp = model_directory + '{}/Depth (0{}AUG2022 {} 01 00).{}.tif'.format(method, D, H, filename_ending)
    
            # To not crash the script if this timeslice's data isnt downloaded
            #try:
                
            ###################################
            # Get the number of cells with flooding >0.1m
            ###################################
            # Get the data for this timeslice
            depth_timeslice, out_meta = open_and_clip_to_catchment(fp, catchment_gdf, crop_or_not = crop_or_not)
            number_flooded_cells = depth_timeslice[depth_timeslice>0].size
            n_flooded_cells.append(number_flooded_cells)

#                 # Remove values <0.1m
#                 # depth_timeslice = remove_little_values_fxn(depth_timeslice, fp, catchment_gdf, True)   
#                 # Count the number of flooded cells (shouldnt need the filter by 0.1 as already done)
#                 number_flooded_cells_over10cm = depth_timeslice[depth_timeslice>0.1].size
#                 # Add values to list
#                 n_flooded_cells_over10cm.append(number_flooded_cells_over10cm)

#                 ###################################
#                 # Get the number of cells with flooding >0.1m which aren't areas or permanent water
#                 ###################################
#                 depth_timeslice_notwater = depth_timeslice.copy()
#                 depth_timeslice_notwater[np.where(landcover_notwater ==16)] = np.nan
#                 # Count number of flooded cells which aren't water
#                 number_flooded_cells_not_water = depth_timeslice_notwater[depth_timeslice_notwater>0.1].size
#                 # Add values to list
#                 n_flooded_cells_notwater.append(number_flooded_cells_not_water)

            ###################################
            # Get the number of cells with flooding >0.1m which are urban
            ###################################
#                 depth_timeslice_urban = depth_timeslice.copy()
#                 depth_timeslice_urban[np.where(landcover_urban ==16)] = np.nan
#                 # Count number of flooded cells which aren't water
#                 number_flooded_cells_urban = depth_timeslice_urban[depth_timeslice_urban>0.1].size
#                 # Add values to list
#                 n_flooded_cells_urban.append(number_flooded_cells_urban)

            ###################################
            # Get the number of cells with flooding >0.1m which are urban
            ###################################
#                 if catchment_name == 'LinDyke':
#                     depth_timeslice_garforth, out_meta = open_and_clip_to_catchment(fp, garforth_gdf, crop_or_not = crop_or_not)
#                     number_flooded_cells_garforth_over10 = depth_timeslice_garforth[depth_timeslice_garforth>0.1].size
#                     number_flooded_cells_garforth = depth_timeslice_garforth[depth_timeslice_garforth>0].size
#                     n_flooded_cells_garforth.append(number_flooded_cells_garforth)
#                     n_flooded_cells_garforth_over10.append(number_flooded_cells_garforth_over10)

#                 ###################################
#                 # Get the number of cells with flooding >0.1m which are urban
#                 ###################################
#                 if catchment_name == 'LinDyke':
#                     depth_timeslice_kippax, out_meta = open_and_clip_to_catchment(fp, kippax_gdf, crop_or_not = crop_or_not)
#                     number_flooded_cells_kippax_over10 = depth_timeslice_kippax[depth_timeslice_kippax>0.1].size
#                     number_flooded_cells_kippax = depth_timeslice_kippax[depth_timeslice_kippax>0].size
#                     n_flooded_cells_kippax.append(number_flooded_cells_kippax)
#                     n_flooded_cells_kippax_over10.append(number_flooded_cells_kippax_over10)


            ###################################
            # Get the number of cells with flooding >0.1m which are urban
            ###################################
            if catchment_name == 'LinDyke':
                depth_timeslice_nowetlands, out_meta = open_and_clip_to_catchment(fp, cutting_off_wetlands_gdf, crop_or_not = crop_or_not)
                depth_timeslice_nowetlands[np.where(landcover_notwater ==16)] = np.nan
                number_flooded_cells_nowetlands_over10 = depth_timeslice_nowetlands[depth_timeslice_nowetlands>0.1].size
                n_flooded_cells_nowetlands_over10.append(number_flooded_cells_nowetlands_over10)                   
                
            #except:
            #    print(fp)

    # Add to dict
    n_flooded_cells_dict[method] = n_flooded_cells
#     n_flooded_cells_dict_over10cm[method] = n_flooded_cells_over10cm
#     n_flooded_cells_dict_notwater[method] = n_flooded_cells_notwater
#     n_flooded_cells_dict_urban[method] = n_flooded_cells_urban
    if catchment_name == 'LinDyke':
#         n_flooded_cells_dict_garforth[method] = n_flooded_cells_garforth
#         n_flooded_cells_dict_garforth_over10[method] = n_flooded_cells_garforth_over10
#         n_flooded_cells_dict_kippax[method] = n_flooded_cells_kippax
#         n_flooded_cells_dict_kippax_over10[method] = n_flooded_cells_kippax_over10   
        n_flooded_cells_dict_nowetlands_over10[method] = n_flooded_cells_nowetlands_over10    
    print("Finished one profile in : ", time.time() - start, '. There were ', n_flooded_cells, ' flooded cells') 

df_allvalues = pd.DataFrame(n_flooded_cells_dict)
# df_over10cm = pd.DataFrame(n_flooded_cells_dict_over10cm)
# df_notwater = pd.DataFrame(n_flooded_cells_dict_notwater)
# df_urban = pd.DataFrame(n_flooded_cells_dict_urban)
if catchment_name == 'LinDyke':
#     df_garforth = pd.DataFrame(n_flooded_cells_dict_garforth)
#     df_garforth_over10 = pd.DataFrame(n_flooded_cells_dict_garforth_over10)
#     df_kippax = pd.DataFrame(n_flooded_cells_dict_kippax)
#     df_kippax_over10 = pd.DataFrame(n_flooded_cells_dict_kippax_over10)
    df_nowetlands = pd.DataFrame(n_flooded_cells_dict_nowetlands)
    df_nowetlands_over10 = pd.DataFrame(n_flooded_cells_dict_nowetlands_over10)
    
# Write to csv
df_allvalues.to_csv("Data/FloodedAreaOverTime/{}/{}/allvalues_2hrs.csv".format(catchment_name,methods_key), index=False)
# df_over10cm.to_csv("Data/FloodedAreaOverTime/{}/{}/over10cm_2hrs.csv".format(catchment_name,methods_key), index=False)
# df_notwater.to_csv("Data/FloodedAreaOverTime/{}/{}/notwater_2hrs.csv".format(catchment_name, methods_key), index=False)
# df_urban.to_csv("Data/FloodedAreaOverTime/{}/{}/urban_2hrs.csv".format(catchment_name, methods_key), index=False)
if catchment_name == 'LinDyke':
#     df_garforth.to_csv("Data/FloodedAreaOverTime/{}/{}/garforth_2hrs.csv".format(catchment_name, methods_key), index=False)
#     df_garforth_over10.to_csv("Data/FloodedAreaOverTime/{}/{}/garforth_over10_2hrs.csv".format(catchment_name, methods_key), index=False)
#     df_kippax.to_csv("Data/FloodedAreaOverTime/{}/{}/kippax_2hrs.csv".format(catchment_name, methods_key), index=False)
#     df_kippax_over10.to_csv("Data/FloodedAreaOverTime/{}/{}/kippax_over10_2hrs.csv".format(catchment_name, methods_key), index=False)
    df_nowetlands_over10.to_csv("Data/FloodedAreaOverTime/{}/{}/nowetlands_nopermwater_over10_2hrs.csv".format(catchment_name, methods_key), index=False)