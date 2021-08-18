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
warnings.simplefilter(action = 'ignore', category = FutureWarning)

# Set up path to root directory
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

## Function for reprojecting from WGS84 to Web Mercator
def reproject_wm (gauges_df):
    gauges_long_wm, gauges_lat_wm = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),
                                            np.array(gauges_df['Longitude']), np.array(gauges_df['Latitude'])) 
    gauges_df['Long_wm'] = gauges_long_wm
    gauges_df['Lat_wm'] = gauges_lat_wm
    return gauges_df


############################################
# Define variables and set up environment
#############################################
# Region over which to plot
region = 'leeds-at-centre' #['Northern', 'leeds-at-centre', 'UK']
# Stats to plot
stats = ['jja_max', 'jja_mean', 'jja_p95', 'jja_p97', 'jja_p99', 'jja_p99.5', 'jja_p99.75', 'jja_p99.9']

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

##############################################################################
##############################################################################
#### Gauge data
##############################################################################
##############################################################################
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

# EA gauges
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
        res_in_leeds = this_point.within(leeds_poly)
        # If the point is within leeds-at-centre geometry
        if res ==True:
            # Add station name and lats/lons to list
            lats.append(lat)
            lons.append(lon)
            station_names.append(station_name)

##################################################################
# Trimming to region
##################################################################
for stat in stats:
    print(stat)
    
    # Load in netcdf files containing the stats data over the whole UK
    obs_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/{}.nc'.format(stat))[0]
    # Trim to smaller area
    if region == 'Northern':
         obs_cube = trim_to_bbox_of_region_obs(obs_cube, northern_gdf)
    elif region == 'leeds-at-centre':
         obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)
    
    # Find min and max vlues in data and set up contour levels
    local_min = np.nanmin(obs_cube.data)
    local_max = np.nanmax(obs_cube.data)     
    contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     
    
    ##### Plotting        
    # Create a colourmap                                   
    precip_colormap = create_precip_cmap()
    
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
    mesh = iplt.pcolormesh(obs_cube, cmap = 'Blues')
    # Add gauges
    for lat, lon in zip(lats, lons):
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
    
    colorbar = plt.colorbar(mesh, colorbar_axes, orientation='vertical',  boundaries = contour_levels)  
    colorbar.set_label('mm/hr', size = 45)
    colorbar.ax.tick_params(labelsize=40)
    colorbar.ax.set_yticklabels(["{:.{}f}".format(i, 2) for i in colorbar.get_ticks()])    
    
    # Save to file
    filename = "Scripts/UKCP18/RainGaugeAnalysis/Figs/GaugesLocationsvsRegionalRainfallStats/{}vsGaugeLocations.png".format(stat)
    
    # Save plot        
    plt.savefig(filename, bbox_inches = 'tight')
    plt.clf()
