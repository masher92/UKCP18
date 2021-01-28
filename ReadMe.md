## UKCP18  

This project contains code for analysis of the UKCP18 local 2.2km precipitation projections. This includes validation of the model projections using a gridded observations dataset CEH-GEAR1hr. 

## Table of contents

1. [ Data Download. ](#datadownload)
2. [ Regridding Observations. ](#regridding)
3. [ Raingauge Analysis. ](#raingauge)
4. [ Regional Rainfall Statistics. ](#regionalstats)
4. [ Precipitation PDFs. ](#precippdfs)
5. [ Unresolved issues. ](#issues)  
  a. [ 360-day calendar ](#issuesa)    
  b. [ Projection ](#issuesb)   
6. [ To do. ](#todo)   

<a name="datadownload"></a>
## Data Download

UKCP18 2.2km precipitation projections are downloaded for all 12 ensemble members, for baseline (1980-2000) and future (2020-2040, 2060-2080) timeslices, via an FTP connection to the CEDA data catalogue.

CEH-GEAR 1km gridded observations are manually downloaded from the CEH datastore.

<a name="regridding"></a>
## Regridding

<table>
  <tbody>
    <tr>    
    <td  align="center" style="width:25%;"> Objective</td>
    <td  align="center" style="width:25%;">Output </td>
    <td align="center" style="width:50%;">Analysis </td>
    </tr>
    <tr>
      <td> To regid the 1km observations onto a 2.2km grid to match the resolution of the model data </td>
      <td align="center">  Regridding is carried out using both linear regridding and nearest neighbour regridding. PDFs are plotted of all the precipitation values from the grid cells in the leeds-at-centre region using the observations on the 1km grid and the observations regridded to 2.2km using both the linear and nearest neighbour methods. </td>
      <td align="left"> The nearest neighbour interpolation method is deemed to be the most appropriate.   </td>
    </tr>    
     </tbody>
</table>


<a name="raingauge"></a>
## Rain Gauge Analysis

| Objective  | Outcome     | Analysis |
| :---: |    :-----------------:   |  :---: |  
| The sources of rain gauge data, their locations and the time periods they covered are documented. | Plot of locations of rain gauges in West Yorkshire  |
| PDFs of precipitation values from the EA and LCC rain gauges are plotted  |  |

To Do:

<a name="regionalstats"></a>
## Regional Rainfall Statistics

<table>
  <tbody>
    <tr>    
    <td  align="center" style="width:25%;"> Objective</td>
    <td  align="center" style="width:25%;">Output </td>
    <td align="center" style="width:50%;">Analysis </td>
    </tr>
    <tr>
      <td> Assess whether regridding the observations to a 2.2km grid, using both linear and nearest neighbour regridding, alters the spatial patterns in hourly precipitation values compared to the observations on the native 1km grid. </td>
      <td align="center">  Hourly JJA mean, max and percentile precipitation values plotted for the model across the UK, the North of England and for the area around Leeds using (1) the native 1km observations, (2) the observations regridded to 2.2km using linear regridding and (3) nearest neighbour regridding </td>
      <td align="left"> There are no substantial differences in spatial patterns using the two regridding methods  </td>
    </tr>    
    <tr>
      <td>Understand spatial distribution of hourly precipitation values in the model at various spatial scales </td>
      <td align="center">  Hourly JJA mean, max and percentile precipitation values plotted for the model across the North of England and for the area around Leeds </td>
      <td align="left">          <ul>  
          <li>There are well defined spatial patterns for the mean and lower percentile values, and these become more diffuse for the max and higher percentiles  </li>
          <li>Over the Northern region, there is generally a gradient of increasing precipitation intensity moving from East-West, with the highest values concentrated over the Pennines</li>
          <li> Over Leeds, there is a gradient of increasing precipitation intensity moving from East-West</li>
        </ul>  </td>
    </tr>
    <tr>
      <td>Understand how spatial distrubtion of hourly precipitation values in the model compares to the regridded, observed values  </td>
      <td align="center">  The difference between the mean model ensemble member values and the regridded observations are also plotted for hourly JJA mean, max and percentile precipitation values  </td>
      <td align="left">  ..  </td>
    </tr>    
     </tbody>
</table>

<a name="precippdfs"></a>
## Precipitation PDFs

<table>
  <tbody>
    <tr>    
    <td  align="center" style="width:15%;"> Objective</td>
    <td  align="center" style="width:15%;">Output </td>
    <td align="center" style="width:70%;">Analysis </td>
    </tr>
    <tr>
      <td align="left" style="width:15%;"> Assess the spread in hourly precipitation intensities across the model ensemble members over the region of Leeds </td>
      <td align="center" style="width:15%;" > PDFs of hourly precipitation intensities drawn from across all the grid boxes over the region of Leeds using both the model, the regridded observations and the native observations. PDFs are plotted using data from (1) the full time period covered by the model (1980-2000) and the full time perdiod covered by the observations (1990-2014) and (2) just the overlapping time period (1990-2000) </td>
      <td align="left" style="width:15%;"> Some ensemble members contain much more intense values (expand on this) </td>
    </tr>    
    <tr>
      <td> Determine the difference in hourly precipitation intensities between the model, the observations and the regridded observations </td>
      <td align="center">  PDFs of hourly precipitation intensities drawn from across all the grid boxes over the region of Leeds using both the model, the regridded observations and the native observations. PDFs are plotted using data from (1) the full time period covered by the model (1980-2000) and the full time perdiod covered by the observations (1990-2014) and (2) just the overlapping time period (1990-2000) </td>
      <td align="left">  The hourly precipitation intensities in the observations are consistently lower </td>
    </tr>
     </tbody>
</table>


<a name="issues"></a>
## Unresolved issues
<a name="issuesa"></a>
#### 360 day calendar
Each month has 30 days: this creates a problem when converting the date to a timestamp format as it cannot recognise 30 days in February. 
Check: https://unidata.github.io/cftime/api.html
<a name="issuesb"></a>
#### Projection
The UKCP18 data is provided in a Rotated Pole coordinate system.  
It is possible to get this Rotated Pole in the format of a cartopy projection: grid_crs = grid.coord('grid_latitude').coord_system.as_cartopy_crs()  
This can then be used to convert the projection of other shapefiles, for instance the outline of Leeds for plotting. To do this, the Cartopy projection Crs must be converted: proj_crs = CRS.from_dict(grid_crs.proj4_params) using from pyproj.crs import CRS  
However, it still does not work plotting the geodataframe of the outline of Leeds with the UKCP18 data cube in its native projection system.  
The 'grid_longitude' coordinate contains values that are >360, whereas these are supposed to (?) wrap around 360 to 0.  
However, if the longitudes are corrected in this way, e.g. with 361 becoming 1, it is no longer possible to plot them spatially as the plotting function does not except longitude values that are not 'monotonically increasing'.

Useful: https://www.bnhs.co.uk/2019/technology/grabagridref/OSGB.pdf 

<a name="todo"></a>
## To do
