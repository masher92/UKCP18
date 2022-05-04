## Defining antecedent conditions

The design storm hyetograph input to Hec-Ras is expected to be the net rainfall after losses have been subtracted. When FEH rainfall depths and ReFH2 design storm profiles are provided, ReFH2 calculates the net rainfall after losses have been subtracted. It is also possible to import observed rainfall data into ReFH2, alongside antecedent rainfall conditions for at least the 3 days prior to the event are required, and the rainfall data with losses subtracted will be returned. 

To calculate appropriate antecedent conditions, the CEH-GEAR precipitation data is extracted for the cells which are found within the catchment area (Figure 1)

<p align="center">
<img src="LinDyke_cells.png" width="350"  />
<p align="center"> Figure 1. <p align="center">

Using the hourly values for June, July and August for the period covered by the data (1990-2014), an average daily rainfall amount is calculated. For the Lin Dyke catchment this is 0.51mm.

## Questions about standard practice for defining antecedent conditions?
  * How is it usually done? https://refhdocs.hydrosolutions.co.uk/Initial-Conditions-Design-Estimates/
  * Could try find out exact method from manual to replicate
  * Or could try testing by experimenting with ReFH2
  * 
