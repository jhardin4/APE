from Core import Procedure
import Procedures.Touch_Probe_A3200_MeasurePt
import json


class Touch_Probe_A3200_SinglePtCorrect(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_SinglePtCorrect'
        self.requirements['point'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to measure relative to start',
        }
        self.measurePt = Procedures.Touch_Probe_A3200_MeasurePt(
            self.apparatus, self.executor
        )

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        alignments = self.apparatus['information']['alignments']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors='motion')

        # Measure surface
        self.measurePt.Do({'point': point,'zreturn':20,'retract':True})

        # Get system information
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']
        origin = self.apparatus.getValue(['information','ProcedureData','Touch_Probe_Measurement','result'])[0]
        
        # Apply change
        alignments['TProbe@start'][zaxis] = origin
        self.Report(message='TPrbe@start alignment set to ' + str(alignments['TProbe@start']) + '.')

        # Save a copy of the alignments to the main folder
        filename = 'robodaddy_alignments.json'
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus.getValue(['information', 'alignments']), TPjson)
