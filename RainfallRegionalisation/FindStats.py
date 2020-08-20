import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import xarray as xr
import os
import geopandas as gpd
import time 
import sys

"""Using numba to extract values above a percentile.
Numba executes loops efficiently
Somehow, the exceptions do not work well within numba, so they are passed out as integers"""
@jit
def values_above_percentile(rain_data,percentile_data,n_highest):
    exception=0
    # length of lons
    imax=np.shape(rain_data)[1] 
    # length of lats
    jmax=np.shape(rain_data)[2]
    if(np.shape(percentile_data)[0]>1):
        exception=1
    # first dimension is for time
    n_highest_array=np.zeros((1,n_highest,imax,jmax))
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            # Find the percentile cutoff value for that cell
            local_percentile=percentile_data[0,i,j]
            # extract values above cutoff percentile, sort these data over percentile in descending order
            # this is the most important line in this piece of code
            data_over_percentile=np.sort(local_raindata[local_raindata>=local_percentile])[::-1]
            local_n_over_percentile=len(data_over_percentile)
            # ensure we have extracted enough values
            if(local_n_over_percentile>=n_highest):
                # only use the n highest values
                n_highest_array[0,:,i,j]=data_over_percentile[:n_highest]
            else:
                exception=2
    return n_highest_array,exception


root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

ems = ['04', '05', '06', '07', '08', '09','10','11','12', '13','15']
#ems = ['11']
years = range(1981,2000)  
n_highest=20
temp_perc_file='/nfs/a319/gy17m2a/Outputs/temp_stats_percentile.nc'

region = 'Northern'
# Create geodataframe of West Yorks
uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
regional_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
# Merge the three regions into one
regional_gdf['merging_col'] = 0
regional_gdf = regional_gdf.dissolve(by='merging_col')

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
 
