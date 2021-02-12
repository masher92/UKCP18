###### Notes on structure of these cubes
# This IRIS cube has a different structure to the UKCP18 data.
# This is something to do with it being in the rotated pole co-ordinate system
# Latitude and longitude are provided on 2d Array. Imagine that the values
# for these that correspond would appear on top of each other if these arrays
# were stacked. I.e. accessing the values from the arrays with the same index
# gives corresponding values. 
#sss

# Import packages
from numpy import array, shape
import numpy as np
import iris
import matplotlib as mpl
import os
import matplotlib.pyplot as plt
import iris.plot as iplt
import iris.quickplot as qplt
from iris.time import PartialDateTime 
import pandas as pd
from timeit import default_timer as timer
import warnings
warnings.simplefilter(action='ignore', category=UserWarning)
import sys 
import glob

# Stops warning on loading Iris cubes
iris.FUTURE.netcdf_promote = True
iris.FUTURE.netcdf_no_unlimited = True

# Provide root_fp as argument
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Obs_functions import *
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Define name and coordinates of location
location = 'Armley'
lat = 53.79282
lon = -1.37818

#############################################################################
# Load in spatial data
# As geodataframes for plotting
# As shapely geometries for checking whether lat/long points are witihn the areas
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

#############################################################################
## Load in the reformatted observations cubes 
# and concatenate into one cube
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
concat_cube = monthly_cubes_list.concatenate_cube()

# Test plotting
iplt.pcolormesh(concat_cube[12])

#############################################################################
## Trim concatenated cube to outline of leeds-at-centre geodataframe
#############################################################################
concat_cube = trim_to_bbox_of_region_obs(concat_cube, leeds_at_centre_gdf)

# Test plotting
iplt.pcolormesh(concat_cube[12])

############################################################
# Create time series cube at this location, and return the associated   
############################################################
# Create time series cube at this location, and return the associated         
result = create_concat_cube_one_location_obs(concat_cube, lat, lon)

# Split out results
time_series_cube, closest_lat, closest_long, closest_point_idx = result[0], result[1], result[2], result[3]

#############################################################################
## Check that the data has been extracted for the correct location
# By creating a cube in which all the data values have been masked out
# except from at the grid cell identified by closest_point_idx
#############################################################################
# Create cube with all values masked out except from cell at closest_point_idx
cube_higlighted_cell = create_grid_highlighted_cell(concat_cube, closest_point_idx)
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

fig, ax = plt.subplots(figsize=(20,10))
extent = tilemapbase.extent_from_frame(leeds_gdf)
plot = plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot =plotter.plot(ax)
# Add edgecolor = 'grey' for lines
plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cube_higlighted_cell_data,
      linewidths=0.4, alpha = 1, cmap = cmap, edgecolors = 'grey')
plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
plt.plot(lon_wm, lat_wm,  'o', color='black', markersize = 2)     
#plt.savefig('Scripts/UKCP18/RainGaugeAnalysis/Figs/NewcastleGaugeGridCells/{}.png'.format(station_name))
plt.show()
   

#############################################################################
# Cut to time period matching up with UKCP18 data
##############################################################################
# Time constraint for which to test the data
days_constraint = iris.Constraint(time=lambda cell: PartialDateTime(year = 1990, month=1, day=11) < cell.point < PartialDateTime(year = 2001, month=1, day=1))

# Trim data to this time period
time_series_cube_1990_2001 = time_series_cube.extract(days_constraint)

############################################################################
# Create as dataframe
##############################################################################
# Create a dataframe containing the date and the precipitation data
df = pd.DataFrame({'Date': np.array(time_series_cube.coord('time').points),
                  'Precipitation (mm/hr)': np.array(time_series_cube.data),
                  'Date_formatted': time_series_cube.coord('time').units.num2date(time_series_cube.coord('time').points)})

# Create a dataframe containing the date and the precipitation data
df_1990_2001 = pd.DataFrame({'Date': np.array(time_series_cube_1990_2001.coord('time').points),
                  'Precipitation (mm/hr)': np.array(time_series_cube_1990_2001.data),
                  'Date_formatted': time_series_cube_1990_2001.coord('time').units.num2date(time_series_cube_1990_2001.coord('time').points)})

###########################################################
# Save cube and csv
###########################################################
iris.save(time_series_cube, 
          "/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_cubes/1990-2014.nc")
iris.save(time_series_cube_1990_2001, 
          "/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_cubes/1990-2001.nc")

df.to_csv("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_csv/1990-2014.csv", index = False)
df_1990_2001.to_csv("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/Armley/TimeSeries_csv/1990-2001.csv", index = False)


### Save the coordinates for which the data was extracted
coordinates_str = "latitude: " + str(lat) + ", longitude: " + str(lon)
f =open("/nfs/a319/gy17m2a/Outputs/TimeSeries/CEH-GEAR/{}/location_coordinates.txt".format(location), "w")
f.write(coordinates_str)
f.close()