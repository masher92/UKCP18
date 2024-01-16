eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa_jasmin

em_code=$1
echo $em_code

mkdir /nfs/a319/gy17m2a/PhD/datadir/UKCP18_30mins/${em_code}/

for year in {1999..2021}
do
    echo "output: $i"
    scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${em_code}a.pr${year}06*  /nfs/a319/gy17m2a/PhD/datadir/UKCP18_30mins/${em_code}/
    scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${em_code}a.pr${year}07*  /nfs/a319/gy17m2a/PhD/datadir/UKCP18_30mins/${em_code}/
    scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/masher/${em_code}/${em_code}a.pr${year}08*  /nfs/a319/gy17m2a/PhD/datadir/UKCP18_30mins/${em_code}/
done
