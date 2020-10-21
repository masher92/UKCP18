'''
This file uses the region cluster codes produced by HiClimR in R to plot the 
spatial distribution of the clusters.

It reads in the files containing the cluster numbers assigned to each lat/long location
and then applies a mask to mask out locations not within the specified region.

Firstly, it then plots for each statistic, and number of clusters, a figure in
which each subplot contains an ensemble member.

Secondly, it plots one figure in which there is a subplot for each of the 5
numbers of clusters used. In each plot, the cell values display the proportion 
of ensemble members which place the cell within the cluster number in which it 
is most commonly placed.
'''

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import numpy.ma as ma

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/RainfallRegionalisation/')
from RainfallRegionalisation_functions import find_biggest_percentage_share
# sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
# from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

############################################
# Define variables and set up environment
#############################################
region = 'Northern' # ['WY', 'Leeds-at-centre' 'Northern']
stats = [ 'Wethours/jja_p99_wh']
#['97th Percentile','Max', 'Mean', 'Greatest_ten','95th Percentile', '99th Percentile', '99.5th Percentile', '99.9th Percentile', '99.99th Percentile']
ems =['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
num_clusters_ls = [2,3,4,5,10]

##############################################################################
# Import necessary spatial files
##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})
northern_gdf = create_northern_outline({'init' :'epsg:27700'})

##############################################################################
# 1. Plotting regional codes:
# For each statistic:
#    For each number of clusters:
#       For each ensemble member.
# This produces one plot per statistic and number of clusters; this one plot
# contains 12 subplots, one for each ensemble member. 
##############################################################################
for stat in stats:
    codes_dict = {}
    print(stat)
    for num_clusters in num_clusters_ls:
        print(num_clusters)      
        
        # Define counter (for defining ensemble member and subplot position)
        em_i = 0
        
        # Set up plotting parameters for a plot with 12 subplots in
        # a 4 rows by 3 columns grid
        rows, cols = 4, 3
        fig, ax = plt.subplots(rows, cols,
                               sharex='col', 
                               sharey='row',
                               figsize=(20, 20))
        
        # Create a dictionary:
        # For the number of clusters that the code is currently working on
        # This will store the cluster numbers for each ensemlbe member as a dictionary entry
        codes_dict_xclusters = {}
        
        # For each position in the subfigure grid, i.e. each ensemble member, create a plot
        for row in range(4):
            for col in range(3):
                
                # Select the ensemble member to use for this subplot
                em = ems[em_i]
                print(em)
                
                ##############################################################################
                # Read in the file containing the cluster number assigned to each lat/long location
                ##############################################################################
                general_filename = 'Outputs/Regionalisation/HiClimR_outputdata/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)
                region_codes = pd.read_csv(general_filename)
                region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})
                       
                ##############################################################################
                # Mask out locations not within specified region
                ##############################################################################
                # Join to mask dataframe (this defines whether each lat/long in the ? region
                # is within the region in the name of the mask - those that are have a 1 value)
                mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
                # Make the lat, lons from the region cluster codes dataframe the same length as the mask (for joining)
                region_codes = region_codes.round({'lat': 8, 'lon': 8})
                mask = mask.round({'lat': 8, 'lon': 8})
            
                # Join the mask with the region codes
                region_codes = mask.merge(region_codes,  on=['lat', 'lon'], how="left")
            
                #############################################################################
                # Save masked region codes to dictionary
                # This dictionary will contain for the particular cluster number
                # The region code values for each ensemble member
                ##############################################################################
                # Add region codes to dictionary
                codes_dict_xclusters[em] = region_codes['regions_values'] 
                
                #############################################################################
                # Prepare data for plotting
                ##############################################################################
                # Convert 1D array back to 2D array
                lats_2d = region_codes['lat'].to_numpy().reshape(144, 114)
                lons_2d = region_codes['lon'].to_numpy().reshape(144, 114)
                region_codes_2d = region_codes['regions_values'].to_numpy().reshape(144, 114)
    
                # Create mask where cells outwith region are masked
                mx = np.ma.masked_invalid(region_codes_2d)
                
                # Apply this to the region_codes and lats and lons
                # Not sure if this is best method...
                mask_cols = ~np.all(mx.mask, axis=0)
                region_codes_2d = region_codes_2d[:, mask_cols]
                lats_2d = lats_2d[:, mask_cols]
                lons_2d = lons_2d[:, mask_cols]
                
                mask_rows = np.all(np.isnan(region_codes_2d) | np.equal(region_codes_2d, 0), axis=1)
                region_codes_2d = region_codes_2d[~mask_rows]
                lats_2d = lats_2d[~mask_rows]
                lons_2d = lons_2d[~mask_rows]

                # Convert the projections
                lons_2d, lats_2d = transform(Proj(init='epsg:4326'), Proj(init='epsg:27700'),lons_2d, lats_2d)
                
                ##############################################################################
                # Plotting
                ##############################################################################
                ax[row, col].pcolormesh(lons_2d, lats_2d, region_codes_2d,
                                  linewidths=3, alpha = 1, cmap = 'tab20')
                leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
                northern_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
                ax[row, col].tick_params(axis='x', labelsize= 25)
                ax[row, col].tick_params(axis='y', labelsize= 25)
                #ax[row, col].set_title('The function g', fontsize=5)
                em_i = em_i +1
        
        # Add the dictionary containing the region codes associated with each ensemble member
        # for this cluster number to a higher level dictionary that contains an entry for
        # each number of clusters (which for each num clusters will contain a dictionary where
        # each entry is an ensemble member)
        # This is to be used in the next stage: ensemble similarity plotting
        codes_dict[num_clusters] = codes_dict_xclusters
        
        ##############################################################################
        # Adjust plotting parameters over all subplots
        ##############################################################################
        fig.subplots_adjust(top=1.5)
        fig.tight_layout()  
        
        ##############################################################################
        # Save figure
        ##############################################################################
        ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_plots/{}/{}'.format(region, stat) 
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
        filename =  ddir + '/{}_clusters.jpg'.format(num_clusters)    
        # Delete figure if it already exists, to avoid overwriting error
        if os.path.isfile(filename):
           os.remove(filename) 
        print("Figure Saved")
        fig.savefig(filename)
    
