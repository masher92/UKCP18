import numpy as np
import os
from datetime import datetime
import pandas as pd
import glob
from shapely.geometry import Point, Polygon
import sys
import folium

# Set up path to root directory
root_fp = '/nfs/a319/gy17m2a/'
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis"
os.chdir(root_fp)

# Create path to files containing functions
sys.path.insert(0, root_fp + 'Scripts/UKCP18/GlobalFunctions')
from Spatial_plotting_functions import *
from Spatial_geometry_functions import *

#############################################################################
# Spatial data
#############################################################################
# This is the outline of Leeds
leeds_gdf = create_leeds_outline({'init' :'epsg:3857'})
# This is a square area surrounding Leeds
leeds_at_centre_gdf = create_leeds_at_centre_outline({'init' :'epsg:4326'})
# Convert to shapely geometry
geometry_poly = Polygon(leeds_at_centre_gdf['geometry'].iloc[0])


#############################################################################
# Loop through every text file in the directory
# Check if its lat-long coordinates are within the leeds-at-centre area
# If so, then find the date times that correspond to the precipitation values
# and save as a CSV.
#############################################################################
filenames= []
lats = []
lons = []
prop_nas = {}
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
        res = this_point.within(geometry_poly)
        
        # If it is then save the filename and the lats and lons
        # Convert to a csv, with datetimes and save to file
        if res ==True:
            filenames.append(filename)
            lats.append(lat)
            lons.append(lon)
            print(station_name)

            # Read in data entries containing precipitation values
            data=np.loadtxt(filename, skiprows = 21)
            
            # Store start and end dates
            startdate = firstNlines[7][16:26]
            enddate = firstNlines[8][14:24]

            # Convert to datetimes
            d1 = datetime(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8]), int(startdate[8:10]))
            d2 = datetime(int(enddate[0:4]), int(enddate[4:6]), int(enddate[6:8]), int(enddate[8:10]))
            
            # Find all hours between these dates
            time_range = pd.date_range(d1, d2, freq='H')    
            
            # Check if there are the correct number
            n_lines = firstNlines[10][19:-1]
            if int(n_lines) != len(time_range):
                print('Incorrect number of lines')
            
            # Create dataframe containing precipitation values as times
            precip_df = pd.DataFrame({'Datetime': time_range,
                                      'Precipitation (mm/hr)': data})
            
            # Save to file
            precip_df.to_csv("datadir/GaugeData/Newcastle/leeds-at-centre_csvs/{}.csv".format(station_name),
                             index = False)


            precip_df_nas = precip_df[precip_df['Precipitation (mm/hr)'] == -999]
            prop_na = round((len(precip_df_nas)/len(precip_df)) *100,2)
            prop_nas[station_name] = prop_na

# Create as a dataframe
locations_df = pd.DataFrame({'ID':'Placeholder',
                             'Latitude': lats,
                             'Longitude': lons})

#############################################################################
### Plot on map
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
m.save('Outputs/RainGaugeAnalysis/Newcastle_gauges_leeds_region.html')




