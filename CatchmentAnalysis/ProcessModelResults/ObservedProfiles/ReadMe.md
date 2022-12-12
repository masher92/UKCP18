
# Impact of rainfall temporal distribution on flooding in Lin Dyke catchment


## Project Summary

Research suggests that the temporal distribution of rainfall within a storm event can influence the nature and severity of flooding resulting from that storm event....

Testing this using synthetic rainfall events derived from FEH/ReFH2. Standard profiles usually have one peak, testing three methods for splitting the total rainfall amount normally concentrated in this one peak into multiple peaks 

Analysing impact on the extent, depth and velocity of flooding, and the spatial distribution of these variables over the catchment



## Land Cover
Uses the CEH 2019 Land cover classification map (this isn't the most recent version, but is what Megan used).  
The land cover classification didn't line up with the other data. To make it do so I used QGIS:  
* Add the land cover data set and one dataset of model results
* Select Export -> Save As 
* Under 'Extent (current layer)' select Calculate from layer and then select the model results data
* Specify an output layer name and select Okay

I then clipped this in Python in the same way as the model output layers, and then they were the same size.  

### Classification numbers
Can't find anything online specifying what the numbers relate to. So, used Megan's report which incldues a figure with the land cover classes plotted with a legened and manually used this to match up the numbers with the different classifications. 
