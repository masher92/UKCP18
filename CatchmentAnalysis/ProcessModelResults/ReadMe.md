
### Hec-Ras
1. Open Hec-Ras
2. Open RASmapper
3. Right click on Depth (max) and select 'Export Layer' and 'Export raster' and define the name to save it as
4. This saves a version of the file in both *.vrt and *.Resampled.Terrain.tif formats
5. ....ipynb contains code which 


### Python
* Convert_VRTtoTif.py --> This script converts .vrt versions of the files to .tifs (although I think this stage is no longer required as .tif versions can be downloaded directly from Hec-Ras) 
* FindDifference.py --> This script creates a raster for each of the 3 methods of creating multiple peaks, where the cell values are the difference between the values for that method and for the single peak method (for both depth and velocity). Also creates a reclassified version with a value of 0 for negative difference values and a value of 1 for positive differences. 
*  Reclassify.py -->
*  
