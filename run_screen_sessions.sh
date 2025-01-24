#!/bin/bash
echo "hellO"
for year in {2006..2019}; do
  screen -dmS "session_$year" /bin/bash -c "
    echo '=== Running python script for year $year ===';
    conda activate ukcp18 &&
    cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/NIMROD/ &&
 pwd &&
    python Aggregate-to-halfhourly.py $year
  "
done
