from Core import Procedure
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion
import Procedures.Aerotech_A3200_Set


class Aerotech_A3200_SolventClean(Procedure):
    def Prepare(self):
        self.name = 'Aerotech_A3200_SolventClean'
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
        self.requirements['swirls'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'How many swirls to do',
        }
        self.requirements['sradius'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'How many swirls to do',
        }

        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)

    def Plan(self):
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors='motion')
        pumpname = self.apparatus.findDevice(descriptors=['pump', self.nozzlename[1:]])
        systemname = self.apparatus.findDevice(descriptors= 'system')

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        pumpon = self.apparatus.GetEproc(pumpname, 'On')
        pumpoff = self.apparatus.GetEproc(pumpname, 'Off')
        # pumpset = self.apparatus.GetEproc(pumpname, 'Set')
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
            self.nozzlename,
            'axismask',
        ]
        self.move.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            nozzlename + '@dump',
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
            self.nozzlename,
            'axismask',
        ]
        self.pmove.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            self.nozzlename + '@dump',
        ]

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.pmove.Do({'priority': [['X', 'Y'], ['Z']]})
        self.move.Do({'relpoint': {'Z': -self.depth}})
        runmove.Do()
        # pumpset.requirements['pressure']['address'] = ['devices', pumpname, 'pressure']
        # pumpset.Do()
        pumpon.Do()
        for n in range(self.swirls):
            self.move.Do(
                {'relpoint': {'X': self.sradius / 2, 'Y': self.sradius / 2, 'Z': -self.depth}}
            )
            self.move.Do(
                {'relpoint': {'X': self.sradius / 2, 'Y': -self.sradius / 2, 'Z': -self.depth}}
            )
            self.move.Do(
                {'relpoint': {'X': -self.sradius / 2, 'Y': -self.sradius / 2, 'Z': -self.depth}}
            )
            self.move.Do(
                {'relpoint': {'X': -self.sradius / 2, 'Y': self.sradius / 2, 'Z': -self.depth}}
            )
        self.move.Do({'relpoint': {'Z': -self.depth}})
        runmove.Do()
        dwell.Do({'dtime': self.delay})
        pumpoff.Do()
        for n in range(self.swirls):
            self.move.Do(
                {'relpoint': {'X': self.sradius / 2, 'Y': self.sradius / 2, 'Z': -self.depth}}
            )
            self.move.Do(
                {'relpoint': {'X': self.sradius / 2, 'Y': -self.sradius / 2, 'Z': -self.depth}}
            )
            self.move.Do(
                {'relpoint': {'X': -self.sradius / 2, 'Y': -self.sradius / 2, 'Z': -self.depth}}
            )
            self.move.Do(
                {'relpoint': {'X': -self.sradius / 2, 'Y': self.sradius / 2, 'Z': -self.depth}}
            )
        self.move.Do({'relpoint': {'Z': -self.depth}})
        self.move.Do({'relpoint': {'Z': 0}})
        zaxis = self.apparatus.getValue(
            ['devices', motionname, self.nozzlename, 'axismask']
        )['Z']
        self.move.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            'safe' + zaxis,
        ]
        self.move.Do()
