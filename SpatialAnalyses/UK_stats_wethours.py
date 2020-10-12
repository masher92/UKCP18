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


@jit
def load_data(cube):
    # Load the data
    rain_data = cube.data
    return rain_data


@jit
def wet_hour_stats(rain_data):

    # length of lons
    imax=np.shape(rain_data)[1] 
    # length of lats
    jmax=np.shape(rain_data)[2]

    # Create empty arrays to be populated by values
    wh_mean_array =np.zeros((imax,jmax))
    wh_max_array=np.zeros((imax,jmax))
    wh_P95_array=np.zeros((imax,jmax))
    wh_P97_array =np.zeros((imax,jmax))
    wh_P99_array =np.zeros((imax,jmax))
    wh_P99_5_array=np.zeros((imax,jmax))
    wh_P99_75_array =np.zeros((imax,jmax))
    wh_P99_9_array =np.zeros((imax,jmax))
    prop_wet_array = np.zeros((imax,jmax))
    
    print("Entering loop")
    # Loop through each of the cells
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            # Keep only values above 0.1 (wet hours)
            wet_hours = local_raindata[local_raindata>0.1]
            
            # Calculate proportion of wet_hours
            prop_wet = (len(wet_hours)/len(local_raindata)) *100
            
            # Calculate statistics on just the wet hours
            wh_mean  = np.mean(wet_hours)
            wh_max  = np.max(wet_hours)
            wh_P95 = np.percentile(wet_hours, 95)
            wh_P97 = np.percentile(wet_hours, 97)
            wh_P99 = np.percentile(wet_hours, 99)
            wh_P99_5 = np.percentile(wet_hours, 99.5)
            wh_P99_75 = np.percentile(wet_hours, 99.75)
            wh_P99_9 = np.percentile(wet_hours, 99.9)
            
            # Store at correct location in array
            wh_mean_array[i,j] = wh_mean
            wh_max_array[i,j] = wh_max
            wh_P95_array[i,j] = wh_P95
            wh_P97_array[i,j]= wh_P97
            wh_P99_array[i,j] = wh_P99
            wh_P99_5_array[i,j] = wh_P99_5
            wh_P99_75_array[i,j] = wh_P99_75
            wh_P99_9_array[i,j] = wh_P99_9
            prop_wet_array[i,j] = prop_wet
      
    return  [prop_wet_array, wh_mean_array, wh_max_array, wh_P95_array, wh_P97_array, wh_P99_array,
             wh_P99_5_array, wh_P99_75_array, wh_P99_9_array]

def save_stats(stats, em):
        np.savez('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Wethours/em_'+ em+ '_stats.npz',
                  mean = stats[0],
                  max = stats[1],
                  P95 =stats[2],
                  P97 =stats[3],
                  P99 =stats[4],
                  P99_5 =stats[5],
                  P99_75 =stats[6],
                  P99_9 =stats[7])


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

ems = ['09','10']
#ems = ['01', '04', '05', '06', '07', '08','09', '10', '11','12','13','15']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

# Create a dictionary within which the stats cubes for each ensemble member will
# be stored
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
    print("Trimmed to UK coastline")
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season year
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 

    ############################################
    # Find wet hour stats
    #############################################
    seconds = time.time()
    rain_data = load_data(jja)
    print("Loaded data in ", time.time() - seconds)
    
    seconds = time.time()
    stats = wet_hour_stats(rain_data)
    print("Found wet hour stats ", time.time() - seconds)

    # seconds = time.time()
    # stats = save_stats(stats, em)
    # print("Saved stats in:", time.time() - seconds)

    np.save('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/Wethours/em_'+ em+ '_wethoursprop.npy',
            stats)


# mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
            
# # Masked data
# masked_data = ma.masked_where(mask == 0, mean_array)

# #grid = trim_to_bbox_of_region(grid, northern_gdf)


# lats_2d =jja.coord('latitude').points
# lats_1d = lats_2d.reshape(-1)
# lons_2d = regional_jja.coord('longitude').points
# lons_1d = lons_2d.reshape(-1)
# inProj = Proj(init='epsg:4326')
# outProj = Proj(init='epsg:3857')
# lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)
   

# fig, ax = plt.subplots()
# my_plot = ax.pcolormesh(lons_2d, lats_2d, masked_data, linewidths=3, 
#                       alpha = 1, cmap = precip_colormap)
# northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)


# def create_northern_gdf:
#   uk_regions = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
#   northern_regions = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
#   #uk_regions = gpd.read_file(root_fp + "datadir/SpatialData/NUTS_Level_1__January_2018__Boundaries-shp/NUTS_Level_1__January_2018__Boundaries.shp") 
#   #northern_regions = uk_regions.loc[uk_regions['nuts118nm'].isin(['North East (England)', 'North West (England)', 'Yorkshire and The Humber'])]
#   # Merge the three regions into one
#   northern_regions['merging_col'] = 0
#   northern_gdf = northern_regions.dissolve(by='merging_col')
#   northern_gdf = northern_gdf.to_crs({'init' :'epsg:3785'}) 
#   return(northern_gdf)

# ### Create larger northern region
# # England part
# wider_northern_gdf = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber', 'East Midlands', 'West Midlands'])]
# wider_northern_gdf['merging_col'] = 0
# wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
# wider_northern_gdf = wider_northern_gdf[['geometry']]

# # Scotland part
# dg = gpd.read_file("datadir/SpatialData/2011_Census_Dumfries_and_Galloway_(shp)/DC_2011_EoR_Dumfries___Galloway.shp")
# dg['merging_col'] = 0
# dg = dg.dissolve(by='merging_col')
# dg.plot()
# borders = gpd.read_file('datadir/SpatialData/Scottish_Borders_shp/IZ_2001_EoR_Scottish_Borders.shp')
# borders['merging_col'] = 0
# borders = borders.dissolve(by='merging_col')
# borders.plot()

# southern_scotland = pd.concat([dg, borders])
# southern_scotland['new_merging_col'] = 0
# southern_scotland = southern_scotland.dissolve(by='new_merging_col')
# southern_scotland = southern_scotland[['geometry']]
# southern_scotland.plot()

# # Join the two
# wider_northern_gdf = pd.concat([southern_scotland, wider_northern_gdf])
# wider_northern_gdf['merging_col'] = 0
# wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
# wider_northern_gdf = wider_northern_gdf.to_crs({'init' :'epsg:3785'}) 

# wider_northern_gdf.plot()