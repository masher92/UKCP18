NONE OF THE CODE OR OUTPUTS IN THIS FOLDER HAS BEEN UPDATED TO INCLUDE THE NEW UKCP18 2.2KM DATA.  
A LOT OF THE SCRIPT IS OLD, AND SO WOULD NEED TOO MUCH UPDATING TO BE CURRENTLY WORTH THE EFFORT

### Point location statistics

The 'CreateTimeSeries' directory contains code which finds the grid cell which a given latitude and longitude point is found within and extracts the timeseries of data for that location. There is a seperate script for the model and for the observations. The resulting timeseries is saved as both a netCDF cube and as a CSV.

The code is supposed to contain a section which checks whether the grid cell from which the data was extracted was the correct grid cell, through making a plot with the grid cell highlighted and the location of the lat/long plotted. This is currently not working.

The 'Animations' directory contains code for animating the plot of hourly rainfalls statistics, trimmed to a certain spatial extent, with a lat, long location highlighted. This is another means of sense checking whether the time series data has been extracted from the correct location. The timeseries is plotted on a graph and then this can be cross referenced against the movement of rainfall in the animation.



