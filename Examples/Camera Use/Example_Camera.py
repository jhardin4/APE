'''
This file is an example of how to interact with APE as a single-process
application.
'''

import Core
import Procedures
from AppTemplates.FlexPrinterMonolith import FlexPrinterMonolith as AppBuilder

MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyApparatus.executor = MyExecutor

materials = [{'test_material': 'ZZ1'}]
# These are other tools that can be added in. Comment out the ones not used.
tools = []
# tools.append({'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_GT2_A3200'})
tools.append({'name': 'camera', 'axis': 'ZZ4', 'type': 'IDS_ueye'})
AppBuilder(MyApparatus, materials, tools)

# Define the rest of the apparatus
mat0 = list(materials[0])[0]
MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
MyApparatus['devices']['n' + mat0]['trace_height'] = 0.1
MyApparatus['devices']['n' + mat0]['trace_width'] = 0.3
MyApparatus['devices']['aeropump0']['descriptors'].append(mat0)
MyApparatus['devices']['gantry']['default']['speed'] = 20  # change the slide default from 40 to 20
MyApparatus['devices']['gantry']['n' + mat0]['speed'] = 20  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['pumpon_time'] = 0.0  # Time from pump on to motion, if calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['mid_time'] = .05  # time from signal sent to motion initiation
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0  # time from end-arrival to turn off pump
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.1
MyApparatus['devices']['aeropump0']['pressure'] = 550
MyApparatus['devices']['aeropump0']['vacuum'] = 0
MyApparatus['devices']['aeropump0']['COM'] = 7
# It is reccomended that this value be added into the apparatus to track how
# long the camera is given to stop vibrating after motion
MyApparatus['devices']['camera']['settle_time'] = 1


# Connect to all the devices in the setup
MyApparatus.Connect_All(simulation=True)
# Renaming some elements for the variable explorer
information = MyApparatus['information']
proclog = MyApparatus['proclog']

# Setup information
MyApparatus['information']['materials'][mat0] = {'density': 1.92, 'details': 'Measured', 'calibrated': False}  # changed from density = 1.048
MyApparatus['information']['materials'][mat0]['do_speedcal'] = True
MyApparatus['information']['materials'][mat0]['do_pumpcal'] = False
MyApparatus['information']['ink calibration']['time'] = 60

# Setup toolpath generation and run a default
GenTP = Procedures.Toolpath_Generate(MyApparatus, MyExecutor)
GenTP.setMaterial(mat0)
GenTP.setGenerator('TemplateTPGen')
GenTP.setParameters()  # Creates the parameter structure for TPGen
TP_gen = MyApparatus['information']['ProcedureData']['Toolpath_Generate']
TP_gen['parameters']['tiph'] = 4
TP_gen['parameters']['length'] = 5

# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
AlignPrinter = Procedures.User_FlexPrinter_Alignments_Align(MyApparatus, MyExecutor)
CalInk = Procedures.User_InkCal_Calibrate(MyApparatus, MyExecutor)
PrintTP = Procedures.Toolpath_Print(MyApparatus, MyExecutor)
Planner = Procedures.Planner_Combinatorial(MyApparatus, MyExecutor)
GenTP = Procedures.Toolpath_Generate(MyApparatus, MyExecutor)
SnapPic = Procedures.Camera_Capture_Image(MyApparatus, MyExecutor)
SnapPicXY = Procedures.Camera_Capture_ImageXY(MyApparatus, MyExecutor)


# Do the experiment
AlignPrinter.Do({'primenoz': 'n' + mat0})
CalInk.Do({'material': mat0})
print('Generating toolpath')
GenTP.Do()
# Let's assume that you just want to take a picture where ever the camera  is
# This procedure needs a time to wait after motion for the camer to settle
# and the name of the camera (it doesn't autofind the camera because there
# could easily be several)
SnapPic.Do({'file':'Data//image.png', 'camera_name':'camera'})
print('Printing toolpath')
PrintTP.Do()
# Now, let's take a picture at the center of the what we printed.  We can use
# information from the toolpath generator to determine the center.
mid_point = {'X':TP_gen['parameters']['length']/2, 'Y':0}
SnapPicXY.Do({'point':mid_point, 'file':'Data//image.png', 'camera_name':'camera'})
MyApparatus.Disconnect_All()
toolpath = TP_gen['toolpath'][0]
#toolpath_parsed = tpt.parse_endofmotion(toolpath, 1E-12)
