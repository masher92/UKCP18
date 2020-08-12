import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'WY'

stats = ['Max', 'Mean', 'Greatest_ten', '95th Percentile']# '97th Percentile', '99th Percentile']
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
num_clusters_ls =[2,3,5,10]

mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))

if region == 'WY':
    lat_length = 22
    lon_length = 29
elif region == 'Northern':
    lat_length = 144
    lon_length = 114
elif region == 'WY_square':
    lat_length = 22
    lon_length = 29 


##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})
#leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
 
################################
for stat in stats:
    print(stat)

    em_i = 0
    
    rows, cols = 4, 3
    fig, ax = plt.subplots(rows, cols,
                           sharex='col', 
                           sharey='row',
                           figsize=(20, 20))
    
    # For each position in the subfigure grid, create a plot
    for row in range(4):
        for col in range(3):
            
            # Select an ensemble member
            em = ems[em_i]
            print(em)
            
            # Load in its region codes
            general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/{}/em{}.csv'.format(region, stat, em)
            raw_data = pd.read_csv(general_filename)
        
            # Take mean over years
            raw_data['mean'] = raw_data.iloc[:, 0:20].mean(axis=1)
        
            # Make the lat, lons from the mask the same length
            raw_data = raw_data.round({'lat': 8, 'lon': 8})
            mask = mask.round({'lat': 8, 'lon': 8})
        
            # Join the mask with the region codes
            df_outer = mask.merge(raw_data,  on=['lat', 'lon'], how="left")
        
            # Convert to 2D
            lats_2d = df_outer['lat'].to_numpy().reshape(lat_length, lon_length)
            lons_2d = df_outer['lon'].to_numpy().reshape(lat_length, lon_length)
            df_outer_2d = df_outer['mean'].to_numpy().reshape(lat_length, lon_length)
            
            # Convert the projections
            inProj = Proj(init='epsg:4326')
            outProj = Proj(init='epsg:3785')
            lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
            
            # Plot
            ax[row, col].pcolormesh(lons_2d, lats_2d, df_outer_2d,
                              linewidths=3, alpha = 1)
            leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
            ax[row, col].tick_params(axis='x', labelsize= 25)
            ax[row, col].tick_params(axis='y', labelsize= 25)
            #ax[row, col].set_title('The function g', fontsize=5)
            em_i = em_i +1
    
    fig.suptitle(stat, fontsize=50)
    fig.subplots_adjust(top=1.5)
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
    fig.savefig(filename)
  

