print("setting up environment")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches
import seaborn as sns
import geopandas as gpd
import contextily as cx
from PIL import Image

from PlotsForPaper_Functions import *

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import sys
sys.path.append("../ProcessModelResults/")
from my_functions import *

methods_key ='Observed'
catchment_name = 'LinDyke'
model_directory = '../../../FloodModelling/{}Models/Model_{}Profiles_export/'.format(catchment_name, methods_key)

sys.path.append("../")
from my_functions import *

if catchment_name == 'LinDyke':
    catchment_name_str = "Resampled.Terrain" 
    catchment_shpfilename = 'CatchmentLinDyke_exported'
    minx, miny, maxx, maxy  = 437000,  426500,  445500, 434300
    catchment_gdf = gpd.read_file(model_directory + 'CatchmentLinDyke_exported.shp')
    
elif catchment_name == 'WykeBeck':
    catchment_name_str = "Terrain.wykeDEM" 
    catchment_shpfilename = 'WykeBeckCatchment'
    minx, miny, maxx, maxy = 430004,  429978, 438660, 440996
    catchment_gdf = gpd.read_file(model_directory + 'WykeBeckCatchment.shp')
    
# Create a bounding box (this is used in preparing the rasters)
bbox = box(minx, miny, maxx, maxy)

methods_dict = {'Idealised': ['6h_sp_fl_0.1', '6h_sp_fl_0.2', '6h_sp_fl_0.3', '6h_sp_fl_0.4','6h_sp_c_0.5',
          '6h_sp_bl_0.6','6h_sp_bl_0.7','6h_sp_bl_0.8','6h_sp_bl_0.9'],
                'Observed':['6h_feh_singlepeak', '6h_c1','6h_c2','6h_c3','6h_c4', '6h_c5', '6h_c6','6h_c7',
             '6h_c8','6h_c9','6h_c10', '6h_c11', '6h_c12','6h_c13','6h_c14','6h_c15'], 
               'SinglePeak_Scaled':['6h_sp_+0%','6h_sp_+5%','6h_sp_+10%','6h_sp_+15%','6h_sp_+20%']}


landcover_directory = '../../../FloodModelling/{}Models/LandCoverData/'.format(catchment_name)
# Water landcover classification - 10 is water, 11 is eveyrthing else
with rasterio.open(landcover_directory + 'LandCover_notwater_classification.tif', 'r') as ds:
    landcover_notwater = ds.read()[0]
    out_meta = ds.meta
    
    
# Create dictionaries to store results for each method
n_flooded_cells_dict = {}
n_flooded_cells_dict_over10cm = {}
n_flooded_cells_dict_notwater = {}


print("Start the processing")
# Create dictionaries to store results for each method
n_flooded_cells_dict = {}
n_flooded_cells_dict_over10cm = {}
n_flooded_cells_dict_notwater = {}

# Loop through methods
#for method in methods_dict['Observed']:
    
# Create lists to store the values for each timeslice for this method
n_flooded_cells = []
n_flooded_cells_over10cm = []
n_flooded_cells_notwater = []

# List of all the Hours and Minutes that we need
Hs=range(12,24)
Ms= range(0,60,10)

method = sys.argv[1]
print(method)
print(os.getcwd())

print('Start the looping')
# Loop through each timeslice
for H in Hs:
    for M in Ms:
        M = str(M).zfill(2)
        # Make fp
        if methods_key == 'Observed' and method == '6h_feh_singlepeak':
            fp = '../../../FloodModelling/{}Models/Model_FEHProfiles_export/6h_feh_singlepeak/Depth (01AUG2022 {} {} 00).Resampled.Terrain.tif'.format(catchment_name, H, M)
        else:
            fp = model_directory + '{}/Depth (01AUG2022 {} {} 00).Resampled.Terrain.tif'.format(method, H, M)

        # To not crash the script if this timeslice's data isnt downloaded
        #try:
            ###################################
            # Get the number of cells with flooding >0.1m
            ###################################
            # Get the data for this timeslice

        depth_timeslice, out_meta = open_and_clip_to_catchment(fp, catchment_gdf, crop_or_not = True)
        number_flooded_cells = depth_timeslice[depth_timeslice>0].size
        n_flooded_cells.append(number_flooded_cells)

        # Remove values <0.1m
        depth_timeslice = remove_little_values_fxn(depth_timeslice, fp, catchment_gdf, True)   
        # Count the number of flooded cells (shouldnt need the filter by 0.1 as already done)
        number_flooded_over10cm = depth_timeslice[depth_timeslice>0.1].size
        # Add values to list
        n_flooded_cells_over10cm.append(number_flooded_cells_over10cm)

        ###################################
        # Get the number of cells with flooding >0.1m which aren't areas or permanent water
        ###################################
        depth_timeslice_and_landcover = pd.DataFrame({'landcovercategory':  landcover_notwater.flatten(),
                                                      'counts': depth_timeslice.flatten()})
        # Keep just the rows in the relevant landcoverclass
        df = depth_timeslice_and_landcover[depth_timeslice_and_landcover['landcovercategory']==10].copy()  
        # remove the NA values (i.e. where there is no flooding)
        df=df[df.counts.notnull()]
        # Count number of flooded cells which aren't water
        number_flooded_cells_not_water = len(df)
        # Add values to list
        n_flooded_cells_notwater.append(number_flooded_cells_not_water)

        #except:
         #   print(fp)

# Add to dict
n_flooded_cells_dict[method] = n_flooded_cells
n_flooded_cells_dict_over10cm[method] = n_flooded_cells_over10cm
n_flooded_cells_dict_notwater[method] = n_flooded_cells_notwater

df_allvalues = pd.DataFrame(n_flooded_cells_dict)
df_over10cm = pd.DataFrame(n_flooded_cells_dict_over10cm)
df_notwater = pd.DataFrame(n_flooded_cells_dict_notwater)

df_allvalues.to_csv("Data/FloodedAreaOverTime/LinDyke/Obesrved/{}_allvalues.csv".format(method))
df_over10cm.to_csv("Data/FloodedAreaOverTime/LinDyke/Obesrved/{}_over10cm.csv".format(method))
df_notwater.to_csv("Data/FloodedAreaOverTime/LinDyke/Obesrved/{}_notwater.csv".format(method))