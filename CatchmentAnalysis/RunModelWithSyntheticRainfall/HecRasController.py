from win32com.client import Dispatch
import rascontrol
import inspect


# Initiate the ras controller class
hec = Dispatch("RAS610.HECRASController") 
RASProject= "Y:\PhD\FloodModelling\MeganModel_v3\DissModel.prj"
# Open ras file
hec.Project_Open(RASProject) 
hec.Plan_SetCurrent ('6h_max-spread')
hec.Project_Save()
hec.Project_Close()
hec.QuitRAS()
hec.QuitRAS()
hec.QuitRAS()
hec.QuitRAS()
hec.QuitRAS()
hec.QuitRAS()



rc = rascontrol.RasController(version='610')
rc.open_project('Y:\PhD\FloodModelling\MeganModel_v3\DissModel.prj')
print(rc.get_current_plan())
rc.run_current_plan()
rc.get_plans()

 



# hec.ShowRas() # show HEC-RAS window

# # hec.Compute_HideComputationWindow
# # hec.Compute_ShowComputationWindow

# for method in ['6h_single-peak', '6h_divide-time', '6h_subpeak-timing', '6h_max-spread']:
#     print(method)
#     hec.Plan_SetCurrent (method)
#     print(hec.CurrentPlanFile())
    
#     # Runs HEC-RAS for current plan
#     hec.Compute_CurrentPlan(None,None)
#     hec.Project_Save
    
# hec.Project_Close()
# hec.QuitRas()
# del(hec)


import pyHMT2D
import inspect

# Create a HEC-RAS model instance
my_hec_ras_model = pyHMT2D.RAS_2D.HEC_RAS_Model(version="6.1.0", faceless=False)

# Initialize the HEC-RAS model
my_hec_ras_model.init_model()

# Open a HEC-RAS project
my_hec_ras_model.open_project("Y:\PhD\FloodModelling\MeganModel_v3\DissModel.prj",
                             "Y:\PhD\FloodModelling\MeganModel_v3\ResampledTerrain.tif")

# Set the plan file
my_hec_ras_model.set_current_plan('6h_divide-time')
my_hec_ras_model.get_current_planFile()

# Run the HEC-RAS model's current project
my_hec_ras_model.run_model()

# Close the HEC-RAS project
my_hec_ras_model.close_project()

# Quit HEC-RAS
my_hec_ras_model.exit_model()






inspect.getmembers(my_hec_ras_model, predicate=inspect.ismethod)
