from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Keyence_GT2_A3200_Measure


class Keyence_GT2_A3200_MeasureXY(Procedure):
    def Prepare(self):
        self.name = 'Keyence_GT2_A3200_MeasureXY'
        self.requirements['point'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'XY point to measure relative to start'}
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.measure = Procedures.Keyence_GT2_A3200_Measure(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        
        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')


        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe'+zaxis]
        
        self.measure.requirements['address']['address']=['information', 'height_data']
        self.measure.requirements['zreturn']['address']=['devices', 'TProbe', 'zreturn']
        self.measure.requirements['retract']['address']=['devices', 'TProbe', 'retract']

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'TProbe@start']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
        self.pmove.Do({'relpoint': {'X': point['X'], 'Y': point['Y']}, 'priority': [['X', 'Y'],['Z']]})
        runmove.Do()
        self.measure.Do()
