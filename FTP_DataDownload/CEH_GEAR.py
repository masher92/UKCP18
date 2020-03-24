#uuname: gy17m2a@leeds.ac.uk
#password: Uganda11Horace18
# Run from cmd python "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/PythonScripts/ftp_conn_obs.py"

import ftplib
import os
from getpass import getpass # Allows typing password invisibly

# Check working directory
os.getcwd()

# Define the local directory name to put data in
ddir="C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/datadir"

# If directory doesn't exist make it
if not os.path.isdir(ddir):
    os.mkdir(ddir)
    print ('Data Directory created')

# Change the local directory to where you want to put the data
os.chdir(ddir)

# When script is run this allows user to type username and password without showing it
uuname = input('username:')
ppword = getpass('password:')

# Login to FTP
f=ftplib.FTP("catalogue.ceh.ac.uk", uuname, ppword)
#f=ftplib.FTP("ftp.ceda.ac.uk", uuname, ppword)

#/datastore/eidchub/d4ddc781-25f3-423a-bba0-747cc82dc6fa"

# Loop through years, months, members, vars...
# Note 1980 only has December, similarly 2000 has January-November
# Try-catch expressions allows for this. 
# Download attempted, for failed attempt empty files are created, so these must be deleted
for year in range(1980, 1991) :
    # Loop through months
    for month in [1,2,3,4,5,6,7,8,9,10,11,12]:
        # Loop over members
        for member in ['01']: # note 02 and 03 are absent, this is currently a string
            # Loop through variables (precipitation and temperature)
            for var in (["pr"]):
                 # Change the remote directory to reflect correct member and variable
                 f.cwd("/badc/ukcp18/data/land-cpm/uk/2.2km/rcp85/"+member+"/"+var+"/1hr/latest")
                 # Define filename, note the use of "360 day years (12 months with 30 days)"
                 ffile="%s_rcp85_land-cpm_uk_2.2km_%s_1hr_%.4d%.2d01-%.4d%.2d30.nc" % (var, member, year, month, year, month)
                 print('Trying to retrieve '+ffile)
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