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

To solve this, I had to change the order in which the lat and long coordinates are given.

```
# Loop through
for i in range(0,lat_length): 
    for j in range(0,lon_length):
        transformer = Transformer.from_crs("epsg:27700", "epsg:3857")
        x, y = transformer.transform(lons[j], lats[i])
        point = Point(x,y) 
        # Check if point is within catchment boundary shapefile
        if lindyke_shp.contains(point)[0]:
            plt.plot(x, y,  'o', color='black', markersize = 5)  
            test_data[i,j]=1
            print(i,j)
```

![image](https://user-images.githubusercontent.com/43998529/163197986-73bdf714-750e-4ea1-93b0-bd3940abc867.png)

I am still not 100% sure about the reasoning behind this. However, I think it is something to do with the fact that in an array the X position is given before the Y position. Whereas on a map the Y coordinate is given before the X coordinate. And on an array you count from the top left, whereas on a map you start on the bottom left. 

![image](https://user-images.githubusercontent.com/43998529/163199246-45162056-7e9d-4657-8606-7bcad6df517a.png)
