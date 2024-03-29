#linestrings.com/bbox

import numpy as np
import geopandas as gpd
import iris
from pyproj import Proj, transform
from shapely.geometry import Point, Polygon, MultiPolygon
import matplotlib.pyplot as plt
# import tilemapbase
import time 
import pandas as pd

root_fp = "/nfs/a319/gy17m2a/"

def create_leeds_at_centre_narrow_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of a square box with Leeds at the centre
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
        leeds_at_centre_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of aquare are with Leeds at centre
    
    ''', 
    # Define lats and lons to make box around Leeds
    
    lons = [54.8, 54.2, 53.2, 53.2]
    lats = [-1.87,-1.1, -1.1, -1.87] 
    
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_narrow_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    leeds_at_centre_narrow_gdf = leeds_at_centre_narrow_gdf.to_crs(required_proj) 

    return leeds_at_centre_narrow_gdf



def create_test_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of a square box with Leeds at the centre
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
        leeds_at_centre_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of aquare are with Leeds at centre
    
    '''
    # Define lats and lons to make box around Leeds
    lons = [54, 54, 53.7, 53.7]
    lats = [-2.2, -1.5, -1.5,  -2.2]
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(required_proj) 

    return leeds_at_centre_gdf


def create_leeds_at_centre_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of a square box with Leeds at the centre
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
        leeds_at_centre_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of aquare are with Leeds at centre
    
    '''
    # Define lats and lons to make box around Leeds
    lons = [54.130260, 54.130260, 53.486836, 53.486836]
    lats = [-2.138282, -0.895667, -0.895667, -2.138282]
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs='epsg:4326', geometry=[polygon_geom])
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(required_proj) 

    return leeds_at_centre_gdf

def create_leeds_at_centre_outline_forgrid (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of a square box with Leeds at the centre
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
        leeds_at_centre_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of aquare are with Leeds at centre
    
    '''
    # Define lats and lons to make box around Leeds
    lons = [54.130260, 54.130260, 53.486836, 53.486836]
    lats = [-2.138282, -0.895667, -0.895667, -2.138282]
    # Convert to polygon
    polygon_geom = Polygon(zip(lats, lons))
    # Convert to geodataframe
    leeds_at_centre_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    leeds_at_centre_gdf = leeds_at_centre_gdf.to_crs(required_proj) 

    return leeds_at_centre_gdf

