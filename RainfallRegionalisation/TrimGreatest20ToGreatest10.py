import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

sys.path.insert(0, root_fp + 'Scripts/UKCP18/SpatialAnalyses')
from Spatial_plotting_functions import *

region = 'leeds-at-centre'
ems = ['01', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '15']


# Loop through ensemble members
# Read in greatest twenty file
# Trim to contain just greatest ten values for each year
# Save to file
for em in ems:
     print(em)
     # Load in the data
     input_filename = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/Greatest_twenty/em_{}.csv'.format(region, em)
     greatest_twenty = pd.read_csv(input_filename)
     # Filter out just the greatest ten
     greatest_ten = greatest_twenty.loc[:,~greatest_twenty.columns.str.contains('_10|_11|_12|_13|_14|_15|_16|_17|_18|_19')]         
     # Save to file
     output_ddir = 'C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Outputs/HiClimR_inputdata/{}/Greatest_ten/'.format(region)
     if not os.path.isdir(output_ddir):
        os.makedirs(output_ddir)
     greatest_ten.to_csv(output_ddir + "em_{}.csv".format(em))
     
     