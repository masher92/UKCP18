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

### <ins> Preparing the data </ins>
The data for this analysis was generated using ReFH2.  
Creating observed events:
* Load in catchment XML file, move to next screen
* Skip through to the second page and select Catchment Descriptors -> Model parameters and select 'Summer' from the season.
* Select Duration as '06:01:00' and the time step as 1 minute
* Select 'Add' under Observed rainfall on the left
* Select rainfall data from file (this must be in a format with no column names, otherwise it will reject it)
* Add antecedent rainfall data from file (this must be in a format with no column names, otherwise it will reject it)
* Select next
* Select 'Observed rainfall - 01/08/22' (or equivalent) from the top down menu at the top left
* Select 'Summer' under conditions
* Select 'export' and then 'this event' above the plot of 'Observed rainfall - 01/08/22 - as rural' to export the rainfall with rural model losses remove
* Select 'export' and then 'this event' above the plot of 'Observed rainfall - 01/08/22 - urbanised' to export the rainfall with urban model losses remove
* Columns "Total net rain mm (Observed rainfall - 05/04/2022) - as 100% rural model" or "Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model" can be used as the input to Hec-Ras

