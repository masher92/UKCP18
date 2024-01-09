#!/bin/bash
# PREREQ's : access to MASS Nimrod radar files (requires Met Office approval)

date_info=$1

day=$(date -d ${date_info} +"%Y%m%d")
day1=$(date -d ${date_info}" +1 day" +"%Y%m%d")
# echo $day1
# echo $day

gws_dir = /nfs/a319/gy17m2a/PhD/datadir
radardir=$/nfs/a319/gy17m2a/PhD/datadir/NimRod/$(date -d ${date_info} +"%Y")
echo $radardir

# # cd $radardir
# # echo *${day1}*.tar
# # for file in *${day}*.dat.gz.tar *${day1}*.dat.gz.tar; do
# #   echo $file
# #   tar xf $file '*_rainrate_composite_1km_merged.Z'
# #   gzip -d *.Z
# # done
# # # cd

# $file = metoffice-c-band-rain-radar_uk_20060101_1km-composite.dat.gz
# tar xf $file '*_rainrate_composite_1km_merged.Z'


#!/bin/bash
# PREREQ's : access to MASS Nimrod radar files (requires Met Office approval)

echo MOlly 

echo /misc/frasia/Y$(date -d ${20120101} +"%Y").tar/*${day}

cd /nfs/a319/gy17m2a/PhD/datadir/NimRod/2004/

# for file in *.tar ; do
#  echo $file
#  tar xf $file '*metoffice-c-band-rain-radar_uk_20040618_1km-composite.dat.gz'
# #  tar xf $file '*_rainrate_composite_1km_merged.Z'
#  gzip -d *.Z
# done
