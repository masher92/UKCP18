import iris.coord_categorisation
import iris
import glob
import numpy as np
from numba import jit
import os
import geopandas as gpd
import time 
import sys

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/')
from Pr_functions import *
sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

ems = ['01','04', '05', '06', '07', '08', '09','10','11','12', '13','15']
start_year = 1980
end_year = 2000 
yrs_range = "1980_2001" 

for em in ems:
    print(em)
    #############################################
    ## Load in the data
    #############################################
    filenames =[]
    # Create filepath to correct folder using ensemble member and year
    general_filename = 'datadir/UKCP18/2.2km/{}/{}/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, yrs_range, em)
    #print(general_filename)
    # Find all files in directory which start with this string
    for filename in glob.glob(general_filename):
        #print(filename)
        filenames.append(filename)
    print(len(filenames))
    
    monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
    for cube in monthly_cubes_list:
         for attr in ['creation_date', 'tracking_id', 'history']:
             if attr in cube.attributes:
                 del cube.attributes[attr]
    
    # Concatenate the cubes into one
    concat_cube = monthly_cubes_list.concatenate_cube()
    
    # Remove ensemble member dimension
    concat_cube = concat_cube[0,:,:,:]
    
    #############################################
    ## Trim to outline of UK
    #############################################
    minmax = lambda x: (np.min(x), np.max(x))
    #bbox = np.array([-8.6500072, 49.863187 ,  1.7632199, 60.8458677])
    bbox = np.array([-10.1500, 49.8963187 ,  1.7632199, 58.8458677])
    # Find the lats and lons of the cube in WGS84
    lons = concat_cube.coord('longitude').points
    lats = concat_cube.coord('latitude').points
    
    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    concat_cube = concat_cube[..., imin:imax+1, jmin:jmax+1]
    
    #qplt.contour(concat_cube[0])
    #plt.gca().coastlines()
    
    ##########################################################################
    # Create geodataframe of UK 
    #uk_gdf = gpd.read_file("datadir/SpatialData/UK_shpfile/UnitedKingdom_Bound.shp") 
    #uk_gdf = uk_gdf.to_crs({'init' :'epsg:3785'}) 
    #uk_gdf.plot()
    
    #regional_cube = trim_to_bbox_of_region(concat_cube, uk_gdf)
    
    ############################################
    # Cut to just June-July_August period
    #############################################
    ## Add season variables
    iris.coord_categorisation.add_season(concat_cube,'time', name = "clim_season")
    # Keep only JJA
    jja = concat_cube.extract(iris.Constraint(clim_season = 'jja'))
    # Add season year
    iris.coord_categorisation.add_season_year(jja,'time', name = "season_year") 
    
    ###########################################
    # Find Max, mean, percentiles
    #############################################
    #seconds = time.time()
    #jja_mean = jja.aggregated_by(['clim_season'], iris.analysis.MEAN)
    jja_max = jja.aggregated_by(['clim_season'], iris.analysis.MAX)
    #jja_percentiles = jja.aggregated_by(['clim_season'], iris.analysis.PERCENTILE, percent=[95,97,99,99.5])
    #percentile_1 = jja_percentiles[0,:,:,:]
    #percentile_2 = jja_percentiles[1,:,:,:]
    #percentile_3 = jja_percentiles[2,:,:,:]
    #percentile_4 = jja_percentiles[3,:,:,:]
    #print("Completed in: ", time.time() - seconds)
    
    #############################################
    # Plotting
    #############################################
    import iris.quickplot as qplt
    import cartopy.crs as ccrs
    import matplotlib 
    import iris.plot as iplt
    
    cube = jja_max
    
    frames = cube.shape[0]   # Number of frames
    min_value = cube.data.min()  # Lowest value
    max_value = cube.data.max()  # Highest value
    
    # Create a colourmap                                   
    tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
    "#72190E","#882E72","#000000"]                                      
    
    precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
    # Set the colour for any values which are outside the range designated in lvels
    precip_colormap.set_under(color="white")
    precip_colormap.set_over(color="pink")
    
    grid = cube[0]
    
    fig=plt.figure(figsize=(20,16))
    levels = np.round(np.linspace(0, max_value, 15),2)
    contour = iplt.contourf(grid,cmap=precip_colormap, levels = levels, extend="both")
    plt.gca().coastlines(resolution='50m', color='black', linewidth=2)
    #plt.plot(0.6628091964140957, 1.2979678925914127, 'o', color='black', markersize = 3) 
    plt.title("JJA mean", fontsize =40) 
    #plt.colorbar(fraction=0.036, pad=0.02)
    cb = plt.colorbar(fraction=0.036, pad=0.02)
    cb.ax.tick_params(labelsize=25)
    
    # Save Figure
    ddir = 'Outputs/UK_plots/JJA_max/'
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
    filename =  (ddir + '/{}.jpg').format(em)
    
    fig.savefig(filename,bbox_inches='tight')
    print("PLot saved")



# #####################################################################
# # Get shapefile of UK 
# #####################################################################
# world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
# uk = world.query('name == "United Kingdom"')
# uk = uk.to_crs({'init' :'epsg:27700'}) 

# # Create geodataframe of UK 
# uk_gdf = gpd.read_file("datadir/SpatialData/UK_shpfile/UnitedKingdom_Bound.shp") 
# uk_gdf = uk_gdf.to_crs({'init' :'epsg:3785'}) 
# uk_gdf.plot()

# # Create geodataframe of UK 
# # roi_gdf = gpd.read_file("datadir/SpatialData/ROI_shpfile/ie_100km.shp") 
# # roi_gdf = roi_gdf.to_crs({'init' :'epsg:3785'}) 
# # roi_gdf.plot()

# # Create region with Leeds at the centre
# lons = [54.130260, 54.130260, 53.486836, 53.486836]
# lats = [-2.138282, -0.895667, -0.895667, -2.138282]
# polygon_geom = Polygon(zip(lats, lons))
# leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
# leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:3785'}) 


# # 'United Kingdom', ())
# #  GBR: { sw: {lat: 49.674, lng: -14.015517}, ne: {lat: 61.061, lng: 2.0919117} }
 
# #  uk_bounds = [-7.57216793459, 49.959999905, 1.68153079591, 58.6350001085]
# #  pts = gpd.GeoDataFrame(uk_bounds)
# # pts.plot() 


# bounding_box = uk_gdf.envelope
# uk_gdf_bbox = gpd.GeoDataFrame(gpd.GeoSeries(bounding_box), columns=['geometry'])
# uk_gdf_bbox.crs = {'init' :'epsg:4326'}

    
# fig, ax = plt.subplots(figsize=(20,20))
# # Add edgecolor = 'grey' for lines
# plot =ax.pcolormesh(lons_cornerpoints, lats_cornerpoints, cube.data,
#               linewidths=3, alpha = 1)
# #plot = region_outline_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
# cbar = plt.colorbar(plot,fraction=0.036, pad=0.02)
# cbar.ax.tick_params(labelsize='xx-large', size = 10, pad=0.04) 
# #cbar.set_label(label='Precipitation (mm/hr)',weight='bold', size =20)
# #plt.colorbar(plot,fraction=0.036, pad=0.04).ax.tick_params(labelsize='xx-large')  
# plot =ax.tick_params(labelsize='xx-large')
# plot = uk_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)


# plot_cube_within_region(grid, uk_gdf)
