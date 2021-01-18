import iris.coord_categorisation
import iris
import glob
import os
from cftime import datetime

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

em = '01'

#############################################
## Load in the data
#############################################
filenames =[]
# Create filepath to correct folder using ensemble member and year
general_filename = 'datadir/UKCP18/2.2km/{}/1980_2001/pr_rcp85_land-cpm_uk_2.2km_{}_1hr_*'.format(em, em)
#print(general_filename)
# Find all files in directory which start with this string
for filename in glob.glob(general_filename):
    #print(filename)
    filenames.append(filename)
print(len(filenames))
   
monthly_cubes_list = iris.load(filenames,'lwe_precipitation_rate')
for cube in monthly_cubes_list:
     for attr in ['creation_date', 'tracking_id', 'history']:
         if attr in cube.attributes:
             del cube.attributes[attr]

# Concatenate the cubes into one
concat_cube = monthly_cubes_list.concatenate_cube()

# Remove ensemble member dimension
concat_cube = concat_cube[0,:,:,:]

# Create time constraint (only keeps hours between 1990 and 2000)
time_constraint = iris.Constraint(time=lambda c: c.point.year >= 1990 and c.point.year <= 2000)
time_constraint_cube =concat_cube.extract(time_constraint)
