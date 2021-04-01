import iris.coord_categorisation
import iris
import numpy as np
import os
import numpy.ma as ma
import iris.plot as iplt
import cartopy.crs as ccrs
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def create_wider_northern_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of the outline of a wider Northern area (including
        North East, North West, Yorkshire and the Humber, East Midlands and West Midlands and
        Dumfries and Galloway and the Borders)
        in the projection specified

    Parameters
    ----------
        required_proj : Dict
            Python dictionary with a key init that has a value epsg:4326. 
            This is a very typical way how CRS is stored in GeoDataFrames 
            e.g. {'init' :'epsg:3785'} for Web Mercator
            or   {'init' :'epsg:4326'} for WGS84

    Returns
    -------
        wider_northern_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of wider Northern region
    
    '''
    # Read in outline of UK
    uk_regions = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
    # England part
    wider_northern_gdf = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber', 'East Midlands', 'West Midlands'])]
    wider_northern_gdf['merging_col'] = 0
    wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
    wider_northern_gdf = wider_northern_gdf[['geometry']]
    
    # Scotland part
    # D and G
    dg = gpd.read_file("datadir/SpatialData/2011_Census_Dumfries_and_Galloway_(shp)/DC_2011_EoR_Dumfries___Galloway.shp")
    dg['merging_col'] = 0
    dg = dg.dissolve(by='merging_col')
    # Borders
    borders = gpd.read_file('datadir/SpatialData/Scottish_Borders_shp/IZ_2001_EoR_Scottish_Borders.shp')
    borders['merging_col'] = 0
    borders = borders.dissolve(by='merging_col')
    
    southern_scotland = pd.concat([dg, borders])
    southern_scotland['new_merging_col'] = 0
    southern_scotland = southern_scotland.dissolve(by='new_merging_col')
    southern_scotland = southern_scotland[['geometry']]
    
    # Join the two
    wider_northern_gdf = pd.concat([southern_scotland, wider_northern_gdf])
    wider_northern_gdf['merging_col'] = 0
    wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
    wider_northern_gdf = wider_northern_gdf.to_crs(required_proj) 
    
    return wider_northern_gdf

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
    gdf = gdf.to_crs({'init' :'epsg:4326'}) 
    
    # Find the bounding box of the region
    bbox = gdf.total_bounds
    
    # Find the lats and lons of the cube in WGS84
    lons = cube.coord('longitude').points
    lats = cube.coord('latitude').points

    inregion = np.logical_and(np.logical_and(lons > bbox[0],
                                             lons < bbox[2]),
                              np.logical_and(lats > bbox[1],
                                             lats < bbox[3]))
    region_inds = np.where(inregion)
    imin, imax = minmax(region_inds[0])
    jmin, jmax = minmax(region_inds[1])
    
    trimmed_cube = cube[..., imin:imax+1, jmin:jmax+1]
    
    return trimmed_cube


#############################################
#############################################
# Define variables and set up environment
#############################################
#############################################
# Define filepath within which data and scripts are found
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/Alasdair")



#############################################################################  
#############################################################################
# Plotting
#############################################################################
#############################################################################
wider_northern_gdf = create_wider_northern_outline({'init' :'epsg:3857'})
#northern_gdf = create_northern_outline({'init' :'epsg:3857'})

#Load mask for wider northern region
#This masks out cells outwith the wider northern region
wider_northern_mask = np.load('Outputs/RegionalMasks/wider_northern_region_mask.npy')

#Load mask for UK
uk_mask = np.load('Outputs/RegionalMasks/uk_mask.npy')  
uk_mask = uk_mask.reshape(458, 383)


em_mean_feb_baseline = iris.load("datadir/UKCP18/2.2km/feb_em_means_1980-2001.nc")[0]

#############################################################################  
#############################################################################
# Plotting
#############################################################################
#############################################################################
# Mask out data points outside UK
em_mean_feb_baseline.data = ma.masked_where(uk_mask == 0, em_mean_feb_baseline.data)  

# Trim to smaller area
em_mean_feb_baseline = trim_to_bbox_of_region(em_mean_feb_baseline, wider_northern_gdf)

# Mask the data so as to cover any cells not within the specified region 
em_mean_feb_baseline.data = ma.masked_where(wider_northern_mask == 0, em_mean_feb_baseline.data)
# Trim to the BBOX of Northern England
# This ensures the plot shows only the bbox around northern england
# but that all land values are plotted
em_mean_feb_baseline = trim_to_bbox_of_region(em_mean_feb_baseline, wider_northern_gdf)


# Set up a plotting figurge with Web Mercator projection
proj = ccrs.Mercator.GOOGLE
fig = plt.figure(figsize=(20,20), dpi=200)
ax = fig.add_subplot(122, projection = proj)
mesh = iplt.pcolormesh(em_mean_feb_baseline)
# Add regional outlines,
wider_northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03)
cb1.ax.tick_params(labelsize=15)
