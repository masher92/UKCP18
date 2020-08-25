import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'Northern'
stats = ['Max', 'Mean', '95th Percentile','97th Percentile', '99th Percentile','99.5th Percentile','Greatest_ten', 'Greatest_twenty']
#stats = ['Mean']
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))

##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})
#leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
 
################################
for stat in stats:
    print(stat)
    real_stat = 'NA'
    # Find max and min values for plotting
    max_val = 0
    print(max_val)
    min_val = 200
    for new_i in range(1, 13):
         # Select an ensemble member
         em = ems[new_i -1]
        
         # Load in its region codes
         if stat == 'Greatest_ten':
            stat = 'Greatest_twenty'
            real_stat = 'Greatest_ten'
             
         general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/{}/em_{}.csv'.format(region, stat, em)
         raw_data = pd.read_csv(general_filename)
    
         if real_stat == 'Greatest_ten': 
             raw_data = raw_data.loc[:,~raw_data.columns.str.contains('_10|_11|_12|_13|_14|_15|_16|_17|_18|_19')]         
             stat = 'Greatest_ten'
         
         # Take mean over years
         raw_data['mean'] = raw_data.iloc[:, 0:20].mean(axis=1)
         
         if raw_data['mean'].max() > max_val:
             max_val = raw_data['mean'].max()
         if raw_data['mean'].min() < min_val:
             min_val = raw_data['mean'].min()
    
    min_val = min_val - (min_val/100 * 2)
    max_val = max_val + (max_val/100 * 2)
    
    ### Plotting
    i=0
    # Width, height
    fig=plt.figure(figsize=(10,16)) # Northern
    #fig=plt.figure(figsize=(13,14)) # Leeds-at-centre
    columns = 3
    rows = 4
    for new_i in range(1, 13):
        real_stat = 'NA'
        print(new_i)
        # Select an ensemble member
        em = ems[new_i -1]
        #print(em)
        
        # Load in its region codes
        if stat == 'Greatest_ten':
            stat = 'Greatest_twenty'
            real_stat = 'Greatest_ten'
        
        # Load in its region codes
        general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/{}/em_{}.csv'.format(region, stat, em)
        raw_data = pd.read_csv(general_filename)
              
        if real_stat == 'Greatest_ten': 
             raw_data = raw_data.loc[:,~raw_data.columns.str.contains('_10|_11|_12|_13|_14|_15|_16|_17|_18|_19')]         
             stat = 'Greatest_ten'
         
        # Take mean over years
        raw_data['mean'] = raw_data.iloc[:, 0:20].mean(axis=1)
        
        # Make the lat, lons from the mask the same length
        raw_data = raw_data.round({'lat': 8, 'lon': 8})
            
        # WHY DO WE USE THE MASK? FOR WHEN WER'RE USING DIFFERENT REGIONS PRESUMABLE
        mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
        mask = mask.round({'lat': 8, 'lon': 8})
    
        # Join the mask with the region codes
        df_outer = mask.merge(raw_data,  on=['lat', 'lon'], how="left")
    
        # Convert to 2D
        lats_2d = df_outer['lat'].to_numpy().reshape(144, 114)
        lons_2d = df_outer['lon'].to_numpy().reshape(144, 114)
        df_outer_2d = df_outer['mean'].to_numpy().reshape(144, 114)
        
        print(df_outer['mean'].max())
        print(df_outer['mean'].mean())
        
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
  

#plt.pcolormesh(lons_2d, lats_2d, df_outer_2d, cmap = 'terrain',  linewidths=3, alpha = 1, vmin = min_val, vmax = max_val)
