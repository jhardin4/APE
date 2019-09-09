from Core import Procedure
import Procedures.User_FlexPrinter_Alignments_Update
import Procedures.User_FlexPrinter_Alignments_Derive
import Procedures.User_Consol_InputOptions
import Procedures.User_Consol_Input
import json
import time


class User_FlexPrinter_Alignments_Load(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Load'
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
        self.updatealign = Procedures.User_FlexPrinter_Alignments_Update(
            self.apparatus, self.executor
        )
        self.derivealign = Procedures.User_FlexPrinter_Alignments_Derive(
            self.apparatus, self.executor
        )
        self.useroptions = Procedures.User_Consol_InputOptions(
            self.apparatus, self.executor
        )
        self.userinput = Procedures.User_Consol_Input(self.apparatus, self.executor)

    def Plan(self):
        measuredlist = self.requirements['Measured_List']['value']
        filename = self.requirements['filename']['value']

        # Doing stuff
        message = 'What filename?'
        default = filename
        self.userinput.Do({'message': message, 'default': default})
        afilename = self.userinput.response
        cur_alignments = self.apparatus.getValue(['information', 'alignments'])
        try:
            with open(filename, 'r') as TPjson:
                falignments = json.load(TPjson)
                for falignment in falignments:
                    cur_alignments[falignment] = falignments[falignment]
                self.apparatus.setValue(
                    ['information', 'alignments'], cur_alignments
                )
        except FileNotFoundError:
            message = 'No file loaded.  Possible error in ' + afilename
            default = ''
            self.userinput.Do({'message': message, 'default': default})
            afilename = self.userinput.response
            return
        # Check that the alignments are valid and return results of analysis
        missing_alignments = []
        incomplete_alignments = []
        for alignment in measuredlist:
            if alignment not in cur_alignments:
                missing_alignments.append(alignment)
            else:
                incomplete = False
                for dim in cur_alignments[alignment]:
                    if not isinstance(cur_alignments[alignment][dim], (int, float)):
                        incomplete = True
                if incomplete:
                    incomplete_alignments.append(alignment)
        message = ''
        if len(missing_alignments) > 0:
            message += 'Missing Alignments:\n'
            message += str(missing_alignments)
        if len(incomplete_alignments) > 0:
            message += 'Incomplete Alignments:\n'
            message += str(incomplete_alignments)
        default = ''
        if message is not '':
            self.userinput.Do({'message': message, 'default': default})

        # Save a copy of the alignments to the main folder and to the log folder
        with open(filename, 'w') as TPjson:
            json.dump(self.apparatus.getValue(['information', 'alignments']), TPjson)

        with open('Logs/' + str(int(round(time.time(), 0))) + filename, 'w') as TPjson:
            json.dump(self.apparatus.getValue(['information', 'alignments']), TPjson)
