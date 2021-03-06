## Creating long time series  
Hourly values are provided for both precipitation observations and projections and these are provided grouped into monthly data files covering the whole of the UK.  
  
For this analysis, a long time-series is required, covering the whole of one of the contiguous time-periods for which data is given (e.g. 1981-2000, 2021-2040, 2061-2080), related to one grid square covering a location of interest.   

The structure of the observations and projections data is different and so the process for extracting this timeseries varies slightly between the two.   

<i> NB: Might seem logical to first concatenate the monthly cubes into one cube and then interpolate just this cube. However, when I attempted to do this on my computer it crashed the computer (something to do with the file being too large to store in memory). Trying this approach on the SEE server it didn't crash but was still slower than with the methods below. </i>

<ins>For modelled projections: </ins> 
* Read all of monthly cubes required for the time-series into a cubeList
* Define the coordinates of the location of interest and convert these into the projection system in which the modelled data is stored (rotated pole)  
* Concatenate the cubes and interpolate to the location of interest. 
    1. Attempted this firstly by concatenating the cubes and then using Iris interpolate method but this was extremely slow/didn't complete, perhaps because the size of the concatenated cube was too large to load into memory. 
    2. Tested two alternative methods for this (option 2 is much faster -- check? -- and the results produced are identical)
        1. Interpolate each cube individually to the location of interest, save interpolated cubes to a list and then concatenate
        2. Concatenate cubeList into a single cube, find the latitude and longitude closest to the point of interest and then extract just the data for that lat/long from the cube (not sure whether this takes into account curvature of earth?). 


<ins>For observations:</ins>  
* Read all of monthly cubes required for the time-series into a cubeList
* Concatenate the list into one cube
* Define the coordinates of the location of interest 
* Find the lat/long in the observations which is closest to the location of interest.
     1. The observations data structure is different to the projections. The lat, long and precipitation values are stored on 2D arrays each with the same dimensions. The corresponding data points are found at the point in the arrays with the same index, e.g. index of 2,3 means at the 3rd row, 4th column. 
     2. Create tuples containing corresponding lat and long values, and loop through each tuple and determine which is closest to the location of interest.
* Trim the concatenated cube to the location of interest by subsetting it with the index of the closest location     


NB: CEH-GEAR data is in OSGB1936 / BNG (they appear in the code to be in the same system as the coordinates we are providing)

