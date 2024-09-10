# Regional rainfall statistics
## Code and workflow summary
<ins> Calculating statistics </ins>  
The values of various statistics of June-July-August (JJA) precipitation for each grid cell within the region covered by the bounding box of the coastline of the UK, are calculated within two separate scripts:  
* Calculating_UK_stats.py -- calculates the statistics over all hours of JJA data
* Calculating_UK_stats_wethours.py -- calculates the statistics over only wet JJA hours (>0.1mm/hr precipitation)

In both cases the following statistics are calculated:  
* JJA Mean
* JJA Max
* JJA Percentiles (95, 97, 99, 99.5, 99.75, 99.9)
The process for this involves using masks generated in the CreatingMasks.py script.

The code can also be adapted to allow plotting of either wet/all hours statistics and, for the plots with subplots, to use either a shared colobar and scale across the 12 ensemble members of to give each subplot its own colorbar and scale.

## Results
For both the Leeds region and the wider Northern region, plots are displayed for the max, mean and various percentiles (95th, 97th, 99th, 99.5th, 99.75th and 99.9th) June-July-August (JJA) precipitation for the period of 1980-2001.  
In section 1, each plot displays the mean value across twelve ensemble members for the statistic indicated in the figure caption.    
In section 2, each plot displays the value for each of the twelve ensemble members.   
In each case the statistics plotted in the left hand plot are calculated across all hours of the data, whilst those plotted in the right hand plot are calculated using only the wet hours (>0.1mm/hr precipitation).

### 1. Ensemble means
#### Leeds region
<p align="left">
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/wet_prop_EM_mean.png" width="200"  title="Regridded 2.2km grid" />  
<p align="left"> JJA proportion of hours that are wet (>0.1mm/hr precipitation) <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_mean_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_mean_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />   </p>
<p align="left">Figure 1. JJA mean for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_p95_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_p95_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
          </p>
<p align="left">Figure 2. JJA 95th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_p97_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_p97_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
          </p>
<p align="left"> Figure 3. JJA 97th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
              <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_p99_EM_mean.png" width="200"  title="Original 1km grid" />
              <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_p99_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
            </p>
<p align="left"> Figure 4. JJA 99th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_p99.5_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_p99.5_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
          </p>
<p align="left"> Figure 5. JJA 99.5th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_p99.75_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_p99.75_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
          </p>
<p align="left"> Figure 6. JJA 99.75th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_p99.9_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_p99.9_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
          </p>
<p align="left"> Figure 7. JJA 99.9th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
      <img src="Figs/leeds-at-centre/AllHours_EM_Difference/jja_max_EM_mean.png" width="200"  title="Original 1km grid" />
      <img src="Figs/leeds-at-centre/WetHours_EM_Difference/jja_max_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
    </p>
<p align="left"> Figure 8. JJA max for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">  

### Northern region     
<p align="left">
            <img src="Figs/Northern/WetHours_EM_Difference/wet_prop_EM_mean.png" width="200"  title="Regridded 2.2km grid" />  
<p align="left"> JJA proportion of hours that are wet (>0.1mm/hr precipitation) <p align="center">

<p align="left">
          <img src="Figs/Northern/AllHours_EM_Difference/jja_mean_EM_mean.png" width="200"  title="Original 1km grid" />
          <img src="Figs/Northern/WetHours_EM_Difference/jja_mean_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
        </p>
<p align="left"> Figure 9. JJA mean for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
          <img src="Figs/Northern/AllHours_EM_Difference/jja_p95_EM_mean.png" width="200"  title="Original 1km grid" />
          <img src="Figs/Northern/WetHours_EM_Difference/jja_p95_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
        </p>
<p align="left"> Figure 10. JJA 95th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
          <img src="Figs/Northern/AllHours_EM_Difference/jja_p97_EM_mean.png" width="200"  title="Original 1km grid" />
          <img src="Figs/Northern/WetHours_EM_Difference/jja_p97_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
        </p>
<p align="left"> Figure 11. JJA 97th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
            <img src="Figs/Northern/AllHours_EM_Difference/jja_p99_EM_mean.png" width="200"  title="Original 1km grid" />
            <img src="Figs/Northern/WetHours_EM_Difference/jja_p99_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
          </p>
<p align="left"> Figure 12. JJA 99th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
          <img src="Figs/Northern/AllHours_EM_Difference/jja_p99.5_EM_mean.png" width="200"  title="Original 1km grid" />
          <img src="Figs/Northern/WetHours_EM_Difference/jja_p99.5_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
        </p>
<p align="left"> Figure 13. JJA 99.5th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
          <img src="Figs/Northern/AllHours_EM_Difference/jja_p99.75_EM_mean.png" width="200"  title="Original 1km grid" />
          <img src="Figs/Northern/WetHours_EM_Difference/jja_p99.75_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
        </p>
<p align="left"> Figure 14. JJA 99.75th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
          <img src="Figs/Northern/AllHours_EM_Difference/jja_p99.9_EM_mean.png" width="200"  title="Original 1km grid" />
          <img src="Figs/Northern/WetHours_EM_Difference/jja_p99.9_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
        </p>
<p align="left"> Figure 15. JJA 99.9th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
    <img src="Figs/Northern/AllHours_EM_Difference/jja_max_EM_mean.png" width="200"  title="Original 1km grid" />
    <img src="Figs/Northern/WetHours_EM_Difference/jja_max_wh_EM_mean.png" width="200"  title="Regridded 2.2km grid" />
  </p>
<p align="left"> Figure 16. JJA max for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">  


## 2. All ensemble plots
### Leeds region
<p align="left">
  <img src="Figs/leeds-at-centre/Allhours/jja_mean.png" width="200"  title="Regridded 2.2km grid" />
  <img src="Figs/leeds-at-centre/Wethours/jja_mean_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left">Figure 17. JJA mean for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_p95.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_p95_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left">Figure 18. JJA 95th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_p97.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_p97_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 19. JJA 97th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_p99.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_p99_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 20. JJA 99th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_p99.5.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_p99.5_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 21. JJA 99.5th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_p99.75.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_p99.75_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 22. JJA 99.75th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_p99.9.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_p99.9_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 23. JJA 99.9th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/leeds-at-centre/Allhours/jja_max.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/leeds-at-centre/Wethours/jja_max_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 24. JJA max for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">  

### Northern region     
<p align="left">
  <img src="Figs/Northern/Allhours/jja_mean.png" width="200"  title="Regridded 2.2km grid" />
  <img src="Figs/Northern/Wethours/jja_mean_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left">Figure 25. JJA mean for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_p95.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_p95_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left">Figure 26. JJA 95th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_p97.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_p97_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 27. JJA 97th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_p99.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_p99_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 28. JJA 99th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_p99.5.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_p99.5_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 29. JJA 99.5th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_p99.75.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_p99.75_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 30. JJA 99.75th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_p99.9.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_p99.9_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 31. JJA 99.9th Percentile for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">

<p align="left">
<img src="Figs/Northern/Allhours/jja_max.png" width="200"  title="Regridded 2.2km grid" />
<img src="Figs/Northern/Wethours/jja_max_wh.png" width="200"  title="Regridded 2.2km grid" /> </p>
<p align="left"> Figure 32. JJA max for all hours (left) and wet hours with >0.1mm/hr precipitation (right) <p align="center">  
