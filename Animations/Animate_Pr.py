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
start_year = 1980
end_year = 1982

# Time constraint for which to test the data
days_constraint = iris.Constraint(time=lambda cell: PartialDateTime(year = end_year, month=11, day=1) < cell.point < PartialDateTime(year = end_year, month=11, day=14))

###############################################################################
# Load in a timeseries for a specific location (data to be checked)
###############################################################################
# Load in the time series cube
pr_ts_cube = iris.load(f'Outputs/TimeSeries_cubes/Pr_{start_year}-{end_year}.nc')[0]
print(pr_ts_cube)
# load in the time series dataframe
#pr_ts_df = pd.read_csv(f"Outputs/TimeSeries/Pr_{start_year}-{end_year}_EM01.csv")
#print(pr_ts_df)

# Extract the data which matches the constraint
pr_ts_cube = pr_ts_cube.extract(days_constraint)

###############################################################################
# Load in one month's worth of data in a cube for whole of country
###############################################################################                               
filename = "datadir/UKCP18/01/1980-2001/pr_rcp85_land-cpm_uk_2.2km_01_1hr_19821101-19821130.nc"
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

ani = animation.FuncAnimation(fig, animate, frames, interval=500, save_count=50, blit=False, init_func=init,repeat=False)
ani.save('PythonScripts/UKCP18/Animations/Figs/1982_whole.mp4', writer=animation.FFMpegWriter(fps=8))


