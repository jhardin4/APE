from Core import Procedure
import Procedures.Motion_RefRelLinearMotion


class Touch_Probe_A3200_Measure(Procedure):
    '''
    The idea behind this general touch probe procedure is to enable functionality
    with both the Keyence_GT2 and Panasonic_HGS displacmenet sensors in addition
    to future possible sensors.
    '''
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_Measure'
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
        # Create the Apparatus entry
        self.apparatus.createAppEntry(self.requirements['target']['value'])
        
        # Initialize the Touch Probe here when procedure is instantiated.
        self.DoEproc('TProbe', 'Initialize',{})
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        retract = self.requirements['retract']['value']
        zreturn = self.requirements['zreturn']['value']

        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors='motion')

        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, 'TProbe', 'axismask'])[
            'Z'
        ]
        speed = self.apparatus.getValue(['devices', motionname, 'default', 'speed'])

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
            'TProbe',
            'axismask',
        ]
        self.move.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            'safe' + zaxis,
        ]

        # Take measurement
        temp_target = [0]
        self.DoEproc('TProbe', 'Measure', {'address': temp_target, 'addresstype': 'pointer', 'retract': retract})
        self.apparatus.setValue(self.target,temp_target)
        
        # Move away from surface after measuring
        self.DoEproc(motionname, 'Set_Motion', {'RelAbs': 'Rel', 'motionmode': 'cmd'})
        self.move.Do(
            {
                'relpoint': {zaxis: zreturn},
                'speed': speed,
            }
        )
        self.DoEproc(motionname, 'Run', {})
        self.DoEproc(motionname, 'Set_Motion', {'RelAbs': 'Abs', 'motionmode': 'cmd'})
