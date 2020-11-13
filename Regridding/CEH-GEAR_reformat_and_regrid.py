import iris
import xarray as xr
import numpy as np
from iris.coords import DimCoord
from iris.coord_systems import TransverseMercator,GeogCS
from iris.cube import Cube
from cf_units import Unit
import cf_units
import os
import glob
from pyproj import Proj, transform
import sys

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/Regridding')
from Regridding_functions import *

# Load UKCP18 model data to use in regriddding
file_model='/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19911201-19911230.nc'
cube_model=iris.load_cube(file_model)
    
# For each file in the CEH-GEAR directory:
# Reformat and then regrid into same format as the UKCP18 model cube
i = 0
for filename in glob.glob("datadir/CEH-GEAR/*")[0:2]:
    print(i)
    # Filename to save reformatted cube to
    filename_reformat = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_reformatted/rf_")
    # Filename to save regridded cube to -- linear
    filename_regrid_lin = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_regridded_2.2km/LinearRegridding/rg_")
    # Filename to save regridded cube to -- nearest neighbour
    filename_regrid_nn = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_regridded_2.2km/NearestNeighbour/rg_")
    
    # If files don't already exist, then create
    if not os.path.isfile(filename_regrid_nn):
      # Open dataset with Xarray
      xr_ds=xr.open_dataset(filename)
      # Convert to cube in the correct format and save
      cube=make_bng_cube(xr_ds,'rainfall_amount')
      iris.save(cube, filename_reformat)
      #### Regrid observaitons onto model grid
      # Lienar interpolation
      #reg_cube_lin =cube.regrid(cube_model,iris.analysis.Linear())      
      # Nearest neighbour
      reg_cube_nn =cube.regrid(cube_model,iris.analysis.Nearest())    
     
      # Area weighted regrid
      # First need to convert projection system
      # Store the crs of the model cube
      #cube_model_crs = cube_model.coord('grid_latitude').coord_system.as_cartopy_crs()
      #from pyproj.crs import CRS
      # cube_model_crs_proj = CRS.from_dict(cube_model_crs.proj4_params) 
      #cube_model_clone = cube_model.copy()
      #print(cube_model_clone)
      #cube_model_clone.remove_coord('longitude')
      #cube_model_clone.remove_coord('latitude')
      #iris.analysis.cartography.project(cube_model_clone, cube_model_crs_proj)
      #reg_cube_aw =cube.regrid(cube_model,iris.analysis.AreaWeighted())   
      
      # Save 
      #iris.save(reg_cube_lin, filename_regrid_lin)
      iris.save(reg_cube_nn, filename_regrid_nn)
    
    i = i+1


xr_ds=xr.open_dataset(filename)

#### Create regional outline
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
lons = [54.130260, 54.130260, 53.486836, 53.486836]
lats = [-2.138282, -0.895667, -0.895667, -2.138282]
polygon_geom = Polygon(zip(lats, lons))
leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs({'init' :'epsg:27700'}) 
########### Convert to cube in the correct format and save
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
da=xr_ds['min_dist']
# Recreate the cube with the data and the dimension coordinates
cube_dist = Cube(np.float32(da.values),  units=da.units, dim_coords_and_dims=[(iris_time, 0), (northings, 1),(eastings, 2)])



xr_ds=xr.open_dataset(filename)
# Convert to cube in the correct format and save
cube_rainfall=make_bng_cube(xr_ds,'rainfall_amount')

# Set -s to NA
cube_dist_data = cube_dist.data
cube_dist_data[cube_dist_data==0] = np.nan

# Take one time slice
one_ts= cube_dist[0,:,:]

# Test plotting
print(one_ts)
qplt.pcolormesh(one_ts)

# PLot manually
lats = one_ts.coord('projection_x_coordinate').points
lons = one_ts.coord('projection_y_coordinate').points
lats_2d, lons_2d = np.meshgrid(lats, lons)
# Convert to web mercator
inProj = Proj(init='epsg:27700')
outProj = Proj(init='epsg:3857')
lats_2d, lons_2d = transform(inProj,outProj,lats_2d, lons_2d)
# Get data
data = one_ts.data

fig, ax  = plt.subplots()
ax.set_xlim([-425481, 50000])
ax.set_ylim([7009576, 7509576])
my_plot = ax.pcolormesh(lats_2d, lons_2d,data, linewidths=3, vmin = 0, vmax = 30000)
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
fig.colorbar(my_plot, ax=ax)

fig, ax  = plt.subplots()
ax.set_xlim([-209481, -120000])
ax.set_ylim([7091576, 7169576])
my_plot = ax.pcolormesh(lats_2d, lons_2d,data, linewidths=3,  vmin = 0, vmax = 15000)
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
plt.axis('off')
fig.colorbar(my_plot, ax=ax)
my_plot = ax.plot(ea_gauges['Long_wm'], ea_gauges['Lat_wm'], 'bo', color='red', markersize =5)
#my_plot = ax.plot(cc_gauges['Long_wm'], cc_gauges['Lat_wm'], 'o', color='green', markersize =10)
my_plot = ax.plot(mo_gauges['Long_wm'], mo_gauges['Lat_wm'], 'o', color='orange', markersize =5)





