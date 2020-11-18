
## Wet hour vs all hour percentile indices for describing extreme precipitation
(Extreme) precipitation statistics can be calculated using either:
* All hours of data  
* Only wet hours of data (generally classed as hours with > 0.1mm of precipitation)

This choice can produce very different results and thus it is important to consider carefully the impacts of each option.

### Implications of using wet-hour percentiles
For percentiles calculated from only wet hours, changes in these percentiles can mean either a change in the frequency of wet hours OR changes in precipitation intensity. That is, wet hour percentiles are affected by changes in the occurrence of weak precipitation events (e.g. drizzle) (Schär et al, 2016). For instance, in a case where there is an increase in the number of hours with drizzle, but a decrease in event intensity in the most wet hours, the wet hour percentile value may still increase. For research focussed on the intensity of these more extreme events, it seems illogical to use an indices which is influenced by these less intense events. 

Using all hours ensures that the sample size being used to calculate percentiles remains constant. Therefore, changes in percentile values are due to changes in intensity alone (Alexander et al, 2019). It also means that the percentiles can be understood directly in terms of events which occur with absoloute frequencies, and so they are less complicated to interpret.  

This can be understood through consideration of Fig. 1, in which two cells, Cell 1 and Cell 2, are compared:  
* The top 50% of values:
    * Identical in Cell 1 and Cell 2
* Bottom 50% of values:
    * Cell 1 - they are all 0 (e.g. dry)
    * Cell 2 - they are all 0.1 (e.g. drizzly)   

<ins> All hour percentiles </ins>  
The most intense events in the two cells are of the same intensity. Therefore, for higher percentiles (e.g. 90th, 95th etc) calculated using all of the hours of data then the values would be the same.   

<ins> Wet hour percentiles </ins>  
For Cell 1 percentiles are calculated using all the hours of data.   
For Cell 2, the bottom 50% of hours are all removed, and the percentiles are calculated using only the highest 50% of values. Consequently, e.g. the 90th Percentile precipitation value for Cell 1 being lower than for Cell 2, despite the intensity of rainfall experienced in both cells being the same.

<p align="center">
<img src="Figs/WetvAllHourPercentiles2.PNG" width="800"  title="Original 1km grid" /> </p>
<p align="center">Figure 1. <p align="center">


### Link between wet-hour proportion and percentile precipitation values


Pattern in mean and lower percentiles (95th, 97th, 99th) matches the pattern in the wet hour proportion.
But this isn't because the wet hour proportion influences these statistics...

<p align="center">
<img src="CalculateStatsForClustering/Figs/wet_prop_EM_mean.png" width="242  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/jja_mean_EM_mean.png" width="250"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/jja_p97_EM_mean.png" width="250"  title="Original 1km grid" />
<p align="center"> Figure 2. Proportion of hours which are wet (left), mean JJA precipitation (middle), 97th Percentile JJA precipitation (right)  <p align="center">

<p align="center">
<img src="CalculateStatsForClustering/Figs/em01_MeanVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_95th PercentileVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_97th PercentileVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_99th PercentileVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_99.5th PercentileVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_99.75th PercentileVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_99.9th PercentileVsWetHourProp.png" width="200"  title="Original 1km grid" />
<img src="CalculateStatsForClustering/Figs/em01_MaxVsWetHourProp.png" width="200"  title="Original 1km grid" /> </p>
<p align="center"> Figure 3. Statistic Values plotted against wet hour proportion for EM01  <p align="center">


### References
* Alexander, L.V., Fowler, H.J., Bador, M., Behrangi, A., Donat, M.G., Dunn, R., Funk, C., Goldie, J., Lewis, E., Rogé, M. and Seneviratne, S.I., 2019. On the use of indices to study extreme precipitation on sub-daily and daily timescales. Environmental Research Letters, 14(12), p.125008.  
* Schär, C., Ban, N., Fischer, E.M., Rajczak, J., Schmidli, J., Frei, C., Giorgi, F., Karl, T.R., Kendon, E.J., Tank, A.M.K. and O’Gorman, P.A., 2016. Percentile indices for assessing changes in heavy precipitation events. Climatic Change, 137(1-2), pp.201-216.
