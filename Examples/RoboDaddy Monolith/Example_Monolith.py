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
GenTP.setGenerator('Ros3daTPGen')
GenTP.setParameters()  # Creates the parameter structure for TPGen
TP_gen = MyApparatus['information']['ProcedureData']['Toolpath_Generate']

# Create instances of the procedures that will be used
# Procedures that will almost always be used at this level
AlignPrinter = Procedures.User_FlexPrinter_Alignments_Align(MyApparatus, MyExecutor)
CalInk = Procedures.User_InkCal_Calibrate(MyApparatus, MyExecutor)
PrintTP = Procedures.Toolpath_Print(MyApparatus, MyExecutor)
TraySetup = Procedures.SampleTray_XY_Setup(MyApparatus, MyExecutor)
TrayRun = Procedures.SampleTray_Start(MyApparatus, MyExecutor)
Planner = Procedures.Planner_Combinatorial(MyApparatus, MyExecutor)
Camera = Procedures.Camera_Capture_ImageXY(MyApparatus,MyExecutor)

class Sample(Core.Procedure):
    def Prepare(self):
        self.name = 'Sample'
        self.GenTP = Procedures.Toolpath_Generate(self.apparatus, self.executor)
        self.PrintTP = Procedures.Toolpath_Print(self.apparatus, self.executor)
        self.Planner = Procedures.Planner_Combinatorial(self.apparatus, self.executor)
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.requirements['material'] = {
            'source': 'direct',
            'address': '',
            'value': '',
            'desc': 'material to be used',
        }

    def Plan(self):
        space = {}
        space['tiph'] = [0.1]
        space['Trace_height'] = [0.6]
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

        material = mat0
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        nozzlename = self.apparatus.findDevice(
            {'descriptors': ['nozzle', material]}
        )
        pumpname = self.apparatus.findDevice(
            {'descriptors': ['pump', material]}
        )
        refpoint = self.apparatus.getValue(
            ['information', 'alignments', nozzlename + '@start']
        )
        speed = self.apparatus.getValue(
            ['devices', motionname, nozzlename, 'speed']
        )
        axismask = self.apparatus.getValue(
            ['devices', motionname, nozzlename, 'axismask']
        )            
        
        def printDotted(periods):
            # Likely this is not the best way to command motion.
            for ind,period in enumerate(periods):
                self.pmove.Do(
                    {
                        'refpoint': refpoint,
                        'relpoint': {'X':4, 'Y':5+4*(ind), 'Z':0.6},
                        'speed': 20,
                        'axismask': axismask,
                        'priority': [['X', 'Y'], ['Z']],
                    }
                )
                self.DoEproc(motionname, 'Run', {})
            
                time_to_complete = 20/speed

                for i in [x*period for x in range(0,int(time_to_complete/period),2)]:
                    self.DoEproc(pumpname, 'DelayedOn', {'delay':i})
                    self.DoEproc(pumpname, 'DelayedOff', {'delay':i+period})

                self.move.Do(
                    {
                        'refpoint': refpoint,
                        'relpoint': {'X':24, 'Y':5+4*(ind), 'Z':0.6},
                        'speed': speed,
                        'axismask': axismask,
                    }
                )
                self.DoEproc(motionname, 'Run', {})
                self.move.Do(
                    {
                        'refpoint': refpoint,
                        'relpoint': {'X':24, 'Y':5+4*(ind), 'Z':0},
                        'speed': 20,
                        'axismask': axismask,
                    }
                )
                self.DoEproc(motionname, 'Run', {})
                self.move.Do(
                    {
                        'refpoint': refpoint,
                        'relpoint': {'X':24, 'Y':5+4*(ind), 'Z':10},
                        'speed': 20,
                        'axismask': axismask,
                    }
                )
                self.DoEproc(motionname, 'Run', {})
            
        def printCrossing(cross_feeds):
            # Go to first crossing
            self.pmove.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-6, 'Y':39.4+8, 'Z':0.0},
                    'speed': 20,
                    'axismask': axismask,
                    'priority': [['X', 'Y'], ['Z']],
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-6, 'Y':39.4-8, 'Z':0.0},
                    'speed': cross_feeds[0],
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-6, 'Y':39.4-8, 'Z':5},
                    'speed': 20,
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})

            # Got to 2nd crossing
            self.pmove.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-2*6, 'Y':39.4+8, 'Z':0.0},
                    'speed': 20,
                    'axismask': axismask,
                    'priority': [['X', 'Y'], ['Z']],
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-2*6, 'Y':39.4-8, 'Z':0.0},
                    'speed': cross_feeds[1],
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-2*6, 'Y':39.4-8, 'Z':5},
                    'speed': 20,
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})
            
            # Go to third crossing
            self.pmove.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-3*6, 'Y':39.4+8, 'Z':0.0},
                    'speed': 20,
                    'axismask': axismask,
                    'priority': [['X', 'Y'], ['Z']],
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-3*6, 'Y':39.4-8, 'Z':0.0},
                    'speed': cross_feeds[2],
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-3*6, 'Y':39.4-8, 'Z':5},
                    'speed': 20,
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})

            # Go to fourth crossing
            self.pmove.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-4*6, 'Y':39.4+8, 'Z':0.0},
                    'speed': 20,
                    'axismask': axismask,
                    'priority': [['X', 'Y'], ['Z']],
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-4*6, 'Y':39.4-8, 'Z':0.0},
                    'speed': cross_feeds[3],
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})
            self.move.Do(
                {
                    'refpoint': refpoint,
                    'relpoint': {'X':34-4*6, 'Y':39.4-8, 'Z':5},
                    'speed': 20,
                    'axismask': axismask,
                }
            )
            self.DoEproc(motionname, 'Run', {})

        self.DoEproc(pumpname, 'Set', {'pressure':MyApparatus['devices']['pump0']['pressure']})
        printDotted(periods=[2.0,1.75,1.5,1.25,1.0,0.75,0.5])
        MyApparatus['devices']['pump0']['pumpon_time'] = 0.5  # Time from pump on to motion, if calibration is on so this is overwritten
        MyApparatus['devices']['pump0']['pumpoff_time'] = 0.0 # time from end-arrival to turn off pump
        self.PrintTP.Do()
        printCrossing(cross_feeds=[1,5,25,100])

# Do the experiment
AlignPrinter.Do({'primenoz': 'n' + mat0})
CalInk.Do({'material': mat0})
TraySetup.Do({'trayname': 'test_samples', 'samplename': 'sample', 'xspacing': 14, 'xsamples': 1, 'yspacing': 15, 'ysamples': 1})
TrayRun.requirements['tray']['address'] = ['information', 'ProcedureData', 'SampleTray_XY_Setup', 'trays', 'test_samples']
TrayRun.Do({'procedure': Sample(MyApparatus, MyExecutor)})
Camera.Do({'point':{'X':3*25/2,'Y':2*25/2},'file':'Samples\mono_test.png','camera_name':'camera'})
MyApparatus.Disconnect_All()
toolpath = TP_gen['toolpath'][0]
