### Raw radar data downloaded from CEDA archive for 2004-2014 (or so)
- Raw radar data at 5 mins is available from CEDA
- Some of this data was already downloaded/processed and stored on iCASP workspace on MASS, so for this I have just transferred the data across, trimmed it to the Leeds region, and removed the non-trimmed version.
- The data is at 5min resolution, but I need to use it aggregated to 30 mins. I action this using the Aggregate-to-halfhourly.py script. This creates daily outputs which include, ideally, 48 values (2 for each of 24 hours). However, when aggregating, if less than 4 values are available in a particular 30 min period then that 30 min period is discarded.
- The radar data is at 1km, and so for the comparisons with the UKCP2.2km data it needs to be regridded. This is done on the 30 minutes data.  

### Process for downloading/transferring data in more detail
#### For 2014/2015/2018/2019/2020
-- Transferred the data from Ben's folder on the iCASP workspace on MASS, using the transferdata.sh script
-- Used TrimBen'sRadarObs_toLeeds.ipynb to cut it to the extent of Leeds

#### Download from CEDA: 
In order to download and process NIMROD raw radar data from a particular year (e.g. 2004):
  * Open MobaXterm
  * cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD
  * ./radar_retrieval.sh 2004 (if this doesnt work first run chmod +755 radar_retrieval.sh)

This radar_retrieval.sh shell scripts:
* Calls Download_from_CEDA.py which downloads data from CEDA archive
* Untars and unzips the data
* Calls merge_into_daily_radar_file.py which converts the .dat files to netCDFs grouped by day AND cuts them to the extent of Leeds

However, haven't been able to do this with data from 2004/2005 because of error with calendar that I can't work out


