import iris.coord_categorisation
import iris
import numpy as np
import os
import geopandas as gpd
import sys
import matplotlib 
import numpy.ma as ma
import warnings
import iris.quickplot as qplt
import iris.plot as iplt
import cartopy.crs as ccrs
from matplotlib import colors
import glob as glob
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Define variables and set up environment
#############################################
timeperiod = 'Baseline' #'Baseline', 'Future_near'
yrs_range = "1980_2001" # "1980_2001", "2020_2041"
resolution = '12km'
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

##################################################################
# Load necessary spatial data
##################################################################
# These geodataframes are square
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outline of the coast of the UK
#uk_gdf = create_uk_outline({'init' :'epsg:3857'})


# Function to reformat the cube
def make_bng_cube(xr_ds,variable):
    # Store the northings values
    raw_northings=xr_ds['y'].values
    # Store the eastings values
    raw_eastings=xr_ds['x'].values
    # Find the length of northings and eastings 
    lrn=len(raw_northings)
    lre=len(raw_eastings)
    # Set up a OS_GB (BNG) coordinate system
    os_gb=TransverseMercator(latitude_of_projection_origin=49.0, longitude_of_central_meridian=-2.0, false_easting=400000.0, false_northing=-100000.0, scale_factor_at_central_meridian=0.9996012717, ellipsoid=GeogCS(semi_major_axis=6377563.396, semi_minor_axis=6356256.909))
    # Create northings and eastings dimension coordinates
    northings = DimCoord(raw_northings, standard_name=u'projection_y_coordinate', 
                         units=Unit('m'), var_name='projection_y_coordinate', coord_system=os_gb)
    eastings = DimCoord(raw_eastings, standard_name=u'projection_x_coordinate', 
                        units=Unit('m'), var_name='projection_x_coordinate', coord_system=os_gb)
    # Create a time dimension coordinate
    iris_time=(xr_ds['time'].values-np.datetime64("1970-01-01T00:00")) / np.timedelta64(1, "s")
    iris_time=DimCoord(iris_time, standard_name='time',units=cf_units.Unit('seconds since 1970-01-01', calendar='gregorian'))
    # Store the data array
    da=xr_ds["pr"]
    # Recreate the cube with the data and the dimension coordinates
    cube = Cube(np.float32(da.values),
                units='mm/hour', 
                dim_coords_and_dims=[(xr_ds['time'].values, 0), (northings, 1),(eastings, 2)])


    return cube




##################################################################
# Trimming to region
##################################################################
for em in ems:
    print(em)
    # Create directory to store outputs in
    ddir = "Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/".format(resolution, timeperiod, em)
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/{}/{}/pr_rcp85_land-rcm_uk_12km_{}_day_*'.format(resolution,em, em)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        print(filename)
        filenames.append(filename)
    print(len(filenames))
       
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    print('Concatenating cube')
    model_cube = monthly_cubes_list.concatenate_cube()      

    ################################################################
    # Cut the cube to the extent of GDF surrounding Leeds  
    ################################################################
    print('trimming cube')
    model_cube = trim_to_bbox_of_region_obs(model_cube, leeds_at_centre_gdf)
    # Test plotting - one timeslice
    #iplt.pcolormesh(model_cube[120])
    
    time_constraint = iris.Constraint(time = lambda cell: cell.point.year  in [1980, 1981,1982, 1983, 1984, 1985, 196, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000])
    model_cube_times = model_cube.extract(time_constraint)    
    
    # Save trimmed netCDF to file    
    print('saving cube')
    iris.save(model_cube_times, "Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/{}/leeds-at-centre.nc".format(resolution, timeperiod,em))
    
    # ################################################################
    # # Once across all ensemble members, save a numpy array storing
    # # the timestamps to which the data refer
    # ################################################################          
    if em == '01':
        times = model_cube_times.coord('yyyymmdd').points
        # Convert to datetime - doesnt work due to 30 days in Feb
        #times = [datetime.datetime.strptime(x, "%Y%m%d%H") for x in times]
        np.save("Outputs/TimeSeries/UKCP18/{}/{}/leeds-at-centre/timestamps.npy".format(resolution, timeperiod), times) 
    
    # ################################################################
    # # Create a numpy array containing all the precipitation values from across
    # # all 20 years of data and all positions in the cube
    # ################################################################
    # Define length of variables defining spatial positions
    lat_length= model_cube_times.shape[1]
    lon_length= model_cube_times.shape[2]
    print("Defined length of coordinate dimensions")
    print(lat_length, lon_length)        
        
    # # # Load data
    print("Loading data")
    data = model_cube_times.data
    print("Loaded data")
    
    # Create an empty array to fill with data
    all_the_data = np.array([])
    
    print("entering loop through coordinates")
    total = 0
    for i in range(0,lat_length):
        for j in range(0,lon_length):
            # Print the position
            print(i,j)
            # Define the filename
            filename = ddir + "{}_{}.npy".format(i,j)
            # If a file of this name already exists saved, then read in this file
            if os.path.isfile (filename):
                print("File exists")
                data_slice = np.load(filename)
            # IF file of this name does not exist, then create by slicing data
            else:
                print("File does not exist")                
                # Take slice from loaded data
                data_slice = data[:,i,j]
                # Remove mask
                data_slice = data_slice.data
                # Save to file
                np.save(filename, data_slice) 
            total = total + data_slice.shape[0]

            # Add the slice to the array containing all the data from all the locations
            all_the_data = np.append(all_the_data,data_slice)
    
    ### Save as numpy array
    print("saving data")
    np.save(ddir + "leeds-at-centre.npy", all_the_data)   
    print("saved data")