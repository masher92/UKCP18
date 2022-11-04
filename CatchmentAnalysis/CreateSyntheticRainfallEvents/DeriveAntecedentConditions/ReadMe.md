## Testing the ReFH2 loss removal 

The Hec-Ras model (the way it is currently set up) requires a net rainfall input, with losses already subtracted.
When design rainfall events are produced using ReFH2, the output includes a net version of the rainfall with losses already subtracted. 

When using observed rainfall events, we can feed these into ReFH2 as observed rainfall events, and it similarly produces a version of the rainfall event with losses subtracted. For this to work, you have to also supply at least 3 days of antecedent rainfall conditions. 

### <ins> How does ReFH2 subtract losses? </ins>

It is not exactly clear how losses are subtracted in ReFH2. There are some details provided in:  
1. https://www.hydrosolutions.co.uk/app/uploads/2019/10/ReFH2-Science-Report-Model-Parameters-and-Initial-Conditions-for-Ungauged-Catchments.pdf; and
2. https://refhdocs.hydrosolutions.co.uk/Simulating-Observed-Events/Estimation-of-Cini-for-Modelling-Observed-Events/.

These suggest that the parameter Cini, which describes the initial depth of water stored in the catchment, is crucial for determining the model's output:
* A low Cini i.e. not much water initially stored in the catchment --> more rainfall is absorbed --> smaller runoff and peak flow 
* A high Cini i.e. a lot of water initially in the catchment --> less rainfall is able to be absorbed --> higher runoff and peak flow.

Cini is calculated based upon BFIHOST (a measure of catchment responsiveness based upon geology) and SAAR (the standard average rainfall between 1960 and 1990). It also says in (2.) that Cini is estimated within ReFH2 through the application of the DAYMOD daily soil moisture accounting procedure.