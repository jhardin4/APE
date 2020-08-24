from Core import Procedure


class Touch_Probe_A3200_Measure(Procedure):
    '''
    The idea behind this general touch probe procedure is to enable functionality
    with both the Keyence_GT2 and Panasonic_HGS displacmenet sensors in addition
    to future possible sensors.
    '''
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_Measure'
        self.requirements['address'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'where to store result',
        }
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

    def Plan(self):
        # Renaming useful pieces of informaiton
        retract = self.requirements['retract']['value']
        zreturn = self.requirements['zreturn']['value']
        address = self.requirements['address']['value']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])[
            'Z'
        ]
        speed = self.apparatus.getValue(['devices', motionname, 'default', 'speed'])

        # Getting necessary eprocs
        measure = self.apparatus.GetEproc('TProbe', 'Measure')
        setmove = self.apparatus.GetEproc(motionname, 'Set_Motion')
        move = self.apparatus.GetEproc(motionname, 'Move')

        # Assign apparatus addresses to procedures

        # Move away from surface after measuring
        measure.Do({'address': address, 'addresstype': 'pointer', 'retract': retract})
        setmove.Do({'RelAbs': 'Rel', 'motionmode': 'cmd'})
        move.Do(
            {
                'motiontype': 'linear',
                'motionmode': 'cmd',
                'point': {zaxis: zreturn},
                'speed': speed,
            }
        )
        setmove.Do({'RelAbs': 'Abs', 'motionmode': 'cmd'})
