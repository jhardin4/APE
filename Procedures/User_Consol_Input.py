from Core import Procedure


class User_Consol_Input(Procedure):
    def Prepare(self):
        self.name = 'User_Consol_Input'
        self.requirements['message'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'Message to be displayed'}
        self.requirements['default'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'default response'}
        self.requirements['target'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'AppAddress where the result is stored'}
        self.requirements['target']['value'] = ['information','procedures','User_Consol_Input', 'result']
        self.apparatus.createAppEntry(self.requirements['target']['value'])
        self.response = ''

    def Plan(self):
        # Renaming useful pieces of informaiton
        message = self.requirements['message']['value']
        default = self.requirements['default']['value']
        target = self.requirements['target']['value']

        consoleName = self.apparatus.findDevice({'descriptors': 'consol'})
        consoleType = self.apparatus.getValue(['devices', consoleName, 'addresstype'])

        # Retreiving necessary device names

        # Getting necessary eprocs

        # Assign apparatus addresses to procedures

        # Doing stuff
        'zmqNode_AppAddress'
        details = {'message': message,
                   'default': default}

        if consoleType == 'pointer':
            details['address'] = target
            details['addressType'] = 'pointer'
        elif consoleType == 'zmqNode':
            details['address'] = {'global': 'appa', 'AppAddress': target}
            details['addressType'] = 'zmqNode_AppAddress'

        self.DoEproc('User', 'GetInput', details)
        if consoleType == 'pointer':
            self.response = target[0]
        elif consoleType == 'zmqNode':
            self.response = self.apparatus.getValue(target)
        self.Report(string=self.response)
