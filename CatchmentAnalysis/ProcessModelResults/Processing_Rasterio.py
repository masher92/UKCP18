import rasterio
import os
import numpy as np
import math

# Set working directory
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/")

# Define whether to filter out values <0.1
remove_little_values = True

######################################################################################
######################################################################################
# Define a function to save an array as a raster
######################################################################################
######################################################################################            
def save_array_as_raster(raster, fp_to_save):
    src = rasterio.open("MeganModel/6hr_{}_u/6hr_{}_velocity.Resampled.Terrain.tif".format(value, key))
    with rasterio.open(fp_to_save, 'w', driver='GTiff', height=raster.shape[0], width=raster.shape[1],
                            count=1, dtype=raster.dtype,crs=src.crs, nodata=np.nan, transform=src.transform) as dst:
             dst.write(raster, 1)      


######################################################################################
######################################################################################
# Read in the rasters for depth/velocity for each method
######################################################################################
######################################################################################
### Define the names of the methods, and the shorthand versions of the names used in the folder naming conventions
method_names_dict =  {'singlepeak' : 'sp', 'dividetime' : 'dt', 'subpeaktiming' : 'sp-t', 'maxspread': 'ms'}

# Create dictionaries to store the rasters for both depth and velocity
depth_rasters_dict = {}
velocity_rasters_dict = {}

# Populate the dictionaries with the depth/velocity rasters
# Filter out values which have a depth of <0.1m
for key, value in method_names_dict.items():
    print(key)
    # Read in the raster files
    velocity_raster = rasterio.open("MeganModel/6hr_{}_u/6hr_{}_velocity.Resampled.Terrain.tif".format(value, key)).read(1)
    depth_raster = rasterio.open("MeganModel/6hr_{}_u/6hr_{}_depth.Resampled.Terrain.tif".format(value, key)).read(1)
    # Set -9999 to NA
    velocity_raster[velocity_raster < -9998] = np.nan
    depth_raster[depth_raster < -9998] = np.nan    
    # Set cell values to Null in cells which have a value <0.1 in the depth raster
    if remove_little_values == True:
            depth_raster[depth_raster < 0.1] = 0
            velocity_raster[velocity_raster < 0.1] = 0
    # Save to dictionary 
    depth_rasters_dict[key] = depth_raster
    velocity_rasters_dict[key] = velocity_raster


breaks_depths = np.array([0,0.1,0.15, 0.3, 0.6, 0.9, 1.2, 1000])    
breaks_velocity = np.array([0,0.25,0.5,2,100])
            

results_dict = {}
for variable in ["depth", "velocity"]:
    counts_df = pd.DataFrame()
    proportions_df = pd.DataFrame()        

    for method_name, shortening in methods.items():    # Define filepath
        print(variable, method_name)
        # Read in the raster files
        raster = rasterio.open("MeganModel/{}_u/6hr_{}_{}.Resampled.Terrain.tif".format(shortening, method_name, variable)).read(1)
        # Set -9999 to NA
        raster[raster < -9998] = np.nan    
        # Set cell values to Null in cells which have a value <0.1 in the depth raster
        if remove_little_values == True:
             raster[raster < 0.1] = np.nan
             

       


######################################################################################
######################################################################################
# Do processing 
######################################################################################
######################################################################################
for raster_name in depth_rasters_dict:
    
    ######################################################################################
    ######################################################################################
    # Reclassify depth/velocity rasters into categories from Megan report
    ######################################################################################
    ######################################################################################

    # Classify
    classified_depth = np.sum(np.dstack([(depth_raster < b) for b in breaks_depths]), axis=2).astype(np.int32)   
    classified_velocity = np.sum(np.dstack([(velocity_raster < b) for b in breaks_velocity]), axis=2).astype(np.int32)
    
    # Reset the np.nans as np.nans
    classified_depth = np.where(np.isnan(depth_raster), np.nan, classified_depth)
    classified_velocity = np.where(np.isnan(depth_raster), np.nan, classified_velocity)
    
    # Save
    save_array_as_raster(classified_depth, ".tiff")    
