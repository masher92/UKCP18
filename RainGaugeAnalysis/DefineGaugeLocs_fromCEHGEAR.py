'''
This script:
    Reads in a CEH-GEAR cube and reformats it to BNG
    Plots its 'dist' parameter to infer locations of gauges
    Overlays locations of EA and MO gauges and compares this
    Defines some extra locations where there seems to be gauges from this dist
        parameter, that aren't included in EA or MO
        
    NB: In "Load in CEH-GEAR data" section, only one month's worth of data is loaded
    The 'dist' parameter changes with each hour of data
    So at each timeslice a different selection of gauges are used to construct it
    If wanted to look into this more closely could use the animation section 
    at bottom
'''

#############################################################################
# Set up environment
#############################################################################
import iris.coord_categorisation
import iris
import numpy as np
import os
import sys
import warnings
import iris.plot as iplt
import cartopy.crs as ccrs
import xarray as xr
from iris.coords import DimCoord
from iris.cube import Cube
from iris.coord_systems import TransverseMercator,GeogCS
from cf_units import Unit
import glob
import cf_units
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

#############################################################################
#############################################################################
# Load in spatial data
# As geodataframes for plotting
# As shapely geometries for checking whether lat/long points are witihn the areas
#############################################################################
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

# Create outlines as shapely geometries
leeds_at_centre_poly = Polygon(create_leeds_at_centre_outline({'init' :'epsg:4326'})['geometry'].iloc[0])
leeds_poly = Polygon(create_leeds_outline({'init' :'epsg:4326'})['geometry'].iloc[0])

#############################################################################
#############################################################################
# Load in CEH-GEAR data
#############################################################################
#############################################################################
# Define file path to one CEH-GEAR file
filename = "datadir/CEH-GEAR/OriginalFormat/CEH-GEAR-1hr_201001.nc"

# Define variable which indiciates the minimum distancxe to a rain gauge
variable = 'min_dist'

###############################################################################
###############################################################################
# Convert to BNG cube
###############################################################################
###############################################################################
# Open dataset with Xarray
xr_ds=xr.open_dataset(filename)

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
da=xr_ds[variable]
#da.attrs['standard_name']= 'min_dist'

# Recreate the cube with the data and the dimension coordinates
distance_to_gauge = Cube(np.float32(da.values), 
            units='mm/hour', dim_coords_and_dims=[(iris_time, 0), (northings, 1),(eastings, 2)])

###############################################################################
###############################################################################
# Trim to leeds-at-centre region
###############################################################################
###############################################################################
region = 'leeds-at-centre'
distance_to_gauge = trim_to_bbox_of_region_obs(distance_to_gauge, leeds_at_centre_gdf)

###############################################################################
###############################################################################
# Read in locations of Newcastle gauges (EA)
###############################################################################
###############################################################################
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

###############################################################################
###############################################################################
# Read in locations of Met Office Gauges
# And define locations where there appears to be gauges from plotting the dist_to_gauge 
# paramater
# NB: I did this using just one timeslice, so its possible there might be more
# of these
###############################################################################
###############################################################################
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

###############################################################################
###############################################################################
# Plot distance to gauges with all the Newcastle gauges on (to compare)
###############################################################################
###############################################################################
# Get one timeslcie
distance_to_gauge_onetimeslice = distance_to_gauge[0,:,:]
print(distance_to_gauge_onetimeslice)

precip_colormap = create_precip_cmap()   

# Define figure size
fig = plt.figure(figsize = (20,30))
# Set up projection system
proj = ccrs.Mercator.GOOGLE
# Create axis using this WM projection
ax = fig.add_subplot(projection=proj)
# Plot
mesh = iplt.pcolormesh(distance_to_gauge_onetimeslice, cmap = precip_colormap)
# add leeds outline
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
# Add gauges
for lat, lon in zip(lats, lons):
        res_in_leeds = this_point.within(leeds_at_centre_poly)
        # If the point is within leeds-at-centre geometry 
        if res_in_leeds ==True :
            lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
            plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 
plt.plot(mo_gauges['Long_wm'], mo_gauges['Lat_wm'], 'o', color='red', markersize =20)
plt.plot(defined_gauges['Long_wm'], defined_gauges['Lat_wm'], 'o', color='yellow', markersize =20)
cb = plt.colorbar(fraction = 0.042, pad = 0.05)
cb.set_label(label = 'Distance to gauge (m)', size = 45)
cb.ax.tick_params(labelsize = 40)

###############################################################################
###############################################################################
# Plot JJA stats with these gauges shown on 
###############################################################################
###############################################################################
##### Plotting  
stat = 'jja_p99.9'
# Load in netcdf files containing the stats data over the whole UK
obs_cube = iris.load('/nfs/a319/gy17m2a/Outputs/RegionalRainfallStats/NetCDFs/Observations/leeds-at-centre/{}.nc'.format(stat))[0]
obs_cube = trim_to_bbox_of_region_obs(obs_cube, leeds_at_centre_gdf)  

# Define figure size
fig = plt.figure(figsize = (20,30))
# Set up projection system
proj = ccrs.Mercator.GOOGLE
# Create axis using this WM projection
ax = fig.add_subplot(projection=proj)
# Plot
mesh = iplt.pcolormesh(obs_cube, cmap = 'Blues')
# add leeds outline
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)
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

# ###############################################################################
# ###############################################################################
# # Animation: testing gauges incldued in each timestep (using distance to gauge parameter)
# ###############################################################################
# ###############################################################################
# frames = distance_to_gauge.shape[0]   # Number of frames

# # Create a figure
# fig = plt.figure(figsize = (20,30))
# def draw(frame):
#     # Clear the previous figure
#     plt.clf()
#     grid = distance_to_gauge[frame]
    
#     ax = fig.add_subplot(projection=proj)
    
#     mesh = iplt.pcolormesh(grid, cmap = precip_colormap)
#     leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)

#     for lat, lon in zip(lats, lons):
#         lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
#         plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 

#     datetime = grid.coord('time').units.num2date(grid.coord('time').points[0]) 
#     plt.title(str(datetime), fontsize = 30)
#     return mesh
    
# def init():
#     return draw(0)

# def animate(frame):
#     return draw(frame)

# # Not sure what, if anything, this does
# from matplotlib import rc, animation
# rc('animation', html='html5')

# ani = animation.FuncAnimation(fig, animate, frames, interval=10, save_count=50, blit=False, init_func=init,repeat=False)
# ani.save('Outputs/RainGaugeAnalysis/DistancetoGauge.mp4', writer=animation.FFMpegWriter(fps=8))


