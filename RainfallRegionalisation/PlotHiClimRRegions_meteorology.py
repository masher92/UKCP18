import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'leeds-at-centre'
stats = ['Max']
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))

all_stats = pd.DataFrame(columns = ['Stat', 'Min', 'Max', 'Mean','Median', 'IQR'])

all_precip_vals_dict = {}
##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})
#leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
################################

###########################################################################
# 1ST LOOP:
# In each plot the color bar used should be the same. To achieve this we need
# to know before plotting any ensemble member's plot what the maximum and
# minimum values will be across all of the ensemble members
###########################################################################
    
for stat in stats:
    print(stat)
    # Make a dataframe in which all the columns from all the ensemble members will be stored
    # This will be used to test....
    all_precip_vals = pd.DataFrame({})

    # Create variables to store the maximum and minimum values across ensemble
    # members and initialise them with unfeasible values
    max_val = 0
    min_val = 3000
    
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
         precip_vals = stat_data.drop(["lat", "lon"], axis=1)

         # Add these to the dataframe containing the precipitatio values from
         # across all the ensemble members
         all_precip_vals = pd.concat([all_precip_vals, precip_vals], axis=1)
         
         # Find the maximum precipitation value for this ensemble member and this stat
         max_actual_value = precip_vals.max().max()
         print("Max: " + str(round(max_actual_value, 2)))
         
         # Create column containing the mean value across all 20 years of data
         precip_vals['mean'] = precip_vals.mean(axis=1)
         
         # If the maximum or minimum of this mean value is bigger/smaller than
         # the max/min values across all ensemble members then set this value
         # as the global max/min
         if precip_vals['mean'].max() > max_val:
             max_val = precip_vals['mean'].max()
         if precip_vals['mean'].min() < min_val:
             min_val = precip_vals['mean'].min()
    
    # Can't remember what the point of this ?
    min_val = min_val - (min_val/100 * 2)
    max_val = max_val + (max_val/100 * 2)
    
  
    ###########################################################################
    # 2ND LOOP:
    # Loop through the 12 positions in a 3x4 subfigure plot
    # For each position read in the data for an ensemble member
    ###########################################################################
    # Width, height
    #fig=plt.figure(figsize=(10,16)) # Northern
    fig=plt.figure(figsize=(13,14)) # Leeds-at-centre
    columns = 3
    rows = 4
    for ensemble_mem_no in range(1, 13):
        # Select an ensemble member
        em = ems[ensemble_mem_no -1]
        print(em)
        
        # Load in the data
        general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/{}/em_{}.csv'.format(region, stat, em)
        stat_data = pd.read_csv(general_filename)
   
        # Select just the precipitation values (delete both lat/lon columns and mask column)
        precip_vals = stat_data.drop(["lat.1", "lon.1", "mask"], axis=1)
        
        # Create column containing the mean value across all 20 years of data
        len(precip_vals.iloc[:,2:].columns)
        precip_vals['mean'] = precip_vals.iloc[:,2:].mean(axis=1)
        
        # In order to plot the data, we need to convert it from the way it has been
        # stored - a 1D dataframe to a 2D array.
        # To do this, we join the lats and lons to a dataframe containing all of 
        # the lats and lons in the Northern region
        
        # Read in CSV containing all the lats and lons in the entire Northern region
        mask = pd.read_csv("Outputs/RegionalMasks/{}_mask.csv".format(region))
        # Round to ensure the data and mask lat and lons are the same length
        mask = mask.round({'lat': 8, 'lon': 8})
        precip_vals = precip_vals.round({'lat': 8, 'lon': 8})
        # Join the mask to the statistics data 
        precip_vals = mask.merge(precip_vals,  on=['lat', 'lon'], how="left")

        # Use this dataset which contains lat/lons for the whole of northern region
        # (with values only for those locations within our region of interest)
        # and convert to 2D for use in plotting
        # This uses dimensios of 144 by 114 which is known as the original 2d
        # dimensions of the northern region
        lats_2d = precip_vals['lat'].to_numpy().reshape(144, 114)
        lons_2d = precip_vals['lon'].to_numpy().reshape(144, 114)
        precip_vals_2d = precip_vals['mean'].to_numpy().reshape(144, 114)
        
        # Mask out cells not within the region of interest
        mx = np.ma.masked_invalid(precip_vals_2d)
        
        # Remove any columns and rows which have no unmasked values in their 
        # whole extent
        mask_cols = ~np.all(mx.mask, axis=0)
        precip_vals_2d = precip_vals_2d[:, mask_cols]
        lats_2d = lats_2d[:, mask_cols]
        lons_2d = lons_2d[:, mask_cols]
        
        mask_rows = np.all(np.isnan(precip_vals_2d) | np.equal(precip_vals_2d, 0), axis=1)
        precip_vals_2d = precip_vals_2d[~mask_rows]
        lats_2d = lats_2d[~mask_rows]
        lons_2d = lons_2d[~mask_rows]

        # Convert the projections to Web Mercator
        inProj = Proj(init='epsg:4326')
        outProj = Proj(init='epsg:3785')
        lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
    
        #### Plot
        ax = fig.add_subplot(rows, columns, ensemble_mem_no)
        my_plot = ax.pcolormesh(lons_2d, lats_2d, precip_vals_2d, cmap = 'PuBu',  linewidths=3, alpha = 1, vmin = min_val, vmax = max_val)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        plt.axis('off')
        
        # Increase the number of ensemble_mem_no, so we move to the next EM
        ensemble_mem_no = ensemble_mem_no +1
    
    # Add one colorbar for whole plot
    cbar_ax = fig.add_axes([0.99, 0.15, 0.05, 0.7])
    cb1 = fig.colorbar(my_plot, cax=cbar_ax, fraction=0.036, pad=0.0)
    # Set formatting
    cb1.ax.tick_params(labelsize=25)
    fig.tight_layout() 

    #############################################################
    # Save figure
    #############################################################
    ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_plots/{}/Meteorology/'.format(region) 
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    filename =  ddir + '/{}.jpg'.format(stat)    
    # Delte figure if it already exists, to avoid overwriting error
    if os.path.isfile(filename):
       os.remove(filename) 
    print("Figure Saved")
    fig.savefig(filename,bbox_inches='tight')
  
    #############################################################
    # Find min, max and mean across all years of data, locations and ensemble members
    #############################################################
    stat = stat.replace('ValuesOver20Years/','')
    arr_all_precip_vals = all_precip_vals.to_numpy()
    all_precip_vals_1d = arr_all_precip_vals.reshape(-1)
    all_precip_vals_dict[stat] = all_precip_vals_1d
    
    # Take mean over years
    
    q75, q25 = np.percentile(all_precip_vals, [75 ,25])
    iqr =  q75 - q25
    print("IQR: " + str(round(iqr, 2)))
    
    min_actual_value = np.min(arr_all_precip_vals)
    print("Min: " + str(round(min_actual_value, 2)))
    
    max_actual_value =  np.max(arr_all_precip_vals)
    print("Max: " + str(round(max_actual_value, 2)))
    
    mean_actual_value = np.mean(arr_all_precip_vals)
    print("Mean: " + str(round(mean_actual_value, 2)))
    
    median_actual_value = np.median(arr_all_precip_vals)
    print("Median: " + str(round(median_actual_value, 2)))
        
        
    df2 = pd.DataFrame([[stat, round(min_actual_value, 2), round(mean_actual_value, 2), 
                         round(max_actual_value, 2),   round(median_actual_value, 2),
                          round(iqr, 2)]],
                       columns = ['Stat', 'Min','Max', 'Mean', 'Median', 'IQR'])
    all_stats = all_stats.append(df2)