save_array_as_raster(classified_depth, ".tiff")  
    ######################################################################################
    ######################################################################################
    # Find difference between depth/velocity rasters from this method, and the single peak method
    ######################################################################################
    ######################################################################################
    if raster_name != 'singlepeak':
        print(raster_name)
        # Depth
        depth_difference_raster = depth_rasters_dict['singlepeak'] - depth_rasters_dict[raster_name]
        
        # Velocity
        velocity_difference_raster = velocity_rasters_dict['singlepeak'] - velocity_rasters_dict[raster_name]

    ######################################################################################
    ######################################################################################
    # Reclassify the difference rasters to represent whether value is positive or negative 
    ######################################################################################
    ######################################################################################
    # Depth
    arcpy.gp.Reclassify_sa(depth_difference_raster, "VALUE", "-100000 0 1;0 100000 2", "Arcpy/depth_difference_singlepeak_{}_reclassified.tif".format(raster_name))
    # Velocity
    arcpy.gp.Reclassify_sa(velocity_difference_raster, "VALUE", "-1000000 0 1;0 100000 2", "Arcpy/velocity_difference_singlepeak_{}_reclassified.tif".format(raster_name)) 

    save_array_as_raster(classified_velocity, ".tiff")  

    ######################################################################################
    ######################################################################################
    # Finding the difference between the single peak method and all other methods
    ######################################################################################
    ######################################################################################
    if raster_name != 'singlepeak':
        # Depth
        depth_difference_raster = depth_rasters_dict['singlepeak'] - depth_rasters_dict[raster_name]
        save_array_as_raster(classified_depth, "Arcpy/depth_difference_singlepeak_{}.tif".format(raster_name))  
        # Velocity
        velocity_difference_raster = velocity_rasters_dict['singlepeak'] - velocity_rasters_dict[raster_name]
        save_array_as_raster(classified_depth, "Arcpy/velocity_difference_singlepeak_{}.tif".format(raster_name))  
       
    ######################################################################################
    ######################################################################################
    # Reclassify the difference rasters to represent whether value is positive or negative 
    ######################################################################################
    ######################################################################################
    breaks_pos_neg = np.array([-10000, 0, 10000])    
    
    # Depth
    pos_neg_depth_diff = np.where(np.isnan(depth_difference_raster), np.nan,
                                  np.where(depth_difference_raster <0, 0, 1))
    save_array_as_raster(pos_neg_depth_diff, "Arcpy/depth_difference_singlepeak_{}_reclassified.tif".format(raster_name))  
    
    # Velocity
    pos_neg_velocity_diff = np.where(np.isnan(velocity_difference_raster), np.nan,
                                  np.where(velocity_difference_raster <0, 0, 1))
    save_array_as_raster(pos_neg_velocity_diff, "Arcpy/velocity_difference_singlepeak_{}_reclassified.tif".format(raster_name))     
    

######################################################################################
######################################################################################
# Find the worst depth and velocity value in each grid cell (across all 4 methods)
# And the method that lead to worst case where:
# 0 = maxspread, 1 = singlepeak, 2 = subpeaktiming, 3 = dividetime
######################################################################################
###################################################################################### 
worst_case_values = np.where((depth_rasters_dict['maxspread'] > depth_rasters_dict['dividetime']) & (depth_rasters_dict['maxspread'] > depth_rasters_dict['singlepeak']) & (depth_rasters_dict['maxspread'] > depth_rasters_dict['subpeaktiming']), depth_rasters_dict['maxspread'],   #when... then
                 np.where((depth_rasters_dict['singlepeak'] > depth_rasters_dict['dividetime']) & (depth_rasters_dict['singlepeak'] > depth_rasters_dict['maxspread']) & (depth_rasters_dict['singlepeak'] > depth_rasters_dict['subpeaktiming']), depth_rasters_dict['singlepeak'] ,  #when... then
                  np.where((depth_rasters_dict['subpeaktiming'] > depth_rasters_dict['dividetime']) & (depth_rasters_dict['subpeaktiming'] > depth_rasters_dict['maxspread']) & (depth_rasters_dict['subpeaktiming'] > depth_rasters_dict['singlepeak']), depth_rasters_dict['subpeaktiming'],  #when... then
                     np.where((depth_rasters_dict['dividetime'] > depth_rasters_dict['subpeaktiming']) & (depth_rasters_dict['dividetime'] > depth_rasters_dict['maxspread']) & (depth_rasters_dict['dividetime'] > depth_rasters_dict['singlepeak']),depth_rasters_dict['dividetime'],
                           np.nan))))     

worst_case_method = np.where((depth_rasters_dict['maxspread'] > depth_rasters_dict['dividetime']) & (depth_rasters_dict['maxspread'] > depth_rasters_dict['singlepeak']) & (depth_rasters_dict['maxspread'] > depth_rasters_dict['subpeaktiming']), 0,   #when... then
                 np.where((depth_rasters_dict['singlepeak'] > depth_rasters_dict['dividetime']) & (depth_rasters_dict['singlepeak'] > depth_rasters_dict['maxspread']) & (depth_rasters_dict['singlepeak'] > depth_rasters_dict['subpeaktiming']), 1,  #when... then
                  np.where((depth_rasters_dict['subpeaktiming'] > depth_rasters_dict['dividetime']) & (depth_rasters_dict['subpeaktiming'] > depth_rasters_dict['maxspread']) & (depth_rasters_dict['subpeaktiming'] > depth_rasters_dict['singlepeak']), 2,  #when... then
                     np.where((depth_rasters_dict['dividetime'] > depth_rasters_dict['subpeaktiming']) & (depth_rasters_dict['dividetime'] > depth_rasters_dict['maxspread']) & (depth_rasters_dict['dividetime'] > depth_rasters_dict['singlepeak']),3,
                           np.nan))))     


classified_worst_case_values =  np.sum(np.dstack([(worst_case_values < b) for b in breaks_depths]), axis=2).astype(np.int32)

save_array_as_raster(classified_depth, ".tiff")    
