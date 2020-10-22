# Rainfall Regionalisation
Rainfall regionaliation is the process of dividing a study region into smaller regions which are homogenous in respect to a particular precipitation characteristic. It is typically achieved using some form of cluster analysis.

## HiClimR

EVT needs sufficient data in order to produce reliable estimates of long return period events. Often both observational records and model runs are not long enough to allow for this. One method of dealing with this data shortage is to pool data spatially and to use data from multiple stations or grid boxes in the same analysis. This regionalisation process trades space for time and allows better estimation of the extreme value distribution. Regionalisation requires a means of determining areas which have similar enough rainfall characteristics to be grouped together. These regions are generally geographically coherent areas with similar physical and/or climatic features according to the focus of the analysis. For instance, where extreme values are of interest, extreme value statistics should be in regionalisation. The size of the regions must be large enough to confer a benefit over analysing all locations separately; however, must not be too large so as points within the region becomes too different from one another (Johnson and Green, 2018).

28/09/20 - spotted significant bug in code. This meant that latitude and longitude were being included as variables in the regionalisation process and consequently significantly altering the results.
Check how it changes Northern results.
Brings back question of whether there is a greater meaning in cluster 1 and cluster 2.

https://github.com/hsbadr/HiClimR/issues/4
Need at least two variables to regionalise on. HiClimR uses correlation distance as a dissimilarity measure, which doesn't support scalars.  
This means its not actually possible to regionalise on singular statistic values calculated over all 20 years.

Different regionalisation method:
Most of them just put nearly the whole area into one cluster, with one cell or so put into a different cluster. McQuitty method gave more reasonable looking clusters, but substantially different to the Ward's method clusters,

From documentation (https://cran.microsoft.com/snapshot/2014-12-22/web/packages/HiClimR/HiClimR.pdf)
The HiClimR function is based on hclust). It performs a hierarchical cluster analysis using Pearson
correlation distance dissimilarity for the N objects being clustered. Initially, each object is assigned
to its own cluster and then the algorithm proceeds iteratively, at each stage joining the two most
similar clusters, continuing until there is just a single cluster. At each stage distances between
clusters are recomputed by a dissimilarity update formula according to the particular clustering
method being used.

https://cmci.colorado.edu/classes/INFO-1301/files/borgatti.htm
Purpose of measures of similarity is to compare two lists of numbers (i.e. vectors) and compute a single number which evaluates their similarity. Most measures were developed in context of comparing pairs of variables across cases (e.g. respondents in a survey).
Correlation between two vectors --

https://www.datanovia.com/en/lessons/clustering-distance-measures/
Most clustering algorithms uses Euclidean distance. Here it uses Pearson's correlation distance dissimilarity. Correlation-based distance considers two objects to be similar if their features are highly correlated, even though the observed values may be far apart in terms of Euclidean distance (Euclidean distance is.... ) Pearson's correlation is quite sensitive to outliers.

https://towardsdatascience.com/calculate-similarity-the-most-relevant-metrics-in-a-nutshell-9a43564f533e
Similarity based metrics determine most similar objects with the highest values as it imples they live in closer neighbourhoods.
Pearson's Correlation: Correlation is a technique for investigating the relationship between two quantitative, continuous variables, for example, age and blood pressure. Pearson’s correlation coefficient is a measure related to the strength and direction of a linear relationship. The Pearson’s correlation can take a range of values from -1 to +1

https://www.datanovia.com/en/lessons/agglomerative-hierarchical-clustering/
AHC clustering starts by treating each object as a singleton (single element) cluster. Next, pairs of clusters are successively merged until all clusters have been merged into one big cluster containing all objects. The result is a tree-based representation of the objects, named dendrogram.
It works in a 'bottom-up' manner. That is, each object is initially considered as a single-element cluster (leaf). At each step of the algorithm, the two clusters that are the most similar are combined into a new bigger cluster (nodes). This procedure is iterated until all points are member of just one single big cluster (root) (see figure below).
1. Preparing the data:
2. Computing (dis)similarity information between every pair of objects in the data set.
3. Using linkage function to group objects into hierarchical cluster tree, based on the distance information generated at step 1. Objects/clusters that are in close proximity are linked together using the linkage function.
4. Determining where to cut the hierarchical tree into clusters. This creates a partition of the data.

The data should be a numeric matrix with:
1. rows representing observations (individuals);
2. and columns representing variables.

In order to decide which objects/clusters should be combined or divided, we need methods for measuring the similarity between objects.


Taking vectors of data values for each location, think it compares each pair of values between two points.


What is Pearson's correlation distance dissimilarity?

