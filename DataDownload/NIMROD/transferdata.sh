eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa_jasmin

year=$1
echo $year

# scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}06* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/



scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0605* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0611* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0613* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0621* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0625* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/

scp masher92@xfer1.jasmin.ac.uk:/gws/nopw/j04/icasp_swf/bmaybee/radar_obs/${year}/${year}0720* /nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/${year}/