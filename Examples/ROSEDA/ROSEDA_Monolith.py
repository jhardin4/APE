'''
This file is an example of how to interact with APE as a single-process
application.
'''

import Core
import Procedures
from AppTemplates import ROSEDA_RoboDaddyMonolith as AppBuilder
import json
import winsound #only works in windows
from Ros3daTPGen import Make_TPGen_Data
import numpy as np

MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyApparatus.executor = MyExecutor

materials = [{'test_material': 'C'}]
# These are other tools that can be added in. Comment out the ones not used.
tools = []
tools.append({'name': 'TProbe', 'axis': 'D', 'type': 'Panasonic_HGS_A3200'})
tools.append({'name': 'camera', 'axis': 'D', 'type': 'IDS_ueye'})
AppBuilder(MyApparatus, materials, tools, prime='TProbe')

# Defining the materials. This can come from an existing file but here we are
# creating a new one.

# Briefly setting up components
HEMA_base = Core.material()
DD_base = Core.material()
FS_base = Core.material()

HEMA_base['names'] = ['HEMA', 'Glycol methacrylate', 'SA#128635']
DD_base['names'] = ['Di-HEMA', 'Diurethane Dimethacrylate', 'SA#436909']
FS_base['names'] = ['Fumed Silica', 'Cab-o-sil TS-720']
samplename = "HDS2_ink20"

# Setting up in for this run
HDS2_ink20 = Core.material()
HDS2_ink20.add_comp(DD_base, mass_perc=95, use_name='Di-HEMA')
HDS2_ink20.add_comp(HEMA_base, mass_perc=0, use_name='HEMA')
HDS2_ink20.add_comp(FS_base, mass_perc=5, use_name='Fumed Silica')
HDS2_ink20.save('Materials//{}.json'.format(samplename))

MyApparatus.createAppEntry(['information','ProcedureData','SampleRepeat_Start','samplename'])
MyApparatus.setValue(['information','ProcedureData','SampleRepeat_Start','samplename'], samplename)

# Define the rest of the apparatus
mat0 = list(materials[0])[0]
MyApparatus.addMaterial(mat0, 'Materials//{}.json'.format(samplename))
MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
MyApparatus['devices']['n' + mat0]['trace_height'] = 0.6
MyApparatus['devices']['n' + mat0]['trace_width'] = 0.6
MyApparatus['devices']['pump0']['descriptors'].append(mat0)
MyApparatus['devices']['gantry']['default']['speed'] = 20 # change the slide default from 40 to 20
MyApparatus['devices']['gantry']['n' + mat0]['speed'] = 2 # Calibration is on so this is overwritten
MyApparatus['devices']['pump0']['pumpon_time'] = 1.0  # Time from pump on to motion, if calibration is on so this is overwritten
MyApparatus['devices']['pump0']['mid_time'] = 0.0  # time from signal sent to motion initiation
MyApparatus['devices']['pump0']['pumpoff_time'] = 1.0  # time from end-arrival to turn off pump
MyApparatus['devices']['pump0']['pumpres_time'] = 0.0
MyApparatus['devices']['pump0']['pressure'] = 14.0
MyApparatus['devices']['pump0']['vacuum'] = 0
MyApparatus['devices']['pump0']['COM'] = 2

# Connect to all the devices in the setup
MyApparatus.Connect_All(simulation=False)
# Renaming some elements for the variable explorer
information = MyApparatus['information']

# Setup toolpath generation and run a default
GenTP = Procedures.Toolpath_Generate(MyApparatus, MyExecutor)
GenTP.setMaterial(mat0)
GenTP.setGenerator('XlineTPGen')
GenTP.setParameters()  # Creates the parameter structure for TPGen
TP_gen = MyApparatus['information']['ProcedureData']['Toolpath_Generate']

# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
AlignPrinter = Procedures.User_RoboDaddy_Alignments_Align(MyApparatus, MyExecutor)
CalInk = Procedures.User_InkCal_Calibrate(MyApparatus, MyExecutor)
startUp = Procedures.User_StartUp(MyApparatus, MyExecutor)
TraySetup = Procedures.SampleTray_XY_Setup(MyApparatus, MyExecutor)
TrayRun = Procedures.SampleRepeat_Start(MyApparatus, MyExecutor)

class Sample(Core.Procedure):
    def Prepare(self):
        self.name='Sample'      
        self.ProbeMeasure = Procedures.Touch_Probe_A3200_MeasureGrid(MyApparatus,MyExecutor)
        self.ProbeCorrect = Procedures.Touch_Probe_A3200_EnableCalibration(MyApparatus,MyExecutor)
        self.ProbeStopCorrect = Procedures.Touch_Probe_A3200_DisableCalibration(MyApparatus,MyExecutor)
        self.Camera = Procedures.Camera_Capture_ImageXY(MyApparatus,MyExecutor)
        self.Cleaner = Procedures.Aerotech_A3200_AirClean(MyApparatus,MyExecutor)
        self.Pause = Procedures.Data_User_Input_Options(MyApparatus, MyExecutor)
        self.testMaterial = Procedures.ROSEDA_TestMaterial(MyApparatus, MyExecutor)
        self.rparameters = Make_TPGen_Data(mat0)

    def Plan(self):
        samplename = MyApparatus.getValue(['information','ProcedureData','SampleRepeat_Start','samplename'])
        self.ProbeMeasure.Do({'start_point':{'X':4,'Y':4},'x_length':67,'y_length':42,'x_count':4,'y_count':3})
        diff = np.max(MyApparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'result']))-np.min(MyApparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'result']))
        while np.abs(diff) > 100:
            # If diff is very large, glass slide may be positioned incorrectly.
            self.Pause.Do({'message':'Large diff accross slide: {}, fix and continue?'.format(),'options':['y'],'default':'y'}) #Note: Doesn't currently do anything with response
            self.ProbeMeasure.Do({'start_point':{'X':4,'Y':4},'x_length':67,'y_length':42,'x_count':4,'y_count':3})
            diff = np.max(MyApparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'result']))-np.min(MyApparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'result']))
        self.ProbeCorrect.Do({'file':'Data\\CalTables\\'+samplename+'.cal','nozzlename': 'n' + mat0})
        #self.testMaterial.Do({'material':mat0, 'parameters':self.rparameters})
        self.Camera.Do({'point':{'X':3*25/2,'Y':2*25/2},'file':'Data\\Pictures\\'+samplename+'.png','camera_name':'camera'}) 
        self.ProbeStopCorrect.Do({})
        #self.Cleaner.Do({'nozzlename':'n' + mat0,'depth':0,'delay':1})
        #winsound.Beep(1000, 5000)
        #self.Pause.Do({'message':'Ready to continue?','options':['y'],'default':'y'}) #Note: Doesn't currently do anything with response

# Do the experiment
#startUp.Do({'filename': 'start_up.json'})
AlignPrinter.Do({'primenoz': 'TProbe', 'chatty':False})
TraySetup.Do({'trayname': 'test_samples', 'samplename': 'sample', 'xspacing': 0, 'xsamples': 1, 'yspacing': 0, 'ysamples': 2})
TrayRun.requirements['tray']['address'] = ['information', 'ProcedureData', 'SampleTray_XY_Setup', 'trays', 'test_samples']
TrayRun.Do({'procedure': Sample(MyApparatus, MyExecutor), 'start_count':2})

MyApparatus.Disconnect_All()

with open(MyApparatus.proclog_address) as p_file:
    proclog = json.load(p_file)
