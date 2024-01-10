In order to download and process NIMROD raw radar data from a particular year (e.g. 2004):
  * Open MobaXterm
  * cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD
  *./radar_retrieval.sh 2004 (if this doesnt work first run chmod +755 radar_retrieval.sh)

This radar_retrieval.sh shell scripts:
* Calls Download_from_CEDA.py which downloads data from CEDA archive
* Untars and unzips the data
* Calls merge_radar.py which converts the .dat files to netCDFs grouped by day

However, haven't been able to do this with data from 2004/2005 because of error with calendar that I can't work out
