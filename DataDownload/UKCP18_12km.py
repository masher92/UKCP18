# masher
#Uganda11

# Run as python UKCP18.py from_year to_year ensemble_members
# e.g. python UKCP18.py 1980 2001 1,2,3,4,5

import ftplib
import os
from getpass import getpass # Allows typing password invisibly
import sys

# Extract from input values the ensemble members and zero pad them
members = [str(member).zfill(2) for member in sys.argv[1].split(',')]    
print("Downloading data for ensemble members " + str(sys.argv[1]))

# When script is run this allows user to type username and password without showing it
uuname = input('username:')
ppword = getpass('password:')

# Login to FTP
f=ftplib.FTP("ftp.ceda.ac.uk", uuname, ppword)
 
# Loop through variables; only precipitation currently
for var in (["pr"]):
# Loop through ensemble members
  for member in members:
    # Loop through years at ten year intervals (blocks that data is stored in)
    for year in range(1980, 2080, 10):
      # Define directory where data should be stored
      ddir = "/nfs/a319/gy17m2a/UKCP18/12km/" + member 
      # If directory doesn't exist make it
      if not os.path.isdir(ddir):
          os.makedirs(ddir)
          print ('Data directory created')
  
      # Change the local directory to where you want to put the data
      os.chdir(ddir)
        
      # Save the file name
      ffile = "pr_rcp85_land-rcm_uk_12km_{}_day_{}1201-{}1130.nc".format(member, year, year+10)
      # Check if directory exists and create if not
      if os.path.exists(ffile):
        print ("File " + ffile + ' already exists, skipping to next file')
      else:     
        # Change the remote directory to reflect correct member and variable
        f.cwd("/badc/ukcp18/data/land-rcm/uk/12km/rcp85/"+member+"/"+var+"/day/latest")
        print('File ' + ffile +  ' does not already exist, attempting to retrieve')
        try:     
           with open(ffile, 'wb') as fp:
               # Download the file
               # If the file doesn't exist then this causes the exception to be generated
               res = f.retrbinary('RETR %s' % ffile , fp.write)
               print ("File Downloaded successfully")
               # Don't know why this bit was there.
               if not res.startswith('226 Transfer complete'):
                   print('Download failed')
                   if os.path.isfile(ffile):
                       os.remove(ffile)          
        except ftplib.all_errors as e:
            # Print fail message 
           print('FTP error:', e) 
           # Check whether the specified path is an existing file, if so remove it
           # Necessary because empty file gets created even though the download fails. 
           if os.path.isfile(ffile):
               os.remove(ffile)                    
f.close()
