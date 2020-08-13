import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'Leeds-at-centre' #['WY', 'Leeds-at-centre']
masked_data = False
stats = ['Mean'] #'Greatest_ten', '99.5th Percentile'
#stats = ['Max', 'Mean', 'Greatest_ten', '99th Percentile', '95th Percentile']
ems =['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
num_clusters_ls = [3,4,5,10, 2]

if region == 'WY':
    lat_length = 22
    lon_length = 29
elif region == 'Northern':
    lat_length = 144
    lon_length = 114
elif region == 'WY_square':
    lat_length = 22
    lon_length = 29 
elif region == 'Leeds-at-centre':
    lat_length = 33
    lon_length = 37  

##############################################################################
leeds_gdf = create_leeds_outline({'init' :'epsg:3785'})
#leeds_gdf = create_leeds_outline({'init' :'epsg:4326'})
################################




for stat in stats:
    
    codes_dict = {}
    for num_clusters in num_clusters_ls:
        print(stat)
    
        em_i = 0
        
        rows, cols = 4, 3
        fig, ax = plt.subplots(rows, cols,
                               sharex='col', 
                               sharey='row',
                               figsize=(20, 20))
        
        codes_dict_xclusters = {}
        # For each position in the subfigure grid, create a plot
        for row in range(4):
            for col in range(3):
                
                # Select an ensemble member
                em = ems[em_i]
                print(em)
                
                # Load in its region codes
                general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_outputdata/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)
                region_codes = pd.read_csv(general_filename)
                region_codes = region_codes.rename(columns={'lats': 'lat', 'lons': 'lon'})
                
                
                #
                codes_dict_xclusters[em] = region_codes.iloc[:,0]
                
                # Make the lat, lons from the mask the same length
                region_codes = region_codes.round({'lat': 8, 'lon': 8})
                
                if masked_data == True:
                    # WHY DO WE USE THE MASK? FOR WHEN WER'RE USING DIFFERENT REGIONS PRESUMABLE
                    mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))
                    mask = mask.round({'lat': 8, 'lon': 8})
                
                    # Join the mask with the region codes
                    region_codes = mask.merge(region_codes,  on=['lat', 'lon'], how="left")
            
                # Convert to 2D
                lats_2d = region_codes['lat'].to_numpy().reshape(lat_length, lon_length)
                lons_2d = region_codes['lon'].to_numpy().reshape(lat_length, lon_length)
                region_codes_2d = region_codes['regions_values'].to_numpy().reshape(lat_length, lon_length)
                
                # Convert the projections
                inProj = Proj(init='epsg:4326')
                outProj = Proj(init='epsg:3785')
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
        fig.suptitle(stat, fontsize=50)
        fig.subplots_adjust(top=1.5)
        fig.tight_layout()  
        ## Save figure
        ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_plots/{}/{}'.format(region, stat) 
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
        filename =  ddir + '/{}_clusters.jpg'.format(num_clusters)    
        # Delte figure if it already exists, to avoid overwriting error
        if os.path.isfile(filename):
           os.remove(filename) 
        print("Figure Saved")
        fig.savefig(filename)
     

        


i=0
fig=plt.figure(figsize=(10,7))
columns = 3
rows = 2
a=np.random.rand(2,3)
for new_i in range(1, 6):
    ax = fig.add_subplot(rows, columns, new_i)
    #fig.add_subplot(rows, columns, new_i)
    lats_2d, lons_2d, percent_2d = find_biggest_percentage_share (codes_dict[num_clusters_ls[i]])
    
    my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d,
                  linewidths=3, alpha = 1)
    #ax.set_title("Num clusters: "+ str(num_clusters_ls[0]), fontsize = 10)
    leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
    
    plt.axis('off')
    plt.title(str(num_clusters_ls[i]) + " Clusters", fontsize=20)
    i= i +1
    
