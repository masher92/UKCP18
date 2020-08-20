# Rainfall Regionalisation
Conducting  EVT  needs  a  lot  of  data.   Observational  records  of  model  runs  are  often  not  long  enough  to  allowreliable estimates of long-return period events.  One method of dealing with this is to pool data spatially and to usedata from multiple stations or grid boxes in the same analysis.  This trade off of space for timeSpatial pooling, or trading space for time Regional frequency analysis, or the index flood method Assume that theparameters of the GEV distribution (shape and scale) are the same over the entire region, and only the locationparameter  varies  Requires  splitting  study  area  into  regions  with  similar  rainfall  characteristics  Apply  EVT  tothe  region,  estimate  shape  and  scale  parameter  Re-apply  to  each  pixel  within  region,  holding  shape  and  scaleparameter constant and allowing the location parameter to vary If the definition of the homogenous regions is poor,the uncertainty around the return level estimates will be under-estimate....>FINISH

## Process
1. Find statistics for all grid cells in a large region covering the North of England. Convert these into the format required by the HiClimR package; this is a dataframe in which each row is a location with a lat and long coordinate, and the columns contain the statistics for that point. Statistics calculated include:
  * Max
  * Mean
  * Percentiles (95th, 97th, 99th, 99.5th) 
  * Greatest ten/twenty values

2. Trim the statistics dataframes so that they refer to smaller regions, e.g. the West Yorkshire Region, a square area centred around Leeds, the region of Northern England with the parts not over land removed.

3. Use the statistics to regionalise the locations into clusters of specified sizes using the HiClimR R Package.

4. Plot the regions.


