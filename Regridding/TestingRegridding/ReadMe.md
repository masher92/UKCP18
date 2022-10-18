## Testing the impact of regridding on data values 

It is important to determine the affect of regridding on the data, and particularly on extreme values which can be smoothed in the regridding process.  
This was tested using both:
* Data from an individual cell
* Data from across all cells

### PDF plotting method
Visualising data distribution 
Histogram - the smaller we make the bins, the smoother the distribution gets. A smoothed density plot is basically the curve that goes through the top of each histogram bar when the bins are very small. 

The precipitation rates are aggregated into logarithmic-spaced histogram bins which are adjusted to ensure that none of the bin widths are narrower than one decimal place, as this is the degree to which the data is rounded. Additionally, bin width is rounded down to a multiple of 0.1, so bin edges are always located mid-way on the discretisation interval. The probability density in each bin with mean precipitation rate, P(r), is calculated as:  
<p align="center">P(r) = n(r)/NΔr <p align="center">

Where n(r) is the number of precipitation rates within the bin, Δr is the width of the bin in mm/hr and N is the total number of measurements in the whole dataset.

This PDF plotting method is based around

That's almost right: the process is indeed based around creating bins of equal width in log10; and where this results in bins on a linear scale which have a width < 0.1 (the level to which the data is rounded) then instead a width of 0.1 is used. Additionally, bin width is rounded down to a multiple of 0.1, so "bin edges" are always located mid-way on the discretisation intervals (this is the right thing to do if the data itself is rounded to the nearest multiple of 0.1). Would it be accurate to say the process is based around creating bins of equal width in log10; however, in cases where this results in bins on a linear scale which have a width < 0.1 (the level to which the data is rounded) then instead a width of 0.1 is used.

https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/qj.1903 == The precipitation rate has been aggregated into logarithmic‐spaced histogram bins (with just over 26 bins per decade) and the probability density in each rain‐rate bin is calculated as
