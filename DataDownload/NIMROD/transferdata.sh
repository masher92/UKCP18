eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa_jasmin

year=$1
echo $year

#scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}06* #/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/
#scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}07* #/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/
#scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}08* /nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/



scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0716* /nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/