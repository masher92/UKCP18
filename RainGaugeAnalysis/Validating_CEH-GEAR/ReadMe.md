## Validating CEH-GEAR1hr gridded observations using quality-controlled gauge data

PDFs of hourly precipitation intensity are plotted using the data from quality-controlled rain gauges and the data from the grid cell in the CEH-GEAR1hr observations dataset that the gauge is found within. In each case, only the overlapping time period between the two datasets is used. NA values are filtered out after finding the overlapping time period, so data for some datetimes may be included in one dataset but not the other.

#### Bramham Logger - 01-01-1990 00:00:00 - 31-12-2014 23:00:00 
<p align="left">
<img src="Figs/CheckingLocations/bramham_logger.png" width="500"  title="Original 1km grid" />
<img src="Figs/PDF_GaugevsGridCell/bramham_logger.png" width="500"  title="Original 1km grid" />
</p>

NA values in gauge data: 3253
NA values in CEH-GEAR grid cell data: 9

#### Knostrop Logger - 01-01-1990 00:00:00 - 31-12-2014 23:00:00
<p align="left">
<img src="Figs/CheckingLocations/knostrop_logger.png" width="500"  title="Original 1km grid" />
<img src="Figs/PDF_GaugevsGridCell/knostrop_logger.png" width="500"  title="Original 1km grid" />
</p>

NA values in gauge data: 14583
NA values in CEH-GEAR grid cell data: 9

#### Eccup Logger - 01-01-1990 00:00:00 - 31-12-2014 23:00:00
<p align="left">
<img src="Figs/CheckingLocations/eccup_logger.png" width="500"  title="Original 1km grid" />
<img src="Figs/PDF_GaugevsGridCell/eccup_logger.png" width="500"  title="Original 1km grid" />
</p>

NA values in gauge data: 3480
NA values in CEH-GEAR grid cell data: 9
  
#### Farnley Hall Logger - 01-01-1990 00:00:00 - 31-12-2014 23:00:00
<p align="left">
<img src="Figs/CheckingLocations/farnley_hall_logger.png" width="500"  title="Original 1km grid" />
<img src="Figs/PDF_GaugevsGridCell/farnley_hall_logger.png" width="500"  title="Original 1km grid" />
</p>

NA values in gauge data: 1436
NA values in CEH-GEAR grid cell data: 9

#### Headingley Logger - 25-01-1996 10:00:00 - 31-12-2014 23:00:00
<p align="left">
<img src="Figs/CheckingLocations/headingley_logger.png" width="500"  title="Original 1km grid" />
<img src="Figs/PDF_GaugevsGridCell/headingley_logger.png" width="500"  title="Original 1km grid" />
</p>

NA values in gauge data: 1078
NA values in CEH-GEAR grid cell data: 0 (because these first 9 dates are already removed in trimming to same time period as gauge)

#### Otley s.wks Logger - 01-01-1990 00:00:00 - 31-12-2014 23:00:00 
<p align="left">
<img src="Figs/CheckingLocations/otley_s.wks_logger.png" width="500"  title="Original 1km grid" />
<img src="Figs/PDF_GaugevsGridCell/otley_s.wks_logger.png" width="500"  title="Original 1km grid" />
</p>

NA values in gauge data: 13483
NA values in CEH-GEAR grid cell data: 9


### Analysis
For the Knostrop, Eccup and Farnely Hall gauges, hourly precipitation values of the same maximum intensity are found in both the gauge data and the CEH-GEAR data.

Bramham, Otley
Green (CEH-GEAR) - line longer

Knostrop, Eccup, Farnley Hall
Lines the same

Headingley:
Red (Gauge) - line longer

|    | Datetime            | Precipitation (mm/hr)_x | Precipitation (mm/hr)_y |
|----|---------------------|-------------------------|-------------------------|
| 0  | 2004-08-09 12:00:00 | 22.4                    | 0.8                     |
| 1  | 2008-08-20 20:00:00 | 17.2                    | 6.3                     |
| 2  | 2009-06-15 12:00:00 | 16.6                    | 0.0                     |
| 3  | 2005-09-10 05:00:00 | 14.6                    | 7.4                     |
| 4  | 2004-08-10 14:00:00 | 13.2                    | 0.0                     |
| 5  | 2001-04-25 16:00:00 | 12.8                    | 0.0                     |
| 6  | 2007-07-01 12:00:00 | 12.0                    | 0.0                     |
| 7  | 2014-08-08 17:00:00 | 11.8                    | 0.9                     |
| 8  | 2000-09-19 22:00:00 | 11.6                    | 7.0                     |
| 9  | 2004-08-10 07:00:00 | 11.6                    | 2.5                     |
| 10 | 2012-07-07 19:00:00 | 11.6                    | 15.9                    |
| 11 | 2006-08-17 14:00:00 | 11.0                    | 0.0                     |
| 12 | 2011-09-16 17:00:00 | 11.0                    | 0.0                     |
| 13 | 2007-06-20 01:00:00 | 10.8                    | 0.4                     |
| 14 | 2006-09-02 11:00:00 | 10.4                    | 2.5                     |
| 15 | 1991-06-28 14:00:00 | 9.8                     | 0.0                     |
| 16 | 1997-08-31 15:00:00 | 9.8                     | 8.4                     |
| 17 | 2004-08-12 18:00:00 | 9.8                     | 5.1                     |
| 18 | 2013-07-28 03:00:00 | 9.8                     | 8.8                     |
| 19 | 2012-08-05 14:00:00 | 9.4                     | 0.0                     |
