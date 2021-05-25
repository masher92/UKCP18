#############################################################################
# Set up environment
#############################################################################
import numpy as np
import os
import pandas as pd
import glob
from shapely.geometry import Point, Polygon
import sys
from pyproj import Proj, transform
import iris.plot as iplt
import matplotlib as mpl
import warnings

# Set up path to root directory
root_fp = '/nfs/a319/gy17m2a/'
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *
from Pr_functions import *
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

warnings.simplefilter(action='ignore', category = FutureWarning)
warnings.simplefilter(action='ignore', category = DeprecationWarning)

#############################################################################
#############################################################################
# Load in spatial data
# As geodataframes for plotting
# As shapely geometries for checking whether lat/long points are witihn the areas
#############################################################################
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

# Create outlines as shapely geometries
leeds_at_centre_poly = Polygon(create_leeds_at_centre_outline({'init' :'epsg:4326'})['geometry'].iloc[0])
leeds_poly = Polygon(create_leeds_outline({'init' :'epsg:4326'})['geometry'].iloc[0])

#############################################################################
#############################################################################
## Load in the reformatted observations cubes 
# and concatenate into one cube
# and trim to leeds-at-centre region
#############################################################################
#############################################################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_*'
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    #print(filename)
    filenames.append(filename)
    print(len(filenames))
# Load all cubes into list
monthly_cubes_list = iris.load(filenames,'rainfall_amount')

# Concatenate the cubes into one
obs_cube = monthly_cubes_list.concatenate_cube()

## Trim concatenated cube to outline of leeds-at-centre geodataframe
obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)

# Test plotting
iplt.pcolormesh(obs_cube[12])

#############################################################################
#############################################################################
## Load in UKCP18 data and concatenate into one cube
#############################################################################
#############################################################################
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']
ems_cubes = {}
for em in ems:
    print(em)
    # Load cube trimmed to Leeds at centre region
    filename = "Outputs/TimeSeries/UKCP18/leeds-at-centre/{}/leeds-at-centre.nc".format(em)
    em_cube = iris.load(filename, 'lwe_precipitation_rate')[0]
    ems_cubes[em] = (em_cube)

# Test plotting
iplt.pcolormesh(em_cube[12])

