'''
This file calculates statistics (mean, max, various percentiles) for each grid 
cell across the whole of the UK.
It plots these and saves the results to file.
'''

import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import os
import geopandas as gpd
import time 
import sys
import iris.quickplot as qplt
import cartopy.crs as ccrs
import matplotlib 
import iris.plot as iplt

# For extracting the variable name from a variable
def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

# Create a dictionary within which the stats cubes for each ensemble member will
# be stored
ems_dict = {}

# Cycle through ensemble members
# For each ensemble member: 
#       Read in all files and join into one cube
#       Trim to the outline of the UK
#       Cut so only hours in JJA remain
#       Find the max, mean and percentile values for each grid square
#       
for em in ems:
    print(em)
    #############################################
    ## Load in the data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
        filenames.append(filename)
    print(len(filenames))
    
    # filenames =[]
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 
    
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    
    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    
    #############################################
    ## Trim to outline of UK
    #############################################
    minmax = lambda x: (np.min(x), np.max(x))
    #bbox = np.array([-8.6500072, 49.863187 ,  1.7632199, 60.8458677])
    bbox = np.array([-10.1500, 49.8963187 ,  1.7632199, 58.8458677])
    # Find the lats and lons of the cube in WGS84
    lons = concat_cube.coord('longitude').points
    lats = concat_cube.coord('latitude').points
    
    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    concat_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season year
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 
    
    ###########################################
    # Find Max, mean, percentiles
    #############################################
    #seconds = time.time()
    jja_mean = jja.aggregated_by(['clim_season'], iris.analysis.MEAN)
    jja_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)
    jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, percent=[95,97,99,99.5, 99.9, 99.99])
    
    ############################################# 
    # Store each stats cube in a dictionary (with name of stat as key and the
    # cube as the item)
    # Keep a running log of the max and min value for each statistic across all
    # ensemble members
    #############################################
    # Create dictionary to store this ensemble members results
    em_dict = {}
    
    # Create a list of the stats
    stats = [jja_mean, jja_max, jja_percentiles]
    
    # If the first ensemble member then initialise dictionaries to store the max
    # and min values and set them to unfeasible values
    if em == '01':
        max_vals_dict = {}
        min_vals_dict = {}
        for stat in stats:
            # Extract various percentiles
            if stat == jja_percentiles:
                for i in range(jja_percentiles.shape[0]):
                    stat = jja_percentiles[i]
                    name = 'P' + str(jja_percentiles[i].coord('percentile_over_clim_season').points[0])         
                    name = name.replace(".", "_")
                    max_vals_dict[name] = 0
                    min_vals_dict[name] = 10000
            else:
                name = namestr(stat, globals())[0]
                max_vals_dict[name] = 0
                min_vals_dict[name] = 10000
        
    # Store all stats values in dictionary
    for stat in stats:
        if stat == jja_percentiles:
            for i in range(jja_percentiles.shape[0]):
                stat = jja_percentiles[i]
                name = 'P' + str(jja_percentiles[i].coord('percentile_over_clim_season').points[0])         
                name = name.replace(".", "_")
                em_dict[name] = stat
                max_vals_dict[name] = stat.data.max() if stat.data.max() > max_vals_dict[name] else max_vals_dict[name]
                min_vals_dict[name] = stat.data.min() if stat.data.min() < min_vals_dict[name] else min_vals_dict[name]      
        else:
            name = namestr(stat, globals())[0]
            em_dict[name] = stat
            max_vals_dict[name] = stat.data.max() if stat.data.max() > max_vals_dict[name] else max_vals_dict[name]
            min_vals_dict[name] = stat.data.min() if stat.data.min() < min_vals_dict[name] else min_vals_dict[name]      
    
    # Add the dictionary of stat names and cubes to the dictionary of ensemble
    # member dictionaries
    ems_dict[em] = em_dict       

#############################################
# Plotting
#############################################
# Create a colourmap                                   
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      

precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="white")

# Loop through each ensemble member's dictionary from the dictionary
for em in ems:  
    print(em)
    em_dict = ems_dict[em]
    # Loop through stats
    for key, value in em_dict.items() :
        print (key)
        
        # Extract the cube
        cube = em_dict[key]
        #Create a 2D grid
        grid = cube[0]
        
        # Extract the max, min values
        max_value = max_vals_dict[key]
        min_value = min_vals_dict[key]
        
        # Plot
        fig=plt.figure(figsize=(20,16))
        levels = np.round(np.linspace(min_value, max_value, 15),2)
        contour = iplt.contourf(grid,levels = levels,cmap=precip_colormap, extend="both")
        plt.gca().coastlines(resolution='50m', color='black', linewidth=2)
        #plt.plot(0.6628091964140957, 1.2979678925914127, 'o', color='black', markersize = 3) 
        #plt.title("JJA mean", fontsize =40) 
        #plt.colorbar(fraction=0.036, pad=0.02)
        cb = plt.colorbar(fraction=0.036, pad=0.02)
        cb.ax.tick_params(labelsize=25)

        # Save Figure
        ddir = 'Outputs/UK_plots/' + key + '/'
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
        filename =  (ddir + '/{}.jpg').format(em)
        
        fig.savefig(filename,bbox_inches='tight')
        print("Plot saved")



