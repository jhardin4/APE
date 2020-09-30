from Core import Procedure
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Aerotech_A3200_Set


class Aerotech_A3200_AirClean(Procedure):
    def Prepare(self):
        self.name = 'Aerotech_A3200_AirClean'
        self.requirements['nozzlename'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of the nozzle being cleaned',
        }
        self.requirements['depth'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'how deep to go into the cleaning vessel',
        }
        self.requirements['delay'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'How long to wait between swirls',
        }

        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful informaiton
        nozzlename = self.nozzlename
        depth = self.depth
        delay = self.delay

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors= 'motion')
        systemname = self.apparatus.findDevice(descriptors= 'system')

        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = [
            'devices',
            motionname,
            'default',
            'speed',
        ]
        self.move.requirements['axismask']['address'] = [
            'devices',
            motionname,
            nozzlename,
            'axismask',
        ]
        self.move.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            nozzlename + '@clean',
        ]

        self.pmove.requirements['speed']['address'] = [
            'devices',
            motionname,
            'default',
            'speed',
        ]
        self.pmove.requirements['axismask']['address'] = [
            'devices',
            motionname,
            nozzlename,
            'axismask',
        ]
        self.pmove.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            nozzlename + '@clean',
        ]

        # Actual motion in and out of nozzle cleaner
        self.motionset.Do({'Type': 'default'})
        # Move up in Z to clear cleaner, then move into position
        self.pmove.Do(
            {
                'relpoint': {'X': 0, 'Y': 0, 'Z': 0},
                'priority': [['Z'],['X', 'Y']],
            }
        )
        # Move down into cleaner using depth argument
        self.move.Do({'relpoint': {'Z': -depth}})
        self.DoEproc(motionname, 'Run', {})
        # Pause in cleaner defined by delay argument
        self.DoEproc(systemname, 'Dwell', {'dtime': delay})
        # Move up and out of cleaner
        self.move.Do({'relpoint': {'Z': 0}})
        self.DoEproc(motionname, 'Run', {})