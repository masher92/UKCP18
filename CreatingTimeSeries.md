## Creating long time series  
Hourly values are provided for both precipitation observations and projections and these are provided grouped into monthly data files covering the whole of the UK.  
  
For this analysis, we are interested in producing a long time-series, for instance covering the whole of one of the contiguous periods for which data is provided (e.g. 1981-2000, 2021-2040, 2061-2080) for one grid square which covers a location of interest.   

The structure of the observations and projections data is different and so the process for extracting this timeseries varies slightly between the two.   

For modelled projections:  
* Read all of monthly cubes required for the time-series into a cubeList
* Define the coordinates of the location of interest and convert these into the projection system in which the modelled data is stored (rotated pole)  
* Concatenate the cubes in the list together:
     * sdsdlsd




For observations:  
* Read all of monthly cubes required for the time-series into a cubeList

