

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
