from Core import Procedure


class Aerotech_A3200_getPosition(Procedure):
    def Prepare(self):
        self.name = 'Aerotech_A3200_getPosition'
        self.requirements['axisList'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Axes to get the position of',
        }
        self.requirements['target'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'AppAddress where the result is stored',
        }
        self.requirements['target']['value'] = [
            'information',
            'procedures',
            'Aerotech_A3200_getPosition',
            'result',
        ]
        self.apparatus.createAppEntry(self.requirements['target']['value'])
        self.response = ''

    def Plan(self):
        # Renaming useful pieces of informaiton
        axisList = self.requirements['axisList']['value']
        target = self.requirements['target']['value']

        motionName = self.apparatus.findDevice({'descriptors': 'motion'})
        motionType = self.apparatus.getValue(['devices', motionName, 'addresstype'])

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        details = {'axislist': axisList}
        if motionType == 'pointer':
            details['address'] = target
            details['addresstype'] = 'pointer'
        elif motionType == 'zmqNode':
            details['address'] = {'global': 'appa', 'AppAddress': target}
            details['addresstype'] = 'zmqNode_AppAddress'

        self.DoEproc(motionName, 'getPosition', details)
        self.response = target[0]
        self.Report(string=self.response)
