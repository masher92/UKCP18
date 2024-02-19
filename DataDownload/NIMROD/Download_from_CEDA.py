import ftplib
import os
from getpass import getpass # Allows typing password invisibly
import sys
import tarfile
import gzip
import shutil


year = int(sys.argv[1])

# When script is run this allows user to type username and password without showing it
# uuname = input('username:')
# ppword = getpass('password:')

uuname = "masher"
ppword = "Uganda11"


# Login to FTP
f=ftplib.FTP("ftp.ceda.ac.uk", uuname, ppword)


# Loop through years 
for year in range(year, year+1, 1):
    ###########################
    # Change to right directory
    ###########################
    f.cwd(f"badc/ukmo-nimrod/data/composite/uk-1km/{year}")
    
    # Define directory where data should be stored
    ddir = f"/nfs/a319/gy17m2a/PhD/datadir/NIMROD/5mins/OriginalFormat_1km/{year}/" 
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
        if not ffile[35:37] in ['01', '02', '03', '04', '05', '09', '10', '11','12']:
#         if ffile == 'metoffice-c-band-rain-radar_uk_20040831_1km-composite.dat.gz.tar':
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