import geopandas as gpd
shapefile = gpd.read_file("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/LeedsCatchments/LeedsCatchments.shp")
print(shapefile)
shapefile.plot(facecolor = 'None', edgecolor = 'black')


df = data.frame(shapefile)
shapefile.data


import numpy as np
import matplotlib.pyplot as plt
np.histogram(shapefile['PLAN_AREA'])
plt.hist(shapefile['PLAN_AREA'])


shapefile['Area_decimal'] = shapefile['PLAN_AREA'].apply(lambda x:'%.08f' % x)
shapefile['Area_decimal'] = float(shapefile['Area_decimal'])
plt.hist(shapefile['Area_decimal'], bins = 25)
plt.xlabel('Catchment area')
plt.ylabel('Number of catchments')