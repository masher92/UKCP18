## Testing the impact of regridding on data values 

It is important to determine the affect of regridding on the data, and particularly on extreme values which can be smoothed in the regridding process.  
This was tested using both:
* Data from an individual cell
* Data from across all cells

### PDF plotting method
The precipitation rates are aggregated into logarithmic-spaced histogram bins which are adjusted to ensure that none of the bin widths are narrower than one decimal place, as this is the degree to which the data is rounded. Additionally, bin width is rounded down to a multiple of 0.1, so bin edges are always located mid-way on the discretisation interval. The probability density in each bin with mean precipitation rate, P(r), is calculated as:  
<p align="center">P(r) = n(r)/NΔr <p align="center">

Where n(r) is the number of precipitation rates within the bin, Δr is the width of the bin in mm/hr and N is the total number of measurements in the whole dataset.
