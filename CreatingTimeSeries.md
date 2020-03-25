## Creating long time series  
Hourly values are provided for both precipitation observations and projections and these are provided grouped into monthly data files covering the whole of the UK.  
  
For this analysis, we are interested in producing a long time-series, for instance covering the whole of one of the contiguous periods for which data is provided (e.g. 1981-2000, 2021-2040, 2061-2080) for one grid square which covers a location of interest.   

The structure of the observations and projections data is different and so the process for extracting this timeseries varies slightly between the two.   

For modelled projections:  
* Read all of monthly cubes required for the time-series into a cubeList
* Define the coordinates of the location of interest and convert these into the projection system in which the modelled data is stored (rotated pole)  
* Concatenate the cubes and interpolate to the location of interest. 
    1. Attempted this firstly by concatenating the cubes and then using Iris interpolate method but this was extremely slow/didn't complete, perhaps because the size of the concatenated cube was too large to load into memory. 
    2. Tested two alternative methods for this (option 2 is much faster -- check? -- and the results produced are identical)
        1. Interpolate each cube individually to the location of interest, save interpolated cubes to a list and then concatenate
        2. Concatenate cubeList into a single cube, find the latitude and longitude closest to the point of interest and then extract just the data for that lat/long from the cube (not sure whether this takes into account curvature of earth?). 




For observations:  
* Read all of monthly cubes required for the time-series into a cubeList
* 



* 

