# Rainfall Regionalisation
EVT needs sufficient data in order to produce reliable estimates of long return period events. Often both observational records and model runs are not long enough to allow for this. One method of dealing with this data shortage is to pool data spatially and to use data from multiple stations or grid boxes in the same analysis. This regionalisation process trades space for time and allows better estimation of the extreme value distribution. Regionalisation requires a means of determining areas which have similar enough rainfall characteristics to be grouped together. These regions are generally geographically coherent areas with similar physical and/or climatic features according to the focus of the analysis. For instance, where extreme values are of interest, extreme value statistics should be used in regionalisation. The size of the regions must be large enough to confer a benefit over analysing all locations separately; however, must not be too large so as points within the region becomes too different from one another (Johnson and Green, 2018).

## Process

1. Find statistics for all grid cells in a large region covering the North of England. Convert these into the format required by the HiClimR package; this is a dataframe in which each row is a location with a lat and long coordinate, and the columns contain the statistics for that point. Statistics calculated include:

Statistics calculated as annual seasonal (June-July-August) values (i.e. one value for each year of data):
   * Max
   * Mean
   * Percentiles (95th, 97th, 99th, 99.5th) 
   * Greatest ten/twenty values
Statistics calculated over the whole time period (i.e. all years of data considered together)
   * Values over percentile - over whole time period 
   
2. Trim the statistics dataframes so that they refer to smaller regions, e.g. the West Yorkshire Region, a square area centred around Leeds, the region of Northern England with the parts not over land removed.

3. Use the statistics to regionalise the locations into clusters of specified sizes using the HiClimR R Package.

4. Plot the regions.


## Code
1. FindStats.py finds all statistics in one go. 
2. 


## Results
