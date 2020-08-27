from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Touch_Probe_A3200_Measure
import numpy as np


class Touch_Probe_A3200_MultiPtHeightCorrect(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_MultiPtHeightCorrect'
        self.requirements['target'] = {
            'source': 'apparatus',
            'address': '',
            'value': [
                'information',
                'ProcedureData',
                'Grid_Measurements',
                'result',
            ],
            'desc': 'AppAddress where the result is stored',
        }
        self.requirements['start_point'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to start grid measurement',
        }
        self.requirements['x_length'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to start grid measurement',
        }
        self.requirements['y_length'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to start grid measurement',
        }
        self.requirements['x_count'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to start grid measurement',
        }
        self.requirements['y_count'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to start grid measurement',
        }
                # Create the Apparatus entry
        self.apparatus.createAppEntry(self.requirements['target']['value'])

        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.measure = Procedures.Touch_Probe_A3200_Measure(
            self.apparatus, self.executor
        )

    def Plan(self):

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors='motion')

        self.pmove.requirements['speed']['address'] = [
            'devices',
            motionname,
            'default',
            'speed',
        ]
        self.pmove.requirements['axismask']['address'] = [
            'devices',
            motionname,
            'TProbe',
            'axismask',
        ]
        self.pmove.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            'TProbe@start',
        ]

        self.start_point = {k.upper(): v for k, v in self.start_point.items()}
        self.pmove.Do(
            {
                'relpoint': {'X': self.start_point['X'], 'Y': self.start_point['Y']},
                'priority': [['Z'],['X', 'Y']],
            }
        )
        self.DoEproc(motionname, 'Run', {})

        grid_results = []
        for y_pos in np.linspace(self.start_point['Y'],self.start_point['Y']+self.y_length,int(self.y_count),endpoint=True):
            for x_pos in np.linspace(self.start_point['X'],self.start_point['X']+self.x_length,int(self.x_count),endpoint=True):
                # Move to grid point
                self.pmove.Do(
                    {
                        'relpoint':{'X': x_pos, 'Y': y_pos},
                        'priority': [['Z'],['X', 'Y']]
                    })
                self.DoEproc(motionname, 'Run', {})
                # Measure using probe
                self.measure.Do({'zreturn':5, 'retract':False})
                grid_results.append(self.apparatus.getValue(['information',
                'ProcedureData',
                'Touch_Probe_Measurement',
                'result'])[0])
                self.apparatus.setValue(self.target,grid_results)
                print(self.apparatus.getValue(self.target))