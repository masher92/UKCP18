### To create an environment:
Type in cmd: conda create --name myenv (replacing myenv with the chosen name)
### To activate
conda activate myenv
### To install Spyder
conda install spyder  
When Spyder opens, check tools, prefereces, python interpretor and make sure it is within the same environment

### To install Iris:
conda install -c conda-forge iris  
conda install -c conda-forge iris-sample-data

### To install nc-time-axis (needed for plotting)
conda install -c conda-forge nc-time-axis

### To install geopandas
conda install -c conda-forge geopandas

### To install tilemapbase

### To install folium  
conda install -c conda-forge folium  


### hateyou - think this was working fine  
conda create --name hateyou  
conda activate hateyou  
conda install descartes  
conda install -c conda-forge geopandas  
conda install rtree  
conda install -c conda-forge iris  
conda install -c conda-forge nc-time-axis  
conda install -c conda-forge spyder  
