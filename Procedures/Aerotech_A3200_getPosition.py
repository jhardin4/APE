from Core import Procedure
import Procedures.User_Consol_Input


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
            'value': [
                'information',
                'ProcedureData',
                'Aerotech_A3200_getPosition',
                'result',
            ],
            'desc': 'AppAddress where the result is stored',
        }
        # Create the Apparatus entry
        self.apparatus.createAppEntry(self.requirements['target']['value'])
        self.response = ''
        # Create required procedures
        self.userinput = Procedures.User_Consol_Input(self.apparatus, self.executor)

    def Plan(self):

        motionName = self.apparatus.findDevice(descriptors='motion')
        motionType = self.apparatus.getValue(['devices', motionName, 'addresstype'])

        # Retreiving necessary device names

        # Assign apparatus addresses to procedures

        # Doing stuff
        details = {'axislist': self.axisList}
        if motionType == 'pointer':
            temp_target = [0]
            details['address'] = temp_target
            details['addresstype'] = 'pointer'
        elif motionType == 'zmqNode':
            details['address'] = {'global': 'appa', 'AppAddress': self.target}
            details['addresstype'] = 'zmqNode_AppAddress'
        # Handle the simulation response
        if self.apparatus.getSimulation():
            message = 'What are simulation values for ' + str(self.axisList) + '?'
            default = ''
            self.userinput.Do({'message': message, 'default': default})
            tempposition = self.userinput.response
            if tempposition == '':
                tempposition = [0 for dim in self.axisList]
            else:
                tempposition = tempposition.replace('[', '')
                tempposition = tempposition.replace(']', '')
                tempposition = tempposition.split(',')
                tempposition = [float(x) for x in tempposition]
            self.response = tempposition
        else:

            self.DoEproc(motionName, 'getPosition', details)
            if motionType == 'pointer':
                self.response = temp_target[0]
            elif motionType == 'zmqNode':
                self.response = self.apparatus.getValue(self.target)
        self.Report(string=self.response)
