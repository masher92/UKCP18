# Regional rainfall statistics

The values of the following statistics of June-July-August (JJA) precipitation are calculated for each grid cell within the coastline of the UK:
* JJA Mean
* JJA Max
* JJA Percentiles (95, 97, 99, 99.5, 99.75, 99.9)

The statistics are calculated for each of the model ensemble members and for the observations regridded to 2.2km (it was also attempted to calculate these statistics using the observations on their native 1km grid, but this produced an error due to memory requirements).

The values of these statistics are plotted over:
* The UK (trimmed to the coastlines)
* The Northern region (North East, North West, Yorkshire and the Humber)
* A square region centred on Leeds.  

For the model, a plot is generated displaying the mean values across the 12 ensemble members, and another is created with 12 subplots containing the results from each ensemble member seperately.

Plots are also generated showing the difference between the mean values across the 12 ensemble members and the value from the regridded observations.
