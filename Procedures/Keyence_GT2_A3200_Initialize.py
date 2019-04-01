from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion


class Keyence_GT2_A3200_Initialize(Procedure):
    def Prepare(self):
        self.name = 'Keyence_GT2_A3200_Initialize'
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs
        initialize = self.apparatus.GetEproc('TProbe', 'Initialize')
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])['Z']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe' + zaxis]

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, 'TProbe', 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'TProbe@TP_init']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['Z'], ['X', 'Y']]})
        runmove.Do()
        initialize.Do()
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
