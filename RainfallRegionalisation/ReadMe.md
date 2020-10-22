# Rainfall Regionalisation
Rainfall regionaliation is the process of dividing a study region into smaller regions which are homogenous in respect to a particular precipitation characteristic. It is typically achieved using some form of cluster analysis.

The regions bear some relationship to topography
Region 1 includes mainly the southern areas of the Zaire basin and the northern slopes of the central African plateau. Region 2, the easternmost region, lies over the western highlands of the Rift Valley. Region 3 includes mainly the highlands of the Central African Republic. Region 4 includes mainly the northern portion of the Zaire basin. Region 5, the westernmost region, includes the Atlantic coast and the highlands of Cameroon.


## Process
1. Find statistics for all grid cells in a large region covering the North of England. Convert these into the format required by the HiClimR package; this is a dataframe in which each row is a location with a lat and long coordinate, and the columns contain the statistics for that point. Statistics calculated include:
* Annual seasonal (June-July-August) values (i.e. one value for each year of data):
   * Max
   * Mean
   * Percentiles (95th, 97th, 99th, 99.5th)
   * Greatest ten/twenty values  
* Values over the whole time period (i.e. all years of data considered together)
   * Values over percentile (i.e. all values bigger than the Xth percentile including 99th, 99.5th, 99.9th, 99.95th, 99.99th percentiles).
   * A seasonal (June-July-August) value (i.e. one value for across the twenty years of data)

2. Trim the statistics dataframes so that they refer to smaller regions, e.g. the West Yorkshire Region, a square area centred around Leeds, the region of Northern England with the parts not over land removed.

3. Use the statistics to regionalise the locations into clusters of specified sizes using the HiClimR R Package.

4. Plot the regions.


## Code
1. FindStats.py finds all statistics in one go.
2.


## Results
Annual seasonal 99.5th, 99th, 97th and 95th percentiles and mean values produce clear clusters. The annual seasonal max and greatest ten and twenty values result in far more random clustering.   

Using values over percentiles for all the year's data concurrently results in the inclusion of the following number of data points:
* 432 values for the 99th Percentile  
* 216 values for the 99.5th Percentile  
* 44 values for the 99.9th Percentile   
* 22 values for the 99.95th Percentiles
* 5 values for the 99.99th Percentile

None of these data sets however result in the production of coherent clusters.

Checking data:
Values for each percentile are coherent e.g. 5 values for 99.99th percentile are the top 5 values in 99th Percentile values and so on.  


## Questions/Thoughts
Northern - tested one ensemble member for values over percentile (97) and it looked similarly noisy to the Leeds area. Didn't seem any point in downloading the rest.

30/09/20 - Noticed discrepancy between the maximum values found when creating table with max/min values etc in the HiCliMRRegions_meteorology () file and the maximum values found when making the UK_stats plots (trimmed to Leeds area). Tried various ways of fixing this discrepancy and realised a number of things:
1. The method for trimming to the region resulted in slightly different numbers of cells included
2. One was using the season_year whilst the other was using just the seasonal (don't think this actually made a difference as the code loops through the years one by one, so the two are essentially the same). For ValuesOver20Years need to use the season in aggregation
3. FindStats did not include data from the year 2000
Think I fixed all these problems in the code (but imagine they could persist elsewhere)

Also requires lots of new production of results:
FindStats - max, mean and 6 percentiles, values over 20 years (max, mean, 6Percentiles) (NOT values above percentiles, seeing as values for this weren't good anyway)
  - Trimmed to leeds-at-centre for all of above  (and exported to desktop)
      - (max, mean, 6Percentiles) - HiClimROutputs and Plots produced
  - Trimmed to Northern for all of above (and exported to desktop)
    - (max, mean, 6Percentiles) - HiClimROutputs and Plots produced
    
ValuesOverPercentile & Greatest_ten = not updated, and deleted results from MobaXterm as they were rubbish