# Take regional cuts
leeds_grid = trim_to_bbox_of_region(one_ts, leeds_at_centre_gdf)
qplt.pcolormesh(leeds_grid)
northern_grid = trim_to_bbox_of_region(one_ts, northern_gdf)
qplt.pcolormesh(northern_grid)

# Try plotting alternative way, so can also plot location of gauges
# Get 2d lats and lons
lats = northern_grid.coord('projection_x_coordinate').points
lons = northern_grid.coord('projection_y_coordinate').points
lats_2d, lons_2d = np.meshgrid(lats, lons)
# Convert to web mercator
inProj = Proj(init='epsg:27700')
outProj = Proj(init='epsg:3857')
lats_2d, lons_2d = transform(inProj,outProj,lats_2d, lons_2d)
# Get data
data = northern_grid.data


fig, ax  = plt.subplots()
my_plot = ax.pcolormesh(lats_2d, lons_2d,data, linewidths=3)
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
northern_regions_combi.plot()



one_ts= cube_dist[0,:,:]
print(one_ts)
qplt.contourf(one_ts)
data = one_ts.data
data[data==0] = np.nan
one_ts.data = data
iplt.contourf(one_ts)



lats = grid.coord('projection_x_coordinate').points
lons = grid.coord('projection_y_coordinate').points
#lons_2d, lats_2d = np.meshgrid(lons_2d, lats_2d)
lats_2d, lons_2d = np.meshgrid(lats, lons)

inProj = Proj(init='epsg:27700')
outProj = Proj(init='epsg:3857')
lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)

my_plot = plt.pcolormesh(lons_2d, lats_2d, grid.data, linewidths=3)

    
data_fl = np.flipud(data)

one_ts= trimmed_cube[0,:,:]
lats = one_ts.coord('projection_x_coordinate').points
lons = one_ts.coord('projection_y_coordinate').points
#lons_2d, lats_2d = np.meshgrid(lons_2d, lats_2d)
lats_2d, lons_2d = np.meshgrid(lats, lons)
inProj = Proj(init='epsg:27700')
outProj = Proj(init='epsg:3857')
lons_2d, lats_2d = transform(inProj,outProj,lons_2d, lats_2d)

fig, ax  = plt.subplots()
my_plot = ax.pcolormesh(lons_2d, lats_2d, one_ts.data, linewidths=3)
leeds_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=3)


def trim_to_bbox_of_region (cube, gdf):
    '''
    Description
    ----------
        Trims a cube to the bounding box of a region, supplied as a geodataframe.
        This is much faster than looking for each point within a geometry as in
        GridCellsWithin_geometry
        Tests whether the central coordinate is within the bbox

    Parameters
    ----------
        cube : iris cube
            1D array of latitudes
        gdf: GeoDataFrame
            GeoDataFrame containing a geometry by which to cut the cubes spatial extent
    Returns
    -------
        trimmed_cube : iris cube
            Cube with spatial extent equivalent to the bounding box of the supplied geodataframe

    '''
    # CReate function to find
    minmax = lambda x: (np.min(x), np.max(x))
    
    # Convert the regional gdf to WGS84 (same as cube)
    gdf = gdf.to_crs({'init' :'epsg:27700'}) 
    
    # Find the bounding box of the region
    bbox = gdf.total_bounds
    
    # Find the lats and lons of the cube in WGS84
    lons = cube.coord('projection_y_coordinate').points
    lats = cube.coord('projection_x_coordinate').points
    lats, lons = np.meshgrid(lats, lons)
    
    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1]
    
    return trimmed_cube



uk_regions = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_regions = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
#uk_regions = gpd.read_file(root_fp + "datadir/SpatialData/NUTS_Level_1__January_2018__Boundaries-shp/NUTS_Level_1__January_2018__Boundaries.shp") 
#northern_regions = uk_regions.loc[uk_regions['nuts118nm'].isin(['North East (England)', 'North West (England)', 'Yorkshire and The Humber'])]
# Merge the three regions into one
northern_regions['merging_col'] = 0
northern_gdf = northern_regions.dissolve(by='merging_col')
northern_regions = northern_regions.to_crs({'init' :'epsg:3785'}) 


# Check by plotting
#fig, ax = plt.subplots(figsize=(20,20))
#plot =northern_regions_combi.plot(ax=ax, categorical=True, alpha=1, edgecolor='red', color='none', linewidth=6)
 
geometry_poly = Polygon(northern_regions_combi['geometry'].iloc[0])
geometry_poly = MultiPolygon(northern_regions_combi['geometry'].iloc[0])

polygon_northern = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:3785'}, geometry=[geometry_poly])   

