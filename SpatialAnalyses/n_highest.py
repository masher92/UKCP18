import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import xarray as xr
import os

os.chdir("/nfs/a319/gy17m2a/Outputs/")

ems = ['01']#, ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
years = range(1981,2000)
n_highest=10
temp_perc_file='/nfs/a319/gy17m2a/Outputs/temp_stats_percentile.nc'
   

for em in ems:
    my_dict = {}
    
    print(em)
    # initialise an empty data set
    n_highest_years_ds=xr.Dataset()
    for this_year in years:
        year=str(this_year)
        print(year)
        filenames=glob.glob('/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/'+em+'/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_'+year+'*.nc')
        monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
        for cube in monthly_cubes_list:
             for attr in ['creation_date', 'tracking_id', 'history']:
                 if attr in cube.attributes:
                     del cube.attributes[attr]
        # Hard-coding indices corresponding to more or less the North of England for convenience
        regional_cube = monthly_cubes_list.concatenate_cube()[0,:,130:400,230:400]
        
        # Note we are dealing with one year at a time already
        iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
        jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))
        iris.coord_categorisation.add_season_year(jja,'time', name = "season") 
        rain_data=jja.data
        # Make a conservative estimate (it is a bit annoying to deal with the rounding issues)
        cutoff_percentile=100.*(1.0-(n_highest+1.0)/(np.shape(rain_data)[0]-1.0))
        yearly_stats_percentile = jja.aggregated_by(['season'], iris.analysis.PERCENTILE, percent=cutoff_percentile)
        percentile_data=yearly_stats_percentile.data
        # Perform the main algorithm.
        n_highest_array,exception=values_above_percentile(rain_data,percentile_data,n_highest)
        if(exception==1):
            raise Exception('The percent_data array has unexpected dimensions')
        if(exception==2):
            raise Exception('Cutoff percentile generates too few data points')
            
        data = n_highest_array [0,:,:,:]           
        
        for i in range(0, data.shape[0]):
            print(i)
            # Get data from one timeslice
            one_ts = data[i,:,:]
            # Extract data from one year 
            one_ts = one_ts.reshape(-1)
            # Store as dictionary with the year name
            name = year + '_' + str(i)
            my_dict[name] = one_ts
        
      test = pd.DataFrame(my_dict)      
      
      lats= jja.coord('latitude').points.reshape(-1)
      lons =  jja.coord('longitude').points.reshape(-1)   
      
      test['lat'], test['lon'] = lats, lons
      
      test.to_csv("Outputs/HiClimR_inputdata/topten.csv", index = False)
      
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
    

cube_iris = n_highest_ds.to_iris()
print(n_highest_years_ds)
print(n_highest_ds)



"""Using numba to extract values above a percentile.
Numba executes loops efficiently
Somehow, the exceptions do not work well within numba, so they are passed out as integers"""
@jit
def values_above_percentile(rain_data,percentile_data,n_highest):
    exception=0
    imax=np.shape(rain_data)[1] 
    jmax=np.shape(rain_data)[2]
    if(np.shape(percentile_data)[0]>1):
        exception=1
    # first dimension is for time
    n_highest_array=np.zeros((1,n_highest,imax,jmax))
    for i in range(imax):
        for j in range(jmax):
            local_raindata=rain_data[:,i,j]
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

