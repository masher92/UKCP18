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
warnings.simplefilter(action = 'ignore', category = DeprecationWarning)

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

############################################
# Define variables and set up environment
#############################################
# Region over which to plot
region = 'leeds-at-centre' #['Northern', 'leeds-at-centre', 'UK']
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

##################################################################
# Load necessary spatial data
##################################################################
# This is the outlins of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})
# Create outlines as shapely geometries
leeds_at_centre_poly = Polygon(create_leeds_at_centre_outline({'init' :'epsg:4326'})['geometry'].iloc[0])

##################################################################
# Location of rain gauges - to add to plots
##################################################################
def reproject_wm (gauges_df):
    gauges_long_wm, gauges_lat_wm = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),
                                            np.array(gauges_df['Longitude']), np.array(gauges_df['Latitude'])) 
    gauges_df['Long_wm'] = gauges_long_wm
    gauges_df['Lat_wm'] = gauges_lat_wm
    return gauges_df


lats,lons, station_names = [], [],[]
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
        res = this_point.within(leeds_at_centre_poly)
        #sres_in_leeds = this_point.within(leeds_poly)
        # If the point is within leeds-at-centre geometry
        if res ==True:
            # Add station name and lats/lons to list
            lats.append(lat)
            lons.append(lon)
            station_names.append(station_name)

# Met Office Gauges
mo_gauges= pd.DataFrame({'ID' : ["Bingley No.2","Huddersfield Oakes","Bradford", 
                                             "Emley moor", "Leeds weather centre",
                                             "Ryhill","Bramham", "Emley Moor No.2" ], 
                         'Latitude' : [53.811, 53.656, 53.814, 53.613, 53.801, 53.628, 53.869, 53.612], 
                         'Longitude' : [-1.867, -1.831, -1.774, -1.665, -1.561, -1.394, -1.319, -1.668]})


# Locations of spots marked on distance to gauge plot as containing a gauge
# but not found in Newcastle/MO gauges (manually defined locations based on
# distance to gauge plot)
defined_gauges= pd.DataFrame({'ID' : ["no1", "no2", "no3", "no4", "no5", "no6"], 
                         'Latitude' : [54.04, 54.07, 54.125, 54.13, 53.58, 53.835], 
                         'Longitude' : [-1.260, -1.78, -1.66, -1.43, -0.89, -1.2]})

# Convert to WM
mo_gauges = reproject_wm (mo_gauges)
defined_gauges = reproject_wm (defined_gauges)



##################################################################
# Trimming to region
##################################################################
for stat in stats:
    print(stat)
    
    # Load in netcdf files containing the stats data over the whole UK
    model_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Model/Allhours/EM_Summaries/{}_EM_mean.nc'.format(stat))[0]
    obs_cube= iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/RegriddedObservations/NearestNeighbour/{}.nc'.format(stat))[0][0]

    # Remove coordinates present in model cube, but not in observations
    model_cube.remove_coord('latitude')
    model_cube.remove_coord('longitude')    
    
    # Find the difference between the two
    diff_cube = model_cube-obs_cube
    
    # Find the percentage difference
    diff_cube = (diff_cube/obs_cube) * 100
    
    # Find absoloute difference    
    #diff_cube = iris.analysis.maths.abs(diff_cube)

    ### Trim 
    # Trim to smaller area
    if region == 'Northern':
         diff_cube = trim_to_bbox_of_region_regriddedobs(diff_cube, northern_gdf)
    elif region == 'leeds-at-centre':
         diff_cube = trim_to_bbox_of_region_regriddedobs(diff_cube, leeds_at_centre_gdf)
    
    print(diff_cube)
    
    # Find min and max vlues in data and set up contour levels
    local_min = np.nanmin(diff_cube.data)
    local_max = np.nanmax(diff_cube.data)  
    
    if abs(local_min) > abs(local_max):
        local_max = abs(local_min)
    elif abs(local_max) > abs(local_min):
        local_min = -(local_max)
    
    contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     
    
    ##### Plotting        
    # Create a colourmap            
    precip_colormap = create_precip_cmap()
    # Create a divergine colormap
    diverging_cmap = matplotlib.cm.RdBu_r
    #diverging_cmap.set_under(color="white")
    #diverging_cmap.set_bad(color="white", alpha = 1.)

    # Normalise data with a defined centre point (in this case 0)
    if local_min < 0:
        norm = colors.TwoSlopeNorm(vmin = local_min, vmax = local_max,
                                    vcenter = 0)
    else:
        norm = None
        diverging_cmap = matplotlib.cm.Reds
    
    # Define figure size
    if region == 'leeds-at-centre':
        fig = plt.figure(figsize = (20,30))
    else:
        fig = plt.figure(figsize = (30,20))     
        
    # Set up projection system
    proj = ccrs.Mercator.GOOGLE
        
    # Create axis using this WM projection
    ax = fig.add_subplot(projection=proj)
    # Plot
    mesh = iplt.pcolormesh(diff_cube, cmap = diverging_cmap, norm=norm)
                          # norm = MidpointNormalize(midpoint=0))
    for lat, lon in zip(lats, lons):
            this_point = Point(lon, lat)
            res_in_leeds = this_point.within(leeds_at_centre_poly)
            # If the point is within leeds-at-centre geometry 
            if res_in_leeds ==True :
                lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
                plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 
    plt.plot(mo_gauges['Long_wm'], mo_gauges['Lat_wm'], 'o', color='red', markersize =20)
    plt.plot(defined_gauges['Long_wm'], defined_gauges['Lat_wm'], 'o', color='yellow', markersize =20)
    
    
    
    # Add regional outlines, depending on which region is being plotted
    # And define extent of colorbars
    if region == 'Northern':
         leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
         northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
         colorbar_axes = plt.gcf().add_axes([0.73, 0.15, 0.015, 0.7])
    elif region == 'leeds-at-centre':
         leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
         colorbar_axes = plt.gcf().add_axes([0.92, 0.28, 0.015, 0.45])
    elif region == 'UK':
         plt.gca().coastlines(linewidth =3)
         colorbar_axes = plt.gcf().add_axes([0.76, 0.15, 0.015, 0.7])

    colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical')  
    colorbar.set_label('mm/hr', size = 20)
    colorbar.ax.tick_params(labelsize=28)
    colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
    
    # Add gauges
    for lat, lon in zip(lats, lons):
            this_point = Point(lon, lat)
            res_in_leeds = this_point.within(leeds_at_centre_poly)
            # If the point is within leeds-at-centre geometry 
            if res_in_leeds ==True :
                lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
                plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 
    plt.plot(mo_gauges['Long_wm'], mo_gauges['Lat_wm'], 'o', color='red', markersize =20)
    plt.plot(defined_gauges['Long_wm'], defined_gauges['Lat_wm'], 'o', color='yellow', markersize =20)
    
    # Set plot title
    ax.set_title(stat, fontsize = 50)
    # Save to file
    filename = "Scripts/UKCP18/RegionalRainfallStats/Difference_ModelVsObs/Figs/{}/percentage_diff_{}_withgauges.png".format(region, stat)
    
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')
    plt.clf()
