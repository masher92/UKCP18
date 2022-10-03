# Rainfall Regionalisation with HiClimR
Rainfall regionalisation is the process of dividing a study region into smaller regions which are homogenous in respect to a particular precipitation characteristic. It is typically achieved using some form of cluster analysis.
This directory contains code for carrying out this clustering using the HiClimR package in R.   

### HiClimR Workflow
* The code in the "RainfallRegionalisation/CalculateStatsForClustering/" directory produces input data for HiClimR in the required format, which is a numeric matrix in which:
    * The rows represent observations (locations)
    * The columns represent variables
* The "Define_HiClimR_Clusters.R" script uses these input files to create clusters. The HiClimR function requires the user to define the number of clusters to use and here clustering is attempted with 2, 3, 4, 5 and 10 clusters. It outputs dataframes in which:
  * The rows represent observations (locations)
  * The columns represent the cluster number into which each location has been placed
* The "PlotHiClimRRegions.py" script takes these output files and plots the cluster codes spatially
* Previously, the "PlotHiClimRRegions_meteorology.py" script was used for plotting the mean value of each statistic across the 12 ensemble members (e.g. for each cell the mean of the max values predicted in the 12 ensemble members). However, this was not actually very useful. The plotting carried out in "RegionalRainfallStats/" directory serves a similar function but shows something which is more clear to interpret.

<!---
Most of them just put nearly the whole area into one cluster, with one cell or so put into a different cluster. McQuitty method gave more reasonable looking clusters, but substantially different to the Ward's method clusters,
-->

### HiClimR Background Info
HiClimR is a tool for Hierarchical Climate Regionalisation. It is based upon Agglomerative Hierarchical Clustering (AHC) and builds on existing statistical tools in R.  
#### Clustering method: Agglomerative Hierarchical Clustering (AHC)
In AHC, initially each object (point location, grid cell etc) is considered to be in its own cluster. The clustering algorithm then works iteratively through these clusters in a 'bottom-up' manner. At each stage the two most similar clusters are merged into a bigger cluster. This is repeated successively until there is only one single, large cluster containing all the objects. As such, the objects can be represented in a tree diagram, known as a dendogram.

#### Similarity measure: Pearson's correlation dissimilarity
Deciding which pair of objects/clusters to merge at each stage requires a method for determining the object similarity. At each stage the distances between clusters are recalculated. Measures of (dis)similarity compare two vectors (lists of number) and return a single number representing their similarity. Euclidean distance is commonly used in clustering algorithms as the similarity measure; however, HiClimR uses Pearson's Correlation Distance Dissimilarity. Correlation based distance measures will consider two vectors to be similar, even if the values are far apart in Euclidean distance, as long as they are highly correlated. Pearson’s correlation coefficient is a measure related to the strength and direction of a linear relationship. The Pearson’s correlation can take a range of values from -1 to +1. Pearson's correlation is quite sensitive to outliers. Correlation based distance does not support scalars and thus HiClimR requires at least two variables for each location to regionalise on.
