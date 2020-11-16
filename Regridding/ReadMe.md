# Regridding

There are two main data sources being used in this analysis:
* UKCP18 2.2km model data
* CEH-GEAR 1km observations

The layout of these grids over the Leeds region can be seen in Figure 1. 

<p align="center">
  <img src="Figs/1km_grid.png" width="300"  title="Original 1km grid" />
  <img src="Figs/2.2km_grid.png" width="300"  title="Regridded 2.2km grid" />
</p>
<p align="center"> Figure 1. Layout of 1km observations grid (model) and 2.2km model grid (right) <p align="center">

In order to use the observations to validate the model data it is necessary to convert the two datasets to a common resolution.  
Iris provides functionality to regrid cube data using the horizontal grid of another cube. For instance, in this case regridding the 1km observations cube using the 2.2km horizontal grid from the model cube.  

Regridding involves changing the grid on which data values are provided, whilst ensuring that the qualities of the data are preserved. This is done using the horizontal grid of another cube.

Iris offers a number of methods by which to perform this regridding:
* Linear regridding: extrapolation point will be calculated by extending the gradient of the closest two points.

Linear interpolation is a simple technique used to estimate unknown values that lie between known values. The concept of linear interpolation relies on the assumption that the rate of change between the known values is constant and can be calculated from these values using a simple slope formula. Then, an unknown value between the two known points can be calculated using one of the points and the rate of change. Linear interpolation is a relatively straightforward method, but is often not sophisticated enough to effectively interpolate station data to an even grid.

* Nearest neighbour regridding: extrapolation points take their value from the nearest source point 

## Code work flow
* CEH-GEAR_reformat_and_regrid.py:   
  * Reformats the observations data so it can be used in Iris regridding functionality; and
  * Performs regridding to the same format as the 2.2km UKCP18 cube.  
  * Saves a netCDF copy of both the reformatted observations and regridded observations.
* Check_reformat.py: 
  * Checks the reformatting process above works. Checks similarity between max/mean values between original and reformatted data and checks plotting.
* TestingRegridding_CreateTimeSeries.py: 
  * Finds the grid cell covering a point of interest for both the original and reformatted observations data.  
  * Creates a csv containing a 20 year time series of data at this location.    
* TestingRegridding_plotPDFs.py: 
  * Uses the timeseries from above to plot PDFs and percentile threshold plots.


## Questions
* Comparing PDF for the grid containing a point location; however, one of these grid cells is over double the size of the other so is this a fair comparison?
* Comparing PDF over a wider area: but if e.g. select 9 grid cells closest to the point of interest this will result in quite significantly areal coverage between the original 1km and regridded 2.2km data. Should they cover same area to be comparable? If just looked at all grid cells covering an area e.g. Leeds this would be very slow (loading 20 years of data for just one grid cell is slow).


## Next steps
* Look at observations from rain gauge data and cross-check the CEH-GEAR data with these as well
* Once satisfied with the regridded observations, plot the observations over the UK for various stats as have done with the model data. Then create difference plots (difference between each EM and the observations).