##############################################################################
# 2. Plotting ensemble member similarity 
# For each statistic this produces one plot, with 5 subplots related to each of the 
# 5 different numbers of clusters.
# Each of these plots shows the proportion of ensemble members which place each grid cell within 
# the cluster in which they are most commonly placed.
##############################################################################    
    # Define counter
    i=0
    # Calculate for each grid cell:
    # The regional cluster code which it is most commonly placed amongst the 12 ensemble members
    # For this most common cluster code, find the proportion of the twelve ensemble members which place it within this
    # This percentage will be used for plotting
    lats_2d, lons_2d, percent_2d = find_biggest_percentage_share (codes_dict[num_clusters_ls[i]])
    
    # Set up plotting parameters
    # Plot with 5 subplots, all within one row
    fig=plt.figure(figsize=(20,16))
    columns = 5
    rows = 1
    
    # Loop through 1-5 (for 5 subplots)
    for new_i in range(1, 6):
        # Define position of subplot in figure
        ax = fig.add_subplot(rows, columns, new_i)
        
        # Create plot
        my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d, linewidths=3, alpha = 1, cmap = "BuPu", vmin=0, vmax=100)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        # Turn off the axis        
        plt.axis('off')
        #plt.title(str(num_clusters_ls[i]) + " Clusters", fontsize=10)
        i= i +1
        
    # Adjust plotting parameters over all subplots
    fig.tight_layout()
    cbar_ax = fig.add_axes([1.02, 0.37, 0.02, 0.25])
    cb1 = fig.colorbar(my_plot, cax=cbar_ax, fraction=0.036, pad=0.0)
    cb1.ax.tick_params(labelsize=25)
    
    ## Save figure
    ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_plots/{}/{}'.format(region, stat) 
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    filename =  ddir + '/EnsembleSimilarity.jpg'
    # Delte figure if it already exists, to avoid overwriting error
    if os.path.isfile(filename):
       os.remove(filename) 
    print("Figure Saved")
    fig.savefig(filename,bbox_inches='tight')

