'''
Reformatting of CEH-GEAR data is required as Iris seems to struggle with processing it.
Want to check that this reformatting doesn't alter the data.
This file loads in an example of an original cube and a reformatted cube for one month.
It loops through timesteps and checks the mean and max value for the original and reformatted cubes
and records the largest difference between the two.
'''

############################################
# Define variables and set up environment
#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

####################################################################
# Load native version of cube, reformatted cube and regridded cube
####################################################################
#Filename of cube
filename = "datadir/CEH-GEAR/CEH-GEAR-1hr_199001.nc"

# Load cube in its native format
cube = iris.load(filename)[5]

# Filename of reformatted cube
filename_reformat = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_reformatted/rf_")
cube_rfmt = iris.load(filename_reformat)[0]

# Filename of regridded cube
filename_regrid = filename.replace("datadir/CEH-GEAR/", "Outputs/CEH-GEAR_regridded_2.2km/rg_")
cube_rgd = iris.load(filename_regrid)[0]

####################################################################
# Check the maximum difference betwen the mean and max in the original 
# and reformatted cubes
####################################################################
max_mean_diff = 0
max_max_diff = 0

for frame in range(100,200):
    #print(frame)
    rfmt_cube = cube_rfmt[frame]
    rfmt_cube_data = rfmt_cube.data
    rfmt_max = np.nanmax(rfmt_cube_data)
    rfmt_mean = np.nanmean(rfmt_cube_data)
    
    orig_cube = cube[frame]
    cube_data = orig_cube.data
    cube_max = np.nanmax(cube_data)
    cube_mean = np.nanmean(cube_data)
    
    max_mean_diff = (rfmt_mean - cube_mean) if (rfmt_mean - cube_mean) > max_mean_diff else max_mean_diff
    max_max_diff = (rfmt_max - cube_max) if (rfmt_max - cube_max) > max_max_diff else max_max_diff

####################################################################
# Checking plotting
####################################################################
import matplotlib.pyplot as plt

# month_uk_cube = cube_rgd
# hour = month_uk_cube[frame]
# #Extract the data
# hour_data = hour.data
# np.nanmean(hour_data)
# np.nanmax(hour_data)
# # Flip the data so it's not upside down
# hour_data_fl = np.flipud(hour_data)
# # Fill empty values with NaN
# hour_data_fl = hour_data_fl.filled(np.nan)  

# contour = plt.contourf(hour_data, cmap=precip_colormap)
# contour = plt.colorbar()
# contour =plt.axes().set_aspect('equal') 


# month_uk_cube = cube_rfmt
# hour= month_uk_cube[frame]
# #Extract the data
# hour_data = hour.data
# np.nanmean(hour_data)
# np.nanmax(hour_data)
# # Flip the data so it's not upside down
# hour_data_fl = np.flipud(hour_data)
# # Fill empty values with NaN
# hour_data_fl = hour_data_fl.filled(np.nan)  

# contour = plt.contourf(hour_data_fl, cmap=precip_colormap)
# contour = plt.colorbar()
# contour =plt.axes().set_aspect('equal') 


# month_uk_cube = cube
# hour = month_uk_cube[frame]
# #Extract the data
# hour_data = hour.data
# np.nanmean(hour_data)
# np.nanmax(hour_data)
# # Flip the data so it's not upside down
# hour_data_fl = np.flipud(hour_data)
# # Fill empty values with NaN
# hour_data_fl = hour_data_fl.filled(np.nan)  

# contour = plt.contourf(hour_data_fl, cmap=precip_colormap)
# contour = plt.colorbar()
# contour =plt.axes().set_aspect('equal') 


# qplt.contourf(hour, cmap=precip_colormap)
# qplt.contourf(hour_rfmt, cmap=precip_colormap)
# qplt.contourf(hour_rgd, cmap=precip_colormap)
