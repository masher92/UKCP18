# Set up environment
import ftplib
import os
from getpass import getpass # Allows typing password invisibly
import sys

# Define the years between which the data is required
from_year = 2001    
to_year = 2002

resolution = '2.2km'

# Define ensemble members for which data is required
members = [ '01']
print("Downloading data for ensemble members " + str(members) + " for years between " + str(from_year) + " and " + str(to_year))

# Define the variables required
vars = ['pr']

# Define the years for which UKCP18 data exists
years_available = list(range(1980, 2022))

# When script is run this allows user to type username and password without showing it
# uuname = input('username:')
# ppword = getpass('password:')

# Login to FTP
#f=ftplib.FTP("ftp.ceda.ac.uk", 'masher', '4C)LyJ-f/t@')
f = ftplib.FTP("ftp.ceda.ac.uk", 'masher', 'Ug@nda!1Leeds23')
# f = ftplib.FTP('ftp.ceda.ac.uk')
#f.login('masher', 'Leedsz23')

# Loop through years, months, members, vars...
# Note 1980 only has December, similarly 2000 has January-November
# Try-catch expressions allows for this. 
# Download attempted, for failed attempt empty files are created, so these must be deleted

for member in members:
    print(member)
    for year in range(int(from_year), int(to_year) + 1):
      # For years where no UKCP18 data exists, skip, where data does exist, continue with processing
      if year in years_available:
      
      # Define directory where data should be stored  
        if 1980 <= year <= 2001:
            ddir = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/" + member + '/1980_2001' 
        elif 2002 <= year <= 2020:
            ddir = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/" + member + '/2002_2020' 
        elif 2020 <= year <= 2041:
            ddir = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/" + member + '/2020_2041' 
        elif 2060 <= year <= 2081:
            ddir = f"/nfs/a319/gy17m2a/PhD/datadir/UKCP18_hourly/{resolution}/" + member + '/2060_2081'    
        print("Data for ensemble member " + member + " for year " + str(year) + " to be stored in: " + ddir)        
              
      # If directory doesn't exist make it
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
            print ('Data directory created')
  
        # Change the local directory to where you want to put the data
        os.chdir(ddir)
        print(os.getcwd()) 
        
        # Loop through months
        for month in [2]:
            for var in vars:
                # Zreo pad number
                month = f'{month:02}'
                print(year)
                # Define filename, note the use of "360 day years (12 months with 30 days)"
                ffile=f"{var}_rcp85_land-cpm_uk_{resolution}_{member}_1hr_{year}{month}01-{year}{month}30.nc"  
                # If the file does not exist, then download it
#                 if os.path.exists(ffile):
#                     print ("File " + ffile + ' already exists, skipping to next file')
                if 1==2:
                    print ("File " + ffile + ' already exists, skipping to next file')
                else:
                    # Change the remote directory to reflect correct member and variable
                    f.cwd(f"/badc/ukcp18/data/land-cpm/uk/{resolution}/rcp85/{member}/{var}/1hr/v20210615")
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