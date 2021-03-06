# masher
#Uganda11

# Run as python UKCP18.py from_year to_year ensemble_members
# e.g. python UKCP18.py 1980 2001 1,2,3,4,5

import ftplib
import os
from getpass import getpass # Allows typing password invisibly
import sys

# Extract from input values the years between which the data is required
from_year = sys.argv[1]
to_year = sys.argv[2]

# Extract from input values the ensemble members and zero pad them
members = [str(member).zfill(2) for member in sys.argv[3].split(',')]    
print("Downloading data for ensemble members " + str(sys.argv[3]) + " for years between " + str(from_year) + " and " + str(to_year))

# Define the years for which UKCP18 data exists
years_available = list(range(1980, 2001)) + list(range(2020, 2041)) + list(range(2060, 2081))

# When script is run this allows user to type username and password without showing it
uuname = input('username:')
ppword = getpass('password:')

# Login to FTP
f=ftplib.FTP("ftp.ceda.ac.uk", uuname, ppword)

# Loop through years, months, members, vars...
# Note 1980 only has December, similarly 2000 has January-November
# Try-catch expressions allows for this. 
# Download attempted, for failed attempt empty files are created, so these must be deleted
for member in members:
  for year in range(int(from_year), int(to_year) + 1):
      # For years where no UKCP18 data exists, skip, where data does exist, continue with processing
      if year in years_available:
      
      # Define directory where data should be stored  
        if 1980 <= year <= 2001:
          ddir = "/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/" + member + '/1980_2001' 
        elif 2020 <= year <= 2041:
          ddir = "/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/" + member + '/2020_2041' 
        elif 2060 <= year <= 2081:
          ddir = "/nfs/a319/gy17m2a/datadir/UKCP18/2.2km/" + member + '/2060_2081'    
        print("Data for ensemble member " + member + " for year " + str(year) + " to be stored in: " + ddir)        
              
      # If directory doesn't exist make it
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
            print ('Data directory created')
  
        # Change the local directory to where you want to put the data
        os.chdir(ddir)
        print(os.getcwd()) 
        
        # Loop through months
        #for month in [3]:
        for month in [1,2,3,4,5,6,7,8,9,10,11,12]:
          for var in (["pr"]):
            # Define filename, note the use of "360 day years (12 months with 30 days)"
            ffile="%s_rcp85_land-cpm_uk_2.2km_%s_1hr_%.4d%.2d01-%.4d%.2d30.nc" % (var, member, year, month, year, month)
            # If the file does not exist, then download it
            if os.path.exists(ffile):
              print ("File " + ffile + ' already exists, skipping to next file')
            else:
              # Change the remote directory to reflect correct member and variable
              f.cwd("/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/"+member+"/"+var+"/1hr/latest")
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
 
