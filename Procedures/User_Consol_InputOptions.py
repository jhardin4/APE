from Core import Procedure


class User_Consol_InputOptions(Procedure):
    def Prepare(self):
        self.name = 'User_Consol_InputOptions'
        self.requirements['message'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Message to be displayed',
        }
        self.requirements['options'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Possible answers',
        }
        self.requirements['default'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'default response',
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
            'User_Consol_InputOptions',
            'result',
        ]
        self.apparatus.createAppEntry(self.requirements['target']['value'])
        self.response = ''

    def Plan(self):
        # Renaming useful pieces of information
        message = self.requirements['message']['value']
        options = self.requirements['options']['value']
        default = self.requirements['default']['value']
        target = self.requirements['target']['value']

        console_name = self.apparatus.findDevice({'descriptors': 'consol'})
        console_type = self.apparatus.getValue(['devices', console_name, 'addresstype'])

        # Retrieving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        details = {'message': message, 'options': options, 'default': default}

        if console_type == 'pointer':
            details['address'] = target
            details['addressType'] = 'pointer'
        elif console_type == 'zmqNode':
            details['address'] = {'global': 'appa', 'AppAddress': target}
            details['addressType'] = 'zmqNode_AppAddress'

        self.DoEproc(console_name, 'GetInputOptions', details)
        if console_type == 'pointer':
            self.response = target[0]
        elif console_type == 'zmqNode':
            self.response = self.apparatus.getValue(target)
        self.Report(self.response)
