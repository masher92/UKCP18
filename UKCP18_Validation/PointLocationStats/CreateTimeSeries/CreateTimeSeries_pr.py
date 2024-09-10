#############################################
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
import iris.plot as iplt
import pandas as pd
#import datetime
warnings.simplefilter(action='ignore', category=FutureWarning)

# Stops warning on loading Iris cubes
#iris.FUTURE.netcdf_promote = True
#iris.FUTURE.netcdf_no_unlimited = True

################################################################
# Define variables and set up environment
################################################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Pr_functions import *
from Spatial_plotting_functions import *

start_year = 1980
end_year = 2001

# Define ensemble member numbers
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

# Define name and coordinates of location
location = 'Armley'
lat = -1.37818
lon = 53.79282

####################################################################
# Read in necessary spatial data
####################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})

################################################################
# Loop through ensemble members, and for each:
    
    
################################################################
for em in ems:
    print ("Checking timeseries for " + location + " using ensemble member " + em + " over years " + str(start_year) + "-" + str(end_year))
    
    # Create paths to the folders where the outputs would be stored
    cubefolder_fp = root_fp + "Outputs/TimeSeries/UKCP18/{}/2.2km/Baseline/TimeSeries_cubes".format(location)
    cube_fp =  cubefolder_fp + '/EM{}_{}-{}.nc'.format(em, start_year, end_year)
    csvfolder_fp =root_fp + "Outputs/TimeSeries/UKCP18/{}/2.2km/TimeSeries_csv".format(location)
    csv_fp = csvfolder_fp + '/EM{}_{}-{}.csv'.format(em, start_year, end_year)
    
    # If both the csv and the cube exist, then read them from their location
    if os.path.exists(csv_fp) & os.path.exists(cube_fp):
        print (csv_fp + " and " + cube_fp + ' already exist.')
        
    # If either the csv or the cube doesn't exist, then run the code to create them
    else:
        print("Either " + csv_fp + " or " + cube_fp + ' does not exist, creating...')
        
        # Define the local directory where the data is stored
        if 1980 <= start_year <= 2001:
          yrs_range = "1980_2001" 
        elif 2020 <= start_year <= 2041:
           yrs_range = "2020_2041" 
        elif 2060 <= start_year <= 2081:
           yrs_range = "2060_2081"  
      
        # Create list of names of cubes for between the years specified
        filenames =[]
        for year in range(start_year,end_year+1):
            # Create filepath to correct folder using ensemble member and year
            general_filename = root_fp + 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_{}*'.format(em, yrs_range, em, year)
            #print(general_filename)
            # Find all files in directory which start with this string
            for filename in glob.glob(general_filename):
                #print(filename)
                filenames.append(filename)

        # Load in filenames into a cube
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

        #############################################
        # Convert the WGS coordinates of the point of interest into the same coordinate
        # system as the precipitation cubes (e.g. rotated pole)
        #############################################
        # Store the coordinate system of the cube
        cs = monthly_cubes_list[0].coord_system()
        
        # Define the location of interest in rotated pole coordinate system
        sample_point = define_loc_of_interest(monthly_cubes_list, lon, lat)
        
        # Reconvert the sample point into lat and longs to check
        #lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(sample_point[1][1]), np.array(sample_point[0][1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        
        #############################################
        # Create a cube containing a precipitation timeseries for the 
        # location of interest
        #############################################    
        start = timer()
        results = create_concat_cube_one_location_m3(concat_cube, sample_point)
        ts_cube = results[0]
        print("Cubes joined and interpolated to location at " + str(lat)+ "," + str(lon) + ' in ' + str(round((timer() - start)/60, 1)) + ' minutes')
        
        # Check centre location of grid cell it used (in lat, lon)
        lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(results[2]), np.array(results[1]), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
        # Find the index of the closest point
        index = results[3]

        #############################################
        # Convert to a dataframe
        #############################################
        print("Converting to dataframe")       
        start_dfconversion_timer = timer()
        ts_df = pd.DataFrame({'Date': np.array(ts_cube.coord('yyyymmddhh').points),
                          'Precipitation (mm/hr)': np.array(ts_cube.data)})
        print("Cube converted to DF in " + str(round((timer() - start_dfconversion_timer)/60, 1)) + ' minutes')
        
        # Format the date column
        ts_df['Date_Formatted'] =  pd.to_datetime(ts_df['Date'], format='%Y%m%d%H',  errors='coerce')
        
        ###########################################################
        # Save cube  and df
        ###########################################################
        # Create directory if it doesn't exist already
        if not os.path.isdir(cubefolder_fp):
            os.makedirs(cubefolder_fp)
        # Save cube
        print("Saving cube to " + cube_fp)
        start_saving_timer = timer()
        iris.save(ts_cube, cube_fp)  
        print("Cube saved in " + str(round((timer() - start_saving_timer)/60, 1)) + ' minutes')
        print("Cube saved in " + str(round(timer() - start_saving_timer, 1)) + ' seconds')
          
        # Create directory if it doesn't exist already
        if not os.path.isdir(csvfolder_fp):
            os.makedirs(csvdolder_fp)
        # Write to a csv
        ts_df.to_csv(csv_fp, index = False)
        print("Saving csv to " + csv_fp)
        print("Complete")

        #############################################      
        # Check results
        #############################################
        # Create a test dataset with all points with same value
        # Set value at the index returned above to something different
        # And then plot data spatially, and see which grid cell is highlighted.        
        test_data = np.full((hour_uk_cube.shape), 0, dtype=int)
        test_data_rs = test_data.reshape(-1)
        test_data_rs[index] = 500
        test_data = test_data_rs.reshape(test_data.shape)
        
        hour_uk_cube.data = test_data
        qplt.pcolormesh(hour_uk_cube)
                       
    #############################################################################
    # Generate test data
    ##############################################################################
    one_hour = concat_cube[0,0,:,:]
    iplt.pcolormesh(one_hour)
    
    iplt.pcolormesh(hour_uk_cube)
    
    # Create a test dataset with all points with value 0
    # Set value(s) at the indexes of the grid cells closest to the sample point as 1
    # And then plot data spatially, and see which grid cell(s) are highlighted.   
    test_data = np.full((one_hour.shape), 0, dtype=int)

    test_data_rs = test_data.reshape(-1)
    test_data_rs[index] = 1
    test_data = test_data_rs.reshape(test_data.shape)
    
    import numpy.ma as ma
    import matplotlib as mpl
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Find cornerpoint coordinates
    lats_cornerpoints = find_cornerpoint_coordinates(concat_cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(concat_cube)[1]
    
    # Trim the data timeslice to be the same dimensions as the corner coordinates
    test_data = test_data[1:,1:]
        
    #############################################################################
    #### # Plot - highlighting grid cells whose centre point falls within Leeds
    # Uses the lats and lons of the corner points but with the values derived from 
    # the associated centre point
    ##############################################################################
    cmap = mpl.colors.ListedColormap(['royalblue'])
    
    fig, ax = plt.subplots(figsize=(20,10))
    extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf)
    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
    plot =plotter.plot(ax)
    # Add edgecolor = 'grey' for lines
    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, test_data,
                  linewidths=1, alpha = 1, edgecolors = 'grey')
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)        

one_hour.data = test_data
iplt.pcolormesh(one_hour)
