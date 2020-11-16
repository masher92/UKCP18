## Testing the impact of regridding on data values 

It is important to determine the affect of regridding on the data, and particularly on extreme values which can be smoothed in the regridding process.  
To test this, a location with specific coordinates is defined and the grid cell which covers this point is determined for both the native 1km and regridded 2.2km observations data. 

The hourly observations are then extracted from the appropriate grid cell over the period for which data is available (1990-2014).   

Using this data, PDFs of precipitation rates are plotted for both the original 1km data and the regridded 2.2km data, using the method specified at the bottom. 

Hourly rainfall accumulations for a range of percentile thresholds are also plotted for both the regridded 2.2km data and the original 1km data.

### <ins> Example 1: Latitude: 53.79282 and longitude: -1.37818 </ins>

<p align="center">
  <img src="Figs/rf_cube.png" width="200"  title="Original 1km grid" />
  <img src="Figs/rg_cube.png" width="200"  title="Regridded 2.2km grid" />
</p>
<p align="center"> Figure 1. Grid cell containing location in east Leeds for 1km grid (left) and 2.2km grid (right) <p align="center">

<p align="center">
  <img src="Figs/log_discrete_histogram_20bins.png" width="200" />
  <img src="Figs/log_discrete_histogram_40bins.png" width="200" />
    <img src="Figs/log_discrete_histogram_60bins.png" width="200" />  
</p>
<p align="center"> Figure 2. PDF of precipitation rates with log-spaced histogram bins  <p align="center">

<p align="center">
  <img src="Figs/percentile_thresholds_allhours.png" width="200" />
  <img src="Figs/percentile_thresholds_wethours.png" width="200" />
</p>
<p align="center"> Figure 3. Hourly rainfall accumulations for percentile thresholds including all hours (left) and wet-hours with rainfall >0.1mm/hr (right) <p align="center">

### <ins> Example 2: Latitude: 53.796638 and longitude: -1.592600 </ins>
<p align="center">
  <img src="Figs/rf_cube_westleeds.png" width="200"  title="Original 1km grid" />
  <img src="Figs/rg_cube_westleeds.png" width="200"  title="Regridded 2.2km grid" />
</p>
<p align="center"> Figure 4. Grid cell containing location in west Leeds for 1km grid (left) and 2.2km grid (right) <p align="center">

<p align="center">
  <img src="Figs/log_discrete_histogram_20bins_westleeds.png" width="200" />
  <img src="Figs/log_discrete_histogram_40bins_westleeds.png" width="200" />
    <img src="Figs/log_discrete_histogram_60bins_westleeds.png" width="200" />  
</p>
<p align="center"> Figure 5. PDF of precipitation rates with log-spaced histogram bins <p align="center">

<p align="center">
  <img src="Figs/percentile_thresholds_allhours_westleeds.png" width="200" />
  <img src="Figs/percentile_thresholds_wethours_westleeds.png" width="200" />
</p>
<p align="center"> Figure 6. Hourly rainfall accumulations for percentile thresholds including all hours (left) and wet-hours with rainfall >0.1mm/hr (right) <p align="center">



