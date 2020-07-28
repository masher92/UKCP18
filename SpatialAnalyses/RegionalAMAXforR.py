import sys
import iris
import cartopy.crs as ccrs
import os
from scipy import spatial
import itertools
import iris.quickplot as qplt
import warnings
import copy
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
import numpy as np
from shapely.geometry import Polygon
import iris.coord_categorisation


# Provide root_fp as argument
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
root_fp = "/nfs/a319/gy17m2a/"

os.chdir(root_fp)
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 
ems = ['12', '13', '15']
region = 'WY'

############################################
# Create regions
#############################################
wy_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
wy_gdf = wy_gdf[wy_gdf['cauth15cd'] == 'E47000003']
wy_gdf = wy_gdf.to_crs({'init' :'epsg:3785'}) 
 
# Create geodataframe of West Yorks
uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
northern_gdf = northern_gdf.to_crs({'init' :'epsg:3785'}) 
# Merge the three regions into one
northern_gdf['merging_col'] = 0
northern_gdf = northern_gdf.dissolve(by='merging_col')

regional_gdf = wy_gdf

#############################################
# Read in files
#############################################

for em in ems:
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
    
    #filenames =[]
    #filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc')  
    #filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19810101-19810130.nc') 
    #filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19820601-19820630.nc') 
    #filenames.append(root_fp + 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19830601-19830630.nc') 
    
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
    #
    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    
    #############################################
    # Trim the cube to the BBOX of the region of interest
    #############################################
    regional_cube = trim_to_bbox_of_region(concat_cube, regional_gdf)
    
    # Check plotting
    #qplt.contourf(regional_cube[10,:,:])       
    #plt.gca().coastlines()   
    # Check plotting #.2
    #plot_cube_within_region(regional_cube[112,:,:], regional_gdf)
    
    #############################################
    # 
    #############################################
    if not 'regional_mask' in globals():
        # Create a masked array - masking out all cells not within the region 
        regional_mask = mask_by_region(regional_cube, regional_gdf)
        print('Creating regional_mask)')
    # Copy the original cube (so as changes arent implemented in original cube as well)
    masked_regional_cube = regional_cube.copy()
    # Set cubes data with the mask
    masked_regional_cube.data =  np.ma.masked_array(masked_regional_cube.data, np.logical_not(regional_mask))
    
    # Check plotting
    #qplt.contourf(masked_regional_cube[10,:,:])       
    #plt.gca().coastlines()   
    
    ############################################
    # Find the maximum value in each June-July_August period
    #############################################
    ## Add season and season_year variables
    iris.coord_categorisation.add_season_year(masked_regional_cube,'time', name = "season_year")
    iris.coord_categorisation.add_season(masked_regional_cube,'time', name = "clim_season")
    
    # Aggregate to get just the maximum value in each seasonal yearly period
    annual_seasonal_max = masked_regional_cube.aggregated_by(['season_year', 'clim_season'], iris.analysis.MAX)
    print(annual_seasonal_max)
    
    # Keep only JJA
    jja = annual_seasonal_max.extract(iris.Constraint(clim_season = 'jja'))
    
     
    ############################################
    # Check plotting
    #############################################
    #qplt.contourf(jja[1,:,:])       
    #plt.gca().coastlines()  
    plot_cube_within_region(jja, regional_gdf)
    
    ############################################
    # Reformat for use in R
    #############################################
    # Get the coords 1D
    # lats = jja.coord('grid_latitude').points
    # lons = jja.coord('grid_longitude').points
    
    # # Convert to 2D
    # lats_2d, lons_2d = np.meshgrid(lats, lons)
    
    # # Convert to 1D
    # lats_1d = lats_2d.reshape(-1)
    # lons_1d = lons_2d.reshape(-1)
    
    # Get the coords 1D
    lats_1d = jja.coord('latitude').points
    lons_1d = jja.coord('longitude').points
    
    # Convert to 2D
    #lats_2d, lons_2d = np.meshgrid(lats, lons)
    
    # Convert to 1D
    lats_1d = lats_1d.reshape(-1)
    lons_1d = lons_1d.reshape(-1)
    
    
    # Create dataframe
    #df = pd.DataFrame({'lons': lons_1d, "lats": lats_1d})
    
    #############################
    # Create a dictionary with each key corresponding to a year and the values
    # containing a 1D array of AMAX values, masked to the region of interest
    my_dict = {}
    for i in range(0, jja.shape[0]):
        print(i)
        # Get data from one timeslice
        one_ts = jja[i,:,:]
        # Extract data from one year 
        data = one_ts.data.reshape(-1)
        year  = one_ts.coord('season_year').points[0]
        # Store as dictionary with the year name
        my_dict[year] = data
    
    # Create as a dataframe
    test = pd.DataFrame(my_dict)
    
    # Join with lats and lons
    test['lat'], test['lon'] = [lats_1d, lons_1d]
    
    # Remove NA rows
    test = test.dropna()
    
    # Save dataframe
    ddir = "Outputs/DataforR/{}/".format(region)
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    test.to_csv(ddir + "em{}.csv".format(em), index = False)
    
    
    
    
