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
            'desc': 'How long to wait in the cleaning vessel',
        }

        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful informaiton
        nozzlename = self.requirements['nozzlename']['value']
        depth = self.requirements['depth']['value']
        delay = self.requirements['delay']['value']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        systemname = self.apparatus.findDevice({'descriptors': 'system'})

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        dwell = self.apparatus.GetEproc(systemname, 'Dwell')

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
        self.pmove.Do(
            {
                'relpoint': {'X': 0, 'Y': 0, 'Z': -depth},
                'priority': [['X', 'Y'], ['Z']],
            }
        )
        runmove.Do()
        dwell.Do({'dtime': delay})
        self.move.Do({'relpoint': {'Z': 0}})
        runmove.Do()