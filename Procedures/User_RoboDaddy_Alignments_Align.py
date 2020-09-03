from Core import Procedure
import Procedures.User_FlexPrinter_Alignments_Update
import json
import time


class User_RoboDaddy_Alignments_Align(Procedure):
    def Prepare(self):
        self.name = 'User_RoboDaddy_Alignments_Align'
        self.requirements['Measured_List'] = {
            'source': 'apparatus',
            'address': ['information', 'alignmentnames'],
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.requirements['primenoz'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'prime material',
        }
        self.requirements['filename'] = {
            'source': 'apparatus',
            'address': ['information', 'alignmentsfile'],
            'value': '',
            'desc': 'name of alignmentfile',
        }
        self.requirements['chatty'] = {
            'source': 'direct',
            'address': '',
            'value': True,
            'desc': 'if false it bypasses the dialogue',
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
        primenoz = self.requirements['primenoz']['value']
        measuredlist = ['initial', primenoz+'@mark', primenoz+'@start', primenoz+'@clean', primenoz+'@mark']
        filename = self.requirements['filename']['value']
        chatty = self.requirements['chatty']['value']

        # Doing stuff

        # Check for loading file
        if chatty:
            alignmentscollected = False
            message = 'Import alignments from file?'
            options = ['y', 'n']
            default = 'y'
            self.useroptions.Do(
                {'message': message, 'options': options, 'default': default}
            )
            doalignment = self.useroptions.response
            if doalignment in ['y', 'Y', 'yes', 'Yes', 'YES', '']:
                message = 'What filename?'
                default = filename
                self.userinput.Do({'message': message, 'default': default})
                afilename = self.userinput.response
                try:
                    with open(afilename, 'r') as TPjson:
                        self.apparatus.setValue(
                            ['information', 'alignments'], json.load(TPjson)
                        )
                    alignmentscollected = True
                except FileNotFoundError:
                    print('No file loaded.  Possible error in ' + afilename)
    
            # If alignments were not collected from a file, collect them directly
            if not alignmentscollected:
                for alignment in measuredlist:
                    self.updatealign.Do({'alignmentname': alignment})
    
            # Check if any alignments need to be redone
            alignmentsOK = False
            while not alignmentsOK:
                message = (
                    self.PrintAlignments(
                        self.apparatus.getValue(['information', 'alignments'])
                    )
                    + 'Would you like to redo any alignments?'
                )
                options = ['y', 'n']
                default = 'n'
                self.useroptions.Do(
                    {'message': message, 'options': options, 'default': default}
                )
                redoalignments = self.useroptions.response
                if redoalignments in ['y', 'Y', 'yes', 'Yes', 'YES']:
                    message = 'Which alignment would you like to redo?'
                    options = measuredlist
                    default = ''
                    self.useroptions.Do(
                        {'message': message, 'options': options, 'default': default}
                    )
                    which_alignment = self.useroptions.response
                    if which_alignment in measuredlist:
                        self.updatealign.Do({'alignmentname': which_alignment})
                    else:
                        print('Alignment is not in list.')
                else:
                    alignmentsOK = True
        else:
            try:
                with open(filename, 'r') as TPjson:
                    self.apparatus.setValue(
                        ['information', 'alignments'], json.load(TPjson)
                    )
                alignmentscollected = True
            except FileNotFoundError:
                print('No file loaded.  Possible error in ' + afilename)

    def PrintAlignments(self, alignments):
        printstr = ''
        for alignment in alignments:
            printstr += alignment + '\n'
            for dim in alignments[alignment]:
                printstr += dim + ' ' + str(alignments[alignment][dim]) + ' '
            printstr += '\n\n'
        return printstr
