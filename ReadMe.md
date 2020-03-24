## Project 2 - Scripts

This project contains tools to model the impact of a bomb exploding on the buildings in its vicinity using Arcmap.  
This project builds on the contents of Practical 1 - Model Builder which created a ModelBuilder model to accomplish this.  
The data it is based on can be found in Data/Practical1-4-Data.zip.      

<b> The file "RunModelFromScript":</b>   
Is an external (and standalone script) which runs the BombExplosion model created in ModelBuilder and stored in the Practical1_Models.tbx. 
It takes as inputs: 
* A shapefile containing the location of an explosion.
* A shapefile containing the outlines and locations of the surrounding buildings.
* A distance at which the impact of the explosion is felt.  

It returns as outputs:  
* A shapefile containing the outlines of the buildings impacted by the explosion.

<b> The file "RunModelAsTool": </b>  
Is a version of this script which is (only) executable from within a Python toolbox i.e. allows us to run the model as a tool. 
It takes the same inputs and returns same output as above, but they must be input as parameters when running the tool.    
This script is contained within the toolbox "Explosion Toolbox (v2).tbx"  
			
<b> The file "CreateLayerFile":</b>  
Provides a script for converting a layer file into a shapefile.

To Do:  
Further improvements to this work would be to attach the script to a menu item, to make it more readily runable.
