# Run model with synthetic rainfall events

## Table of contents

1. [ Hec-Ras file structure](#filestructure)  
2. [ Run model in Hec-Ras](#runmodel)  
  a.  [ Run model in Hec-Ras](#runmodel)   
  b. [ Post process model outputs in Hec-Ras](#postprocess)  
  c. [ Process outputs in QGIS](#qgis)   
  d. [ Plot results in Python](#python)   


<a name="filestructure"></a>
## 1.Hec-Ras file structure

There are a number of files required by Hec-Ras to run:
*	.prj is the project file
*	.g01 etc. are geometry files.
  *	These describe how water will move through the river system. 
  *	They include the 2D flow area, land use, topography and channel structures
*	.p01 etc. are plan files (each file p01, p02 etc is a different plan)
  *	Plan files combine a geometry and an unsteady flow file
	* They can be opened by going to ‘Perform an unsteady flow’ button, then selecting ‘File’ -> ‘Open plan’
*	.u01 etc. are unsteady flow files 
  *	Precipitation data can be accessed by ‘Edit’ -> ‘Unsteady flow data’ -> ‘Precipitation’ is at the bottom 
*	.hdf are results files

First step in performing a simulation is putting together a Plan.  Plan is a combination of geometry and flow data (boundary conditions (wherever water comes from and goes to a boundary condition is needed). This defines:
*	Geometry and unsteady flow data
*	Description
*	Simulation time window
*	Computation settings
*	Simulation options

 <a name="runmode"></a>
## 2.Running a model in Hec-Ras

1. Open Hec-Ras 
2. File -> Open Project -> Double click the .prj file
3. Create unsteady flow file
	a. Edit -> Unsteady Flow data 
	b. Double click 'Precipitation

### <ins> Flood extent and depth </ins>


 
                                                                                                                         
