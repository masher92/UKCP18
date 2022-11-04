## Testing the ReFH2 loss removal 

### <ins> Background </ins>
The Hec-Ras model (the way it is currently set up) requires a net rainfall input, with losses already subtracted.

There are two means of producing a net rainfall input from ReFH2:
* Use a design event:
    * Specify a duration and return period and a rainfall event is returned which includes a net rainfall rate
* Use an observed event:
    * Feed in an observed rainfall event AND somewhere between 3 and 365 days of daily antecedent rainfall data. 

### <ins> Aim </ins>
It is not clear exactly how the supplied antecedent conditions influence the amount of losses subtracted from observed events.   
Therefore, this research considers:
* The impact of the magnitude of the daily rainfall rate supplied
* The impact of the number of days of antecedent conditions supplied
* How the removal of losses from observed events differs from the loss removal in design events

### <ins> Literature </ins>
It is not exactly clear how losses are subtracted in ReFH2. There are some details provided in:  
1. https://www.hydrosolutions.co.uk/app/uploads/2019/10/ReFH2-Science-Report-Model-Parameters-and-Initial-Conditions-for-Ungauged-Catchments.pdf; and
2. https://refhdocs.hydrosolutions.co.uk/Simulating-Observed-Events/Estimation-of-Cini-for-Modelling-Observed-Events/.

These suggest that the parameter Cini, which describes the initial depth of water stored in the catchment, is crucial for determining the model's output:
* A low Cini i.e. not much water initially stored in the catchment --> more rainfall is absorbed --> smaller runoff and peak flow 
* A high Cini i.e. a lot of water initially in the catchment --> less rainfall is able to be absorbed --> higher runoff and peak flow.

Cini is calculated based upon BFIHOST (a measure of catchment responsiveness based upon geology) and SAAR (the standard average rainfall between 1960 and 1990). It also says in (2.) that Cini is estimated within ReFH2 through the application of the DAYMOD daily soil moisture accounting procedure.


### <ins> Method </ins>
