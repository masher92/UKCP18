# Percentage difference between Model and Observations

Compare to what's in: https://www.metoffice.gov.uk/binaries/content/assets/metofficegovuk/pdf/research/ukcp/ukcp18_cpm_launch_kendon_sept19-20190926_with-notes.pdf
This looks at wet day frequency - could I calculate this?

The mean value across the twelve UKCP18 2.2km model ensemble members are calculated for various statistics of present day rainfall. The difference between these mean values and those found in the CEH-GEAR observations data, regridded to 2.2km, are then calculated to establish the presence of model bias.

RCMs -- have a tendency for light rainfall events to occur too often ('drizzle effect') and for extreme rainfall events to be under represented.
CPMs -- have a tendency to simulate heavy rainfall events as too intense

<p align="left">
            <img src="Figs/UK/percentage_diff_jja_mean.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_p95.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_p97.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_p99.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_p99.5.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_p99.75.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_p99.9.png" width="200" />
            <img src="Figs/UK/percentage_diff_jja_max.png" width="200""/>   </p>
<p align="left"> Figure 1. The percentage difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics (model value - obs value/obs value) <p align="center">

<p align="left">
            <img src="Figs/Northern/percentage_diff_jja_mean.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_p95.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_p97.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_p99.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_p99.5.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_p99.75.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_p99.9.png" width="200" />
            <img src="Figs/Northern/percentage_diff_jja_max.png" width="200""/>   </p>
<p align="left">Figure 2. The difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/percentage_diff_jja_mean.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_p95.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_p97.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_p99.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_p99.5.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_p99.75.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_p99.9.png" width="200" />
            <img src="Figs/leeds-at-centre/percentage_diff_jja_max.png" width="200""/>   </p>
<p align="left">Figure 3. The difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics <p align="center">

For the 99.5, 99.75th and 99.9th percentiles and the maximum precipitation intensities, the modelled values are higher than the observations across the whole country (check if some of the values are 0?). The maximum percentage difference between these values gets higher at higher percentiles, up to a maximum difference of 800% in the maximum values. The model gets the values of extremes too high. 

For the lower percentiles (95th, 97th, 99th) and the mean, there is a geographical divide in the difference between the model and the observations. The model overpredicts (compared to the observations) over the Pennines and Scottish hills; however, this same effect is not seen over the Welsh hills or in higher elevation areas in the South. This difference is surprising (would expect the model to be higher (too wet) than the observations everywhere). Need to also consider that the particularly high difference between the model and observations over the mountains might be due to the observations not capturing the extremes, rather than the model underpredicting. E.g. in the mountains there may not be many rain gauges and thus values in these areas undergo more smoothing in the interpolation process. A lack of rain gauges in the mountains might also have been corrrected for, and perhaps it is this correction process that is relevant to the patterns seen. The map doesn't present as a map of rain gauges, so this is encouraging that the influence of the interpolation of the gauge data is not too significant. (check CEH-GEAR rain gauge map and plot distance to nearest gauge over whole of UK). 

There is a considerable difference in the spatial patterns between the maximum and the higher percentiles, and the mean and the lower percentiles. In some cases, for instance the area over Leeds (see Figure X) there is an opposite trend in the lower percentiles (P95 and P97) compared to the higher percentiles, specifically with the model underpredicting in the lower percentiles, and the model overpredicting in the higher percentiles. To understand this need to think about the rainfall regime that the various percentiles and the mean are representative of. For instance, when it is raining the model may predict more heavy hourly rainfall intensities than those found in the observations; however, the model may also contain a greater number of dry days. As such, the model may be associated with higher hourly rainfall accumulations at higher percentiles, but lower percentiles might correspond to lighter rain or drier days than the observations. Also need to understand what values dominate the mean (which corresponds to the total rainfall amount over a period). The total rainfall amount over this period might be mostly contributed to by events with substantial amounts of rainfall, or alternatively may result from gradual accumulation from continual, drizzly rainfall. The mean is not the 50th perecentile and in reality might be more closely aligned to a much higher percentile. 

<p align="left">
            <img src="Figs/Topography/UK.PNG" width="200" />
            <img src="Figs/Topography/Northern.png" width="200" />
            <img src="Figs/Topography/leeds-at-centre.png" width="200" /> </p>
<p align="left"> Figure 4. The percentage difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics (model value - obs value/obs value) <p align="center">

<p align="left">
            <img src="/RainGaugeAnalysis/Figs/CEH-GEAR_locations.PNG" width="200" />
<p align="left"> Figure 5. The percentage difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics (model value - obs value/obs value) <p align="center">

# Difference between Model and Observations

The mean value across the twelve UKCP18 2.2km model ensemble members are calculated for various statistics of present day rainfall. The difference between these mean values and those found in the CEH-GEAR observations data, regridded to 2.2km, are then calculated to establish the presence of model bias.

<p align="left">
            <img src="Figs/UK/jja_mean.png" width="200" />
            <img src="Figs/UK/jja_p95.png" width="200" />
            <img src="Figs/UK/jja_p97.png" width="200" />
            <img src="Figs/UK/jja_p99.png" width="200" />
            <img src="Figs/UK/jja_p99.5.png" width="200" />
            <img src="Figs/UK/jja_p99.75.png" width="200" />
            <img src="Figs/UK/jja_p99.9.png" width="200" />
            <img src="Figs/UK/jja_max.png" width="200""/>   </p>
<p align="left"> Figure 1. The difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics  <p align="center">

<p align="left">
            <img src="Figs/Northern/jja_mean.png" width="200" />
            <img src="Figs/Northern/jja_p95.png" width="200" />
            <img src="Figs/Northern/jja_p97.png" width="200" />
            <img src="Figs/Northern/jja_p99.png" width="200" />
            <img src="Figs/Northern/jja_p99.5.png" width="200" />
            <img src="Figs/Northern/jja_p99.75.png" width="200" />
            <img src="Figs/Northern/jja_p99.9.png" width="200" />
            <img src="Figs/Northern/jja_max.png" width="200""/>   </p>
<p align="left">Figure 2. The difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics <p align="center">

<p align="left">
            <img src="Figs/leeds-at-centre/jja_mean.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_p95.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_p97.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_p99.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_p99.5.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_p99.75.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_p99.9.png" width="200" />
            <img src="Figs/leeds-at-centre/jja_max.png" width="200""/>   </p>
<p align="left">Figure 3. The difference between UKCP18 2.2km local and CEH-GEAR observations regridded to 2.2km for various precipitation statistics <p align="center">
