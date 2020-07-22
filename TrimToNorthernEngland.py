import numpy as np
import geopandas as gpd
import iris
from pyproj import Proj, transform
from shapely.geometry import Point, Polygon


# Data from https://geoportal.statistics.gov.uk/datasets/regions-december-2015-full-extent-boundaries-in-england/data
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"

# Create geodataframe of West Yorks
wy_gdf = gpd.read_file(root_fp + "datadir/SpatialData/Region__December_2015__Boundaries-shp/Region__December_2015__Boundaries.shp") 
northern_regions = wy_gdf.loc[wy_gdf['rgn15nm'].isin(['North East', 'North West', 'Yorkshire and The Humber'])]
#northern_regions = northern_regions.to_crs({'init' :'epsg:3785'}) 

# Merge the three regions into one
northern_regions['merging_col'] = 0
northern_regions_combi = northern_regions.dissolve(by='merging_col')

# Check by plotting
fig, ax = plt.subplots(figsize=(20,20))
plot =northern_regions_combi.plot(ax=ax, categorical=True, alpha=1, edgecolor='red', color='none', linewidth=6)

