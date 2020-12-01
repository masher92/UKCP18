##############################################################################
import matplotlib.pyplot as plt
import tilemapbase
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
from matplotlib import colors as c
from pyproj import Proj, transform
import folium
import pandas as pd
from branca.element import MacroElement
from jinja2 import Template

# Define the local directory 
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/")

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
    <li><span style='background:red;opacity:0.7;'></span>Environment Agency</li>
    <li><span style='background:green;opacity:0.7;'></span>City Council</li>
        <li><span style='background:orange;opacity:0.7;'></span>Met Office </li>
    <li><span style='background:purple;opacity:0.7;'></span>University (NCAS)</li>
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

##############################################################################
#### Create a shapely geometry of the outline of Leeds
##############################################################################
wards = gpd.read_file("datadir/SpatialData/england_cmwd_2011.shp")
# Create column to merge on
wards['City'] = 'Leeds'
# Merge all wards into one outline
leeds = wards.dissolve(by = 'City')

# Convert Leeds outline geometry to WGS84
leeds.crs = {'init' :'epsg:27700'}
leeds = leeds.to_crs({'init' :'epsg:3785'})

# Convert outline of Leeds into a polygon
leeds_poly = Polygon(leeds['geometry'].iloc[0])

#############################################################################
#### Rain gauge locations
##############################################################################
# Mo gauges
# Locations from
#mo_gauges = pd.read_csv('mo_raingauges_westyorks.csv')
#mo_gauges.rename({'Latitude':'Lat', '$Longitude':'Lon'}, axis='columns')

# Locations from subdirectories here: http://data.ceda.ac.uk/badc/ukmo-midas-open/data/uk-hourly-rain-obs/dataset-version-201901/west-yorkshire
# All the gauges here were also in the above dataset
mo_gauges= pd.DataFrame({'ID' : ["Bingley No.2","Huddersfield Oakes","Bradford", 
                                             "Emley moor", "Leeds weather centre",
                                             "Ryhill","Bramham", "Emley Moor No.2" ], 
                         'Latitude' : [53.811, 53.656, 53.814, 53.613, 53.801, 53.628, 53.869, 53.612], 
                         'Longitude' : [-1.867, -1.831, -1.774, -1.665, -1.561, -1.394, -1.319, -1.668]})
# Environment Agency gauges near leeds
ea_gauges = pd.DataFrame({'ID' : ["Eccup","Heckmondwike","Wakefield", "Farnley Hall", "Headingley"], 
                          'Latitude' : [53.88,  53.70, 53.68, 53.79, 53.83], 'Longitude' : [-1.53, -1.67, -1.48, -1.63, -1.59]})
# City council gauge
# Realised these are hourly gauges
# cc_gauges= pd.DataFrame({'Location' : ["Shadwell","Allerton Bywater","Pottery Fields", "Middleton", "Wetherby", "Otley"], 
#                          'Latitude' : [53.854273,  53.743051, 53.784921, 53.743026, 53.92456, 53.903934], 
#                          'Longitude' : [-1.475909, -1.366736,-1.541380, -1.551743, -1.389078, -1.694290]})

cc_gauges= pd.DataFrame({'ID' : ["Pottery Fields", ], 
                         'Latitude' : [53.784921], 
                         'Longitude' : [-1.541380]})

# The city council monitoring points
cc_monitoringpoints = pd.read_csv("datadir/GaugeData/CityCouncil/MonitoringPointLocations.csv",usecols = [0,1,2])
# Convert to WGS84
longs, lats = transform(Proj(init='epsg:27700'), Proj(init='epsg:4326'),
                                            np.array(cc_monitoringpoints['Northing']), 
                                            np.array(cc_monitoringpoints['Easting']))
cc_monitoringpoints['Longitude'], cc_monitoringpoints['Latitude'] = longs, lats
#cc_monitoringpoints = cc_monitoringpoints[cc_monitoringpoints['Monitoring Point']!= "St James's Street, Barleyfields, Wetherby"]



