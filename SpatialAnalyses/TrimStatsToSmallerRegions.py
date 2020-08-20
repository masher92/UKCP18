############################################
# Set up environment
#############################################
import sys
import iris
import os
import iris.quickplot as qplt
import warnings
from timeit import default_timer as timer
import glob
import numpy as np
import iris.quickplot as qplt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import tilemapbase
from shapely.geometry import Polygon
import iris.coord_categorisation
import time 
warnings.filterwarnings("ignore")

# Set working directory - 2 options for remote server and desktop
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
#root_fp = "/nfs/a319/gy17m2a/"
os.chdir(root_fp)

region= 'Leeds-at-centre'
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']

############################################
# Create regions
#############################################
if region == 'WY' or region == 'WY_square':
    regional_gdf = gpd.read_file("datadir/SpatialData/combined-authorities-april-2015-super-generalised-clipped-boundaries-in-england.shp") 
    regional_gdf = regional_gdf[regional_gdf['cauth15cd'] == 'E47000003']
    regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
elif region == 'Northern': 
    # Create geodataframe of West Yorks
    uk_gdf = gpd.read_file("datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
    regional_gdf = uk_gdf.loc[uk_gdf['rgn15nm'].isin(['North West', 'North East', 'Yorkshire and The Humber'])]
    regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
    # Merge the three regions into one
    regional_gdf['merging_col'] = 0
    regional_gdf = regional_gdf.dissolve(by='merging_col')
elif region == 'Leeds-at-centre':
    # Create region with Leeds at the centre
    lons = [54.130260, 54.130260, 53.486836, 53.486836]
    lats = [-2.138282, -0.895667, -0.895667, -2.138282]
    polygon_geom = Polygon(zip(lats, lons))
    regional_gdf = gpd.GeoDataFrame(index=[0], crs={'init': 'epsg:4326'}, geometry=[polygon_geom])
    regional_gdf = regional_gdf.to_crs({'init' :'epsg:3785'}) 
    
    
########    
for em in ems:    
    print(em)
    #Read in data        
    stats_data = pd.read_csv("Outputs/HiClimR_inputdata/NorthernSquareRegion/Greatest_ten/em_{}.csv".format(em))
    mask = pd.read_csv("Outputs/HiClimR_inputdata/{}/mask.csv".format(region))

    str(mask['lon'].iloc[25])[::-1].find('.')
    str(stats_data['lon'].iloc[200])[::-1].find('.')
    str(stats_data['lat'].iloc[200])[::-1].find('.')
    str(mask['lat'].iloc[200])[::-1].find('.')
    
    if not str(ArithmeticErrorstats_data['lon'].iloc[200])[::-1].find('.') == str(mask['lon'].iloc[25])[::-1].find('.'):
        print("Rounding problem in lons")
    if not str(stats_data['lat'].iloc[200])[::-1].find('.') == str(mask['lat'].iloc[25])[::-1].find('.'):
        print("Rounding problem in lats")
    
    # Round for joining    
    stats_data = stats_data.round({'lat': 5, 'lon': 5})
    mask= mask.round({'lat': 5, 'lon': 5})
    
    if not str(stats_data['lon'].iloc[200])[::-1].find('.') == str(mask['lon'].iloc[25])[::-1].find('.'):
        print("Still rounding problem in lons")
    if not str(stats_data['lat'].iloc[200])[::-1].find('.') == str(mask['lat'].iloc[25])[::-1].find('.'):
        print("Still rounding problem in lats")
    
    # Join the mask with the stats 
    #joined = pd.concat([mask, stats_data], axis=1)
    joined = mask.merge(stats_data,  on=['lat', 'lon'], how="left")
    
    # Remove NAs - outside mask
    print(joined.isnull().values.any())
    joined = joined.dropna()
    
    # Keep only the relevant columns
    joined = joined.iloc[:,20:]
    
    ddir = "Outputs/HiClimR_inputdata/{}/Greatest_ten/".format(region)
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
        print("Greatest ten doesn't already exist, creating...")
    
    print(len(joined))
    if len(joined) == len(mask):
        joined.to_csv(ddir + "em{}.csv".format(em), index = False, float_format='%.12f')
        print("CSV created")
    
    ##### Testing
    #stats_data.loc[stats_data['lat'] == 53.499430342671]
    
    # # Save lats and lons
    # lats, lons = mask['lat'], mask['lon']

    # # Round for joining    
    # stats_data = stats_data.round({'lat': 2, 'lon': 2})
    # mask = mask.round({'lat': 2, 'lon': 2})
    
    # # Join the mask with the region codes
    # joined = mask.merge(stats_data,  on=['lat', 'lon'], how="left")
    
    # # Keep only the relevant columns
    # joined = joined.iloc[:,20:]


