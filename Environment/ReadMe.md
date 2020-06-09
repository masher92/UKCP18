conda env export --no-builds >env.yml -- didn't work  
conda env export --from-history | grep -v prefix > environment.yml -- didn't work, as grep gives error  
conda env export --from-history > environment.yml -- didn't work   
conda env export --no-build > environment_nobuild.yml -- didn't work  

Manually move all packages that come under the error message under the pip section in the .yml file. This gets rid of initial error message but get a different error instead.

Using the approach suggested by IT service desk, the environment was created successfully and all packages installed; however got an error to do with the CRS when trying to use tilemapbase.  

Successfully imported environment from desktop computer to remote server, by:  
Create env.yml file on desktop  
Run conda env create -f env.yml on remote server.  

However, this wasn't working.  
After running conda update -n base conda it worked  

Further problems with the tilemapbase cache:  
Resolved by running from tilemapbase import init  
init(create = True)

