# Run model with synthetic rainfall events
This contains instructions from setting up and running the Hec-Ras model within Hec-Ras, and also references an (unsuccesful) attempt to automate the process of setting up and running the Hec-Ras model. 

## Table of contents

1. [ Hec-Ras file structure](#filestructure)  
2. [ Opening a Hec-Ras Project](#openproject)
3. [ Creating an unsteady flow file](#unsteadyflow)
4. [ Running model](#runmodel)

<a name="filestructure"></a>
## 1. Hec-Ras file structure

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
## 2. Opening a Hec-Ras Project

1. Open Hec-Ras 
2. File -> Open Project -> Double click the .prj file

<a name="unsteadyflow"></a>
## 3. Creating unsteady flow file
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

<ins> It is also possible to edit the plan files and geometry files in a text editor. I thought that this might make it possible to set up plan files using each of our rainfall scenarios using a Python script which edited the precipitation data in each iteration, whilst keeping the other aspects constant. This is implemented in CreatePlan_and_UnsteadyFlowFiles.ipynb. However, this didn't work as even those these text files appeared to be identical to those produced by Hec-Ras they were not being recognised. I think this is something to do with the fact that when you produce the files in Hec-Ras it stores some internal reference to the name of the scenario, which if doesn't exist then it doesn't think to look for the files (although, not sure if this is correct or not). So, reverted to manually entering the data into Hec-Ras. CreatePlan_and_UnsteadyFlowFiles.ipynb does include some code to read in the plan files created in Hec-Ras and cross check their precipitation values against precipitation values in the csv files.</ins> 

<a name="runmodel"></a>
## 4. Running model                                                                                                              
To RUN model:
1. Press Run - > ‘Unsteady Flow Analysis’ button
2. File -> Open Plan -> Select plan that you want to run
3. Options - > Computation options and tolerances -> Advanced time step control. Complete as follows:   
	* Maximum courant: 2.
	* Minimum courant 0.75
	* Number of steps below minimum before doubling: 4
	* Maximum number of doubling base time step: 5 (32 min)
	* Maximum number of halving base time step: 10 (0.06 secs)
4. Press compute