# Convert to format for pasting in Latex
#all_stats.to_latex()


## PLotting
data = [all_precip_vals_dict['95th Percentile'], all_precip_vals_dict['97th Percentile']]
red_square = dict(markerfacecolor='r', marker='s')
plt.boxplot(all_precip_vals_dict['95th Percentile'], flierprops=red_square, vert=False, whis=0.75)
plt.boxplot(all_precip_vals_dict['95th Percentile'], vert = False)
plt.boxplot(data, vert = False)


# Set color of marker edge
flierprops = dict(marker='.', markerfacecolor='black', markersize=.1)
# Plot
fig, ax = plt.subplots()
# Showfliers, set to false for no outliers
ax.boxplot(all_precip_vals_dict.values(),  showfliers=False,flierprops=flierprops)
ax.set_xticklabels(all_precip_vals_dict.keys(), ha='right')
ax.tick_params(axis='x', rotation=45)



######## Taking only stats with smaller values
# small_precip_vals_dict = {}
# i = 0
# for key, val in all_precip_vals_dict.items():
#     print(key)
#     if i in [1,2,3,4,5]:
#         print('2')
#         small_precip_vals_dict[key] = val
    
#     i= i +1

# fig, ax = plt.subplots()
# ax.boxplot(small_precip_vals_dict.values())
# ax.set_xticklabels(small_precip_vals_dict.keys())
# ax.tick_params(axis='x', rotation=45)


