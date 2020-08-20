############################################
# Set up environment
#############################################
import sys
import iris
import os
import iris.quickplot as qplt
import warnings
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
from shapely.geometry import Polygon
import iris.coord_categorisation
import time 
warnings.filterwarnings("ignore")

# Set working directory - 2 options for remote server and desktop
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
#root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

# Define required variables
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
ems = ['05'] #['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
region = 'Leeds-at-centre' #['Northern', 'WY_square', 'WY']

# Define whether to mask out cells not within the specific area of itnerest
if region == 'WY_square' or region == 'Leeds-at-centre':
  mask_to_region = False
else:
  mask_to_region = True
  
print("Region = ", region, "Masking is : "  , mask_to_region)

############################################
# Create regions
#############################################
if region == 'WY' or region == 'WY_square':
    regional_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
    regional_gdf = regional_gdf[region_gdf['cauth15cd'] == 'E47000003']
    regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
elif region == 'Northern': 
    # Create geodataframe of West Yorks
    uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
    regional_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
    regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
    # Merge the three regions into one
    regional_gdf['merging_col'] = 0
    regional_gdf = regional_gdf.dissolve(by='merging_col')
elif region == 'Leeds-at-centre':
    # Create region with Leeds at the centre
    lons = [54.130260, 54.130260, 53.486836, 53.486836]
    lats = [-2.138282, -0.895667, -0.895667, -2.138282]
    polygon_geom = Polygon(zip(lats, lons))
    regional_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 

#############################################
# Read in files
#############################################
for em in ems:
    start_time = time.time()
    print ("Ensemble member {}".format(em))
       
    # Create list of names of cubes for between the years specified
    filenames =[]
    for year in range(start_year,end_year+1):
        # Create filepath to correct folder using ensemble member and year
        general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
        #print(general_filename)
        # Find all files in directory which start with this string
        for filename in glob.glob(general_filename):
            #print(filename)
            filenames.append(filename)
    
    ####### For testing on desktop comuter #######
    # filenames =[]
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
    # filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 
    
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    print(str(len(monthly_cubes_list)) + " cubes found for this time period.")
    
    #############################################
    # Concat the cubes into one
    #############################################
    # Remove attributes which aren't the same across all the cubes.
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
     
     # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()

    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    print ("Joined cubes into one")
    
    #############################################
    # Trim the cube to the BBOX of the region of interest
    #############################################
    seconds = time.time()
    regional_cube = trim_to_bbox_of_region(concat_cube, regional_gdf)
    print("Trimmed to extent of bbox in: ", time.time() - seconds)
    
    #seconds = time.time()
    #regional_cube = mask_by_region(regional_cube, regional_gdf)
    #print('Created regional_mask in: ', time.time() - seconds)
    #mask_3d = np.repeat(regional_mask[np.newaxis,:, :], regional_cube.shape[0], axis=0)
    #print("Seconds to run =", time.time() - seconds)	
    #regional_cube.data =  np.ma.masked_array(regional_cube.data, np.logical_not(mask_3d))
    
    ############################################
    # Generate cube containing only hourly values in June-July-August period
    # and which contains a variable for the 'season year'
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(regional_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = regional_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season_year variable
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 
    print('Cut to June-July-August period')

    #############################################
    # Finding biggest ten for each year
    #############################################
    # Check if folder already exists, if it doesn't then create it  
    ddir = "Outputs/HiClimR_inputdata/{}/{}/".format(region, 'Greatest_ten')
    if not os.path.isfile(ddir + "em{}.csv".format(em)):
        os.makedirs(ddir)
        print("Greatest ten doesn't already exist, creating...")
   
    # Use function from Spatial_plotting_functions file to find top ten values
    # If using mask, then import this and use in function
    if mask_to_region == True:
       # Read from file, delete NAs
       mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))
       mask = mask.dropna()
       
       seconds = time.time()
       df_newmethod = n_largest_yearly_values_method2(jja, mask_to_region, mask)
       print("Found N largest values in: ", time.time() - seconds)
    elif mask_to_region == False:
       seconds = time.time()
       df_newmethod = n_largest_yearly_values_method2(jja, mask_to_region)
       print("Found N largest values in: ", time.time() - seconds)  
   
# Save the output to file
df_newmethod.to_csv(ddir + "em{}.csv".format(em), index = False)


### Testing if both methods produce same result
# Old method - cell by cell
# np.sort(df.iloc[0][0:10])
# # New method - Iris percentiles
# np.sort(df_newmethod.iloc[0][0:10])

