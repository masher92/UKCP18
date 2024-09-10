import iris
import os 
import matplotlib.pyplot as plt
import sys
import matplotlib as mpl
import iris.plot as iplt

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/RegriddingObservations')
from Regridding_functions import plot_grid_highlight_cells

####################################################################
# Read in necessary spatial data
####################################################################
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})

####################################################################
# Load model and observations (native, regridded, reformatted) cubes
####################################################################
filename_model = 'datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc'
model = iris.load(filename_model,'lwe_precipitation_rate')[0]
model = model[0,:,:,:]

#Filename of cube
filename = "datadir/CEH-GEAR/CEH-GEAR-1hr_199001.nc"
obs = iris.load(filename)[0]

# Filename of reformatted cube
filename_reformat = "Outputs/RegriddingObservations/CEH-GEAR_reformatted/rf_CEH-GEAR-1hr_199001.nc"
obs_rfmt = iris.load(filename_reformat)[0]

# Filename of regridded cube
filename_regrid = "Outputs/RegriddingObservations/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_CEH-GEAR-1hr_199001.nc"
obs_rgd = iris.load(filename_regrid)[0]


hour = model[0,:,:]
iplt.pcolormesh(hour)
cube = model

def plot_cube_grid(cube, 
    
    #############################################################################
    # Generate test data
    ##############################################################################
    # Create a test dataset with all points with value 0
    # Set value(s) at the indexes of the grid cells closest to the sample point as 1
    # And then plot data spatially, and see which grid cell(s) are highlighted.   
    test_data = np.full((cube[0].shape), 0, dtype=int)
    if closest_point_idx is not None:
      test_data_rs = test_data.reshape(-1)
      test_data_rs[closest_point_idx] = 1
      test_data = test_data_rs.reshape(test_data.shape)
    
    test_data = ma.masked_where(test_data<1,test_data)
    
    # Find cornerpoint coordinates
    lats_cornerpoints = find_cornerpoint_coordinates(cube)[0]
    lons_cornerpoints = find_cornerpoint_coordinates(cube)[1]
    
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
                  linewidths=1, alpha = 1, cmap = cmap, edgecolors = 'grey')
    plot = ax.xaxis.set_major_formatter(plt.NullFormatter())
    plot = ax.yaxis.set_major_formatter(plt.NullFormatter())
    plot =leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    plot =leeds_at_centre_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=2)
    

  