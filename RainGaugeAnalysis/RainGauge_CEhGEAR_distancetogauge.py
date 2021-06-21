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
filename = "datadir/CEH-GEAR/CEH-GEAR-1hr_199001.nc"

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
# Newcastle gauges to remove (as not included)
stations_to_exclude = ['knostrop_logger', 'silsden_res_logger', 'skipton_council_logg', 'Trawden_Auto',
                       'gorple_logger', 'great_walden_edge_no.2_tbr', 'Kitcliffe_LOG', 'Broadhead_Noddle_LOG',
                       'Greenfield_S.Wks_LOG', 'roecliffe_logger']
stations_to_exclude = []
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
        if res ==True and station_name not in stations_to_exclude:
            # Add station name and lats/lons to list
            lats.append(lat)
            lons.append(lon)
            station_names.append(station_name)

###############################################################################
###############################################################################
# Animation: testing gauges incldued in each timestep (using distance to gauge parameter)
###############################################################################
###############################################################################
frames = distance_to_gauge.shape[0]   # Number of frames

# Create a figure
fig = plt.figure(figsize = (20,30))
def draw(frame):
    # Clear the previous figure
    plt.clf()
    grid = distance_to_gauge[frame]
    
    ax = fig.add_subplot(projection=proj)
    
    mesh = iplt.pcolormesh(grid, cmap = precip_colormap)
    leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)

    for lat, lon in zip(lats, lons):
        lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
        plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 

    datetime = grid.coord('time').units.num2date(grid.coord('time').points[0]) 
    plt.title(str(datetime), fontsize = 30)
    return mesh
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

# Not sure what, if anything, this does
from matplotlib import rc, animation
rc('animation', html='html5')

ani = animation.FuncAnimation(fig, animate, frames, interval=10, save_count=50, blit=False, init_func=init,repeat=False)
ani.save('Outputs/RainGaugeAnalysis/DistancetoGauge.mp4', writer=animation.FFMpegWriter(fps=8))

###############################################################################
###############################################################################
# Plot distance to gauges with all the Newcastle gauges on (to compare)
###############################################################################
###############################################################################
# Get one timeslcie
distance_to_gauge_onetimeslice = distance_to_gauge[200,:,:]
print(distance_to_gauge_onetimeslice)

# plot with stations overlain 
# Define figure size
fig = plt.figure(figsize = (20,30))

precip_colormap = create_precip_cmap()   
# Set up projection system
proj = ccrs.Mercator.GOOGLE
    
# Create axis using this WM projection
ax = fig.add_subplot(projection=proj)
# Plot
mesh = iplt.pcolormesh(distance_to_gauge_onetimeslice, cmap = precip_colormap)

for lat, lon in zip(lats, lons):
        this_point = Point(lon, lat)
        res_in_leeds = this_point.within(leeds_at_centre_poly)
        # If the point is within leeds-at-centre geometry 
        if res_in_leeds ==True :
            lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
            plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 

leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)


###############################################################################
###############################################################################
# Include Met Office gauges
# And remove gauges not shown up on distance to gauge plot
###############################################################################
###############################################################################
# Find index of stations to remove
# index = station_names.index('knostrop_logger')
# # remove form lats/lons
# del lats[-index], lons[-index]

# Extra MO gauges to add
mo_gauges= pd.DataFrame({'ID' : ["Bingley No.2","Bradford", 
                                  "Ryhill","Emley Moor No.2" ], 
                         'Latitude' : [53.811, 53.814, 53.628,  53.612], 
                         'Longitude' : [-1.867,  -1.774,  -1.394, -1.668]})



mo_gauges= pd.DataFrame({'ID' : ["Huddersfield Oakes","Leeds weather centre"], 
                         'Latitude' : [53.656, 53.801], 
                         'Longitude' : [-1.831,  -1.561]})



mo_gauges= pd.DataFrame({'ID' : ["Huddersfield Oakes","Leeds weather centre"], 
                         'Latitude' : [53.656, 53.801], 
                         'Longitude' : [-1.831,  -1.561]})


# Locations of spots marked on distance to gauge plot as containing a gauge
# but not found in Newcastle/MO gauges (manually defined locations based on
# distance to gauge plot)
defined_gauges= pd.DataFrame({'ID' : ["no1", "no2", "no3", "no4", "no5"], 
                         'Latitude' : [54.04, 54.07, 54.125, 54.13, 53.58], 
                         'Longitude' : [-1.260, -1.78, -1.66, -1.43, -0.89]})

# Convert to WM
mo_gauges = reproject_wm (mo_gauges)
defined_gauges = reproject_wm (defined_gauges)

###############################################################################
###############################################################################
# Plot JJA stats with these gauges shown on 
###############################################################################
###############################################################################
##### Plotting  
stat = 'jja_p99'
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

  

##############################
stations_to_include = ['knostrop_logger', 'silsden_res_logger', 'skipton_council_logg', 'Trawden_Auto',
                       'gorple_logger', 'great_walden_edge_no.2_tbr', 'Kitcliffe_LOG', 'Broadhead_Noddle_LOG',
                       'Greenfield_S.Wks_LOG', 'roecliffe_logger']


# Find min and max vlues in data and set up contour levels
local_min = np.nanmin(obs_cube.data)
local_max = np.nanmax(obs_cube.data)     
contour_levels = np.linspace(local_min, local_max, 11,endpoint = True)     

  
# Define figure size
fig = plt.figure(figsize = (20,30))

# Set up projection system
proj = ccrs.Mercator.GOOGLE
    
# Create axis using this WM projection
ax = fig.add_subplot(projection=proj)
# Plot
mesh = iplt.pcolormesh(obs_cube, cmap = precip_colormap)

for lat, lon in zip(lats, lons):
        this_point = Point(lon, lat)
        res_in_leeds = this_point.within(leeds_at_centre_poly)
        # If the point is within leeds-at-centre geometry 
        #if 1 == 1:
        if res_in_leeds ==True :
            lon_wm,lat_wm = transform(Proj(init = 'epsg:4326') , Proj(init = 'epsg:3857') , lon, lat)
            plt.plot(lon_wm, lat_wm,   'o', color='black', markersize = 20) 


leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=4)

plt.plot(mo_gauges['Long_wm'], mo_gauges['Lat_wm'], 'o', color='red', markersize =20)



