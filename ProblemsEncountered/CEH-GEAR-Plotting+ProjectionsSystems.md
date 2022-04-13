###

Trying to identify which CEH-GEAR 1km grid cells are within the boundaries of a certain catchment. 

Include code with which I was getting the mirror image plot:

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

![image](https://user-images.githubusercontent.com/43998529/163194254-011f074f-df9e-47af-9e86-8add2cef2067.png)
