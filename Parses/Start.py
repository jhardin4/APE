from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelPriorityLineMotion


class Start(Procedure):
    def Prepare(self):
        self.name = 'Start'
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        matList = list(self.apparatus['information']['materials'])

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.pmove.requirements['speed']['address'] = ['devices', motionname, 'default', 'speed']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', 'initial']

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['ZZ1', 'ZZ2', 'ZZ3', 'ZZ4'], ['X', 'Y']]})
        runmove.Do()
