### Process land cover data

The landcover data orginally has nine classes (suburban, arable, decidious woodland, freshwater, improved grassland, urban, neutral grassland, calcareous grassland and heather grassland).   
This is reclassified into two classes (urban (including suburban and urban) and not-urban (the rest).

In this script, the model results (for each of the sets of profiles) are also trimmed to the extent of the Garforth and Kippax boundaries.  

An official shapefile for Garforth itself couldn't be found, so I created this boundary in QGIS:  
* In QGIS select Layer -> Create layer -> new shapefile layer.
* Press the three dots beside filename to select location to save to.
* Select UTF-8 File encoding and type as Polygon.
* Right click layer, and select 'toggle editing' and then select 'Add Poylgon feature' from toolbar at the top

Versions of the results files trimmed to the extents are saved to file.
