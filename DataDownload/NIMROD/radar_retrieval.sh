#!/bin/bash
# PREREQ's : access to MASS Nimrod radar files (requires Met Office approval)

year=$1
echo ${year}

ssh -A cloud9 "python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/Download_from_CEDA.py" $year

# user_dir= /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/
# gws_dir= /nfs/a319/gy17m2a/PhD/datadir/NimRod/2004/
# mkdir ${radardir}
# rm $radardir/*
# echo /nfs/a319/gy17m2a/PhD/datadir/NimRod/${year}/
cd /nfs/a319/gy17m2a/PhD/datadir/NimRod/${year}/
for file in *.tar ; do
# for file in metoffice-c-band-rain-radar_uk_20060626_1km-composite.dat.gz.tar ; do
  echo $file
  tar xf $file 
  gzip -d *.dat.gz
  ssh -A cloud9 "conda activate pygeospatial; python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_radar.py" $year
  rm $file
  rm *.dat
done
cd