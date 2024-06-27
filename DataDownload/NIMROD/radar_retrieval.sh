#!/bin/bash
# set -e
# PREREQ's : access to MASS Nimrod radar files (requires Met Office approval)

year=$1
echo $year

# conda activate ukcp18
# python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/Download_from_CEDA.py $year
cd /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

# for file in *.tar; do
#   echo "Processing $file"
  
#   # Generate the corresponding .nc filename
#   nc_file="${file%.tar}.nc"
  
#   # Check if the .nc file exists
#   if [ -f "$nc_file" ]; then
#     echo "Found existing .nc file: $nc_file. Deleting $file and skipping."
#     rm -f "$file"
#     continue
#   fi
  
#   # Extract the .tar file
#   tar xf "$file"
  
#   # Decompress .dat.gz files
#   for gz_file in *.dat.gz; do
#     gzip -d "$gz_file"
#   done

#   # Activate the conda environment and run the Python script
#   # conda activate ukcp18
#   python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year
  
#   # Clean up
#   rm -rf "$file"
#   rm -rf *.dat
# done

# for gz_file in *.dat.gz; do
#     gzip -d "$gz_file"
# done
# python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year


# Activate the conda environment and run the Python script
# conda activate ukcp18
# python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year


for file in *.tar ; do
  echo $file
  tar xf $file 
  gzip -d *.dat.gz
  # conda activate ukcp18
  python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year
  rm -rf $file
  rm -rf *.dat
done


# for file in *.tar; do
#     echo $file
#     #   tar -xvf $file 
#     for file in *.dat.gz; do
#         echo $file
#         gzip -d $file
#     done
#     # conda activate ukcp18
#     python /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/merge_into_daily_radar_file.py $year
#     rm -rf $file
#     rm -rf *.dat
# done

cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/

