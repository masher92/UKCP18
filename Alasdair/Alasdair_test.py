#############################################
#############################################
# Load in required packages
#############################################
#############################################
import iris.coord_categorisation
import iris
import glob
import numpy as np
import os
import sys
import numpy.ma as ma
import iris.plot as iplt
import cartopy.crs as ccrs

#############################################
#############################################
# Define variables and set up environment
#############################################
#############################################
# Define filepath within which data and scripts are found
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# Define ensemble member numbers
ems = ['12','13','15']
yrs_range = "2060_2081" 

#############################################
#############################################
# Cycle through ensemble members
# For each ensemble member: 
#       Read in all files and join into one cube
#       Trim to the outline of the bounding box UK
#       Cut so only hours in month of February remain
#       Find the mean value for each grid square
#############################################
#############################################
# Create a list
cube_list = []     
for em in ems:
    print(em)
    #############################################
    # Data for each ensemble member is stored in monthly files
    # Load in the data for all months for this ensemble member 
    # Join them together to create one cube containing all hours of data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        filenames.append(filename)
    print(len(filenames))
    
    #filenames.remove("datadir/UKCP18/2.2km/11/2060_2081/pr_rcp85_land-cpm_uk_2.2km_11_1hr_20690201-20690230.nc")
    
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    
    #############################################
    ## Trim to outline of UK
    #############################################
    concat_cube = trim_to_bbox_of_uk(concat_cube)
    
    ############################################
    ## Cut to containing only hours of data within February
    #############################################
    # Create time constraint to keep only hours in February
    time_constraint = iris.Constraint(time=lambda c: c.point.month == 2)
    # Apply time constraint
    feb=concat_cube.extract(time_constraint)

    ###########################################
    ## Find the mean value in February
    #############################################
    # Find mean
    feb_mean = feb.aggregated_by(['month_number'], iris.analysis.MEAN)
    # Remove time dimension
    feb_mean = feb_mean[:,0,:,:]
    
    ###########################################
    # Add the february mean results for this ensemble member to the list
    #############################################
    cube_list.append(feb_mean)

#############################################################################
#############################################################################  
# Join together the cubes for all the ensemble members into one 
#############################################################################
#############################################################################
# Convert list into cube list
cube_list2 = copy.deepcopy(cube_list)
#del cube_list2[8:12]
del cube_list2[8:9]

ir_cube_list = iris.cube.CubeList(cube_list2)
# Join all the cubes into the list together
cubes = ir_cube_list.concatenate_cube()


for cube in ir_cube_list:
    print(cube.coordinates)
       for attr in ['creation_date', 'tracking_id', 'history']:
           if attr in cube.attributes:
               del cube.attributes[attr]

#############################################################################
#############################################################################
# Calculate the mean values across the 12 ensemble members
#############################################################################
#############################################################################
em_mean = cubes.collapsed(['ensemble_member'], iris.analysis.MEAN)

#############################################################################
#############################################################################
# Load necessary spatial data
#############################################################################
#############################################################################
# These geodataframes are square
#northern_gdf = create_northern_outline({'init' :'epsg:3857'})
#wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
# This masks out cells outwith the wider northern region
#wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')

# Load mask for UK
#uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  
#uk_mask = uk_mask.reshape(458, 383)


iris.save(em_mean ,"datadir/UKCP18/2.2km/feb_em_means_1980-2001.nc")
iris.save(em_mean ,"datadir/UKCP18/2.2km/feb_em_means_2060-2081.nc")

#############################################################################  
#############################################################################
# Plotting
#############################################################################
#############################################################################
# Mask out data points outside UK
em_mean.data = ma.masked_where(uk_mask == 0, em_mean.data)  

# Trim to smaller area
em_mean = trim_to_bbox_of_region(em_mean, wider_northern_gdf)

# Mask the data so as to cover any cells not within the specified region 
em_mean.data = ma.masked_where(wider_northern_mask == 0, em_mean.data)
# Trim to the BBOX of Northern England
# This ensures the plot shows only the bbox around northern england
# but that all land values are plotted
em_mean = trim_to_bbox_of_region(em_mean, northern_gdf)


# Set up a plotting figurge with Web Mercator projection
proj = ccrs.Mercator.GOOGLE
fig = plt.figure(figsize=(20,20), dpi=200)
ax = fig.add_subplot(122, projection = proj)
mesh = iplt.pcolormesh(em_mean)
# Add regional outlines,
northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03)
cb1.ax.tick_params(labelsize=15)

