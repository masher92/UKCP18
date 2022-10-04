# Run model with synthetic rainfall events

## Table of contents

1. [ Hec-Ras file structure](#filestructure)  
2. [ Opening a Hec-Ras Project](#openproject)
3. [ Create an unsteady flow file](#unsteadyflow)
4. [ Run model](#runmodel)

<a name="filestructure"></a>
## 1.Hec-Ras file structure

There are a number of files required by Hec-Ras to run:
*	.prj is the project file
* .g01 etc. are geometry files.
	* These describe how water will move through the river system. 
  	* They include the 2D flow area, land use, topography and channel structures
* .p01 etc. are plan files (each file p01, p02 etc is a different plan)
	* Plan files combine a geometry and an unsteady flow file
	* They can be opened by going to ‘Perform an unsteady flow’ button, then selecting ‘File’ -> ‘Open plan’
*	.u01 etc. are unsteady flow files 
*	.hdf are results files

<a name="openproject"></a>
## 2.Opening a Hec-Ras Project

1. Open Hec-Ras 
2. File -> Open Project -> Double click the .prj file

<a name="unsteadyflow"></a>
## 3. Create unsteady flow file

First step in performing a simulation is putting together a Plan.  Plan is a combination of geometry and flow data (boundary conditions (wherever water comes from and goes to a boundary condition is needed). This defines:
*	Geometry and unsteady flow data
*	Description
*	Simulation time window
*	Computation settings
*	Simulation options

This steps required to put together a plan:
1. Edit -> Unsteady Flow data 
2. Double click 'Precipitation
3. Change data time interval to 1 minute
4. Select No.Ordinates and increase to 300
5. Press Plot Data to check plotting
6. Had problem with dates being funny, and skipping certain time steps. But when you check table which you can produce from within the plotting window, the dates become normal. Closing the window and reopening it again also seemed to resolve the data issue
7. Close this window
8. In main Hec-Ras window select View/edit geometric data button (three from the left on top panel, with little lines)
9. Select the 2D flow area button the left hand side and select “Generate computation points on regular interval with all break lines”
10. How to save?       

<a name="runmodel"></a>
## 4. Run model                                                                                                              
To RUN model:
	a. Press Run - > ‘Unsteady Flow Analysis’ button
	b. File -> Open Plan -> Select plan that you want to run
	c. Options - > Computation options and tolerances -> Advanced time step control. Complete as follows:   
	
