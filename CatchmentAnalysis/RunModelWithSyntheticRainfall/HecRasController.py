from win32com.client import Dispatch
# Initiate the ras controller class
hec = Dispatch("RAS610.HECRASController") 
RASProject= "Y:\PhD\FloodModelling\Megans Model\DissModel.prj"
# Open ras file
hec.Project_Open(RASProject) 

hec.Compute_HideComputationWindow
hec.Compute_ShowComputationWindow

hec.Plan_SetCurrent ("6hr_dividetime")
# Runs HEC-RAS for current plan
hec.Compute_CurrentPlan(None,None)
hec.Project_Save
hec.Project_Close()
hec.QuitRas()
del(hec)
