'''
This file is an example of how to interact with APE as a single-process
application.
'''

import Core
import Procedures
from AppTemplates import RoboDaddyMonolith as AppBuilder

MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyApparatus.executor = MyExecutor

materials = [{'test_material': 'A'}]
# These are other tools that can be added in. Comment out the ones not used.
tools = []
# tools.append({'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_GT2_A3200'})
tools.append({'name': 'camera', 'axis': 'B', 'type': 'IDS_ueye_3250CP2'})
AppBuilder(MyApparatus, materials, tools)

# Define the rest of the apparatus
mat0 = list(materials[0])[0]
MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
MyApparatus['devices']['n' + mat0]['trace_height'] = 0.6
MyApparatus['devices']['n' + mat0]['trace_width'] = 0.61
MyApparatus['devices']['pump0']['descriptors'].append(mat0)
MyApparatus['devices']['gantry']['default']['speed'] = 20 # change the slide default from 40 to 20
MyApparatus['devices']['gantry']['n' + mat0]['speed'] = 2 # Calibration is on so this is overwritten
MyApparatus['devices']['pump0']['pumpon_time'] = 1.0  # Time from pump on to motion, if calibration is on so this is overwritten
MyApparatus['devices']['pump0']['mid_time'] = 0.0  # time from signal sent to motion initiation
MyApparatus['devices']['pump0']['pumpoff_time'] = 1.0  # time from end-arrival to turn off pump
MyApparatus['devices']['pump0']['pumpres_time'] = 0.0
MyApparatus['devices']['pump0']['pressure'] = 10
MyApparatus['devices']['pump0']['vacuum'] = 0
MyApparatus['devices']['pump0']['COM'] = 4

# Connect to all the devices in the setup
MyApparatus.Connect_All(simulation=True)
# Renaming some elements for the variable explorer
information = MyApparatus['information']


# Setup information
MyApparatus['information']['materials'][mat0] = {'density': 1.92, 'details': 'Measured', 'calibrated': False}  # changed from density = 1.048
MyApparatus['information']['materials'][mat0]['do_speedcal'] = True
MyApparatus['information']['materials'][mat0]['do_pumpcal'] = False
MyApparatus['information']['ink calibration']['time'] = 60

# Setup toolpath generation and run a default
GenTP = Procedures.Toolpath_Generate(MyApparatus, MyExecutor)
GenTP.setMaterial(mat0)
GenTP.setGenerator('XlineTPGen')
GenTP.setParameters()  # Creates the parameter structure for TPGen
TP_gen = MyApparatus['information']['ProcedureData']['Toolpath_Generate']

# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
AlignPrinter = Procedures.User_FlexPrinter_Alignments_Align(MyApparatus, MyExecutor)
CalInk = Procedures.User_InkCal_Calibrate(MyApparatus, MyExecutor)
Camera = Procedures.Camera_Capture_ImageXY(MyApparatus,MyExecutor)
testMaterial = Procedures.ROSEDA_TestMaterial(MyApparatus, MyExecutor)

# Do the experiment
AlignPrinter.Do({'primenoz': 'n' + mat0})
CalInk.Do({'material': mat0})
from Ros3daTPGen import Make_TPGen_Data
rparameters = Make_TPGen_Data(mat0)
testMaterial.Do({'material':mat0, 'parameters':rparameters})
Camera.Do({'point':{'X':3*25/2,'Y':2*25/2},'file':'Samples\mono_test.png','camera_name':'camera'})
MyApparatus.Disconnect_All()
toolpath = TP_gen['toolpath'][0]
