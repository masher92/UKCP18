##################################################################
# This Script:
#    - Gets all 30 mins radar files for one year
#    - Joins them and masks out values over the sea
#    - Gets a 1D array of the data and removes masked out (over the sea
#      values) and np.nan values
##################################################################


##################################################################
# SET UP ENVIRONMENT
##################################################################
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
import datetime
warnings.simplefilter(action = 'ignore', category = FutureWarning)
from iris.experimental.equalise_cubes import equalise_attributes

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, '/nfs/a319/gy17m2a/PhD/Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

resolution = '12km'
filtering_name='filtered_100'

##################################################################
# FOR ONE YEAR AT A TIME
##################################################################
##################################################################
# FOR ONE YEAR AT A TIME
##################################################################
for year in range(2015,2016):
    print(year)
    
    if not  os.path.isfile("/nfs/a319/gy17m2a/PhD/" + ddir + f'compressed_{year}.npy'):
    
        # Create directory to store outputs in and get general filename to load files from
        if resolution =='1km':
            ddir = f"ProcessedData/TimeSeries/NIMROD/30mins/OriginalFormat_1km/"
            general_filename = f'datadir/NIMROD/30mins/OriginalFormat_1km/{year}/*'      
        elif resolution == '2.2km':
            ddir = f"ProcessedData/TimeSeries/NIMROD/30mins/NIMROD_regridded_2.2km/"
            general_filename = f'datadir/NIMROD/30mins/NIMROD_regridded_2.2km/{filtering_name}/AreaWeighted/{year}/*'        
        elif resolution == '12km':
            ddir = f"ProcessedData/TimeSeries/NIMROD/30mins/NIMROD_regridded_12km/"    
            general_filename = f'datadir/NIMROD/30mins/NIMROD_regridded_12km/{filtering_name}/AreaWeighted/{year}/*'      
        if not os.path.isdir(ddir):
            os.makedirs(ddir)

        # GET LIST OF ALL FILENAMES FOR THIS YEAR
        filenames =[]
        # Find all files in directory which start with this string
        for filename in glob.glob(general_filename):
            # print(filename)
            filenames.append(filename)
        print(f"loading {len(filenames)} filenames")
        sorted_list = sorted(filenames)

        # LOAD THE DATA
        monthly_cubes_list = iris.load(sorted_list)

        ##################################################################
        # CLEAN AND JOIN THE DATA
        ##################################################################
        # Try to make attributes the same
        iris.util.equalise_attributes(monthly_cubes_list)

        for cube in monthly_cubes_list:
            cube.rename("Rain rate Composite")    

        # CONVERT TO FLOAT64
        for i in range(0, len(monthly_cubes_list)):
            monthly_cubes_list[i].data = monthly_cubes_list[i].data.astype('float64')

        model_cube = monthly_cubes_list.concatenate_cube()

        print(model_cube.coord('time')[0])
        print(model_cube.coord('time')[-1])

        # Get rid of negative values
        compressed = model_cube.data.compressed()
        compressed.shape[0]

        ########
        # Get the times
        ########
        # Step 3: Extract corresponding time values
        time_values = model_cube.coord('time')

        # Save to file
        np.save("/nfs/a319/gy17m2a/PhD/" + ddir + f'timevalues.npy', time_values) 
        np.save("/nfs/a319/gy17m2a/PhD/" + ddir + f'compressed_{year}_{filtering_name}.npy', compressed) 

        # Generate the plot
        iplt.contourf(model_cube[10])

        # Add a title, labels, or any customization if needed
        plt.title("Contour Plot of Model Cube at Index 10")
        plt.xlabel("X Coordinate")
        plt.ylabel("Y Coordinate")

        # Save the figure to a file
        plt.savefig("/nfs/a319/gy17m2a/PhD/" + ddir + f"model_cube_contour_{year}.png", dpi=300, bbox_inches='tight')    
    else:
        print(f"Already exists for {year}")
