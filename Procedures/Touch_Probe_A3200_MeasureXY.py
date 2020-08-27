from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Touch_Probe_A3200_MeasureXY


class Touch_Probe_A3200_MeasureXY(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_MeasureXY'
        self.requirements['zreturn'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'how high to return after measurement',
        }
        self.requirements['retract'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'retract probe after measurement',
        }
        self.requirements['target'] = {
            'source': 'apparatus',
            'address': '',
            'value': [
                'information',
                'ProcedureData',
                'Touch_Probe_Measurement',
                'result',
            ],
            'desc': 'AppAddress where the result is stored',
        }
        self.requirements['point'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to measure relative to start',
        }
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.measure = Procedures.Touch_Probe_A3200_Measure(
            self.apparatus, self.executor
        )

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']

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

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do(
            {
                'relpoint': {'X': point['X'], 'Y': point['Y']},
                'priority': [['Z'],['X', 'Y']],
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.measure.Do({'zreturn':self.zreturn, 'retract':self.retract})
