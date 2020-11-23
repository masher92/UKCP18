# Regional rainfall statistics - Observations
## Code and workflow summary
<ins> Calculating statistics </ins>  
The values of various statistics of June-July-August (JJA) precipitation for each grid cell within the region covered by the bounding box of the coastline of the UK, are calculated within the script:
* Calculating_UK_Stats.py

In both cases the following statistics are calculated (across ALL hours of data):  
* JJA Mean
* JJA Max
* JJA Percentiles (95, 97, 99, 99.5, 99.75, 99.9)

<ins> Plotting statistics </ins>  
Plots of the JJA statistic values at each grid cell are plotted within two scripts:
* The "RegionalStats_plotting.py" -- for each statistic a spatial plot showing the value of the statistic at each grid cell is created

In both cases plots can be generated for any of three defined regions:
* The UK (trimmed to the coastlines)
* The Northern region (North East, North West, Yorkshire and the Humber)
* A square region centred on Leeds.  

The process for this involves using masks generated in the CreatingMasks.py script.

## Results
For both the Leeds region and the wider Northern region, plots are displayed for the max, mean and various percentiles (95th, 97th, 99th, 99.5th, 99.75th and 99.9th) June-July-August (JJA) precipitation for the period of 1980-2001.  

#### Northern region
<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_mean.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_mean.png" width="200"    </p>
<p align="left"> Fig 1. JJA mean hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_p95.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_p95.png" width="200"    </p>
<p align="left"> Fig 2. JJA 95th Percentile hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_p97.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_p97.png" width="200"    </p>
<p align="left"> Fig 3. JJA 97th Percentile hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_p99.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_p99.png" width="200"    </p>
<p align="left"> Fig 4. JJA 99th Percentile hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_p99.5.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_p99.5.png" width="200"    </p>
<p align="left"> Fig 5. JJA 99.5th Percentile hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_p99.75.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_p99.75.png" width="200"    </p>
<p align="left"> Fig 6. JJA 99.75th Percentile hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_p99.9.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_p99.9.png" width="200"    </p>
<p align="left"> Fig 7. JJA 99.9th Percentile hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right) <p align="center">

<p align="left">
            <img src="Figs/NearestNeighbour/Northern/jja_max.png" width="200"  title="Regridded 2.2km grid" />  
            <img src="Figs/LinearRegridding/Northern/jja_max.png" width="200"    </p>
<p align="left"> Fig 8. JJA max hourly precipitation from CEH-GEAR 1km observations, regridded to a 2.2km grid using nearest neighbour regridding (left) and linear regridding (right)) <p align="center">
