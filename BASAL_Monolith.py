'''
This file is an example of how to interact with APE as a single-process
application.
'''
import glob
from datetime import datetime
import os
import Core
import Procedures
from AppTemplates.FlexPrinterMonolith import FlexPrinterMonolith as AppBuilder
import UI.run_ape as run_ape
import UI.start_ape as start_ape


sa = start_ape.startape ( )
if sa.checksfile ( ) == 'ready 1':
    pass
elif sa.checksfile ( ) == 'ready 0':
    sa.installape ( )
MyApparatus = Core.Apparatus()
MyExecutor = Core.Executor()
MyApparatus.executor = MyExecutor
MyExecutor.debug = True

materials = [{'test_material': 'ZZ1'}]
# These are other tools that can be added in. Comment out the ones not used.
tools = []
# tools.append({'name': 'TProbe', 'axis': 'ZZ2', 'type': 'Keyence_GT2_A3200'})
# tools.append({'name': 'camera', 'axis': 'ZZ4', 'type': 'IDS_ueye'})
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
GenTP.setGenerator('UI_Generator')
GenTP.setParameters()  # Creates the parameter structure for TPGen
TP_gen = MyApparatus['information']['ProcedureData']['Toolpath_Generate']
TP_gen['parameters']['tiph'] = 4
TP_gen['parameters']['length'] = 5

# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
AlignPrinter = Procedures.User_FlexPrinter_Alignments_Align(MyApparatus, MyExecutor)
CalInk = Procedures.User_InkCal_Calibrate(MyApparatus, MyExecutor)
PrintTP = Procedures.Toolpath_Print(MyApparatus, MyExecutor)
TraySetup = Procedures.SampleTray_XY_Setup(MyApparatus, MyExecutor)
TrayRun = Procedures.SampleTray_Start(MyApparatus, MyExecutor)
Planner = Procedures.Planner_Combinatorial(MyApparatus, MyExecutor)



class Sample(Core.Procedure):
    def Prepare(self):
        self.name = 'Sample'
        self.GenTP = Procedures.Toolpath_Generate(self.apparatus, self.executor)
        self.PrintTP = Procedures.Toolpath_Print(self.apparatus, self.executor)
        self.Planner = Procedures.Planner_Combinatorial(self.apparatus, self.executor)

    def Plan(self):
        space = {}
        space['tiph'] = [0.1 * n for n in range(5)]
        space['Trace_height'] = [0.15 * m for m in range(5)]
        AppAdds = {}
        AppAdds['tiph'] = ['information', 'ProcedureData', 'Toolpath_Generate', 'parameters', 'tiph']
        AppAdds['Trace_height'] = ['devices', 'n' + mat0, 'trace_height']
        priority = ['Trace_height', 'tiph']
        self.Planner.Do({'space': space, 'Apparatus_Addresses': AppAdds, 'file': 'run.json', 'priority': priority})
        if not self.Planner.Done:
            if self.apparatus.simulation:
                import time
                time.sleep(1)
                print('Generating toolpath')
                self.GenTP.requirements['generator']['address'] = ['information', 'ProcedureData', 'Toolpath_Generate', 'generator']
                self.GenTP.Do()
                print('Printing toolpath')
                self.PrintTP.requirements['toolpath']['address'] = ['information', 'ProcedureData', 'Toolpath_Generate', 'toolpath']
                self.PrintTP.Do()
                

# Do the experiment
AlignPrinter.Do({'primenoz': 'n' + mat0})
CalInk.Do({'material': mat0})
TraySetup.Do({'trayname': 'test_samples', 'samplename': 'sample', 'xspacing': 14, 'xsamples': 1, 'yspacing': 15, 'ysamples': 1})
TrayRun.requirements['tray']['address'] = ['information', 'ProcedureData', 'SampleTray_XY_Setup', 'trays', 'test_samples']
TrayRun.Do({'procedure': Sample(MyApparatus, MyExecutor)})
MyApparatus.Disconnect_All()
toolpath = TP_gen['toolpath'][0]
#toolpath_parsed = tpt.parse_endofmotion(toolpath, 1E-12)
"""
#now the experiment has ended... time for feedback
import glob, os
from datetime import datetime

if os.name == 'posix':
    globpath = os.path.expanduser('~')+'/Print_With_APE/'+'*.txt'
elif os.name == 'nt':
    path = os.path.expanduser('~')+'\Print_With_APE\ '
    path = path.rstrip(path[-1])
    globpath = path+'*.txt'
    

archive_format = datetime.now().strftime(globpath)
archives = glob.glob(archive_format)

if len(archives) > 0:
    # The files should come sorted, return the last one in the list.
    datafile = archives[-1]
else:
    # No files were matched
    pass
print (datafile)
readdatafile = open(datafile, 'r')
newfile = 'cmd'+readdatafile.readline()
newfile = newfile.rstrip(newfile[-1])
readdatafile.close()
print(newfile)


if os.name == 'posix':
    path = os.path.expanduser('~')+'/Print_With_APE/'+newfile+'.txt'
elif os.name == 'nt':
    path = os.path.expanduser('~')+'\Print_With_APE\ '
    path = path.rstrip(path[-1])
    path = path+newfile+'.txt'
else:
    pass
if os.path.exists(path):
    f = open(path, 'r')
    itteration = f.readlines()[3]
    f.close()
    print(itteration)
    os.remove(path)
else:
    itteration = -1
itteration = int(itteration)
f = open(path, 'a')
f.write('continue: \n')
if itteration > 3:
    f.write('0 \n')
else:
    f.write('2 \n')
f.write('itteration: \n')
if itteration == -1:
    itterationwrite = '0 \n'
else:
    itteration = itteration + 1
    itterationwrite = str(itteration) + ' \n'
f.write(itterationwrite)
f.write('duplicate_move_x: \n')
if itteration > 0:
    editwrite = str(itteration * 5 + 5) + ' \n'
    f.write(editwrite)
else:
    f.write('5 \n')
#f.write('scale_u \n')
#f.write('2 \n')
f.write('prop_edit_+z_z: \n')
if itteration > 0:
    editwrite = str(itteration * 0.1 + 0.1) + ' \n'
    f.write(editwrite)
else:
    f.write('0.1 \n')
f.write('select_new_object: \n')
if itteration > 0:
    editwrite = 'Cube' + str(.001 * itteration) + ' \n' #find a way to derive cube instead of being explicit
else:
    editwrite = 'Cube' + ' \n' #find a way to derive cube instead of being explicit
f.write(editwrite)
f.write('duplicate_move_x: \n')
if itteration > 0:
    editwrite = str(itteration * 5 + 5) + ' \n'
    f.write(editwrite)
else:
    f.write('5 \n')
f.write('boolean_subtract: \n')
readdatafile = open(datafile, 'r')
name = readdatafile.readline()
readdatafile.close()
if itteration > 0:
    name = name.rstrip(name[-1]) + str(.001 * itteration + .001) + ' \n'
else:
    name = name.rstrip(name[-1]) + '.001 \n'
f.write(name)
f.close()
"""