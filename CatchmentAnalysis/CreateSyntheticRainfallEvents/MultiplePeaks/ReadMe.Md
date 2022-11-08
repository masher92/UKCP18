NB: LOSS REMOVAL NEEDS TO BE REDONE, AND MODELS RERUN BECAUSE THE LOSS REMOVAL PROCESS USED WAS WRONG (ON SEVERAL COUNTS)

Several methods are explored for generating synthetic design storm hyetographs which preserve the total event rainfall volume and duration, but splitting this rainfall volume into multiple peaks. For now, an event with 3 peaks will be considered.

# Constructing multiple peaks

The following parameters must be accounted for to construct multiple peaks:
  1. The rainfall volume for each peak  
    * Suggestion: Divide the total volume by the number of peaks so each peak has an equal volume and there is the same total rainfall.
  2. The shape of each peak  
    * Suggestion: Use the same shape, but different peak rainfall height so it gives the desired volume given a start-to-end duration for the peak.
  3. The start-to-end duration of each peak  
    * This is a parameter we can play with, but probably we will mainly look at short durations.
  4. The spacing between peaks  
    * What is a "fair" spacing for comparison so that the overall "event duration" is the same (i.e. the total length of the event including the non rain periods)?

Three different possible approaches are considered for constructing a multi-peaked hyetograph (with 3 peaks):
- 'Divide-time'  
  - The first peak starts at the same time as the single peak, and the last peak finishes at the same time,  and there is a third peak located in the middle.
- 'Max-spread'  
  - The centre of the peaks are equally spread out over the duration of the event. There is the same amount of time between the start of the event and the 1st peak, the 1st peak and the 2nd peak, the 2nd peak and the 3rd peak, and the 3rd peak and the end of the event. (i.e. centre of the peaks at t=(1/6)*d, (3/6)*d, and (5/6)*d)
- 'Sub-peak timing'  
  - Divide the single peak into 3 sections so that each has the same volume of rainfall. Then calculate the "average arrival time" of the rainfall in each subpeak (using these as the centre for the multiple peaks). Peak timing calculated so that Nth part of rainfall falls on average at the same time as in the single peak consider each minute as a block with constant rainfall rate for simplicity (don't understand this)

Figure 3 visualises these 3 methods alongside an equivalent single peaked storm for 1h, 3h and 6h durations.

<p align="center">
<img src="LinDyke_DataAndFigs/SyntheticEvents_preLossRemoval/1h/1h_allmethods.jpg" width="300"  />
<img src="LinDyke_DataAndFigs/SyntheticEvents_preLossRemoval/3h/3h_allmethods.jpg" width="300" />
<img src="LinDyke_DataAndFigs/SyntheticEvents_preLossRemoval/6h/6h_allmethods.jpg" width="300"  />    
<p align="center"> Figure 3. Shows the synthetic rainfall events (pre loss removal) produced using the four methods (1= single peak, 2=divide-time, 3=max-spread, 4=sub-peak timing), for 1hr (left), 3hr (middle) and 6hr (right).  <p align="center">

 <!-- Script initially calculates a rate in mm/hr, can divide this by 60 to get a rate in mm/min
 Best to use 1 minute data to drive the model
 Input for Hec-Ras = mm/timestep.

 Does using multiple peaks make sense for a 1hr storm? SB: Even for the 6-hour rainfall events, most of the rainfall occurs in a much shorter period (maybe an hour or so). With a 1-hour duration, the peaks become very narrow to begin with, so splitting a single hour up into sub-peaks may not be so realistic. For 3 hours, it probably still makes sense.

 where I’ve been using ReFH2 to generate inputs to Hec-Ras I have been using the 6th column – ‘Total net rain mm (100 year) – urbanised model’, which has had some kind of losses removed from it, and is what I believe you are supposed to use as input to the flood model.  -->
