ems=( "01" "04" 05 06 07 08 09 10 11 12 13 15 )
yrs=( '01' '02' '03' '04' '05' '09' '10' '11' '12')

for em in "${ems[@]}"
do
    echo $em
    cd /nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/2.2km_regridded_12km/${em}/NearestNeighbour/1980_2001/
    for yr in "${yrs[@]}"
    do 
        echo $yr
        rm -rf *${yr}01*
    done

done


cd /nfs/a319/gy17m2a/PhD/Scripts/DataDownload/UKCP18/