##################################################################
# Set up environment and define variables
##################################################################
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns
import glob

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/"
os.chdir(root_fp)

#########
catchment_names  = glob.glob("*")
for catchment_name in catchment_names:
    print(catchment_name)
    filename = glob.glob(root_fp + "{}/CatchmentDescriptors/*.csv".format(catchment_name))[0]
    catchment_descriptors = pd.read_csv(filename)
    catchment_descriptors =catchment_descriptors[2:]     
    catchment_descriptors = catchment_descriptors[catchment_descriptors.columns[0:2]]
    
    if "df" not in globals():
        print("True")
        df = catchment_descriptors

    df[catchment_name]=catchment_descriptors[' "FEH CD-ROM"']    
    # Convert column to numeric
    df[catchment_name] =pd.to_numeric(df[catchment_name])    
    
# Rename columns
df.rename(columns={"VERSION": "Catchment Descriptor"}, inplace = True)
# Delete extra column
del df[' "FEH CD-ROM"']  

# Reformat
transposed = df.transpose()
transposed.rename(columns=transposed.iloc[0], inplace = True)
transposed = transposed[1:]

##### Plot area --
plt.hist(transposed['AREA'], bins =15, color='darkblue', edgecolor='black')
plt.xlabel('Catchment area (km2)')
plt.ylabel('Number of catchments')

plt.hist(transposed['ALTBAR'], bins =15, color='darkblue', edgecolor='black')
plt.xlabel('Mean Catchment Altitude (m above sea level)')
plt.ylabel('Number of catchments')

plt.hist(transposed['URBEXT2000'], bins =15, color='darkblue', edgecolor='black')
plt.xlabel('Urban Extent (2000)')
plt.ylabel('Number of catchments')

plt.hist(transposed['SAAR'], bins =15, color='darkblue', edgecolor='black')
plt.xlabel('Standard Average Areal Rainfall (mm)')
plt.ylabel('Number of catchments')

plt.hist(transposed['BFIHOST'], bins =15, color='darkblue', edgecolor='black')
plt.xlabel('BFIHOST')
plt.ylabel('Number of catchments')

# Scatter plots
#colors = np.where(transposed['URBEXT2000']>=0.3,'green','black').tolist()
plt.scatter(transposed['BFIHOST'], transposed['URBEXT2000'])
plt.xlabel('BFIHOST')
plt.ylabel('URBEXT2000')
plt.legend()

plt.scatter(transposed['ALTBAR'], transposed['SAAR'])
plt.xlabel('Mean Catchment Altitude (m above sea level)')
plt.ylabel('Standard Average Areal Rainfall (mm)')

##################################################################
##################################################################

# Define rootfp and set as working directory
root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/IndividualCatchments/"
os.chdir(root_fp)

#########
catchment_names  = glob.glob("*")
for catchment_name in catchment_names:
    print(catchment_name)
    filename = glob.glob(root_fp + "{}/DesignRainfall/*.csv".format(catchment_name))[0]
    design_rainfall = pd.read_csv(filename, skiprows =9)


    plt.bar(design_rainfall['Duration hours'], height =design_rainfall['2 year rainfall (mm)'] )

    
# Rename columns
df.rename(columns={"VERSION": "Catchment Descriptor"}, inplace = True)
# Delete extra column
del df[' "FEH CD-ROM"']  