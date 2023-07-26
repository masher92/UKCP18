### Process land cover data

Before running this script for Wyke Beck I had to trim the LandCover.tif file in QGIS to the extent of one of the Hec-Ras results files, using the function: ClipRasterByExtent. I don't exactly understand this as the file being clipped is smaller than the file it's being clipped by, but it seems to work (not sure I did something similar with Lin Dyke, as I can't remember)

The landcover data orginally has nine classes (suburban, arable, decidious woodland, freshwater, improved grassland, urban, neutral grassland, calcareous grassland and heather grassland).   
This is reclassified into two classes (urban (including suburban and urban) and not-urban (the rest).

In this script, the model results (for each of the sets of profiles) are also trimmed to the extent of the Garforth and Kippax boundaries.  

An official shapefile for Garforth itself couldn't be found, so I created this boundary in QGIS:  
* In QGIS select Layer -> Create layer -> new shapefile layer.
* Press the three dots beside filename to select location to save to.
* Select UTF-8 File encoding and type as Polygon.
* Right click layer, and select 'toggle editing' and then select 'Add Poylgon feature' from toolbar at the top

Versions of the results files trimmed to the extents are saved to file.

<ins> How is this information used? </ins>

In ProcessingModelResults, the Processing2.ipynb and Analysis.ipynb have a region variable, which depending on whether set to: '', 'Garforth' or 'Kippax' will perform the analysis for the whole of the region, just the cells within Garforth or Kippax

The results are further broken down to just include the urban cells within all of these areas.

Processing2.ipynb makes use of the functions:

Create_binned_counts_and_props:
  * This function reads in the results for each rainfall scenario method and counts the number of cells in each velocity/depth category bin

Create_binned_counts_and_props_urban:
  * This function reads in the results for each rainfall scenario method, and filters out the cells which are the urban landcover category, and then counts the number of cells in each velocity/depth category bin

