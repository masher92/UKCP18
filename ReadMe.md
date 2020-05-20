## UKCP18  

<ins> Unresolved issues </ins>  
Each month has 30 days: this creates a problem when converting the date to a timestamp format as it cannot recognise 30 days in February. 

<ins> To do </ins>  
Update scripts so there is a file with functions and then can just run one script which does all the processing and saving various things (checking first if they already exist) rather than having to go in and out of various files.   

<ins> Running file with sys.argv within Spyder </ins>  
Open Run -> Configuration per file (Ctrl + f6) and enter the variables into command line arguments and press run.  

## Note on projections
grid_latitude and grid_longitude are in rotated pole
These are stored as 1D structure 
rot_lat = hour_uk_cube.coord('grid_latitude').points
rot_lon = hour_uk_cube.coord('grid_longitude').points
latitude and longitude are in regular coordinates
These are stored as a 2D array
lats = hour_uk_cube.coord('latitude').points
lons = hour_uk_cube.coord('longitude').points

Can convert rotated coordinates to the regular coordinates as follows:
x, y = np.meshgrid(rot_lon, rot_lat)
cs = hour_uk_cube.coord_system()
lons, lats = iris.analysis.cartography.unrotate_pole(x, y, cs.grid_north_pole_longitude, cs.grid_north_pole_latitude)

