import pandas as pd 

def create_unsteady_flow_file (precip_fp, output_fp):
    
    with open('../../../FloodModelling/MeganModel_v3/template_unsteadyflowfile.txt') as f:
        contents = f.read()
    
    ### Read in precipitation values which we want to insert into the string
    precip = pd.read_csv(precip_fp)
    precip = precip['Total net rain mm (Observed rainfall - 01/08/2022) - urbanised model']
    precip= precip[0:361]
        
    ### Read in the precipitation values from the plan to a list
    start=contents.find('Precipitation Hydrograph= 361')+len('Precipitation Hydrograph= 361')     
    end=contents.find('DSS Path') 
    precip_values = contents[start:end]
    
    ### Define a string which contains the precipitation values, with the numbers replaced with placeholders
    new_precip_values = precip_values#.copy()
    # loop for all characters
    for ele in precip_values:
        if ele.isdigit():
            new_precip_values = new_precip_values.replace(ele, '{}')
        
    ### Where number is more than one digit long it puts a place holder for each digit, replace with one placeholder per number
    # new_precip_values = new_precip_values.replace('.{}{}{}', '{}')
    # new_precip_values = new_precip_values.replace('.{}{}', '{}')
    
    ### Fill in our new precipitation values into the string
    new_precip_values = new_precip_values.format(*precip)
    
    ### Add the new precipitation values to the whole string
    newcontents = contents.replace(precip_values,new_precip_values)
    
    ### Save to text file
    with open(output_fp, 'w') as f:
        f.write(contents)


def create_plan (plan_title, short_identifier, unsteadyflow_file, output_fp):
    # Read file
    with open('../../../FloodModelling/MeganModel_v3/template_plan.txt') as f:
        contents = f.read()
    
    # Replace the variable with the correct values
    contents = contents.replace("plan_title", plan_title)
    contents = contents.replace("short_identifier", short_identifier)
    contents = contents.replace("unsteadyflow_file", unsteadyflow_file)
    
    ### Save to text file
    with open(output_fp, 'w') as f:
        f.write(contents)
        
        
short_ids = ['6h_sp', '6h_dt', '6h_spt', '6h_ms', 'c1','c2','c3','c4', 'c5', 'c6','c7','c8','c9','c10', 'c11', 'c12',
             'c13','c14','c15',]   
methods = ['6h_single-peak', '6h_divide-time', '6h_subpeak-timing', '6h_max-spread', '1', '2', '3', '4', '5',
           '6', '7', '8', '9','10', '11', '12', '13', '14', '15']  

for method_number, method in enumerate(methods, start=1):
    print(method)
    if '6h' in method:
        print("no")
        # precip_file = "../CreateSyntheticRainfallEvents/MultiplePeaks/PostLossRemoval/6h/{}_urban.csv".format(method)
    else:
        precip_file = "../CreateSyntheticRainfallEvents/RobertoProfiles/PostLossRemoval/6hr_100yrRP/cluster{}_urban_summer.csv".format(method)
    
        unsteadyflow_file = '../../../FloodModelling/MeganModel_v3/DissModel.u0{}'.format(method_number)
        output_fp = '../../../FloodModelling/MeganModel_v3/DissModel.p0{}'.format(method_number)
        create_unsteady_flow_file(precip_file, unsteadyflow_file)
        create_plan(method, short_ids[method_number-1], unsteadyflow_file,output_fp )
  
    
    

