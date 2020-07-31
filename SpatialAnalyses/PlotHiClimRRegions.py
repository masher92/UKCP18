import pandas as pd
import matplotlib.pyplot as plt
import os

from Spatial_plotting_functions import *

stat = '95th Percentile'
region = 'WY_square'
ems = ['01', '04','05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
num_clusters =3

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))

##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})
#leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
 
################################
em_i = 0

rows, cols = 4, 3
fig, ax = plt.subplots(rows, cols,
                       sharex='col', 
                       sharey='row',
                       figsize=(20, 20))

for row in range(4):
    for col in range(3):
                
        em = ems[em_i]
        print(em)
        general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_outputdata/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)

        region_codes = pd.read_csv(general_filename)
        region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})
    
        # Make the lat, lons the same length
        region_codes = region_codes.round({'lat': 8, 'lon': 8})
        mask = mask.round({'lat': 8, 'lon': 8})
    
        # Join
        df_outer = mask.merge(region_codes,  on=['lat', 'lon'], how="left")
    
        # Convert to 1D
        df_outer['lat']
        lats_2d = df_outer['lat'].to_numpy().reshape(22, 29)
        lons_2d = df_outer['lon'].to_numpy().reshape(22, 29)
        
        inProj = Proj(init='epsg:4326')
        outProj = Proj(init='epsg:3785')
        lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
        
        regional_codes = df_outer['regions_values'].to_numpy().reshape(22, 29)
    
        ax[row, col].pcolormesh(lons_2d, lats_2d, regional_codes,
                          linewidths=3, alpha = 1, cmap = 'tab20')
        leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
        ax[row, col].tick_params(axis='x', labelsize= 25)
        ax[row, col].tick_params(axis='y', labelsize= 25)
        #ax[row, col].set_title('The function g', fontsize=5)
        em_i = em_i +1

fig.tight_layout()  

## Save figure
ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_plots/{}/'.format(region) 
if not os.path.isdir(ddir):
    os.makedirs(ddir)
filename =  ddir + '{}_{}_clusters.jpg'.format(stat, num_clusters)    

fig.savefig(filename)
  

# for row in range(4):
#     for col in range(3):
                
#         em = ems[em_i]
#         print(em)
#         general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_data/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)

#         region_codes = pd.read_csv(general_filename)
#         region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})
    
#         # Make the lat, lons the same length
#         region_codes = region_codes.round({'lat': 8, 'lon': 8})
#         mask = mask.round({'lat': 8, 'lon': 8})
    
#         # Join
#         df_outer = mask.merge(region_codes,  on=['lat', 'lon'], how="left")
    
#         # Convert to 1D
#         df_outer['lat']
#         lats_2d = df_outer['lat'].to_numpy().reshape(22, 29)
#         lons_2d = df_outer['lon'].to_numpy().reshape(22, 29)
#         regional_codes = df_outer['regions_values'].to_numpy().reshape(22, 29)
    
#         ax[row, col].pcolormesh(lons_2d, lats_2d, regional_codes,
#                           linewidths=3, alpha = 1, cmap = 'tab20')
#         leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=2)
#         ax[row, col].tick_params(axis='x', labelsize= 25)
#         ax[row, col].tick_params(axis='y', labelsize= 25)
#         #ax[row, col].set_title('The function g', fontsize=5)
#         em_i = em_i +1

# fig.tight_layout()    
# fig.tight_layout()  
# fig.tight_layout()
# fig.tight_layout()
# fig.tight_layout()
# fig.tight_layout()
# fig.savefig(filename)
      


################################## testing plotting
# leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
# fig, ax = plt.subplots(figsize=(20,10))
# ax.pcolormesh(lons_2d, lats_2d, regional_codes,
#                           linewidths=3, alpha = 1, cmap = 'tab20')
# leeds_gdf.plot(ax =ax, edgecolor='black', color='none', linewidth=6)



# plt.figure(0)
# for em in ems:
#     print(em)
#     general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_data/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)

#     region_codes = pd.read_csv(general_filename)
#     region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})

#     # Make the lat, lons the same length
#     region_codes = region_codes.round({'lat': 8, 'lon': 8})
#     mask = mask.round({'lat': 8, 'lon': 8})

#     # Join
#     df_outer = mask.merge(region_codes,  on=['lat', 'lon'], how="left")

#     # Convert to 1D
#     df_outer['lat']
#     lats_2d = df_outer['lat'].to_numpy().reshape(22, 29)
#     lons_2d = df_outer['lon'].to_numpy().reshape(22, 29)
#     regional_codes = df_outer['regions_values'].to_numpy().reshape(22, 29)

#     plt.pcolormesh(lons_2d, lats_2d, regional_codes,
#                       linewidths=3, alpha = 1, cmap = 'tab10')
#     plt.show()
#     plt.save('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_plots/{}/{}/{} clusters/em{}.jpg'.format(region, stat, num_clusters,em))
    
    
# import matplotlib.pyplot as plt
# plt.figure(0)
# #plots = []
# em_i = 0
# for i in range(4):
#     print(i)
#     for j in range(3):
#         print(j)
#         ax = plt.subplot2grid((4,3), (i,j))
        
#         em = ems[em_i]
#         print(em)
#         general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_data/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)

#         region_codes = pd.read_csv(general_filename)
#         region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})
    
#         # Make the lat, lons the same length
#         region_codes = region_codes.round({'lat': 8, 'lon': 8})
#         mask = mask.round({'lat': 8, 'lon': 8})
    
#         # Join
#         df_outer = mask.merge(region_codes,  on=['lat', 'lon'], how="left")
    
#         # Convert to 1D
#         df_outer['lat']
#         lats_2d = df_outer['lat'].to_numpy().reshape(22, 29)
#         lons_2d = df_outer['lon'].to_numpy().reshape(22, 29)
#         regional_codes = df_outer['regions_values'].to_numpy().reshape(22, 29)
    
#         ax.pcolormesh(lons_2d, lats_2d, regional_codes,
#                           linewidths=3, alpha = 1, cmap = 'tab10')
        
        
#         em_i = em_i +1

# fig.tight_layout()    
# plt.show()   