for em in ems:
    print(em)
    top_ten_dict = {}
    mean_dict = {}
    max_dict = {}
    percentile1_dict ={}
    percentile2_dict ={}
    percentile3_dict ={}
    percentile4_dict ={}
    for this_year in years:
        year=str(this_year)
        print(year)
        filenames=glob.glob('datadir/UKCP18/2.2km/'+em+'/1980_2001/pr_rcp85_land-cpm_uk_2.2km_' +em+'_1hr_'+year+'*.nc')
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
        # Trim the cube to the BBOX of the region of interest
        #############################################
        seconds = time.time()
        regional_cube = trim_to_bbox_of_region(concat_cube, regional_gdf)
        print("Trimmed to extent of bbox in: ", time.time() - seconds)
        
        #### Mask data     
        # if mask_to_region == True:   
        #   seconds = time.time()
        #   regional_cube = mask_by_region(regional_cube, regional_gdf)
        #   print('Created regional_mask in: ', time.time() - seconds)
        #   mask_3d = np.repeat(regional_mask[np.newaxis,:, :], regional_cube.shape[0], axis=0)
        #   print("Seconds to run =", time.time() - seconds)	
        #   regional_cube.data =  np.ma.masked_array(regional_cube.data, np.logical_not(mask_3d))
        #   print ("Joined cubes into one")
        
        # Note we are dealing with one year at a time already
        iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
        jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))
        iris.coord_categorisation.add_season_year(jja,'time', name = "season") 
        rain_data=jja.data
                       
        ### Find Max, mean
        jja_mean = jja.aggregated_by(['season'], iris.analysis.MEAN)
        jja_max = jja.aggregated_by(['season'], iris.analysis.MAX)
        jja_percentiles = jja.aggregated_by(['season'], iris.analysis.PERCENTILE, percent=[95,97,99,99.5])
        percentile_1 = jja_percentiles[0,:,:,:]
        percentile_2 = jja_percentiles[1,:,:,:]
        percentile_3 = jja_percentiles[2,:,:,:]
        percentile_4 = jja_percentiles[3,:,:,:]
        
        mean_dict[year] = jja_mean.data.reshape(-1)
        max_dict[year] = jja_max.data.reshape(-1)
        percentile1_dict[year] = percentile_1.data.reshape(-1)
        percentile2_dict[year] = percentile_2.data.reshape(-1)
        percentile3_dict[year] = percentile_3.data.reshape(-1)
        percentile4_dict[year] = percentile_4.data.reshape(-1)
        
        # Make a conservative estimate (it is a bit annoying to deal with the rounding issues)
        cutoff_percentile=100.*(1.0-(n_highest+1.0)/(np.shape(rain_data)[0]-1.0))
        yearly_stats_percentile = jja.aggregated_by(['season'], iris.analysis.PERCENTILE, percent=cutoff_percentile)
        
        ### Find top ten values
        percentile_data=yearly_stats_percentile.data
        # Perform the main algorithm.
        n_highest_array,exception=values_above_percentile(rain_data,percentile_data,n_highest)
        if(exception==1):
            raise Exception('The percent_data array has unexpected dimensions')
        if(exception==2):
            raise Exception('Cutoff percentile generates too few data points')
         
        ######## Store in format for R  
        # Remove Ensemble member dimension 
        data = n_highest_array [0,:,:,:]           
        
        
        # Loops through each of the top ten values and store in a dictionary
        # with the year name
        for i in range(0, data.shape[0]):
            #print(i)
            # Get data from one timeslice
            one_ts = data[i,:,:]
            # Extract data from one year 
            one_ts = one_ts.reshape(-1)
            # Store as dictionary with the year name
            name = year + '_' + str(i)
            top_ten_dict[name] = one_ts
            
    # Convert to dataframe
    top_ten_df= pd.DataFrame(top_ten_dict)      
    max_df = pd.DataFrame(max_dict)   
    mean_df = pd.DataFrame(mean_dict)   
    percentile1_df = pd.DataFrame(percentile1_dict)   
    percentile2_df = pd.DataFrame(percentile2_dict)   
    percentile3_df = pd.DataFrame(percentile3_dict)   
    percentile4_df = pd.DataFrame(percentile4_dict)   
    
    # Add lats and lons
    lats= jja.coord('latitude').points.reshape(-1)
    lons =  jja.coord('longitude').points.reshape(-1)   
    
    #
    top_ten_df['lat'], top_ten_df['lon'] = lats, lons
    mean_df['lat'], mean_df['lon'] = lats, lons
    max_df['lat'], max_df['lon'] = lats, lons
    percentile1_df['lat'], percentile1_df['lon'] = lats, lons
    percentile2_df['lat'], percentile2_df['lon'] = lats, lons
    percentile3_df['lat'], percentile3_df['lon'] = lats, lons
    percentile4_df['lat'], percentile4_df['lon'] = lats, lons
    
    # Save to file
    top_ten_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/Greatest_ten/em_{}.csv".format(em), index = False, float_format = '%.20f')
    max_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/Max/em_{}.csv".format(em), index = False, float_format = '%.20f')
    mean_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/Mean/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile1_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/95th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile2_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/97th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile3_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/99th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    percentile4_df.to_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/99.5th Percentile/em_{}.csv".format(em), index = False, float_format = '%.20f')
    
    
    #     # Save the percentile data, open it with xarray later on
    #     # Remove the temporary file with percentile data if it exists (need to figure out a better solution to ensure this file is closed)
    #     if os.path.exists(temp_perc_file):
    #         os.remove(temp_perc_file)
    #     iris.save(yearly_stats_percentile,temp_perc_file)
    #     # Save the results using xarray (easier for me to add a new dimension)
    #     percentile_ds=xr.open_dataset(temp_perc_file)
    #     # Add the "rank_in_season" dimension
    #     n_highest_ds=xr.Dataset(
    #     coords={
    #         "time": percentile_ds.time,
    #         "rank_in_season": ("rank_in_season", np.arange(1,np.shape(n_highest_array)[1]+1), {"long_name": "rank_in_season", "units": "-"},),
    #         "grid_latitude": percentile_ds.grid_latitude,
    #         "grid_longitude": percentile_ds.grid_longitude,
    #     })
    #     n_highest_ds["time"]=percentile_ds["time"]
    #     n_highest_ds["latitude"]=("grid_latitude", "grid_longitude"),percentile_ds["latitude"]
    #     n_highest_ds["longitude"]=("grid_latitude", "grid_longitude"),percentile_ds["longitude"]
    #     n_highest_ds["pr_n_highest"]=("time","rank_in_season","grid_latitude","grid_longitude"),n_highest_array
    #     # Merge dataset with that of previous years
    #     n_highest_years_ds=xr.merge((n_highest_years_ds, n_highest_ds), compat = 'override')
    # # The encoding here is used to ensure ncview is happy with the data
    #     output_fp ='/nfs/a319/gy17m2a/Outputs/mem_'+ em+ '_pr_n_highest.nc'
    
    # n_highest_years_ds.to_netcdf(output_fp, encoding={'rank_in_season': {'dtype': 'i4'}})
    

