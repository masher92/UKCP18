# Derive antecedent conditions
Antecedent conditions (daily rainfall values) must be supplied alongside observed rainfall events in ReFH2, in order to remove the losses.  
In order to estimate a reasonable value to supply for Lin Dyke catchment, the CEH-GEAR gridded 1km hourly observations are used.  
All 1km grid cells which have their midpoint withiun the Lin Dyke catchment boundary are selected.  
Daily rainfall rates are calculated from the hourly values.  
Various percentiles of daily rainfall over the whole catchment are then calculated:  
* The mean rainfall (1.78mm) for the catchment 
* The 25th percentile rainfall (0mm) 
* The 50th percentile rainfall (0.1mm) 
* The 90th percentile rainfall (5.5mm) 
* The 95th percentile rainfall (8.6mm) 
* The 99th percentile rainfall (18.3mm)

These values are then converted into the format required by ReFH2 (although for some reason ReFH2 does not like the formatting of the datetime). So, had to manually type in values and then copy/paste into different spreadsheets.

NB:
* There was originally a mistake in this whereby was only calculating statistics over JJA data
* This has now been corrected to include whole year
* Also, values derived for JJA (e.g. 0.51mm for the mean) also were not correct even for JJA. This was because to go from hourly values to daily values I interpolated the data, and this filled in a load of values between August and June which were all assigned a value of 0, thus skewing the results
