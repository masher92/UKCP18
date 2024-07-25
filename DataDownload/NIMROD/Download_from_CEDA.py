import ftplib
import os
from getpass import getpass # Allows typing password invisibly
import sys
import tarfile
import gzip
import shutil

year = int(sys.argv[1])
# 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020

# When script is run this allows user to type username and password without showing it
uuname = 'masher'
ppword = 'T{$WW"8bLlAt'

# Login to FTP
f = ftplib.FTP("ftp.ceda.ac.uk", uuname, ppword)

# Loop through years 
for year in range(year, year+1, 1):
    print(year)
    ###########################
    # Change to right directory
    ###########################
    f.cwd(f"badc/ukmo-nimrod/data/composite/uk-1km/{year}")
    
    # Define directory where data should be stored
    ddir = f"/nfs/a161/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/" 
    # If directory doesn't exist make it
    if not os.path.isdir(ddir):
        os.makedirs(ddir)
        print ('Data directory created')
    # Change the local directory to where you want to put the data
    os.chdir(ddir)

    ###########################
    # Get a list of files to download from this folder
    ###########################
    dir_list = []
    f.dir(dir_list.append)
    dir_list
    for line_num, line in enumerate(dir_list):
        dir_list[line_num] = "%s" % "','".join(line[55:].strip().split(' '))
    
    ###########################
    # Loop through list and download files
    ###########################
    for ffile in dir_list:
#         if ffile[35:37] in ['06', '07', '08']:
#             print(ffile[37:39])
#             if ffile[37:39] in ['26']:
        if ffile == 'metoffice-c-band-rain-radar_uk_20121117_1km-composite.dat.gz.tar':
                with open(ffile, 'wb') as fp:
                    print("Downloading")
                    # Download the file
                    # If the file doesn't exist then this causes the exception to be generated
                    res = f.retrbinary('RETR %s' % ffile , fp.write)
                    # Don't know why this bit was there.
                    if not res.startswith('226 Transfer complete'):
                        print(ffile, 'Download failed')
                        if os.path.isfile(ffile):
                            os.remove(ffile)         
    print(f"Download complete for {year}")
    
    