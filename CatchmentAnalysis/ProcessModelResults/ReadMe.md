# Post process model outputs in Python
The directory contains multiple subdirectories, each containing analysis of the outputs of running model with a set of profiles. The sets of profiles include:
* Observed profiles (based on work by Roberto Villalobos-Herrera)
* Idealised profiles:
* Idealised profiles (scaled):
* Idealised profiles (drier antecedent conditions):
* Synthetic profiles, based on the volume of rainfall in an FEH event for this catchment, but with this volume split over multiple peaks.
* Single peak (scaled) 

### Process outputs in Hec-Ras
The initial required stage is to export the outputs from Hec-Ras as .tif files.  
* This can be done from within Hec-Ras for each scenario individually:
   * Open Ras Mapper
   * Right click on Depth (max) and select 'Export Layer' and 'Export raster' and define the name to save it as. This saves a version of the file in both *.vrt and *.Resampled.Terrain.tif formats
* Or, can be automated for all results layers. 
   * Tools -> Create Multiple Maps -> Dragging down to select all options on left -> Then select relevant option(s) in other two columns
   * OR -> Project -> Manage Results Maps -> And select the results map you want for each layer -> Select 'Compute/Update stored maps' to produce them

### Time series values at profile lines
* Create profile line, moving from left bank to right bank (looking downstream)
* Ensure all the layers are selected (both depth and velocity)
* Right click on profile line and select 'Plot Timeseries' -> Depth/Velocity
* Click on table and right click and select to remove the rounding
* Copy and paste the data to export it


### Processing-1.ipynb
* Reads in .tif files for velocity and depth
* Creates a hazard raster based on a combination of depth and velocity from Megan's report which is based on *XXX*
* Classifies both depth, velocity and hazard according to categories from Megan's report which are based on *XXX*
* Creates a plot of these classified depth/velocity/hazard rasters
* Finds the difference between the (unclassified) depth, velocity and hazard rasters for each rainfall scenario and the FEH single peak scenario
* Classifies the difference rasters according to categories from Megan's report which are based on *XXX*
* Creates a plot of these classified difference depth/velocity/hazard rasters
* Creates a version of the classified difference raster which just shows whether each scenario leads to deeper/faster flooding in each cell than in the FEH single peak scenario

### Processing-2.ipynb
* Creates a .csv file stored in Data/allclusters_summary.csv which contains for each scenario:
    * MaxRainfallIntensity (the maximum intensity values over the course of the event)
    * MaxRainfallIntensityMinute (the minute in which this maximum value occurs)
    * TotalFloodedArea	
    * %Diff_FloodedArea_fromSP	
    * %Diff_FloodedArea_fromSP_formatted	
    * Abs%Diff_FloodedArea_fromSP	
    * UrbanFloodedArea	
    * %Diff_UrbanFloodedArea_fromSP	
    * %Diff_UrbanFloodedArea_fromSP_formatted	
    * Abs%Diff_UrbanFloodedArea_fromSP	
    * WorstCaseDepth_ncells	
    * WorstCaseVelocity_ncells
    * The proportion and number of cells in each depth/velocity/hazard category, and which have moved hazard category by 1,2,3 categories lower or higher

### Analysis.ipynb
Plots:
* Relationship between the number of flooded cells in urban and non-urban areas
* Relationship between the total flooded area & the rainfall scenario used
    * Plot the maximum peak intensity value against the flooded area
* Relationship between flood severity & the rainfall scenario used
    * Plot the proportion of the total flooded cells in various depth/velocity/hazard categories
    * Plot the maximum peak intensity value against the flooded area
* Method leading to deepest/fastest flooding in each cell 

# Post process model outputs in Hec-Ras Mapper
  
Originally, the processing of the results was done in Hec-Ras mapper using the method below. 
  
The results of running the Hec-Ras model can be processed using Hec-Ras mapper. This involves 3 main stages:
1. Filtering out cells with flood depths of less than 0.1m (setting the value of these cells to NoData), and rounding the remaining depth values to 2 decimal places;
2. Categorising the cells according to which of the following flood depth categories they are in 0.1-0.3m, 0.3-0.6m, 0.6-1.2m, 1.2m+
3. Finding the method for each cell which resulted in the greatest flood depth 

In each case, this involves the following stages:  
* Tools -> Create calculated layer -> + Layer -> Map Type: 'Depth', Animation Behaviour: 'Fixed Profile', Profile: 'Max' -> Change variable name to depth    
* Open scripts (to select an existing script, alternatively  write one from scratch)  
    * Layer created under 'Map layers' heading  
    * Save layer as a raster:  
          * Right click -> Export layer -> Export as raster     
* Move the layer above OpenStreetMaps in the ordering (otherwise won't see it)  
* Image display properties:  
    * Right click layer and select image display properties  
    * Double click on colour bar and change colour ramp to ‘Depth’  
      * For (1): Change number of values to 7, and change values to 0, 0.15, 0.3, 0.6, 0.9, 1.20, 20  
      * For (2): Change number of values to 3, and change values to 0 (0.1-0.3m), 1 (0.3-0.6m), 2 (0.6-1.2m), 3 (1.2m+)  
      * For (3): Change number of values to 3, and change values to 0 (divide-time), 1 (maximum spread), 2 (single peak), 3 (sub-peak timing)  

<a name="qgis"></a>
### Process outputs in QGIS

QGIS is used to count the number of cells of each depth within the Lin Dyke area. This involves the following stages:
* Layer -> Add Layer -> Add Raster Layer
* Processing -> Toolbox -> Raster layer unique values report -> Define a location to save the 'unique values table' to

This outputs csv files containing depth values, a count of the number of cells with that value, and the area of the cells covered by that depth




 
                                                                                                                         
