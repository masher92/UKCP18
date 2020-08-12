import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'WY'

stats = ['Max', 'Mean', 'Greatest_ten', '99th Percentile', '95th Percentile', '97th Percentile']
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
num_clusters_ls =[2,3,5,10]

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
stat = 'Max'
num_clusters = 2
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
codes_dict = {}
for em in ems:
    # Load in its region codes
    general_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_outputdata/{}/{}/{} clusters/em{}.csv'.format(region, stat, num_clusters,em)
    region_codes = pd.read_csv(general_filename)
    codes_dict[em] = region_codes.iloc[:,0]

test = pd.DataFrame(codes_dict)
test['Percent_1'] = (test.apply(lambda s: (s == 1).sum(), axis=1))/12 * 100
test['Percent_2'] = (test.apply(lambda s: (s == 2).sum(), axis=1))/12 * 100
#test['Percent_3'] = (test.apply(lambda s: (s == 3).sum(), axis=1))/12 * 100
#test['Percent'] = (test.apply(lambda s: (s['Percent_1 == 1).sum(), axis=1))/12 * 100
test['Percent'] = test.iloc[:,[12,13]].max(axis=1)

# Add lats and lons and remove unneeded columns                                           
test['lat'], test['lon'] = region_codes['lats'], region_codes['lons']

# Kep only last 3 cols
test = test[test.columns[-3:]]


mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))

 # Make the lat, lons from the mask the same length
test = test.round({'lat': 8, 'lon': 8})
mask = mask.round({'lat': 8, 'lon': 8})

# Join the mask with the region codes
test = mask.merge(test,  on=['lat', 'lon'], how="left")


  # Convert to 2D
lats_2d = test['lat'].to_numpy().reshape(lat_length, lon_length)
lons_2d = test['lon'].to_numpy().reshape(lat_length, lon_length)
percent_2d = test['Percent'].to_numpy().reshape(lat_length, lon_length)

# Convert the projections
inProj = Proj(init='epsg:4326')
outProj = Proj(init='epsg:3785')
lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)


### Plot
fig, ax = plt.subplots(figsize=(20,20))
my_plot = ax.pcolormesh(lons_2d, lats_2d, percent_2d,
                  linewidths=3, alpha = 1)
leeds_gdf.plot(ax= ax, edgecolor='black', color='none', linewidth=5)
#fig.colorbar(mypltp, ax=ax, fraction=0.036, pad=0.02)
cbar = plt.colorbar(my_plot,fraction=0.036, pad=0.02)
cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
plt.title(('% of cells in same cluster: '+ stat + '_' + str(num_clusters) + ' clusters'), fontsize=50)

ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_plots/{}/EnsembleAgreement/'.format(region) 
if not os.path.isdir(ddir):
    os.makedirs(ddir)
filename =  ddir + '/{}_{}_clusters.jpg'.format(stat, num_clusters)    
# Delte figure if it already exists, to avoid overwriting error
if os.path.isfile(filename):
   os.remove(filename) 
print("Figure Saved")
fig.savefig(filename)
