### Aim

Create a spatial map of the model grid over the Leeds and West Yorkshire region.  
In this, the central coordinate of each square is the latitude, longitude pair associated with each precipitation value.  
Plotting with pcolormesh interprets the coordiantes given as the bottom left coordinate of the grid cell, so need to calculate these for each grid before plotting.    
Colour the grids according to the mean or percentile precipitation value over a certain time period.  
Currently this only uses one ensemble member. Test with using all ensemble members.  

Realised that memory requirements could be decreased by trimming at an early stage to just an area covering West Yorkshire. Don't think this process is working exactly right - but almost.  

Started work on plotting PDFs for an area expanding out around a location of interest, e.g. 3x3, 5x5 etc. But need to apply this to calcualting the PDFs. 
Think on desktop PC this was very slow due to interpolation?! need to check this on remote server.  