uni_gauges= pd.DataFrame({'ID' : ["NCAS", ], 
                         'Latitude' : [53.804560], 
                         'Longitude' : [-1.561534]})

#############################################################################
#### Reproject data to WM
#############################################################################
def reproject_wm (gauges_df):
    gauges_long_wm, gauges_lat_wm = transform(Proj(init='epsg:4326'),Proj(init='epsg:3785'),
                                            np.array(gauges_df['Longitude']), np.array(gauges_df['Latitude'])) 
    gauges_df['Long_wm'] = gauges_long_wm
    gauges_df['Lat_wm'] = gauges_lat_wm
    return gauges_df
    
ea_gauges = reproject_wm (ea_gauges)
cc_gauges = reproject_wm (cc_gauges)
mo_gauges = reproject_wm (mo_gauges)
uni_gauges = reproject_wm (uni_gauges)

#############################################################################
#### Plot static map
#############################################################################
fig, ax = plt.subplots(figsize=(20,20))
extent = tilemapbase.extent_from_frame(leeds, buffer=30)
plotter = tilemapbase.Plotter(extent, tilemapbase.tiles.build_OSM(), width=600)
plot = plotter.plot(ax)
plot = ax.plot(ea_gauges['Long_wm'], ea_gauges['Lat_wm'], 'o', color='black', markersize =10)
plot = ax.plot(cc_gauges['Long_wm'], cc_gauges['Lat_wm'], 'o', color='green', markersize =10)
plot = ax.plot(mo_gauges['Long_wm'], mo_gauges['Lat_wm'], 'o', color='red', markersize =10)
leeds.plot(ax=ax, categorical=True, alpha=1, edgecolor='firebrick', color='none', linewidth=6)
#plt.colorbar(plot,fraction=0.046, pad=0.04).ax.tick_params(labelsize='xx-large')
ax.tick_params(labelsize='xx-large')

#############################################################################
#### Plot folium map
#############################################################################
m = folium.Map(location=[53.826919, -1.530074])
# Add Leeds outline
folium.GeoJson(leeds).add_to(m)
# Add gauge data
for lon, lat, ID in zip(np.array(ea_gauges['Longitude']), ea_gauges['Latitude'], np.array(ea_gauges['ID'])):
    folium.Marker(location=[lat, lon],  icon=folium.Icon(color='red')).add_child(folium.Popup(ID)).add_to(m)
for lon, lat, Location in zip(np.array(cc_monitoringpoints['Longitude']), np.array(cc_monitoringpoints['Latitude']),  np.array(cc_monitoringpoints['Monitoring Point'])):
    folium.Marker(location=[lat, lon],popup = Location ,  icon=folium.Icon(color='green')).add_to(m)
#for lon, lat, ID in zip(np.array(cc_gauges['Longitude']), np.array(cc_gauges['Latitude']), np.array(cc_gauges['ID'])):
#    folium.Marker(location=[lat, lon],  icon=folium.Icon(color='green')).add_child(folium.Popup(ID)).add_to(m)
for lon, lat, ID in zip(np.array(mo_gauges['Longitude']), np.array(mo_gauges['Latitude']), np.array(mo_gauges['ID'])):
    folium.Marker(location=[lat, lon],  icon=folium.Icon(color='orange')).add_child(folium.Popup(ID)).add_to(m)
for lon, lat, ID in zip(np.array(uni_gauges['Longitude']), np.array(uni_gauges['Latitude']), np.array(uni_gauges['ID'])):
    folium.Marker(location=[lat, lon],  icon=folium.Icon(color='purple')).add_child(folium.Popup(ID)).add_to(m)    
# for lon, lat, Location in zip(np.array(mo_gauges_extra['Longitude']), np.array(mo_gauges_extra['Latitude']),  np.array(mo_gauges_extra['Location'])):
#     folium.Marker(location=[lat, lon],popup = Location ,  icon=folium.Icon(color='purple')).add_to(m)
# Add the legend sing template below
macro = MacroElement()
macro._template = Template(template)
m.get_root().add_child(macro)
m.save('Outputs/RainGaugeAnalysis/rain_gauges.html')


