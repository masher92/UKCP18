import os
import pandas as pd
import matplotlib.pyplot  as plt

#############################################
root_fp = "/nfs/a319/gy17m2a/"
#root_fp = "C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/"
os.chdir(root_fp)

#####################
# Read in data
#####################
stat = 'Wethours/wet_prop'
region = 'leeds-at-centre'
em = '01'

wet_prop = pd.read_csv("Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Wethours/ValuesOver20Years/wet_prop/em_{}.csv".format(em))

stats = ["ValuesOver20Years/Mean", "ValuesOver20Years/95th Percentile", "ValuesOver20Years/97th Percentile",
         "ValuesOver20Years/99th Percentile", "ValuesOver20Years/99.5th Percentile", "ValuesOver20Years/99.75th Percentile",
         "ValuesOver20Years/99.9th Percentile",  "ValuesOver20Years/Max"]
for stat in stats:
    stat_csv = pd.read_csv("Outputs/RainfallRegionalisation/HiClimR_inputdata/leeds-at-centre/Allhours/{}/em_{}.csv".format(stat,em))
    stat_name = stsat.split('/')[1] 
    plt.scatter(stat_csv.iloc[:,2], wet_prop['wet_prop'], s=1.5)
    plt.ylabel('Proportion of wet hours')
    plt.xlabel(stat_name + ' hourly precipitation')
    plt.savefig("Scripts/UKCP18/RainfallRegionalisation/CalculateStatsForClustering/Figs/em{}_{}VsWetHourProp.png".format(em, stat_name))
    plt.show()
