## Code
Uses CSV files created in CreateTimeSeries.py to plot PDFs.  
Currently this includes plotting of individual PDFs, and a single plot with multiple PDFs included (e.g. observations, projections from different ensemble members).  
It also has the option to convert one/both axes to a log scale. 

### Methods for plotting PDFs
#### Log Discreate Histogram
This PDF plotting method is based around 

That's almost right: the process is indeed based around creating bins of equal width in log10; and where this results in bins on a linear scale which have a width < 0.1 (the level to which the data is rounded) then instead a width of 0.1 is used. Additionally, bin width is rounded down to a multiple of 0.1, so "bin edges" are always located mid-way on the discretisation intervals (this is the right thing to do if the data itself is rounded to the nearest multiple of 0.1).
Would it be accurate to say the process is based around creating bins of equal width in log10; however, in cases where this results in bins on a linear scale which have a width < 0.1 (the level to which the data is rounded) then instead a width of 0.1 is used.

https://rmets.onlinelibrary.wiley.com/doi/full/10.1002/qj.1903 == 
The precipitation rate has been aggregated into logarithmic‐spaced histogram bins (with just over 26 bins per decade) and the probability density in each rain‐rate bin is calculated as
