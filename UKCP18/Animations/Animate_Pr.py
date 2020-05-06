# Script is very temperamental
#The plt.rcParams line seemingly needs to come straight after the plt.rcParams
# Can which locaiton of ffmpeg with "which ffmpeg" on linux

#############################################
# Set up environment
#############################################
import iris
import os
import iris.quickplot as qplt
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
import matplotlib.pyplot as plt
plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'
warnings.simplefilter(action='ignore', category=FutureWarning)

# Define the local directory where the data is stored
ddir="/nfs/a319/gy17m2a/"
os.chdir(ddir)

# Specify path to ffmpeg wrier
#plt.rcParams['animation.ffmpeg_path'] = '/nfs/a319/gy17m2a/ffmpeg-latest-win64-static/bin/ffmpeg'
#plt.rcParams['animation.ffmpeg_path'] = '/usr/bin/ffmpeg'
#plt.rcParams['animation.ffmpeg_path'] = 'ffmpeg-20200225-36451f9-win64-static/bin/ffmpeg'

# Time constraint for which to test the data
days_constraint = iris.Constraint(time=lambda cell: PartialDateTime(year = 1980, month=12, day=1) < cell.point < PartialDateTime(year = 1980, month=12, day=5))

###############################################################################
# Load in a timeseries for a specific location (data to be checked)
###############################################################################
# Load in the time series cube
pr_ts_cube = iris.load('Outputs/TimeSeries_cubes/Armley/2.2km/EM01_1980-2001.nc')[0]
# load in the time series dataframe
#pr_ts_df = pd.read_csv(f"Outputs/TimeSeries/Pr_{start_year}-{end_year}_EM01.csv")
#print(pr_ts_df)

# Extract the data which matches the constraint
pr_ts_cube = pr_ts_cube.extract(days_constraint)

###############################################################################
# Load in one month's worth of data in a cube for whole of country
###############################################################################                               
filename = "UKCP18/2.2km/01/1980_2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19801201-19801230.nc"
month_uk_cube = iris.load(filename,'lwe_precipitation_rate')[0]
# Remove ensemble member dimension
month_uk_cube = month_uk_cube[0, :]

# Extract the data which matches the constraint
month_uk_cube = month_uk_cube.extract(days_constraint)

#################################################################
# Trim the precipitation cube to a narrower area
###############################################################################
# Zoom
lat_constraint = iris.Constraint(grid_latitude=lambda cell: -1 < cell < 2)
long_constraint = iris.Constraint(grid_longitude=lambda cell: 359 < cell < 362)

# Mega Zoom
#lat_constraint = iris.Constraint(grid_latitude=lambda cell: 0.95 < cell < 1.55)
#long_constraint = iris.Constraint(grid_longitude=lambda cell: 360.5 < cell < 360.9)

# DO the trimming
month_uk_cube = month_uk_cube.extract(lat_constraint)
month_uk_cube = month_uk_cube.extract(long_constraint)

###############################################################################
# Plot the timeseries
###############################################################################
qplt.plot(pr_ts_cube)
#plt.xticks(rotation=90)
plt.show()

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
    # Clear the previous figure
    plt.clf()
    grid = month_uk_cube[frame]
    levels = np.round(np.linspace(0.1, max_value, 50 ), 2 )
    contour = qplt.contourf(grid,levels=levels,cmap=precip_colormap, extend="both")
    plt.gca().coastlines(resolution='50m', color='black', linewidth=0.5)
    plt.plot(0.6628091964140957, 1.2979678925914127, 'o', color='black', markersize = 3) 
    # Create datetime in human readable format
    datetime = grid.coord('time').units.num2date(grid.coord('time').points[0]) 
    title = u"%s — %s" % (month_uk_cube.long_name, str(datetime))
    plt.title(title)
    return contour
    
def init():
    return draw(0)

def animate(frame):
    return draw(frame)

# Not sure what, if anything, this does
from matplotlib import rc, animation
rc('animation', html='html5')

ani = animation.FuncAnimation(fig, animate, frames, interval=10, save_count=50, blit=False, init_func=init,repeat=False)
ani.save('Outputs/CEH-GEAR/Armley/Dec1980.mp4', writer=animation.FFMpegWriter(fps=8))



