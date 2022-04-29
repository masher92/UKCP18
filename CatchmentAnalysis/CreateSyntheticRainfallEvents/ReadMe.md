Normally, REFH2 uses a single peak, and this peak can be characterised by:
1) the total corresponding rainfall volume $V$. 
2) the duration $d$ (start to end).
3) the shape of the peak, defined here (I will try to turn this into an equation for rainfall rate as a function of time): https://refhdocs.hydrosolutions.co.uk/Design-DDF-Rainfall-Hyetographs/Design-Storm-Profiles/
 
If we use N multiple peaks, we need to know:
1) the rainfall volume$ V_1,...V_N$ for each peak. Suggestion: use $V/N$, so we have the same total rainfall.
2) the shape of each peak. Suggestion: use the same shape, but different peak rainfall height so it gives the desired volume given a start-to-end duration for the peak.
3) the start-to-end duration of each peak. This is a parameter we can play with, but probably we will mainly look at short durations.
4) the spacing between peaks. Here, the question is what a "fair" spacing for comparison so that the overall "event duration" is the same (i.e. the total length of the event including the non rain periods)


, and this is probably a bit subjective. We could also consider this as another parameter to play with.
- One approach would be that the first peak starts at the same time as the "long single peak" above and the last peak finishes at the same time. However, this may not be the best representation as the "long peak" is only drizzling at the start/end time. 
- Another simple approach, which may not be bad and avoids the criticism above, would be to put the peaks at a regular intervals related to the total duration of the event $d$. For example, for 3 peaks, put the centre of the peaks at t=(1/6)*d, (3/6)*d, and (5/6)*d.
- I have thought of more representative ways of doing this. One approach would be to dive the "long peak" into N sections with equal corresponding rainfall volume, and then calculate the "average arrival time" of the rainfall in each subpeak (using these as the centre for the multiple peaks). 
Let me know what you think. I can try making some example plots, which could help to discuss this.


<p align="center">
  <img src=".PNG" width="300" />
<img src="1hr_syntheticevents.jpg" width="300"  /> 
<img src="3hr_syntheticevents.jpg" width="300" />
<img src="6hr_syntheticevents.jpg" width="300"  />    
<p align="center"> Figure 1. <p align="center">
