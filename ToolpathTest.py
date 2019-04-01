# APE framework.  Procedure may not be necessary
import Core
import Procedures

# Import the procedure sets that are needed

# Import other libraries
import FlexPrinterApparatus  # This is specific to the Flex Printer at AFRL
import XlineTPGen as TPGen  # Toolpath generator
import time

# Create apparatus and executor
MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyExecutor.debug = True  # Leave this as-is for now.

# ____FLexPrinterApparatus____#
# Set up a basic description of the system that is later used to create an
# apparatus specific to the Flex Printer at AFRL

materials = [{'TestMaterial': 'ZZ1'}]
# These are other tools that can be added in. Comment out the ones not used.
tools = []
# tools.append({'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_GT2_A3200'})
# tools.append({'name': 'camera', 'axis': 'ZZ4', 'type': 'IDS_ueye'})

FlexPrinterApparatus.Build_FlexPrinter(materials, tools, MyApparatus)
mat0 = [list(materials[n])[0] for n in range(len(materials))][0]
# Define the rest of the apparatus
MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
MyApparatus['devices']['n' + mat0]['trace_height'] = 0.1
MyApparatus['devices']['n' + mat0]['trace_width'] = 0.2
MyApparatus['devices']['aeropump0']['descriptors'].append(mat0)
MyApparatus['devices']['gantry']['default']['speed'] = 40
MyApparatus['devices']['gantry']['n' + mat0]['speed'] = 0.3  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['pumpon_time'] = 1  # Calibration is on so this is overwritten
MyApparatus['devices']['aeropump0']['mid_time'] = 1
MyApparatus['devices']['aeropump0']['pumpoff_time'] = 0
MyApparatus['devices']['aeropump0']['pumpres_time'] = 0.3
MyApparatus['devices']['aeropump0']['pressure'] = 155
MyApparatus['devices']['pump0']['COM'] = 9

MyApparatus['information']['materials'][mat0]['density'] = 1.84
MyApparatus['information']['toolpaths'] = {}
MyApparatus['information']['toolpaths']['generator'] = TPGen.GenerateToolpath
MyApparatus['information']['toolpaths']['parameters'] = TPGen.Make_TPGen_Data(mat0)
MyApparatus['information']['toolpaths']['toolpath'] = [0]
MyApparatus['information']['ink calibration']['time'] = 30

information = MyApparatus['information']
proclog = MyApparatus['proclog']

# Connect to all the devices in the setup
MyApparatus.Connect_All(MyExecutor, simulation=True)


gentp = Procedures.Toolpath_Generate(MyApparatus, MyExecutor)

gentp.Do()

MyApparatus.Disconnect_All()
