## UKCP18  

<ins> Unresolved issues </ins>  
Each month has 30 days: this creates a problem when converting the date to a timestamp format as it cannot recognise 30 days in February. 


### Projection
The UKCP18 data is provided in a Rotated Pole coordinate system.  
It is possible to get this Rotated Pole in the format of a cartopy projection: grid_crs = grid.coord('grid_latitude').coord_system.as_cartopy_crs()  
This can then be used to convert the projection of other shapefiles, for instance the outline of Leeds for plotting. To do this, the Cartopy projection Crs must be converted: proj_crs = CRS.from_dict(grid_crs.proj4_params) using from pyproj.crs import CRS  
However, it still does not work plotting the geodataframe of the outline of Leeds with the UKCP18 data cube in its native projection system.  
The 'grid_longitude' coordinate contains values that are >360, whereas these are supposed to (?) wrap around 360 to 0.  
However, if the longitudes are corrected in this way, e.g. with 361 becoming 1, it is no longer possible to plot them spatially as the plotting function does not except longitude values that are not 'monotonically increasing'.
