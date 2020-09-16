## Regridding

There are two main data sources being used in this analysis:
* UKCP18 2.2km model data
* CEH-GEAR 1km observations

In order to use the observations to validate the model data it is necessary to convert the two datasets to a common resolution.
Iris provides functionality to regrid the cube data from one model, using the horizontal grid of another cube. For instance, in this case regridding the 1km observations cube using the 2.2km horizontal grid from the model cube. A linear regridding scheme is used which calculates the value at a point by extending the gradient of the closest two points.

<p align="center">
  <img src="Figs/rf_cube_grid.png" width="300"  title="Original 1km grid" />
  <img src="Figs/rg_cube_grid.png" width="300"  title="Regridded 2.2km grid" /> 
</p>
<p align="center"> 1km grid on which observations are originally supplied (left); and UKCP18 2.2km grid onto which the observations are regridded (right) <p align="center">

It is important to determine the affect of regridding on the data, and particularly on extreme values which can be smoothed in the regridding process. To test this, a location is defined in east Leeds at latitude: 53.79282 and longitude: -1.37818. The grid cell which covers this point is determined for both the native 1km and regridded 2.2km observations data 
<p align="center">
  <img src="Figs/rf_cube.png" width="300"  title="Original 1km grid" />
  <img src="Figs/rg_cube.png" width="300"  title="Regridded 2.2km grid" /> 
</p>
<p align="center"> Grid cell containing location in east Leeds for 1km grid (left) and 2.2km grid (right) <p align="center">

The hourly observations are then extracted from the appropriate grid cell over the period for which data is available (1990-2014). Using this data, PDFs of precipitation rates during wet hours (<0.1mm/hr) are plotted for both the original 1km data and the regridded 2.2km data.  The precipitation rates are aggregated into logarithmic-spaced histogram bins which are adjusted to ensure that none of the bin widths are narrower than one decimal place, as this is the degree to which the data is rounded. Additionally, bin width is rounded down to a multiple of 0.1, so bin edges are always located mid-way on the discretisation interval. The probability density in each bin with mean precipitation rate, P(r), is calculated as:
P(r) = n(r)/Nr
Where n(r) is the number of precipitation rates within the bin, r is the width of the bin in mm/hr and N is the total number of measurements in the whole dataset (Holloway et al., 2012).

Across most probabilities, the observed precipitation rate is lower then the modelled precipitation rate across all ensembles. This is increasingly true for higher intensity precipitation rates. It should be noted that the CEH-GEAR data is interpolated and so extreme values are likely to be smoothed. In Fig. 5.3b a smoother line is achieved for the projections as data is accumulated across ensemble members, but there are still too few observations at higher intensities to produce a good line.




