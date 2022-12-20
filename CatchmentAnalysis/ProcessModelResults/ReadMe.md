# Post process model outputs in Python
The directory contains two subdirectories. One contains analysis of outputs of running model with observed profiles (based on work by Robrto Villalobos-Herrera) and the other containing analysis of outputs of running model with synthetic profiles, based on the volume of rainfall in an FEH event for this catchment, but with this volume split over multiple peaks.

It also contains a script "ProcessLandCoverData.ipynb" which is to classify each cell as either Urban or Non-Urban, for use in the rest of the analysis.

### Process outputs in Hec-Ras
* Need to save the outputs as .tif
* This can be done from within Hec-Ras for each scenario individually:
   * Open Ras Mapper
   * Right click on Depth (max) and select 'Export Layer' and 'Export raster' and define the name to save it as. This saves a version of the file in both *.vrt and *.Resampled.Terrain.tif formats
* Or, can be automated for all results layers. 
   * Tools -> Create Multiple Maps -> Dragging down to select all options on left -> Then select relevant option(s) in other two columns
   * OR -> Project -> Manage Results Maps -> And select the results map you want for each layer -> Select 'Compute/Update stored maps' to produce them

### Process outputs in QGIS

### Plot results


# Post process model outputs in Hec-Ras Mapper
   
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




 
                                                                                                                         
