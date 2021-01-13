### PDFs of precipitation intensity

PDFs of precipitation intensity are plotted using data from across all cells in the "Leeds-at-centre" region.  
In "CombineAllYearsDataAcrossregion.py", for each ensemble member, for each cell in this 'leeds-at-centre' region a numpy array is saved which contains the precipitation values across the full 1980-2000 period. An array is then also saved which contains all of the data from all of the cells stacked into one array. An array is also saved which contains the time-stamps to which these precipitation values refer.  
The PDFs are plotted in "CompareModel_Obs_PDFs.py". PDFs are plotted using both 1. All the model data (1980-2000) and all the observations data (1990-2014) and 2. Just the model and observations data from within the overlapping time period.  
Extracting the data from within just the overlapping time period is complicated because the model uses a 360 day calendar (12 months of 30 days). This means that it is not possible to simply save the dates as datetime objects and to filter out dates not in the overlapping period. A method was devised to deal with this issue:
* sdfd

#### Using model data 1980-2000 and observations data (1990-2014)

##### Observations vs 12 individual model ensemble members 
PDFs of precipitation intensity values across the whole of the Leeds area are plotted for the 1km observations, the regridded 2.2km observations and the twelve model ensemble members.  

<p align="center">
  <img src="PDFs/10Bins.png" width="300"  />
  <img src="PDFs/13Bins.png" width="300"  />
  <img src="PDFs/16Bins.png" width="300"  />  
  <img src="PDFs/21Bins.png" width="300"  />  
  <img src="PDFs/25Bins.png" width="300"  />  
  <img src="PDFs/29Bins.png" width="300"  />
  <img src="PDFs/45Bins.png" width="300"  />    
<p align="center"> Figure 1. PDF of precipitation intensity across the Leeds area <p align="center">

##### Observations vs combined model data across twelve ensemble members
PDFs of precipitation intensity values across the whole of the Leeds area are plotted for the 1km observations, the regridded 2.2km observations and the combined data from the twelve model ensemble members.  

<p align="center">
  <img src="PDFs/ModelVsObs_25Bins.png" width="300"  />
  <img src="PDFs/ModelVsObs_33Bins.png" width="300"  />
  <img src="PDFs/ModelVsObs_37Bins.png" width="300"  />
  
<p align="center"> Figure 2. PDF of precipitation intensity across the Leeds area <p align="center">


#### Using just overlapping time period ()