#############################################################################
#############################################################################
# Loop through every text file in the directory
# Check if its lat-long coordinates are within the leeds-at-centre area
# If so, then find the date times that correspond to the precipitation values
# and save as a CSV.
#############################################################################
#############################################################################
for filename in glob.glob("datadir/GaugeData/Newcastle/E*"):
    with open(filename) as myfile:
        # read in the lines of text at the top of the file
        firstNlines=myfile.readlines()[0:21]
        
        # Extract the lat, lon and station name
        station_name = firstNlines[3][23:-1]
        lat = float(firstNlines[5][10:-1])
        lon = float(firstNlines[6][11:-1])
        
        # Check if point is within leeds-at-centre geometry
        this_point = Point(lon, lat)
        res = this_point.within(leeds_poly)
       
        # If the point is within leeds-at-centre geometry 
        if res ==True :
            print(station_name)
            print(lat,lon)
           
            # ############################################################################
            # # Create a csv containing the data and the dates
            # ############################################################################
            # #Read in data entries containing precipitation values
            # data=np.loadtxt(filename, skiprows = 21)
            
            # # Store start and end dates
            # startdate = firstNlines[7][16:26]
            # enddate = firstNlines[8][14:24]

            # # Convert to datetimes
            # d1 = datetime(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8]), int(startdate[8:10]))
            # d2 = datetime(int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), int(enddate[8:10]))
            
            # # Find all hours between these dates
            # time_range = pd.date_range(d1, d2, freq='H')    
            
            # # Check if there are the correct number
            # n_lines = firstNlines[10][19:-1]
            # if int(n_lines) != len(time_range):
            #     print('Incorrect number of lines')
            
            # # Create dataframe containing precipitation values as times
            # precip_df = pd.DataFrame({'Datetime': time_range,
            #                           'Precipitation (mm/hr)': data})
            
            # # Save to file
            # precip_df.to_csv("datadir/GaugeData/Newcastle/leeds-at-centre_csvs/{}.csv".format(station_name),
            #                   index = False)

            #############################################################################
            # Create a csv containing the data and the dates for the CEH-GEAR grid cell which
            # the gauge is located within
            #############################################################################
            #  Create time series cube at this location, and return the associated         
            result_obs= create_concat_cube_one_location_obs(obs_cube, lat, lon)
            
            #Split out results
            obs_cube_thisloc, closest_lat, closest_long, closest_point_idx = result_obs[0], result_obs[1], result_obs[2], result_obs[3]

            # Save the cube
            #iris.save(obs_cube_thisloc, 
            #"Outputs/TimeSeries/CEH-GEAR/Gauge_GridCells/TimeSeries_cubes/{}.nc".format(station_name))

            # Create dataframe with timeseries
            #ts_df = pd.DataFrame({'Date_formatted': obs_cube_thisloc.coord('time').units.num2date(obs_cube_thisloc.coord('time').points),
            #                  'Precipitation (mm/hr)': np.array(obs_cube_thisloc.lazy_data())})
            
            # Save to file
            #ts_df.to_csv("Outputs/TimeSeries/CEH-GEAR/Gauge_GridCells/TimeSeries_csv/{}.csv".format(station_name),
            #index= False)
             
            #############################################################################
            #############################################################################
            ## Check that the data has been extracted for the correct location
            # By creating a cube in which all the data values have been masked out
            # except from at the grid cell identified by closest_point_idx
            #############################################################################
            #############################################################################
            # Create cube with all values masked out except from cell at closest_point_idx
            cube_higlighted_cell = create_grid_highlighted_cell_obs(obs_cube, closest_point_idx)
            cube_higlighted_cell_data = cube_higlighted_cell.data
            
            # Find cornerpoint coordinates (for use in plotting)
            lats_cornerpoints = find_cornerpoint_coordinates_obs(cube_higlighted_cell)[0]
            lons_cornerpoints = find_cornerpoint_coordinates_obs(cube_higlighted_cell)[1]
            
            # Trim the data timeslice to be the same dimensions as the corner coordinates
            cube_higlighted_cell_data = cube_higlighted_cell_data[1:,1:]

            #############################################################################
            #### # Plot - highlighting grid cells whose centre point falls within Leeds
            # Uses the lats and lons of the corner points but with the values derived from 
            # the associated centre point
            ##############################################################################
            # Create location in web mercator for plotting
            lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
            
            # Create a colormap
            cmap = mpl.colors.ListedColormap(['yellow'])
            
            fig, ax = plt.subplots(figsize=(30,30))
            extent = tilemapbase.extent_from_frame(leeds_gdf)
            plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
            plot =plotter.plot(ax)
            # Add edgecolor = 'grey' for lines
            plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cube_higlighted_cell_data,
                  linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')
            plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
            plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
            plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
            plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
            plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 10)     
            plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Validating_CEH-GEAR/Figs/CheckingLocations/CEH-GEAR/{}.png'.format(station_name),
                        bbox_inches = 'tight')
            plt.show()

            #############################################################################
            # Create a csv containing the data and the dates for the UKCP18 grid cell which
            # the gauge is located within
            #############################################################################
            for em in ems:
                print(em)
                em_cube = ems_cubes[em]
                
                # Define a sample point in the correct projection
                sample_point = define_loc_of_interest(em_cube, lon, lat)    
                # Create time series cube at this location, and return the associated   
                result_model= create_concat_cube_one_location_m3(em_cube, sample_point)
                # Split out results
                time_series_cube, closest_lat, closest_long, closest_point_idx = result_model[0], result_model[1], result_model[2], result_model[3]
                
                # # Check centre location of grid cell it used (in lat, lon)
                # cs = em_cube[0].coord_system() # coordinate system of original cube
                # lon_calc, lat_calc = iris.analysis.cartography.unrotate_pole(np.array(closest_long), np.array(closest_lat), cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)
                # print(lat_calc, lon_calc)
    
                # # Save the cube
                # print('Saving cube')
                # iris.save(time_series_cube, 
                # "Outputs/TimeSeries/UKCP18/Gauge_GridCells/TimeSeries_cubes/{}_{}.nc".format(station_name, em))
    
                # ## Create dataframe with timeseries
                # print("Creating DF")
                # ts_df = pd.DataFrame({'Date_formatted': time_series_cube.coord('time').units.num2date(time_series_cube.coord('time').points),
                #                   'Precipitation (mm/hr)': np.array(time_series_cube.lazy_data())})
                # print('saving DF')
                # # Save to file
                # ts_df.to_csv("Outputs/TimeSeries/UKCP18/Gauge_GridCells/TimeSeries_csv/{}_{}.csv".format(station_name, em),
                #              index= False)
                 
                #############################################################################
                ## Check that the data has been extracted for the correct location
                # By creating a cube in which all the data values have been masked out
                # except from at the grid cell identified by closest_point_idx
                #############################################################################
                if em == '01':
                    # Create cube with all values masked out except from cell at closest_point_idx
                    cube_higlighted_cell = create_grid_highlighted_cell(em_cube, closest_point_idx)
                    cube_higlighted_cell_data = cube_higlighted_cell.data
                    
                    # Find cornerpoint coordinates (for use in plotting)
                    lats_cornerpoints = find_cornerpoint_coordinates(cube_higlighted_cell)[0]
                    lons_cornerpoints = find_cornerpoint_coordinates(cube_higlighted_cell)[1]
                    
                    # Trim the data timeslice to be the same dimensions as the corner coordinates
                    cube_higlighted_cell_data = cube_higlighted_cell_data[1:,1:]
        
                    #############################################################################
                    #### # Plot - highlighting grid cells whose centre point falls within Leeds
                    # Uses the lats and lons of the corner points but with the values derived from 
                    # the associated centre point
                    ##############################################################################
                    # Create location in web mercator for plotting
                    print('Creating plot')
                    lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
                    
                    # Create a colormap
                    cmap = mpl.colors.ListedColormap(['yellow'])
                    
                    fig, ax = plt.subplots(figsize=(30,30))
                    extent = tilemapbase.extent_from_frame(leeds_gdf)
                    plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=500)
                    plot =plotter.plot(ax)
                    # Add edgecolor = 'grey' for lines
                    plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cube_higlighted_cell_data,
                          linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')
                    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
                    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
                    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
                    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
                    plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 10)     
                    plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Validating_CEH-GEAR/Figs/CheckingLocations/UKCP18/{}_{}.png'.format(station_name, em),
                                bbox_inches = 'tight')
                    plt.show()
    
        