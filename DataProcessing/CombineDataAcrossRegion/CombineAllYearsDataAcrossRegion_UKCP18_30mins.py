import iris
import os
import glob as sir_globington_the_file_gatherer
import datetime as datetime
import iris.coord_categorisation as cat
import sys
import time
import multiprocessing as mp
import glob as glob

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/PhD/"
os.chdir(root_fp)

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

##################################################################
# Load necessary spatial data
##################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
uk_gdf = create_uk_outline({'init' :'epsg:3857'})
gb_gdf = create_gb_outline({'init' :'epsg:3857'})
##################################################################

# ### Establish the ensemble member
trim_to_leeds = False

ems= ['bc005', 'bc006', 'bc007', 'bc009', 'bc010', 'bc011', 'bc013',  'bc015',  'bc016', 'bc017', 'bc018', 'bc012']
yrs_range = "2002_2020"
resolution = '2.2km' #2.2km, 12km, 2.2km_regridded_12km
in_jja=iris.Constraint(time=lambda cell: 6 <= cell.point.month <= 8)
yrs= range(2002,2020)


em = 'bc006'
for yr in yrs:
    ddir = f"ProcessedData/TimeSeries/UKCP18_every30mins/{resolution}/{yrs_range}/{em}_wholeyear/"
    if not os.path.isfile(ddir + f'{yr}_timevalues.npy'):
        print(em, yr, resolution)

        ### Save as numpy array
        #print("saving data")
        if not os.path.isdir(ddir):
            os.makedirs(ddir)

        # ### Get a list of filenames for this ensemble member, for just JJA
        if resolution == '2.2km':
            general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/{em}/{yrs_range}/{em}a.pr{yr}*'
        elif resolution == '12km':
              general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/{em}/{yrs_range}/pr_rcp85_land-rcm_uk_12km_{em}_day_*'
        elif resolution == '2.2km_regridded_12km':
            general_filename = f'/nfs/a319/gy17m2a/PhD/datadir/UKCP18_every30mins/{resolution}/{em}/NearestNeighbour/{yrs_range}/rg_{em}a.pr{yr}*'
        general_filename

        filenames = []
        for filename in glob.glob(general_filename):
            if '2000' not in filename and 'pr2020' not in filename:
                filenames.append(filename)
        print(len(filenames))

        ### Load in the data
        monthly_cubes_list = iris.load(filenames)

        ### Concatenate cubes into one
        model_cube = monthly_cubes_list.concatenate_cube()      

        # ### Trim to UK
        if resolution  == '2.2km':
            masked_cube = trim_to_bbox_of_region_regriddedobs(model_cube, gb_gdf)
        else:
            masked_cube = trim_to_bbox_of_region_obs(model_cube, gb_gdf)


        ### Get the mask
        print("getting mask")
        if resolution =='2.2km':
            gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_2.2km_GB_Mask.npy")
        else:
            gb_mask = np.load("/nfs/a319/gy17m2a/PhD/datadir/UKCP18_12km_GB_Mask.npy")


          # masked_cube_data = masked_cube * gb_mask[np.newaxis, :, :]

        # # APPLY THE MASK
        reshaped_mask = np.tile(gb_mask, (masked_cube.shape[0], 1, 1))
        reshaped_mask = reshaped_mask.astype(int)
        reversed_array = ~reshaped_mask.astype(bool)

        # Mask the cube
        masked_cube = iris.util.mask_cube(masked_cube, reversed_array)  

        # Check the plotting
        #iplt.contourf(masked_cube[10])
        #plt.gca().coastlines(resolution='10m', color='black', linewidth=0.5);

        # Get rid of negative values
        compressed = masked_cube.data.compressed()
        print(f"compressed has length: {compressed.shape[0]}")

        ########
        # Get the times
        ########
        # Step 2: Get the indices of the non-masked values in the original data
        non_masked_indices = np.where(~masked_cube.data.mask)

        # Step 3: Extract corresponding time values
        time_values = masked_cube.coord('time').points[non_masked_indices[0]]

        # Save to file
        if not os.path.isfile(ddir + f'timevalues.npy'):
            np.save(ddir + f'timevalues.npy', time_values) 
        np.save(ddir + f'{yr}_compressed.npy', compressed) 
        iris.save(masked_cube, ddir + f'{yr}_maskedcube.nc') 
    else:
        print(f"{yr} already exists")