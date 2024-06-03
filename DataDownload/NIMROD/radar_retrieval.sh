#!/bin/bash
# set -e
# PREREQ's : access to MASS Nimrod radar files (requires Met Office approval)

# year=$1
for year in 2018 ; do
    echo $year

    conda activate pygeospatial
    python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/Download_from_CEDA.py $year

    # rm $radardir/*
    # echo /nfs/a319/gy17m2a/PhD/datadir/NimRod/${year}/
    cd /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/
    for file in *.tar ; do
      echo $file
      tar xf $file 
      gzip -d *.dat.gz
      conda activate ukcp18
      python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year
      rm -rf $file
      rm -rf *.dat
    done
done

cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/


