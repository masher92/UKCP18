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
warnings.simplefilter(action = 'ignore', category = FutureWarning)

def namestr(obj, namespace):
    return [name for name in namespace if namespace[name] is obj]

root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

############################################
# Define variables and set up environment
#############################################
# List of ensemble members
ems = ['01', '04', '05', '06', '07', '08', '09','10','11','12', '13','15']

# Plotting variables
shared_axis = False

# PLotting region
region = 'leeds-at-centre'
#region = ['Northern', 'leeds-at-centre', 'UK']

##################################################################
# Load necessary spatial data
##################################################################
# Load required geodataframes
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
northern_gdf = create_northern_outline({'init' :'epsg:3857'})
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})

# Load mask for wider northern region
mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')
  
##################################################################
# Create dictionaries storing the maximum and minimum values found for 
# each statistic, considering all ensemble members and all grid cells
##################################################################
# List of stats to loop through
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

# Create a dictionary.
# The keys will be ensemble member numbers and the values will be dictionarys
# Each ensemble member's dictionary will in turn have statistic names as keys
# and the cube of that statistic as values
ems_dict = {}
# Create dictionaries to store max and min values for each stat
max_vals_dict = {}
min_vals_dict = {}

# Loop through ensemble members
for em in ems:
    print(em)
    # Create dictionary for that ensemble member to store results of differnet stats
    em_dict = {}
    # Loop through stats
    for stat in stats:
          # Load in netcdf files containing the stats data over the whole UK
          stat_cube = iris.load('/nfs/a319/gy17m2a/Outputs/UK_stats_netcdf/em_'+ em+ '_' + stat + '.nc')[0] 
          
          # Trim to smaller area
          if region == 'Northern':
              stat_cube = trim_to_bbox_of_region(stat_cube, wider_northern_gdf)
          elif region == 'leeds-at-centre':
              stat_cube = trim_to_bbox_of_region(stat_cube, leeds_at_centre_gdf)
              
          # If this is the first time through the loop e.g. the first ensemble member, 
          # then create dictionary which will store the max and min values for each 
          # statistic across all the ensemble members
          if em == '01':
            # Loop through stats setting max = 10000 and min = 0
            #name = namestr(stat, globals())[0]
            max_vals_dict[stat] = 0
            min_vals_dict[stat] = 10000
          # For all ensemble members store the file in a dictionary
          # And check if it's max/min value is higher/lower than the current value
          # and store it if it is
          print(stat)
          print (stat_cube.data.max()) 
          em_dict[stat] = stat_cube
          max_vals_dict[stat] = stat_cube.data.max() if stat_cube.data.max() > max_vals_dict[stat] else max_vals_dict[stat]
          min_vals_dict[stat] = stat_cube.data.min() if stat_cube.data.min() < min_vals_dict[stat] else min_vals_dict[stat]       
          
          # Save the dictionary of stat cubes to 
          ems_dict[em] = em_dict         

#############################################
# Plotting
#############################################
# Create a colourmap                                   
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      
precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="white")

# stats = []
# for key, value in em_dict.items() :
#     stats.append(key)
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

