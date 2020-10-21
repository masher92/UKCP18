'''
Uses region cluster codes produced in HiClimR.R
'''

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import numpy.ma as ma

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

############################################
# Define variables and set up environment
#############################################
region = 'Northern' # ['WY', 'Leeds-at-centre' 'Northern']
stats = [ 'Wethours/jja_p99_wh']
#['97th Percentile','Max', 'Mean', 'Greatest_ten','95th Percentile', '99th Percentile', '99.5th Percentile', '99.9th Percentile', '99.99th Percentile']
ems =['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
num_clusters_ls = [2,3,4,5,10]

### 
lat_length = 144
lon_length = 114

##############################################################################
# Import necessary spatial files
##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:27700'})


##############################################################################
# For each statistic:
#    For each number of clusters:

##############################################################################
for stat in stats:
    codes_dict = {}
    for num_clusters in num_clusters_ls:
        print(stat)
        
        # Define counter
        em_i = 0
        
        # Set up plotting parameters for a plot with 12 subplots in
        # a 4 rows by 3 columns grid
        rows, cols = 4, 3
        fig, ax = plt.subplots(rows, cols,
                               sharex='col', 
                               sharey='row',
                               figsize=(20, 20))
        
        
        # Create a dictionary to store results for Xth cluster number
        codes_dict_xclusters = {}
        
        # For each position in the subfigure grid, create a plot
        for row in range(4):
            for col in range(3):
                
                # Select an ensemble member
                em = ems[em_i]
                print(em)
                
                # Load in its region cluster codes
                general_filename = 'Outputs/Regionalisation/HiClimR_outputdata/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)
                region_codes = pd.read_csv(general_filename)
                region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})
                                
                # Make the lat, lons from the mask the same length
                region_codes = region_codes.round({'lat': 8, 'lon': 8})
                    
                # WHY DO WE USE THE MASK? FOR WHEN WER'RE USING DIFFERENT REGIONS PRESUMABLE
                mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
                mask = mask.round({'lat': 8, 'lon': 8})
            
                # Join the mask with the region codes
                region_codes = mask.merge(region_codes,  on=['lat', 'lon'], how="left")
            
                # Add region codes to dictionary
                codes_dict_xclusters[em] = region_codes['regions_values'] 
                
                # Convert to 2D
                lats_2d = region_codes['lat'].to_numpy().reshape(lat_length, lon_length)
                lons_2d = region_codes['lon'].to_numpy().reshape(lat_length, lon_length)
                region_codes_2d = region_codes['regions_values'].to_numpy().reshape(lat_length, lon_length)
    
                ##### TRIM
                mx = np.ma.masked_invalid(region_codes_2d)
                
                mask_cols = ~np.all(mx.mask, axis=0)
                region_codes_2d = region_codes_2d[:, mask_cols]
                lats_2d = lats_2d[:, mask_cols]
                lons_2d = lons_2d[:, mask_cols]
                
                mask_rows = np.all(np.isnan(region_codes_2d) | np.equal(region_codes_2d, 0), axis=1)
                region_codes_2d = region_codes_2d[~mask_rows]
                lats_2d = lats_2d[~mask_rows]
                lons_2d = lons_2d[~mask_rows]

                # Convert the projections
                inProj = Proj(init='epsg:4326')
                outProj = Proj(init='epsg:27700')
                lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
                
                # Plot
                ax[row, col].pcolormesh(lons_2d, lats_2d, region_codes_2d,
                                  linewidths=3, alpha = 1, cmap = 'tab20')
                leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
                ax[row, col].tick_params(axis='x', labelsize= 25)
                ax[row, col].tick_params(axis='y', labelsize= 25)
                #ax[row, col].set_title('The function g', fontsize=5)
                em_i = em_i +1
        
        ###
        codes_dict[num_clusters] = codes_dict_xclusters
        
        ###
        #fig.suptitle(stat, fontsize=50)
        fig.subplots_adjust(top=1.5)
        fig.tight_layout()  
        ## Save figure
        ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/Regionalisation/HiClimR_plots/{}/{}'.format(region, stat) 
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
        filename =  ddir + '/{}_clusters.jpg'.format(num_clusters)    
        # Delte figure if it already exists, to avoid overwriting error
        if os.path.isfile(filename):
           os.remove(filename) 
        print("Figure Saved")
        fig.savefig(filename)
     
    i=0
    fig=plt.figure(figsize=(20,16))
    columns = 5
    rows = 1
    for new_i in range(1, 6):
        ax = fig.add_subplot(rows, columns, new_i)
        #fig.add_subplot(rows, columns, new_i)
        lats_2d, lons_2d, percent_2d = find_biggest_percentage_share (codes_dict[num_clusters_ls[i]])
        my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d, linewidths=3, alpha = 1, cmap = "BuPu", vmin=0, vmax=100)
        #my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d, linewidths=3, alpha = 1, vmin=0, vmax=100)
        
        #ax.set_title("Num clusters: "+ str(num_clusters_ls[0]), fontsize = 10)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        #fig.colorbar(my_plot, ax=ax, fraction=0.036, pad=0.02)
        
        plt.axis('off')
        #plt.title(str(num_clusters_ls[i]) + " Clusters", fontsize=10)
        i= i +1
        
    #fig.suptitle(stat, fontsize=20)
   # fig.subplots_adjust(top=1.5, bottom = 0.4)
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

