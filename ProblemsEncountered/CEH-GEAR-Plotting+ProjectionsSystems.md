### Goal:  
To find all grid cells within a certain catchment, to combine the precipitation data from all the cells and to find an average daily/monthly/weekly rainfall amount

### Script:   
```UKCP18/CatchmentAnalysis/ObservedCatchmentRainfallAnalysis/FindCatchmentAvgRainfall.py```

### Problems encountered:  
I wrote some code to loop through each lat, long pair and to check whether the coordinate is found within the catchment. If it is then a point is plotted on the figure in that cell, and the corresponding value in the test_data array (which is created as an array filled with 0s) is set to 1.

```
# Loop through
for i in range(0,lat_length): 
    for j in range(0,lon_length):
        transformer = Transformer.from_crs("epsg:27700", "epsg:3857")
        x, y = transformer.transform(lats[i], lons[j])
        point = Point(x,y) 
        # Check if point is within catchment boundary shapefile
        if lindyke_shp.contains(point)[0]:
            plt.plot(x, y,  'o', color='black', markersize = 5)  
            test_data[i,j]=1
```

However, in the resulting plot, the grid cells highlighted and the cells in which a point was plotted did not match up
![image](https://user-images.githubusercontent.com/43998529/163194254-011f074f-df9e-47af-9e86-8add2cef2067.png)