for stat in stats:
    print(stat)
    # Extract the max, min values
    # For shared axis plotting
    max_value = max_vals_dict[stat]
    min_value = min_vals_dict[stat]
    # Set up counters
    i=1
    # Set up plot
    if region == 'Northern':
        fig=plt.figure(figsize=(24,32))
    elif region == 'leeds-at-centre':
        fig=plt.figure(figsize=(24,24))
    columns = 3
    rows = 4
    
    #for new_i in range(1, 13):
    for em in ems:
        # Extract data for correct ensemble member and stat
        # Remove time dimension (only had one value)
        em_dict = ems_dict[em]
        stats_cube = em_dict[stat][0]
                  
        # Mask the data so as to cover any cells not within
        # The wider northern region
        if region == 'Northern':
            stats_cube.data = ma.masked_where(mask == 0, stats_cube.data)
            # Trim to the BBOX of Northern England
            # This ensures the plot shows nly the bbox around northern england
            # but that all land values are plotted
            stats_cube = trim_to_bbox_of_region(stats_cube, northern_gdf)
    
        # Extract lats and lons for ploting and change projection
        lats_2d = stats_cube.coord('latitude').points
        lons_2d = stats_cube.coord('longitude').points
        lons_2d, lats_2d = transform(Proj(init='epsg:4326'),Proj(init='epsg:3857'),lons_2d, lats_2d)
         
        ax = plt.gca()
        
        
        #lats_2d, lons_2d =find_cornerpoint_coordinates(stats_cube)   
        #stats_cube = stats_cube[0:32,0:36]

        # CHecking plotting 
        
        qplt.pcolormesh(stats_cube)
        qplt.contourf(stats_cube)
        
        fig, ax = plt.subplots()
        my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3)
                             # alpha = 1, cmap = precip_colormap, vmin =0, vmax = 175)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        #northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        fig.colorbar(my_plot, ax=ax, fraction=0.06, pad=0.02)
        
        fig1 = plt.figure()
        ax = plt.gca()
       # ax= fig1.add_subplot(2,1,1)
        #fig, ax = plt.subplots()
        qplt.contourf(stats_cube, axes=ax)
        
                             # alpha = 1, cmap = precip_colormap, vmin =0, vmax = 175)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        #northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        fig.colorbar(my_plot, ax=ax, fraction=0.06, pad=0.02)
        
        proj = ccrs.Mercator.GOOGLE
        ax = plt.subplot(122, projection=proj)
        qplt.pcolormesh(stats_cube, 25)
        #iplt.pcolormesh(stats_cube,cmap = precip_colormap, 25)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        #plt.gca().coastlines()
        plt.show()
        
        ######################### 
        # Think this is what is needed
        # Need to work out subplotting
        plt.axes(projection=ccrs.Mercator.GOOGLE)
        # Make a pseudocolour plot using this colour scheme.
        mesh = iplt.pcolormesh(stats_cube, cmap=precip_colormap)
        # Add a colourbar, with extensions to show handling of out-of-range values.
        bar = plt.colorbar(mesh, orientation='vertical', extend='both')
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)        
        
        proj = ccrs.Mercator.GOOGLE
        ax = plt.subplot(122, projection=proj)
        mesh = iplt.pcolormesh(stats_cube)
        #iplt.pcolormesh(stats_cube,cmap = precip_colormap, 25)
        leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=1)
        #cb1 = fig.colorbar(mesh, ax=ax, fraction=0.06, pad=0.02)
        #cb1.ax.tick_params(labelsize=20)
        #bar = plt.colorbar(mesh, orientation='vertical', extend='both')
        #cbar_ax = fig.add_axes([1, 0.15, 0.035, 0.7])
        #cb1 = fig.colorbar(mesh, cax=cbar_ax, fraction=0.36, pad=0.04)
        #cb1.ax.tick_params(labelsize=20)
        plt.show()
        
        # Create subplot and plot
        #(should we really find the corner coordinates?)
        ax = fig.add_subplot(rows, columns, i)
        ax.set_axis_off()
        if shared_axis == True:
            my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3, 
                                    alpha = 1, cmap = precip_colormap,vmin = min_value,vmax = max_value)
            if region == 'Northern':
                leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=3)
                northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
            elif region == 'leeds-at-centre':
                leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
            
        elif shared_axis == False:
            my_plot = ax.pcolormesh(lons_2d, lats_2d, stats_cube.data, linewidths=3, 
                                    alpha = 1, cmap = precip_colormap)
            if region == 'Northern':
                leeds_gdf.plot(ax=ax, edgecolor='red', color='none', linewidth=3)
                northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
            elif region == 'leeds-at-centre':
                leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)
            #fig.colorbar(my_plot, ax=ax, fraction=0.036, pad=0.02)
            cb1 = fig.colorbar(my_plot, ax=ax, fraction=0.06, pad=0.02)
            cb1.ax.tick_params(labelsize=40)
                    
        # Move counter on to next ensemble member
        i = i+1
      
    # Set up plottingparameters over whole subfigure
    fig.tight_layout()
    if shared_axis == True:
        cbar_ax = fig.add_axes([0.99, 0.15, 0.035, 0.7])
        #cbar_ax = fig.add_axes([1.05, 0.15, 0.05, 0.7])
        cb1 = fig.colorbar(my_plot, cax=cbar_ax, fraction=0.36, pad=0.04)
        cb1.ax.tick_params(labelsize=50)
        filename = "Outputs/Stats_Spatial_plots/{}/{}.png".format(region, stat)
    elif shared_axis == False:
        filename = "Outputs/Stats_Spatial_plots/{}/{}_diffscales.png".format(region, stat)
    fig.savefig(filename, bbox_inches = 'tight')
   
def main():
    # extract surface temperature cubes which have an ensemble member coordinate, adding appropriate lagged ensemble metadata
    surface_temp = iris.load_strict(iris.sample_data_path('GloSea4', 'ensemble_???.pp'),
                  iris.Constraint('surface_temperature', realization=lambda value: True),
                  callback=realization_metadata,
                  )

 # ----------------------------------------------------------------------------------------------------------------
    # Plot #1: Ensemble postage stamps
    # ----------------------------------------------------------------------------------------------------------------

    # for the purposes of this example, take the last time element of the cube
    last_timestep = surface_temp[:, -1, :, :]

    # Make 50 evenly spaced levels which span the dataset
    contour_levels = numpy.linspace(numpy.min(last_timestep.data), numpy.max(last_timestep.data), 50)

    # Create a wider than normal figure to support our many plots
    plt.figure(figsize=(12, 6), dpi=100)

    # Also manually adjust the spacings which are used when creating subplots
    plt.gcf().subplots_adjust(hspace=0.05, wspace=0.05, top=0.95, bottom=0.05, left=0.075, right=0.925)

    # iterate over all possible latitude longitude slices
    for cube in stats_cube.slices(['grid_latitude', 'grid_longitude']):
        print(cube)
        
        # get the ensemble member number from the ensemble coordinate
        ens_member = cube.coord('realization').points[0]

        # plot the data in a 4x4 grid, with each plot's position in the grid being determined by ensemble member number
        # the special case for the 13th ensemble member is to have the plot at the bottom right
        if ens_member == 13:
            plt.subplot(4, 4, 16)
        else:
            plt.subplot(4, 4, ens_member+1)

        cf = iplt.contourf(cube, contour_levels)

        # add coastlines
        m = iplt.gcm()
        m.drawcoastlines()

    # make an axes to put the shared colorbar in
    colorbar_axes = plt.gcf().add_axes([0.35, 0.1, 0.3, 0.05])
    colorbar = plt.colorbar(cf, colorbar_axes, orientation='horizontal')
    colorbar.set_label('%s' % last_timestep.units)

    # limit the colorbar to 8 tick marks
    import matplotlib.ticker
    colorbar.locator = matplotlib.ticker.MaxNLocator(8)
    colorbar.update_ticks()

    # get the time for the entire plot
    time_coord = last_timestep.coord('time')
    time = time_coord.units.num2date(time_coord.points[0])

    # set a global title for the postage stamps with the date formated by "monthname year"
    plt.suptitle('Surface temperature ensemble forecasts for %s' % time.strftime('%B %Y'))

    iplt.show()

