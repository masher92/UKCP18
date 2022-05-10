import os
import pandas as pd
os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/Scripts/UKCP18/CatchmentAnalysis/CreateSyntheticRainfallEvents")

pre_loss_removal = pd.read_csv("DataAndFigs/SyntheticEvents_preLossRemoval/6h/6h_divide-time.csv")

post_loss_removal_urban = pd.read_csv("DataAndFigs/SyntheticEvents_postLossRemoval/6h/6h_divide-time_urban.csv")
post_loss_removal_rural = pd.read_csv("DataAndFigs/SyntheticEvents_postLossRemoval/6h/6h_divide-time_rural.csv")