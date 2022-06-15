import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

os.chdir("C:/Users/gy17m2a/OneDrive - University of Leeds/PhD/DataAnalysis/FloodModelling/MeganModel/Calculated Layers")

# Create dictionary mapping method name to csv file containing values
methods = {'divide-time':"6hr_dt_u_uniquevaluesreport.csv",
           'max-spread': "6hr_ms_u_uniquevaluesreport.csv",
           'single-peak': "6hr_sp_u_uniquevaluesreport.csv",
           "subpeak-timing": "6hr_sp-t_u_uniquevaluesreport.csv"}

counts_df = pd.DataFrame()
proportions_df = pd.DataFrame()

# Loop through methods and populate dataframes
for method_name, file_location in methods.items():
    # Read in file
    method_file = pd.read_csv(file_location, encoding = 'unicode_escape')
    # Cut by depth bins
    method_file['depth_range']= pd.cut(method_file.value, bins=[0,0.15,0.30,0.60, 0.9, 1.2,99], right=False)
    depth_groups = method_file.groupby(['depth_range']).sum()
    depth_groups = depth_groups.reset_index()
    # Find the sum
    total_n_cells = depth_groups['count'].sum()
    # Find the number of cells in each group as a proportion of the total
    depth_groups['Proportion'] = round((depth_groups['count']/total_n_cells) *100,1)
    # Add values to dataframes
    counts_df[method_name] = depth_groups['count']
    proportions_df[method_name] = depth_groups['Proportion']

counts_df.reset_index(inplace=True)
counts_df['index'] = ['0-0.15m', '0.15-0.3m', '0.3-0.6m', '0.6-0.9m', '0.9-1.2m', '1.2m+']
proportions_df.reset_index(inplace=True)
proportions_df['index'] = ['0-0.15m', '0.15-0.3m', '0.3-0.6m', '0.6-0.9m', '0.9-1.2m', '1.2m+']

# Set colors for plots
colors = ['black', 'lightslategrey', 'darkslategrey', 'darkgreen']

# plot count bar chart
counts_df.plot(x='index',kind='bar', stacked=False, width=0.8, legend = True, color = colors)
plt.xticks(rotation=30)
plt.xlabel('Flood depth')
plt.ylabel('Number of cells')

# plot proportions bar chart
proportions_df.plot(x='index', kind='bar', stacked=False, width=0.8, legend = True, color = colors)
plt.xticks(rotation=30)
plt.xlabel('Flood depth')
plt.ylabel('Proportion of cells')

# Create dataframe with just totals 
totals_df = counts_df.append(counts_df.sum(numeric_only=True), ignore_index=True)
totals_df = totals_df.iloc[[6]]
totals_df.drop(columns = 'index', inplace = True)

# PLot
y_pos = np.arange(len(methods.keys()))

# Create bars
plt.bar(y_pos, totals_df.iloc[[0]].values.tolist()[0], color=colors,
        width = 0.9)
# Create names on the x-axis
plt.xticks(y_pos, methods.keys())
# plt.xlabel('Method')
plt.ylabel('Number of flooded cells')

#########################
((totals_df['subpeak-timing'] - totals_df['single-peak'])/totals_df['subpeak-timing'])*100

########################
method_file = pd.read_csv("6hr_ms_u_uniquevaluesreport_nopreprocessing.csv", encoding = 'unicode_escape')

#########################
# Worst case
#########################
worst_case = pd.read_csv("6hr_worstcase.csv", encoding = 'unicode_escape')
worst_case2 = pd.read_csv("6hr_worstcase_method2.csv", encoding = 'unicode_escape')


# Create bars
plt.bar(np.arange(len(worst_case2)), worst_case2['count'], color=colors,
        width = 0.9)
# Create names on the x-axis
plt.xticks(y_pos, methods.keys())
# plt.xlabel('Method')
plt.ylabel("Number of cells")




