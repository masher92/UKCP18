import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'leeds-at-centre'
stats = ['Max', 'Mean', '95th Percentile','97th Percentile', '99th Percentile','99.5th Percentile','Greatest_ten', 'Greatest_twenty']
stats = ['Greatest_twenty']
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))

##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})
#leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
 
################################

for stat in stats:
    print(stat)
    ###########################################################################
    # In each plot the color bar used should be the same. To achieve this we need
    # to know before plotting any ensemble member's plot what the maximum and
    # minimum values will be across all of the ensemble members
    ###########################################################################
    
    # Make a dataframe in which all the columns from all the ensemble members will be stored
    # This will be used to test....
    all_precip_vals = pd.DataFrame({})

    # Create variables to store the maximum and minimum values across ensemble
    # members and initialise them with unfeasible values
    max_val = 0
    min_val = 200
    
    # Loop through ensemble members
    # Read in the data for the stat
    # Print the maximum value for this stat (across all years and locations)
    # If the max and min values for this stat are the most extreme so far then
    # save their values to the global variables
    for new_i in range(1, 13):
         em = ems[new_i -1]
         print(em)
          
         # Load in the data
         general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/{}/em_{}.csv'.format(region, stat, em)
         stat_data = pd.read_csv(general_filename)
    
         # Select just the precipitation values (delete both lat/lon columns and mask column)
         precip_vals = stat_data.drop(["lat", "lon", "lat.1", "lon.1", "mask"], axis=1)

         # Add these to the dataframe containing the precipitatio values from
         # across all the ensemble members
         all_precip_vals = pd.concat([all_precip_vals, precip_vals], axis=1)
         
         # Find the maximum precipitation value for this ensemble member and this stat
         max_actual_value = precip_vals.max().max()
         print("Max: " + str(round(max_actual_value, 2)))
         
         # Create column containing the mean value across all 20 years of data
         stat_data['mean'] = stat_data.iloc[:, 3:22].mean(axis=1)
         
         # If the maximum or minimum of this mean value is bigger/smaller than
         # the max/min values across all ensemble members then set this value
         # as the global max/min
         if stat_data['mean'].max() > max_val:
             max_val = stat_data['mean'].max()
         if stat_data['mean'].min() < min_val:
             min_val = stat_data['mean'].min()
    
    # Can't remember what the point of this ?
    min_val = min_val - (min_val/100 * 2)
    max_val = max_val + (max_val/100 * 2)
    
  
    ###########################################################################
    # Loop through the 12 positions in a 3x4 subfigure plot
    # For each position read in the data for an ensemble member
    # 
    ###########################################################################
    i=0
    # Width, height
    fig=plt.figure(figsize=(10,16)) # Northern
    #fig=plt.figure(figsize=(13,14)) # Leeds-at-centre
    columns = 3
    rows = 4
    for new_i in range(1, 13):
        # Select an ensemble member
        em = ems[new_i -1]
        print(em)
        
        # Load in the data
        general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/{}/em_{}.csv'.format(region, stat, em)
        stat_data = pd.read_csv(general_filename)
              
        # Create column containing the mean value across all 20 years of data
        stat_data['mean'] = stat_data.iloc[:, 3:22].mean(axis=1)
         
        # Make the lat, lons from the mask the same length
        stat_data = stat_data.round({'lat': 8, 'lon': 8})
            
        # WHY DO WE USE THE MASK? FOR WHEN WER'RE USING DIFFERENT REGIONS PRESUMABLE
        mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
        mask = mask.round({'lat': 8, 'lon': 8})
    
        # Join the mask with the region codes
        df_outer = mask.merge(stat_data,  on=['lat', 'lon'], how="left")
    
        # Convert to 2D
        lats_2d = df_outer['lat'].to_numpy().reshape(144, 114)
        lons_2d = df_outer['lon'].to_numpy().reshape(144, 114)
        df_outer_2d = df_outer['mean'].to_numpy().reshape(144, 114)
        
        ##### TRIM
        mx = np.ma.masked_invalid(df_outer_2d)
        
        mask_cols = ~np.all(mx.mask, axis=0)
        df_outer_2d = df_outer_2d[:, mask_cols]
        lats_2d = lats_2d[:, mask_cols]
        lons_2d = lons_2d[:, mask_cols]
        
        mask_rows = np.all(np.isnan(df_outer_2d) | np.equal(df_outer_2d, 0), axis=1)
        df_outer_2d = df_outer_2d[~mask_rows]
        lats_2d = lats_2d[~mask_rows]
        lons_2d = lons_2d[~mask_rows]

        # Convert the projections
        inProj = Proj(init='epsg:4326')
        outProj = Proj(init='epsg:3785')
        lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
    
        ax = fig.add_subplot(rows, columns, new_i)
        #fig.add_subplot(rows, columns, new_i)
        my_plot = ax.pcolormesh(lons_2d, lats_2d, df_outer_2d, cmap = 'terrain_r',  linewidths=3, alpha = 1, vmin = min_val, vmax = max_val)
        
        #ax.set_title("Num clusters: "+ str(num_clusters_ls[0]), fontsize = 10)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        #if new_i == 6 or new_i == 3 or new_i ==9 or new_i ==12:
        #    fig.colorbar(my_plot, ax=ax, fraction=0.036, pad=0.02)
        
        plt.axis('off')
        #plt.title(str(num_clusters_ls[i]) + " Clusters", fontsize=10)
        i= i +1
    
    #fig.suptitle(stat, fontsize=50)
   # fig.subplots_adjust(top=1.5)
    cbar_ax = fig.add_axes([0.99, 0.15, 0.05, 0.7])
    cb1 = fig.colorbar(my_plot, cax=cbar_ax, fraction=0.036, pad=0.0)
    cb1.ax.tick_params(labelsize=25)
    fig.tight_layout() 

    ## Save figure
    ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_plots/{}/Meteorology/'.format(region) 
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    filename =  ddir + '/{}.jpg'.format(stat)    
    # Delte figure if it already exists, to avoid overwriting error
    if os.path.isfile(filename):
       os.remove(filename) 
    print("Figure Saved")
    fig.savefig(filename,bbox_inches='tight')
  
    
    # Take mean over years
    min_actual_value = all_the_data.min().min()
    print("Min: " + str(round(min_actual_value, 2)))
    max_actual_value = all_the_data.max().max()
    print("Max: " + str(round(max_actual_value, 2)))
    mean_actual_value = all_the_data.mean().mean()
    print("Mean: " + str(round(mean_actual_value, 2)))
    

#plt.pcolormesh(lons_2d, lats_2d, df_outer_2d, cmap = 'terrain',  linewidths=3, alpha = 1, vmin = min_val, vmax = max_val)
