# Import necessary functions
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

## Create function to create a colour map which visualises precipitation values nicely
def create_precip_cmap():
    tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
    "#72190E","#882E72","#000000"]                                      
    precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
    # Set the colour for any values which are outside the range designated in lvels
    precip_colormap.set_under(color="white")
    precip_colormap.set_over(color="white")
    return precip_colormap


#############################################
# Read in data
#############################################
em_mean_feb_baseline = iris.load("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/Alasdair/datadir/UKCP18/feb_em_means_1980-2001_trimmed.nc")[0]
em_mean_feb_future= iris.load("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir/Alasdair/datadir/UKCP18/feb_em_means_2060-2081_trimmed.nc")[0]

#############################################################################  
#############################################################################
# Plotting
#############################################################################
#############################################################################
# Create a colourmap                                   
precip_colormap = create_precip_cmap()

# Set up a plotting figurge with Web Mercator projection
proj = ccrs.Mercator.GOOGLE
fig = plt.figure(figsize=(20,20), dpi=200)
ax = fig.add_subplot(122, projection = proj)
mesh = iplt.pcolormesh(em_mean_feb_future,cmap = precip_colormap)
# Add regional outlines,
wider_northern_gdf.plot(ax=ax, edgecolor='black', color='none', linewidth=2)
cb1 = plt.colorbar(mesh, ax=ax, fraction=0.053, pad=0.03)
cb1.ax.tick_params(labelsize=15)
