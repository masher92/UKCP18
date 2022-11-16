import pandas as pd 
import matplotlib.pyplot as plt
from math import log10, floor
import re

# def round_sig(x, sig=5):
#     if x == 0:
#         return 0
#     elif x <0.1:
#         x = round(x,sig)
#         if str(x)[::-1].find('.') != 5:
#         return round(x,sig)
#     else: 
#         return round(x, sig-int(floor(log10(abs(x))))-1)

def round_sig(x, sig=7):
    if x == 0:
        return 0
    elif x <0.1:
        return round(x,sig)
    else: 
        return round(x, sig-int(floor(log10(abs(x))))-1)

def format_number(x):
    if x == 0:
        return '0       '
    else:
        str_x = format(x, '.7f')
        str_x = str_x.lstrip('0')
        if x>1:
            str_x = ' ' + str_x
        return str_x

def create_unsteady_flow_file (precip_fp, output_fp, flow_title):
    
    with open('../../../FloodModelling/MeganModel_v3/template_unsteadyflowfile.txt') as f:
        contents = f.read()
    
    ### Read in precipitation values which we want to insert into the string
    precip = pd.read_csv(precip_fp)
    precip = precip['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model']
    precip= precip[0:360]
    precip = precip.apply(round_sig)
    precip = precip.apply(format_number)
    precip = precip.str.cat(sep='')
    precip = re.sub("(.{80})", "\\1\n", precip, 0, re.DOTALL)
    
    # Replace flow title
    if '6h' not in flow_title:
        flow_title = '6h_Cluster{}'.format(flow_title)
    contents = contents.replace("flow_title", flow_title)
    
    ### Read in the precipitation values from the plan to a list
    contents = contents.replace('precip_values', precip)
              
    ### Save to text file
    with open(output_fp, 'w') as f:
        f.write(contents)

def create_plan (plan_title, short_identifier, unsteadyflow_file, output_fp):
    # Read file
    with open('../../../FloodModelling/MeganModel_v3/template_plan.txt') as f:
        contents = f.read()
    if '6h' not in plan_title:
        plan_title = '6h_Cluster{}'.format(plan_title)
    
    # Replace the variable with the correct values
    contents = contents.replace("plan_title", plan_title)
    contents = contents.replace("short_identifier", short_identifier)
    contents = contents.replace("unsteadyflow_file", unsteadyflow_file)
    
    ### Save to text file
    with open(output_fp, 'w') as f:
        f.write(contents)
        
        
short_ids = ['6h_sp', '6h_dt', '6h_spt', '6h_ms', '6h_c1','6h_c2','6h_c3','6h_c4', '6h_c5', '6h_c6','6h_c7',
             '6h_c8','6h_c9','6h_c10', '6h_c11', '6h_c12','6h_c13','6h_c14','6h_c15',]   
methods = ['6h_single-peak', '6h_divide-time', '6h_subpeak-timing', '6h_max-spread', '1', '2', '3', '4', '5',
           '6', '7', '8', '9','10', '11', '12', '13', '14', '15']  

for method_number, method in enumerate(methods, start=1):
    # Read the precipitation data for this method
    print(method)
    if '6h' in method:
        precip_file = "../CreateSyntheticRainfallEvents/MultiplePeaks/PostLossRemoval/6h/{}_urban.csv".format(method)
    else:
        precip_file = "../CreateSyntheticRainfallEvents/RobertoProfiles/PostLossRemoval/6hr_100yrRP/cluster{}_urban_summer.csv".format(method)
    
    # Define filepaths to save the unsteady flow file and plan file to
    unsteadyflow_output_fp = '../../../FloodModelling/MeganModel_v3/DissModel.u0{}'.format(method_number)
    plan_output_fp = '../../../FloodModelling/MeganModel_v3/DissModel.p0{}'.format(method_number)
        
    # Define the unsteady flow file number (used as an input to the plan)
    unsteadyflow_file_number = 'u0{}'.format(method_number)

    # Create unsteady flow and then create the plan
    create_unsteady_flow_file(precip_file, unsteadyflow_output_fp, method)
    create_plan(method, short_ids[method_number-1], unsteadyflow_output_fp, plan_output_fp)
        
    
# with open('../../../FloodModelling/MeganModel_v3/template_unsteadyflowfile.txt') as f:
#     contents = f.read()

# ### Read in precipitation values which we want to insert into the string
# precip = pd.read_csv("../CreateSyntheticRainfallEvents/RobertoProfiles/PostLossRemoval/6hr_100yrRP/cluster{}_urban_summer.csv".format(method))
# precip = precip['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model']
# precip= precip[0:360]

# # Replace flow title
# if '6h' not in flow_title:
#     flow_title = '6h_Cluster{}'.format(flow_title)
# contents = contents.replace("flow_title", flow_title)

# ### Read in the precipitation values from the plan to a list
# start=contents.find('Precipitation Hydrograph= 360')+len('Precipitation Hydrograph= 360')     
# end=contents.find('DSS Path') 
# precip_values = contents[start:end]

# ### Define a string which contains the precipitation values, with the numbers replaced with placeholders
# new_precip_values = precip_values#.copy()
# # loop for all characters
# for ele in precip_values:
#     if ele.isdigit():
#         new_precip_values = new_precip_values.replace(ele, '{}')

#     ### Fill in our new precipitation values into the string
#     new_precip_values = new_precip_values.format(*precip)
    
#     ### Add the new precipitation values to the whole string
#     newcontents = contents.replace(precip_values,new_precip_values)
    
#     ### Save to text file
#     with open(output_fp, 'w') as f:
#         f.write(newcontents)

