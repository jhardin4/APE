from Core import Procedure
from Core import Apparatus
import json

class Touch_Probe_A3200_EnableCalibration(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_EnableCalibration'
        self.debug = False
        self.requirements['file'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'path to store image',
        }
        self.requirements['nozzlename'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of the nozzle being cleaned',
        }

    def Plan(self):
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors= 'motion')
        alignments = self.apparatus['information']['alignments']

        self.target_settings = self.apparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'settings'])
        self.target_results = self.apparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'result'])
        
        
        # Multi point correction consists of:
        # 1. Calibration table with corrections with last measurement as zero
        self.apparatus.AddTicketItem({'calTable':self.file})

        # Target settings must be modified based on nozzle offsets
        if self.debug:
            outaxis = 'D'

        else:
            outaxis = self.apparatus.getValue(['devices', motionname, self.nozzlename, 'axismask'])['Z']
            offset_x = alignments[self.nozzlename+'@mark']['X'] - alignments['TProbe@mark']['X']
            offset_y = alignments[self.nozzlename+'@mark']['Y'] - alignments['TProbe@mark']['Y']
            self.target_settings['start_point']['X'] += offset_x
            self.target_settings['start_point']['Y'] += offset_y
        
        self.DoEproc(motionname, 'gen_cal_table', dict({'outaxis':outaxis,'file':self.file,'result':self.target_results},**self.target_settings))
        self.DoEproc(motionname, 'enableCalTable', {'file':self.file, 'task':1})
        self.DoEproc(motionname, 'Run', {})
        
        # 2. Setting last measurement to TProbe@start
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']

        # Apply change
        alignments['TProbe@start'][zaxis] = self.target_results.flatten()[-1]
        self.Report(message='TProbe@start alignment set to ' + str(alignments['TProbe@start']) + '.')

        # Save a copy of the alignments to the main folder
        filename = 'robodaddy_alignments.json'
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus.getValue(['information', 'alignments']), TPjson)