def create_leeds_outline_square (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of the outline of Leeds in the projection specified

    Parameters
    ----------
        required_proj : Dict
            Python dictionary with a key init that has a value epsg:4326. 
            This is a very typical way how CRS is stored in GeoDataFrames 
            e.g. {'init' :'epsg:3785'} for Web Mercator
            or   {'init' :'epsg:4326'} for WGS84

    Returns
    -------
        leeds_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of Leeds
    
    '''
    # Read in outline of Leeds wards  
    wards = gpd.read_file("/nfs/a319/gy17m2a/PhD/datadir/SpatialData/england_cmwd_2011/england_cmwd_2011.shp")
    # Create column to merge on
    wards['City'] = 'Leeds'
    # Merge all wards into one outline
    leeds = wards.dissolve(by = 'City')

    # Convert Leeds outline geometry to WGS84
    leeds.crs = {'init' :'epsg:27700'}
    leeds_gdf = leeds.to_crs(required_proj)

    leeds_gdf_square = leeds_gdf.envelope
    leeds_gdf_square = gpd.GeoDataFrame(gpd.GeoSeries(leeds_gdf_square), columns = ['geometry'], crs={'init': 'epsg:3857'},)

    return leeds_gdf_square



def create_leeds_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of the outline of Leeds in the projection specified

    Parameters
    ----------
        required_proj : Dict
            Python dictionary with a key init that has a value epsg:4326. 
            This is a very typical way how CRS is stored in GeoDataFrames 
            e.g. {'init' :'epsg:3785'} for Web Mercator
            or   {'init' :'epsg:4326'} for WGS84

    Returns
    -------
        leeds_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of Leeds
    
    '''
    # Read in outline of Leeds wards  
    wards = gpd.read_file("/nfs/a319/gy17m2a/PhD/datadir/SpatialData/england_cmwd_2011/england_cmwd_2011.shp")
    # Create column to merge on
    wards['City'] = 'Leeds'
    # Merge all wards into one outline
    leeds = wards.dissolve(by = 'City')

    # Convert Leeds outline geometry to WGS84
    leeds.crs = {'init' :'epsg:27700'}
    leeds_gdf = leeds.to_crs(required_proj)

    return leeds_gdf


# def create_northern_outline (required_proj):
#     '''
#     Description
#     ----------
#         Creates a shapely geometry of the outline of the Northern area (including
#         North East, North West and Yorkshire and the Humber) in the projection specified

#     Parameters
#     ----------
#         required_proj : Dict
#             Python dictionary with a key init that has a value epsg:4326. 
#             This is a very typical way how CRS is stored in GeoDataFrames 
#             e.g. {'init' :'epsg:3785'} for Web Mercator
#             or   {'init' :'epsg:4326'} for WGS84

#     Returns
#     -------
#         northern_gdf : Geodataframe
#             Dataframe contaiing coordinates of outline of Northern region
    
#     '''
#     # Read in outline of UK
#     uk_regions = gpd.read_file("PhD/datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
#     # Select only requried regions
#     northern_regions = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
#     # Merge the three regions into one
#     northern_regions['merging_col'] = 0
#     northern_gdf = northern_regions.dissolve(by='merging_col')
#     northern_gdf = northern_gdf.to_crs(required_proj)
    
#     return northern_gdf


# def create_wider_northern_outline (required_proj):
#     '''
#     Description
#     ----------
#         Creates a shapely geometry of the outline of a wider Northern area (including
#         North East, North West, Yorkshire and the Humber, East Midlands and West Midlands and
#         Dumfries and Galloway and the Borders)
#         in the projection specified

#     Parameters
#     ----------
#         required_proj : Dict
#             Python dictionary with a key init that has a value epsg:4326. 
#             This is a very typical way how CRS is stored in GeoDataFrames 
#             e.g. {'init' :'epsg:3785'} for Web Mercator
#             or   {'init' :'epsg:4326'} for WGS84

#     Returns
#     -------
#         wider_northern_gdf : Geodataframe
#             Dataframe contaiing coordinates of outline of wider Northern region
    
#     '''
#     # Read in outline of UK
#     uk_regions = gpd.read_file("PhD/datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
#     # England part
#     wider_northern_gdf = uk_regions.loc[uk_regions['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber', 'East Midlands', 'West Midlands'])]
#     wider_northern_gdf['merging_col'] = 0
#     wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
#     wider_northern_gdf = wider_northern_gdf[['geometry']]
    
#     # Scotland part
#     # D and G
#     dg = gpd.read_file("PhD/datadir/SpatialData/2011_Census_Dumfries_and_Galloway_(shp)/DC_2011_EoR_Dumfries___Galloway.shp")
#     dg['merging_col'] = 0
#     dg = dg.dissolve(by='merging_col')
#     # Borders
#     borders = gpd.read_file('PhD/datadir/SpatialData/Scottish_Borders_shp/IZ_2001_EoR_Scottish_Borders.shp')
#     borders['merging_col'] = 0
#     borders = borders.dissolve(by='merging_col')
    
#     southern_scotland = pd.concat([dg, borders])
#     southern_scotland['new_merging_col'] = 0
#     southern_scotland = southern_scotland.dissolve(by='new_merging_col')
#     southern_scotland = southern_scotland[['geometry']]
    
#     # Join the two
#     wider_northern_gdf = pd.concat([southern_scotland, wider_northern_gdf])
#     wider_northern_gdf['merging_col'] = 0
#     wider_northern_gdf = wider_northern_gdf.dissolve(by='merging_col')
#     wider_northern_gdf = wider_northern_gdf.to_crs(required_proj) 
    
#     return wider_northern_gdf

def create_uk_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of the outline of the UK in the projection specified
        Involves joining a gdf of UK with one of Ireland
        
    Parameters
    ----------
        required_proj : Dict
            Python dictionary with a key init that has a value epsg:4326. 
            This is a very typical way how CRS is stored in GeoDataFrames 
            e.g. {'init' :'epsg:3785'} for Web Mercator
            or   {'init' :'epsg:4326'} for WGS84

    Returns
    -------
        uk_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of UK region
    
    '''
    # Read in outline of UK
    uk_regions = gpd.read_file("/nfs/a319/gy17m2a/PhD/datadir/SpatialData/UK_shp/GBR_adm1.shp") 
    uk_regions = uk_regions.to_crs({'init' :'epsg:27700'}) 
    uk_regions = uk_regions[['geometry']]

    roi_regions = gpd.read_file("/nfs/a319/gy17m2a/PhD/datadir/SpatialData/IRL_adm/IRL_adm1.shp") 
    roi_regions = roi_regions.to_crs({'init' :'epsg:27700'}) 
    roi_regions = roi_regions[['geometry']] 

    # # Join the two
    uk_gdf = pd.concat([uk_regions, roi_regions])
    uk_gdf['merging_col'] = 0
    uk_gdf = uk_gdf.dissolve(by='merging_col')

    # Convert to required projection
    uk_gdf = uk_gdf.to_crs(required_proj) 

    return uk_gdf


def create_gb_outline (required_proj):
    '''
    Description
    ----------
        Creates a shapely geometry of the outline of the UK in the projection specified
        Involves joining a gdf of UK with one of Ireland
        
    Parameters
    ----------
        required_proj : Dict
            Python dictionary with a key init that has a value epsg:4326. 
            This is a very typical way how CRS is stored in GeoDataFrames 
            e.g. {'init' :'epsg:3785'} for Web Mercator
            or   {'init' :'epsg:4326'} for WGS84

    Returns
    -------
        uk_gdf : Geodataframe
            Dataframe contaiing coordinates of outline of UK region
    
    '''
    # Read in outline of UK
    uk_regions = gpd.read_file("/nfs/a319/gy17m2a/PhD/datadir/SpatialData/UK_shp/GBR_adm1.shp") 
    uk_regions= uk_regions[uk_regions['NAME_1'] !='Northern Ireland'] 
    uk_regions = uk_regions.to_crs({'init' :'epsg:27700'}) 
    uk_regions = uk_regions[['geometry']]

    # Convert to required projection
    uk_regions = uk_regions.to_crs(required_proj) 

    merged_geometry = uk_regions.geometry.unary_union

    # Convert the merged geometry into a single Polygon
    if merged_geometry.geom_type == 'MultiPolygon':
        # If the merged geometry is a MultiPolygon, you can take its convex hull
        # or apply any other method to convert it into a single Polygon.
        single_polygon = merged_geometry.convex_hull
    elif merged_geometry.geom_type == 'Polygon':
        # If the merged geometry is already a Polygon, you can directly use it.
        single_polygon = merged_geometry
    else:
        # Handle other cases if necessary
        single_polygon = None
    merged_geometry

    # Create a DataFrame with a single row containing the merged geometry
    data = {'geometry': [merged_geometry]}
    merged_gdf = gpd.GeoDataFrame(data, crs=uk_regions.crs)
    
    return merged_gdf
