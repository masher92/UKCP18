## Testing the impact of regridding on data values 

The impact of regridding on data values is tested here by comparing precipitation values from across all grid cells covering the 'leeds-at-centre' region for both the native 1km and regridded 2.2km observations data, shown in Figure 1. 

<p align="center">
  <img src="Figs/1km_grid.png" width="320" />
  <img src="Figs/2.2km_grid.png" width="320" />
</p>
<p align="center"> Figure 1. Layout of 2.2km (left) and 1km (grid) over 'leeds-at-centre' region. NB: some of the grid is msising in the bottom left hand corner because the only way I could get it to plot was by using the matplotlib pcolormesh rather than iplt.pcolormesh and finding the corner coordinates. <p align="center">

In each case, across all the grid cells within this area, all hourly precipitation observations are extracted over the whole period for which data is available (1990-2014).

Using this data, PDFs of precipitation rates are plotted for both the original 1km data and the regridded 2.2km data, using the method specified at the bottom.

<p align="center">
  <img src="Figs/log_discrete_histogram_43bins.png" width="320" />
  <img src="Figs/log_discrete_histogram_65bins.png" width="320" />
    <img src="Figs/log_discrete_histogram_77bins.png" width="320" />  
</p>
<p align="center"> Figure 1. PDF of precipitation rates with log-spaced histogram bins  <p align="center">
