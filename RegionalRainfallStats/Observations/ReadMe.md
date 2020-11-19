Plotting regridded observations -->
* In order to trim to the extent of UK/Northern region etc need some coordinates in WGS84
* Tried to do this by unrotating the coordinates
* This seems to work but when trim cube and plot then they don't cover the correct area
* Tested with the model cube and found that the lat and long coordinates derived in this way by unrotating the coordinate were (almost) the same as the lat/long coordinates on the cube. 
