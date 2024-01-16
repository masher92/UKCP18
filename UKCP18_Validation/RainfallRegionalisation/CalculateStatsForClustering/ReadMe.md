## Calculating statistics for clustering
This directory contains code for producing statistics to be used in clustering a region on the basis of characteristics of its rainfall.

The clustering is performed in the RainfallRegionalisation/MakeClustersFromStats/ directory using the R package HiClimR.

HiClimR requires inputs in the format of dataframes in which the rows are locations, and the columns contain the lat and long values of these locations, and then the values to be used in defining the clusters.

### Workflow
* The FindStats*.py files create such dataframes for a region covering the bounding box of the Northern England region (North East, North West and Yorkshire and the Humber).
* CreateRegionalMasks.py creates masks which are used to trim these outputs to cover smaller specific regions. These masks have a row for each lat/long location from the cubes found within the region fo the bounding box of Northern England. Beside each location is a flag determining whether that location is found within the region to which the mask refers.
* TrimStatsToSmallerRegions.py is used to mask the outputs of FindStats*.py with the masks.

### Statistics calculated
* Annual values of the max, mean and percentiles (95,9 97, 99, 99.5, 99.75 and 99.9) are calculated for each year in 1980-2001. These are calculated using all yeas of data and using just the wet hours of data (0.1mm/hr precipitation) -- FindStats.py and FindStats_wethours.py
* One value for the max, mean and percentiles (95,9 97, 99, 99.5, 99.75 and 99.9) across all years of data is calculated using all hours of data -- FindStats_ValuesOver20Years.py. It was subsequently discovered that HiClimR requires at least 2 variables for each location to base clustering on and so this wasn't applied to the wet hours.
* All values over certain percentiles (95,9 97, 99, 99.5, 99.75 and 99.9) for each year of data between 1980-2001 are calculated using all hours of data -- FindStats_ValuesOverPercentile.py. Using these values in clustering in HiClimR did not produced good results and so this wasn't applied to the wet hours.
* The FindStats.py scripts originally contained code to find the greatest 20 values in each year. This was then trimmed to also produce a file containing only the greatest ten. This also did not produce good results, however, and so this was removed from the FindStats.py code.
