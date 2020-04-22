## Data download

<ins>UKCP18 Projections</ins>  
The projections are available via an FTP connection from the CEDA data catalogue.  
On the CEDA data catalogue precipitation data is stored in monthly precipitation netCDF files, with each file providing data for the whole of the UK (meaning you have to download it all).  
It is also possible to access the data through a User interface at https://ukclimateprojections-ui.metoffice.gov.uk/user/login?next=%2Fsubmit%2Fform%3Fproc_id%3DLS3A_Subset_01  
The UKCP18.py script automates download from the CEDA cataglogue. The script is set-up so that arguments specifying years and ensemble member for which download is desired are provided when the script is run from the command line.
e.g. python UKCP18.py from_year to_year ensemble_members
e.g. python UKCP18.py 1980 2001 1,2,3,4,5

12km data is available here: http://data.ceda.ac.uk/badc/ukcp18/data/land-rcm/eur/12km

<ins>Observations</ins>  
CEH-GEAR-1km data is not available via FTP, and has to be downloaded manually from: https://catalogue.ceh.ac.uk/datastore/eidchub/d4ddc781-25f3-423a-bba0-747cc82dc6fa/.

[//]: # (Data for CEH-GEAR was downloaded on the SEE Linux remote server https://www.see.leeds.ac.uk/linux/desktop/.
Attempted using wget to automate this, but it didn't download file properly (very small file; html). So, instead had to manually point and click to files and then transfer them to the correct folder in a319 using terminal and mv -v ~/Downloads/* /nfs/a319/gy17m2a/CEH-GEAR.)


<ins> To Do </ins>  
Could this be set-up to clip the data to the Leeds region on download to save on memory requirements?
