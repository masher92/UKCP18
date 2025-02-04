# Run model with synthetic rainfall events
This describes the model and contains instructions from setting up and running the model within Hec-Ras, and also references an (unsuccesful) attempt to automate the process of setting up and running the Hec-Ras model. 

The Lin Dyke model is ran for a 6hr duration storm using the FEh single peak profile, 15 profiles based on observed rainfall and 3 synthetic profiles with multiple peaks. The details of the methods are in https://github.com/masher92/UKCP18/tree/master/CatchmentAnalysis/CreateSyntheticRainfallEvents

## Table of contents

1. [ The Model](#themodel)
2. [ Hec-Ras file structure](#filestructure)  
3. [ Opening a Hec-Ras Project](#openproject)
4. [ Creating an unsteady flow file](#unsteadyflow)
5. [ Running model](#runmodel)

<a name="themodel"></a>
## 1. The Model
The model is a 2D rain-on-grid flood model, built in Hec-Ras, and ran using the 2D unsteady diffusion wave equation set. It is based on land cover and terrain data both at 1m resolution. It is ran for 12 hours (with a 6 hour event) to ensure that all the processes occurring even after the rainfall event are accounted for. The timestep is set at 1 minute to balance model run time and accuracy, with a variable computational timestep based on keeping the courant condition between 0.75 and 2.  This is because the Courant should be as close to 1 as possible to generate reliable results.

 The external boundary condition is along the entire edge of the 2D Flow Area. It is a normal depth with an assumed slope of 0.001m to allow flow to leave the catchment. Otherwise, the runoff would inaccurately accumulate at the boundary.The 2D Flow Area is the computational mesh for the model. In this case the perimeter has been drawn offset from the perimeter of the catchment, to calculate the runoff more accurately at the edge at the catchment boundary. There can also be issues when generating the mesh if the boundary line is complex, therefore it has been simplified. This can be seen in Figure 5.6, it also shows the mesh at 10m resolution. This is to optimise the time taken to run the model while still preserving details. The mesh has been generated to include a breakline along the main 20 watercourse in the catchment to improve the accuracy of the calculations in the channel. This was assumed from the OS Open Rivers data.

The model covers the Lin Dyke catchment, to the east of Leeds, and includes two urban areas in Kippax and Garforth, as well as some wetlands in the lower reaches of the catchment before finally draining into the Aire. The catchment is a bit of a known local flooding hotspot, and has had several major pluvial flooding incidents in recent years.

Cell size is 1m (see email chain with Mark: "RE: Hec-ras cell size"). But are cells cut in half at the edges? Or does it always just keep a square edge? Do I filter to the catchment boundary, or do I include the boundary area? Zoom in on the Hec-Ras map and check - I tried to do this but connection was slow, but they didn't look square!

<a name="filestructure"></a>
## 2. Hec-Ras file structure

There are a number of files required by Hec-Ras to run:
* .prj is the project file
* .g01 etc. are geometry files.
	* These describe how water will move through the river system. 
  	* They include the 2D flow area, land use, topography and channel structures
* .p01 etc. are plan files (each file p01, p02 etc is a different plan)
	* Plan files combine a geometry and an unsteady flow file
	* They can be opened by going to ‘Perform an unsteady flow’ button, then selecting ‘File’ -> ‘Open plan’
*	.u01 etc. are unsteady flow files 
*	.hdf are results files

There are also a number of files created when the model is ran:
* .b01
* .bco01
* .IC.01

<a name="openproject"></a>
## 3. Opening a Hec-Ras Project

1. Open Hec-Ras 
2. File -> Open Project -> Double click the .prj file

<a name="unsteadyflow"></a>
## 4. Creating unsteady flow file
First step in performing a simulation is putting together a Plan.  Plan is a combination of geometry and flow data (boundary conditions (wherever water comes from and goes to a boundary condition is needed). This defines:
*	Geometry and unsteady flow data
*	Description
*	Simulation time window
*	Computation settings
*	Simulation options

These are the steps required to put together a plan in Hec-Ras:
1. Run -> Unsteady Flow Analysis
2. Set Starting and Ending Date to 01Jan2022, StartingTime to 1200 and EndingTime to 2400
3. Set ComputationInterval, MappingOutputInterval, HydrographOutputInterval, DetailedOutputInterval all to 1 minute
4. File -> Save Plan As
5. (Whilst this window is still open), from main Hec-Ras window select Edit Unsteady Flow Data
6. Double click 'Precipitation
7. Select Use Simulation Time and ensure this is set to start at 01Jan2022 at 1200
8. Change data time interval to 1 minute
9. Select No.Ordinates and increase to 300
10. Paste in data from excel files using column "Total net rain mm (Observed rainfall - 05/04/2022) - urbanised model"
11. Press Plot Data to check plotting
12. Had problem with dates being funny, and skipping certain time steps. But when you check table which you can produce from within the plotting window, the dates become normal. Closing the window and reopening it again also seemed to resolve the data issue
14. In main Hec-Ras window select View/edit geometric data button (three from the left on top panel, with little lines)
15. Select the 2D flow area button the left hand side and select “Generate computation points on regular interval with all break lines”
16. To save in the Run -> Unsteady Flow Analysis window-> Save plan as    

Alternative method (I guess for when there is already a plan loaded in Hec-Ras):
1. Edit -> Unsteady Flow Data -> Double click precipitation
2. Copy and paste in the post-loss removal precipitation data
3. File -> Save unsteady flow data as -> enter name -> close window
4. Run -> Unsteady flow analysis 
5. File -> Save Plan as (Check correct unsteady flow file selected)

*It is also possible to edit the plan files and geometry files in a text editor. I thought that this might make it possible to set up plan files using each of our rainfall scenarios using a Python script which edited the precipitation data in each iteration, whilst keeping the other aspects constant. This is implemented in CreatePlan_and_UnsteadyFlowFiles.ipynb. However, this didn't work as even those these text files appeared to be identical to those produced by Hec-Ras they were not being recognised. I think this is something to do with the fact that when you produce the files in Hec-Ras it stores some internal reference to the name of the scenario, which if doesn't exist then it doesn't think to look for the files (although, not sure if this is correct or not). So, reverted to manually entering the data into Hec-Ras. CreatePlan_and_UnsteadyFlowFiles.ipynb does include some code to read in the plan files created in Hec-Ras and cross check their precipitation values against precipitation values in the csv files.*

*Neeraj Sah did have a suggestion for getting around this (check emails) but at this point I felt like I had spent way too much time on this and needed to revert to setting up within Hec-Ras as normal*

<a name="runmodel"></a>
## 5. Running model                                                                                                              
To run model:
1. Press Run - > ‘Unsteady Flow Analysis’ button
2. File -> Open Plan -> Select plan that you want to run
3. Options - > Computation options and tolerances -> Advanced time step control. Complete as follows:   
	* Maximum courant: 2.
	* Minimum courant 0.75
	* Number of steps below minimum before doubling: 4
	* Maximum number of doubling base time step: 5 (32 min)
	* Maximum number of halving base time step: 10 (0.06 secs)
4. Press compute

Can also run multiple plans, by:
* Run -> Run multiple plans
* Selecting the plans you want

*I also set-up a script for running the models, which works, but probably doesn't offer any real advantage over the Hec-Ras capability to run multiple plans. This is RunHecRas_pyHMT2D.ipynb*
