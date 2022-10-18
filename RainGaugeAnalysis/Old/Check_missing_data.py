import datetime
import pandas as pd
import os
import numpy as np

root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

# Read in dataframe
df = pd.read_csv("datadir/GaugeData/EA_RainfallHourlyTotals/Wakefield_080282_HourlyRain_190385_031120.csv", 
                        skiprows = 20, usecols = [0,1,2,3,4,5,6])
#df = pd.read_csv("datadir/GaugeData/EA_RainfallHourlyTotals/Eccup_063518_RainHourly_130886_021120.csv", 
#                       skiprows = 20, usecols = [0,1,2,3,4,5,6])
#df = pd.read_csv("datadir/GaugeData/EA_RainfallHourlyTotals/FarnleyHall_076204_HourlyRain_101287_041120.csv", 
#                        skiprows = 20, usecols = [0,1,2,3,4,5,6])
df = pd.read_csv("datadir/GaugeData/EA_RainfallHourlyTotals/HeadingleyLogger_076413_HourlyRain_250196_031120.csv", 
                        skiprows = 20, usecols = [0,1,2,3,4,5,6])
df = pd.read_csv('datadir/GaugeData/EA_RainfallHourlyTotals/Heckmondwike_079621_HourlyRain_070685_031120.csv', 
                       skiprows = 20, usecols = [0,1,2,3,4,5,6])

# Replace rows with '---' for value with NA
df['Value[mm]'] = df['Value[mm]'].replace('---', np.nan, regex=True)
# Set column type to float
df['Value[mm]'] = df['Value[mm]'].astype(float)

# Find NA vlaues
nas = df[df['Value[mm]'].isnull()]

# FInd number of na values
len(nas)
# Find proportion which are nas
na_prop = round((len(nas)/len(df)) *100,2)

# Add column with the season
for index, row in nas.iterrows():
    date_time_str = row['Time stamp']
    date_time_obj = datetime.datetime.strptime(date_time_str, '%d/%m/%Y %H:%M:%S')
    if date_time_obj.month in (3,4,5):
                           nas.loc[index, 'season'] = 'mam'
    elif date_time_obj.month in (6,7,8):
                           nas.loc[index, 'season'] = 'jja'
    elif date_time_obj.month in (9,10,11):
                           nas.loc[index, 'season'] = 'son'                           
    elif date_time_obj.month in (12,1,2):
                           nas.loc[index, 'season'] = 'djf'  
                           
season_counts = pd.DataFrame(nas['season'].value_counts()   ) 
season_counts['Percentage data missing within this season'] = round((season_counts['season']/len(nas) ) *100,1)
