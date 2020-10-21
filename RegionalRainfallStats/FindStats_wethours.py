#############################################
# Import necessary packages
#############################################
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
import re
import iris.plot as iplt
import multiprocessing as mp

@jit
def wet_hour_stats(rain_data, statistic_name):
    '''
    Description
    ----------
        Takes the data from a cube and loops through each cell in the array of data
        and extracts just the wet hours (>0.1mm/hr). Using these wet hours it calculates
        a single value related to the specified 'statistic_name' parameter. This value is the
        saved at that location. A 2d array of data values is returned containing one value
        for each cell corresponding to the input statistic_name.
    Parameters
    ----------
        rain_data: array
            3D array containing the data from an iris cube, with multiple timelices for each location
        statistic_name: String
            A string specifying the statistic to be calculated
    Returns
    -------
        stats_array: array
            A 2D array containing for each location the value corresponing to the statistic
            given as an input to the function      
    '''
    
    # Define length of lons
    imax=np.shape(rain_data)[1] 
    # Define length of lats
    jmax=np.shape(rain_data)[2]
    
    # Create empty array to populate with stats value
    stats_array =np.zeros((imax,jmax))

    # Loop through each of the cells, and find the value of the specified statistic
    # in that cell. Save this value to the correct position in the array
    print("Entering loop")
    for i in range(imax):
        for j in range(jmax):
            # Get data at one cell
            local_raindata=rain_data[:,i,j]
            # Keep only values above 0.1 (wet hours)
            wet_hours = local_raindata[local_raindata>0.1]         
            
            # Calculate statistics on just the wet hours
            # If the statistic name is a percentile then need to first extract the 
            # percentile number from the string 'statistic_name'
            if statistic_name == 'jja_mean_wh':
               statistic_value  = np.mean(wet_hours)
            elif statistic_name == 'jja_max_wh':
              statistic_value  = np.max(wet_hours)
            elif statistic_name == 'wet_prop':
               statistic_value  = (len(wet_hours)/len(local_raindata)) *100
            else:
              percentile_str =re.findall(r'\d+', statistic_name)
              if len(percentile_str) == 1:
                  percentile_no = float(percentile_str[0])
              elif len(percentile_str) ==2:
                 percentile_no = float(percentile_str[0] + '.' + percentile_str[1])
              statistic_value =  np.percentile(wet_hours, percentile_no)
            
            # Store at correct location in array
            stats_array[i,j] = statistic_value

    return  stats_array
    

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
from Spatial_geometry_functions import *

#ems = ['01', '04', '05', '06', '07', '08', '10', '11','12','13','15']
ems= ['09']
stats = ['jja_p99_wh']
#stats = ['jja_mean_wh', 'jja_max_wh', 'wet_prop', 'jja_p95_wh', 'jja_p97_wh', 'jja_p99_wh',  'jja_p99.5_wh', 'jja_p99.75_wh', 'jja_p99.9_wh']
yrs_range = "1980_2001" 

##################################################################
# Load necessary spatial data
##################################################################
northern_gdf = create_northern_outline({'init' :'epsg:3857'})

##################################################################

##################################################################
def create_stats_df(em):
#for em in ems:
    print(em)
    #############################################
    ## Load in the data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/1980_2001/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em,  em)
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
    # Trim the cube to the BBOX of the North of England 
    #############################################
    seconds = time.time()
    concat_cube = trim_to_bbox_of_region(concat_cube, northern_gdf)
    print("Trimmed to extent of bbox in: ", time.time() - seconds)
    
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
    # Loop through stats
    for stat in stats:
      print(stat)
    
      # Create dataframe with lat and long values
      df = pd.DataFrame({'lats': jja.coord('latitude').points.reshape(-1),
                       'lons': jja.coord('longitude').points.reshape(-1)})
    
      # For each year find the value at each location for the defined statistic
      # and save these to a dataframe
      years = range(1981,2001)
      for year in years:
        print(year)
        # Cut cube to just that year
        one_year_jja = jja.extract(iris.Constraint(year = year))
        # Extract data
        rain_data = one_year_jja.data
        # Find value corresponding to name stat
        stats_array = wet_hour_stats(rain_data, stat)
        # Convert to 1D
        stats_array_1d = stats_array.reshape(-1)
        # Append to dataframe
        df = df.join(pd.DataFrame({str(year) : stats_array_1d}))

      # Save to file
      ddir = "Outputs/HiClimR_inputdata/NorthernSquareRegion/Wethours/{}/".format(stat)
      if not os.path.isdir(ddir):
           os.makedirs(ddir)
      df.to_csv(ddir + "em_{}.csv".format(em), index = False, float_format = '%.20f')
      print("Saved to Dataframe")

        
pool = mp.Pool(mp.cpu_count())
results = [pool.apply_async(create_stats_df, args=(x,)) for x in ems]
output = [p.get() for p in results]
print(output)              
        
    


