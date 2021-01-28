# Regional rainfall statistics

The values of the following statistics of June-July-August (JJA) precipitation are calculated for each grid cell within the coastline of the UK:
* JJA Mean
* JJA Max
* JJA Percentiles (95, 97, 99, 99.5, 99.75, 99.9)

For each of the model ensemble members and for the observations regridded to 2.2km (it was also attempted to calculate these statistics using the observations on their native 1km grid, but this produced an error due to memory requirements).

The values of these statistics are plotted over:
* The UK (trimmed to the coastlines)
* The Northern region (North East, North West, Yorkshire and the Humber)
* A square region centred on Leeds.  

For the model, a plot is generated displaying the mean values across the 12 ensemble members, and another is created with 12 subplots containing the results from each ensemble member seperately.


Plots of the JJA statistic values at each grid cell are plotted within two scripts:
* The "RegionalStats_plotting.py" -- for each statistic each plot includes 12 subplots for the 12 ensemble members showing the value of the statistic at each grid cell
* The "RegionalEnsembleSummary_plotting" -- for each statistic two plots are created: 1. A plot of the mean value across all 12 ensemble members at each grid cell and 2. A plot of the ensemble spread (the standard deviation) at each grid cell.  

In both cases plots can be generated for any of three defined regions:
