import numpy as np
import os
import sys
from datetime import date, timedelta as td, datetime
import pandas as pd
import glob as glob
from pyproj import Proj, transform
import tilemapbase
from shapely.geometry import Point, Polygon
import folium

# Set up path to root directory
root_fp = '/nfs/a319/gy17m2a/'
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:3857'})

##############################################################################
## For adding static legend
##############################################################################
from branca.element import Template, MacroElement
# From: https://nbviewer.jupyter.org/gist/talbertc-usgs/18f8901fc98f109f2b71156cf3ac81cd
template = """
{% macro html(this, kwargs) %}

<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>jQuery UI Draggable - Default functionality</title>
  <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

  <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
  <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
  
  <script>
  $( function() {
    $( "#maplegend" ).draggable({
                    start: function (event, ui) {
                        $(this).css({
                            right: "auto",
                            top: "auto",
                            bottom: "auto"
                        });
                    }
                });
});

  </script>
</head>
<body>

 
<div id='maplegend' class='maplegend' 
    style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
     border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>
     
<div class='legend-title'>Rain gauge</div>
<div class='legend-scale'>
  <ul class='legend-labels'>
    <li><span style='background:red;opacity:0.7;'></span>QC Gauges.</li>
  </ul>
</div>
</div>
 
</body>
</html>

<style type='text/css'>
  .maplegend .legend-title {
    text-align: left;
    margin-bottom: 5px;
    font-weight: bold;
    font-size: 90%;
    }
  .maplegend .legend-scale ul {
    margin: 0;
    margin-bottom: 5px;
    padding: 0;
    float: left;
    list-style: none;
    }
  .maplegend .legend-scale ul li {
    font-size: 80%;
    list-style: none;
    margin-left: 0;
    line-height: 18px;
    margin-bottom: 2px;
    }
  .maplegend ul.legend-labels li span {
    display: block;
    float: left;
    height: 16px;
    width: 30px;
    margin-right: 5px;
    margin-left: 0;
    border: 1px solid #999;
    }
  .maplegend .legend-source {
    font-size: 80%;
    color: #777;
    clear: both;
    }
  .maplegend a {
    color: #777;
    }
</style>
{% endmacro %}"""


#################################################
lats = []
lons = []
station_names = []
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
        if res ==True :
            # Add station name and lats/lons to list
            lats.append(lat)
            lons.append(lon)
            station_names.append(station_name)
            
            
locations_df = pd.DataFrame({'ID':station_names,
                             'Latitude': lats,
                             'Longitude': lons})

#################################################
def reproject_wm (gauges_df):
    gauges_long_wm, gauges_lat_wm = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),
                                            np.array(gauges_df['Longitude']), np.array(gauges_df['Latitude'])) 
    gauges_df['Long_wm'] = gauges_long_wm
    gauges_df['Lat_wm'] = gauges_lat_wm
    return gauges_df
    
locations_df = reproject_wm (locations_df)

#############################################################################
#### Plot static map
#############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds_at_centre_gdf, buffer=30)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot = plotter.plot(ax)
plot = ax.plot(locations_df['Long_wm'], locations_df['Lat_wm'], 'o', color='red', markersize =10)
leeds_gdf.plot(ax=ax, categorical=True, alpha=1, edgecolor='black', color='none', linewidth=6)
#plt.colorbar(plot,fraction=0.046, pad=0.04).ax.tick_params(labelsize='xx-large')
ax.tick_params(labelsize='xx-large')

#############################################################################
#### Plot folium map
#############################################################################
m = folium.Map(location=[53.826919, -1.530074])
# Add Leeds outline
folium.GeoJson(leeds_gdf).add_to(m)
# Add gauge data
for lon, lat, ID in zip(np.array(locations_df['Longitude']), locations_df['Latitude'], np.array(locations_df['ID'])):
    folium.Marker(location=[lat, lon],  icon=folium.Icon(color='red')).add_child(folium.Popup(ID)).add_to(m)
# Add the legend sing template below
macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)
m.save('Outputs/RainGaugeAnalysis/Newcastle_gauges.html')
