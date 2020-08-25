from Core import Procedure
import Procedures.Aerotech_A3200_getPosition


class User_FlexPrinter_Alignments_Update(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Update'
        self.requirements['alignmentname'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'parameters used to generate toolpath',
        }
        self.getPos = Procedures.Aerotech_A3200_getPosition(
            self.apparatus, self.executor
        )
        self.userinput = Procedures.User_Consol_Input(self.apparatus, self.executor)

    def Plan(self):
        alignmentname = self.requirements['alignmentname']['value']
        alignment = self.apparatus.getValue(
            ['information', 'alignments', alignmentname]
        )

        _ = self.apparatus.findDevice(descriptors='motion')

        # Doing stuff
        message = 'Move to ' + alignmentname + ',and press ENTER when there.'
        default = ''
        self.userinput.Do({'message': message, 'default': default})
        dimlist = list(alignment)

        self.getPos.Do({'axisList': dimlist})
        tempposition = self.getPos.response

        n = 0
        for dim in dimlist:
            alignment[dim] = tempposition[n]
            n += 1

        self.apparatus.setValue(['information', 'alignments', alignmentname], alignment)
