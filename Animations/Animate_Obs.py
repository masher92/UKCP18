#############################################
# Set up environment
#############################################
import iris
import os
import iris.quickplot as qplt
#import iris
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import iris.plot as iplt
from iris.time import PartialDateTime 
import matplotlib.animation as animation
#import time
import warnings
import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib  
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the local directory where the data is stored
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(ddir)

# Speify path to ffmpeg wrier
plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg-20200225-36451f9-win64-static/bin/ffmpeg'

# Data date range
start_year = 1990
end_year = 1992

# Time constraint for which to test the data
days_constraint = iris.Constraint(time=lambda cell: PartialDateTime(year = end_year, month=12, day=12) < cell.point < PartialDateTime(year = end_year, month=12, day=18))


###############################################################################
# Animate a month's worth of data over whole UK
###############################################################################  
# Create a colourmap                                   
tol_precip_colors = ["#90C987", "#4EB256","#7BAFDE", "#6195CF", "#F7CB45", "#EE8026", "#DC050C", "#A5170E",
"#72190E","#882E72","#000000"]                                      

precip_colormap = matplotlib.colors.ListedColormap(tol_precip_colors)
# Set the colour for any values which are outside the range designated in lvels
precip_colormap.set_under(color="white")
precip_colormap.set_over(color="pink")

# Create a figure
fig = plt.figure()

frames = month_uk_cube.shape[0]   # Number of frames
min_value = month_uk_cube.data.min()  # Lowest value
max_value = month_uk_cube.data.max()  # Highest value

def draw(frame):
    # Clear the previous figure, so that the colourbars dont overlay each other.
    plt.clf()
    # Extract one hour 
    hour = one_day[frame]
    #Extract the data
    hour_data = hour.data
    # Flip the data so it's not upside down
    hour_data_fl = np.flipud(hour_data)
    # Fill empty values with NaN
    hour_data_fl = hour_data_fl.filled(np.nan)  

    # Create the contour plot, with colourbar, with axes correctly spaced
    contour = plt.contourf(hour_data_fl, cmap=precip_colormap)
    contour = plt.colorbar()
    contour =plt.axes().set_aspect('equal') 
    #plt.gca().coastlines(resolution='50m', color='black', linewidth=0.5)
    # Make mark at index of point closest to our point of interest
    plt.plot(rv_closest_idx_fl[1], rv_closest_idx_fl[0], 'o', color='black', markersize = 3) 
        
    # Alternative using the Iris plotting functions
    hour.data = np.flipud(hour.data)
    contour = qplt.contourf(hour, cmap=precip_colormap, levels = levels)
    contour = plt.axes().set_aspect('equal') 
    plt.plot(rv_closest_idx_fl[1], rv_closest_idx_fl[0], 'o', color='black', markersize = 3) 
    # Coastlines doesnt work as not plotting spatial coordinates
    #plt.gca().coastlines(resolution='50m', color='black', linewidth=0.5)
    #plt.plot(53.802070, -1.588941, 'o', color='black', markersize = 10) 
      
    # Create datetime in human readable format
    datetime = hour.coord('time').units.num2date(hour.coord('time').points[0]) 
    
    title = u"%s — %s" % (hour.long_name, str(datetime))
    plt.title(title)
    return contour
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

ani = animation.FuncAnimation(fig, animate, frames, interval=5000, blit=False, init_func=init,
                              repeat=False)
ani.save('C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/test_obvs.mp4', writer=animation.FFMpegWriter(fps=8))
#plt.close(fig)