fig.tight_layout()  
    
    
    
    my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d,
                      linewidths=3, alpha = 1)
    leeds_gdf.plot(ax= ax, edgecolor='black', color='none', linewidth=5)
    
    
    
    leeds_gdf.plot(ax= ax, edgecolor='black', color='none', linewidth=5)
    #fig.colorbar(mypltp, ax=ax, fraction=0.036, pad=0.02)
    cbar = plt.colorbar(my_plot,fraction=0.036, pad=0.02)
    cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    plt.title(('% of cells in same cluster: '+ stat + '_' + str(num_clusters) + ' clusters'), fontsize=50)
    
    
    #plt.plot(a)### what you want you can plot  
    lats_2d, lons_2d, percent_2d = find_biggest_percentage_share (codes_dict[num_clusters_ls[0]])
    my_plot = ax[row, col].pcolormesh(lons_2d, lats_2d, percent_2d,
                  linewidths=3, alpha = 1)
    ax[row, col].set_title("Num clusters: "+ str(num_clusters_ls[0]), fontsize = 30)
    leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=5)
    add_colorbar(my_plot)
plt.show()

         
rows, cols = 2,3
fig, ax = plt.subplots(rows, cols,
                       sharex='col', 
                       sharey='row',
                       figsize=(20, 20))   
i=0
for row in range(2):
    for col in range(3): 
        if i < len(num_clusters_ls):
            lats_2d, lons_2d, percent_2d = find_biggest_percentage_share (codes_dict[num_clusters_ls[i]])
            my_plot = ax[row, col].pcolormesh(lons_2d, lats_2d, percent_2d,
                              linewidths=3, alpha = 1)
            ax[row, col].set_title("Num clusters: "+ str(num_clusters_ls[i]), fontsize = 30)
            leeds_gdf.plot(ax=ax[row, col], edgecolor='black', color='none', linewidth=5)
            add_colorbar(my_plot)
            i= i +1
        else:
            break


fig.tight_layout()  






#########
# https://stackoverflow.com/questions/23876588/matplotlib-colorbar-in-each-subplot
def add_colorbar(mappable):
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    import matplotlib.pyplot as plt
    last_axes = plt.gca()
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = fig.colorbar(mappable, cax=cax)
    plt.sca(last_axes)
    return cbar        
        


def find_biggest_percentage_share (dictionary):
    # Create a dataframe containing the region codes for each ensemble member in the columns        
    codes_df = pd.DataFrame(dictionary)    
    
    # Create a dictionary to store for each cluster the % of ensemble members wher
    # the location is in that cluster
    percents_dict = {}
    # For each cluster in the number of clusters
    for n in range(num_clusters): 
        # Find the percentage of ensemble members in that cluster and add to the dictionary
        percent_n = (codes_df.apply(lambda s: (s == (n+1)).sum(), axis=1))/12 * 100
        percents_dict['Percent_' + str(n+1)] = percent_n
    
    # Create this as a dataframe
    percents_df = pd.DataFrame(percents_dict)        
    # Add to dataframe containing codes
    codes_df = codes_df.assign(**percents_df)
    # Find the maximum percentage in any one cluster
    codes_df['Percent'] = codes_df.iloc[:,12:len(codes_df.columns)].max(axis=1)           
     # Add lats and lons and remove unneeded columns                                           
    codes_df['lat'], codes_df['lon'] = region_codes['lat'], region_codes['lon']
    
    # Kep only last 3 cols
    codes_df = codes_df[codes_df.columns[-3:]]
    
    # Read in the mask
    mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))
     # Make the lat, lons from the mask the same length
    codes_df = codes_df.round({'lat': 8, 'lon': 8})
    mask = mask.round({'lat': 8, 'lon': 8})
    # Join the mask with the region codes
    codes_df = mask.merge(codes_df,  on=['lat', 'lon'], how="left")   
    
     # Convert to 2D
    lats_2d = codes_df['lat'].to_numpy().reshape(lat_length, lon_length)
    lons_2d = codes_df['lon'].to_numpy().reshape(lat_length, lon_length)
    percent_2d = codes_df['Percent'].to_numpy().reshape(lat_length, lon_length)
    
    # Convert the projections
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:3785')
    lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
    
    return lats_2d, lons_2d, percent_2d

    ### Plot
    # fig, ax = plt.subplots(figsize=(20,20))
    # my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d,
    #                   linewidths=3, alpha = 1)
    # leeds_gdf.plot(ax= ax, edgecolor='black', color='none', linewidth=5)
    # #fig.colorbar(mypltp, ax=ax, fraction=0.036, pad=0.02)
    # cbar = plt.colorbar(my_plot,fraction=0.036, pad=0.02)
    # cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
    # plt.title(('% of cells in same cluster: '+ stat + '_' + str(num_clusters) + ' clusters'), fontsize=50)

