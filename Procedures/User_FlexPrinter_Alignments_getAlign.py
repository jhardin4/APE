from Core import Procedure
import Procedures.Aerotech_A3200_getPosition
import Procedures.User_Consol_InputOptions
import json
import time


class User_FlexPrinter_Alignments_getAlign(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_getAlign'
        self.requirements['Measured_List'] = {
            'source': 'apparatus',
            'address': ['information', 'alignmentnames'],
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.requirements['filename'] = {
            'source': 'apparatus',
            'address': ['information', 'alignmentsfile'],
            'value': '',
            'desc': 'name of alignmentfile',
        }
        self.getPos = Procedures.Aerotech_A3200_getPosition(
            self.apparatus, self.executor
        )
        self.useroptions = Procedures.User_Consol_InputOptions(
            self.apparatus, self.executor
        )
    def Plan(self):
        mlist = self.requirements['Measured_List']['value']
        filename = self.requirements['filename']['value']

        # Doing stuff
        message = 'Select which alignment you are at.'
        options = mlist
        default = mlist[0]
        self.useroptions.Do(
            {'message': message, 'options': options, 'default': default}
        )
        alignment = self.useroptions.response
        cur_alignment = self.apparatus.getValue(
            ['information', 'alignments', alignment]
        )
        dimlist = list(cur_alignment)
        self.getPos.Do({'axisList': dimlist})
        tempposition = self.getPos.response

        newalignment = {}
        n = 0
        for dim in dimlist:
            newalignment[dim] = tempposition[n]
            n += 1

        self.apparatus.setValue(['information', 'alignments', alignment], newalignment)

        # Save a copy of the alignments to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus.getValue(['information', 'alignments']), TPjson)

        with open('Logs/' + str(int(round(time.time(), 0))) + filename, 'w') as TPjson:
            json.dump(self.apparatus.getValue(['information', 'alignments']), TPjson)