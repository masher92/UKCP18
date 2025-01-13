#!/bin/bash
# set -e
# PREREQ's : access to MASS Nimrod radar files (requires Met Office approval)

year=$1
echo $year

# conda activate ukcp18
#python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/Download_from_CEDA.py $year
cd /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

for file in *.tar ; do
  echo $file
  tar xf $file 
  gzip -d *.dat.gz
  # conda activate ukcp18
  python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year
  rm -rf $file
  rm -rf *.dat
done

cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/
