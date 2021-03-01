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



# Firgreen Beck
urbext = [0.0165]
saar6190 = [690]
propwet = [0.32]
area = [34.54] #km2

# Guiseley Beck
urbext = [0.2628]
saar6190 = [829]
propwet = [0.32]
area = [13.935] #km2

# Oil Mill Beck
urbext = [0.2141]
saar6190 = [801]
propwet = [0.32]
area = [16.27] #km2

# Lin Dyke
urbext = [0.1321]
saar6190 = [652]
propwet = [0.32]
area = [20.36] #km2

# Gill Beck- Aire
urbext = [0.0199]
saar6190 = [894]
propwet = [0.32]
area = [13.94] #km2

# Lin Dyke rainfall data
urbext = [0.1321]
saar6190 = [652]
propwet = [0.32]
area = [20.36] #km2

# Holbeck rainfall data
urbext = [0.2822]
saar6190 = [762]
propwet = [0.32]
area = [62.56] #km2

# Meanwood Beck data
urbext = [0.3605]
saar6190 = [753]
propwet = [0.32]
area = [42.57] #km2

# Mill Beck data
urbext = [0.0458]
saar6190 = [657]
propwet = [0.32]
area = [7.29] #km2

# Wyke Beck data
urbext = [0.3427]
saar6190 = [706]
propwet = [0.32]
area = [27.29] #km2

# Fairbun Ings rainfall data
urbext2000 = [0.0102]
saar6190 = [628]
propwet = [0.32]
area = [13.35] #km2
durations = [1,3,5,7, 9,11,13,15,17,19,21,23,25,27,29,31,33,35,37,39]
total_rainfall = [4.45, 9.12, 12.05, 14.14, 15.59,16.81,17.86, 18.8,19.64,20.41, 21.13,21.80,22.42,22.97,23.49, 23.99, 24.47,
                  24.92, 25.36, 25.77]
peak_rainfall = [1.97, 1.56, 1.26, 1.06, 0.91, 0.81,0.73,0.66, 0.61, 0.57, 0.53, 0.50, 0.47, 0.45,0.43, 0.41, 0.39, 0.38,
                 0.36, 0.35]