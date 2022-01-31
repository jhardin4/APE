#Import APE bits
import Core
import Procedures
import json
#Import AppTemplate for Extrusion Calibration
from AppTemplates.GenericExtCal import ExtCal as AppBuilder

#Build Apparatus and executor
MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyApparatus.executor = MyExecutor
MyApparatus.run_name = 'Extrusion calibration'

#List materials as a dictionary with locations
materials = [{'test_material0': 'ZZ1'},{'test_material1': 'ZZ2'}]
#Build App from template
AppBuilder(MyApparatus, materials)

# Material setup 
# Repeat for each material 
SE1700_base = Core.material()
blue_pigment = Core.material()
white_pigment = Core.material()
ink = Core.material()
# Define attributes
SE1700_base.add_property('density', 1.1, 'g/cc') #needed for mass calculations
SE1700_base['names'] = ['SE1700', 'PDMS', 'silicone', 'base']
blue_pigment['names'] = ['silcpig', 'blue', 'silicone', 'pigment']
white_pigment['names'] = ['silcpig', 'white', 'silicone', 'pigment']
#100:1:1 ratio
ink.add_comp(SE1700_base, mass_perc=98.039216, use_name='base')
ink.add_comp(blue_pigment, mass_perc=0.98039216, use_name='pigment')
ink.add_comp(white_pigment, mass_perc=0.98039216, use_name='pigment')
ink.add_property('density', 1.1, 'g/cc') #needed for mass calculations
ink.save('Materials//ink.json')


# Define the rest of the apparatus 
mat0 = list(materials[0])[0]
MyApparatus.addMaterial(mat0, 'Materials//ink.json')

MyApparatus['devices']['n' + mat0]['descriptors'].append(mat0)
MyApparatus['devices']['n' + mat0]['trace_height'] = 0.840
MyApparatus['devices']['n' + mat0]['trace_width'] = 0.840
MyApparatus['devices']['extruder0']['type'] = 'Nordson_UltimusV'
MyApparatus['devices']['extruder0']['pumpres_time'] = 0.3
MyApparatus['devices']['extruder0']['descriptors'].append(mat0)
MyApparatus['devices']['extruder0']['pressure'] = 200
MyApparatus['devices']['extruder0']['vacuum']= 0
MyApparatus['devices']['extruder0']['COM'] = 13

ink1 = Core.material()
# Define attributes
#8:1:1 ratio
ink1.add_comp(SE1700_base, mass_perc=80, use_name='base')
ink1.add_comp(blue_pigment, mass_perc=10, use_name='pigment')
ink1.add_comp(white_pigment, mass_perc=10, use_name='pigment')
ink1.add_property('density', 1.1, 'g/cc') #needed for mass calculations
ink1.save('Materials//ink1.json')

mat1 = list(materials[1])[0]
MyApparatus.addMaterial(mat1, 'Materials//ink1.json')

MyApparatus['devices']['n' + mat1]['descriptors'].append(mat1)
MyApparatus['devices']['n' + mat1]['trace_height'] = 0.840
MyApparatus['devices']['n' + mat1]['trace_width'] = 0.840
MyApparatus['devices']['extruder1']['type'] = 'Nordson_UltimusV'
MyApparatus['devices']['extruder1']['pumpres_time'] = 0.3
MyApparatus['devices']['extruder1']['descriptors'].append(mat1)
MyApparatus['devices']['extruder1']['pressure'] = 222
MyApparatus['devices']['extruder1']['vacuum']= 0
MyApparatus['devices']['extruder1']['COM'] = 12

# Connect to all the devices in the setup
MyApparatus.Connect_All(simulation=True)

# Setup information
MyApparatus['information']['ink calibration']['time'] = 60
MyApparatus['information']['materials'][mat0]['do_speedcal'] = True
MyApparatus['information']['materials'][mat0]['do_pumpcal'] = True
MyApparatus['information']['materials'][mat1]['do_speedcal'] = True
MyApparatus['information']['materials'][mat1]['do_pumpcal'] = True
# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
CalInk = Procedures.User_InkCal_Calibrate_PO(MyApparatus, MyExecutor)
CalSpeed = Procedures.User_InkCal_Calculate_PO(MyApparatus, MyExecutor)

# Do the experiment
CalInk.Do({'material': mat0})
CalSpeed.Do({'material': mat0})
CalInk.Do({'material': mat1})
CalSpeed.Do({'material': mat1})


MyApparatus.Disconnect_All()

print('Ink0 ' + str(MyApparatus['devices']['ntest_material0']['speed']))

print('Ink1 ' + str(MyApparatus['devices']['ntest_material1']['speed']))