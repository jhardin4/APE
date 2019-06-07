from Core import Procedure
import Procedures.Aerotech_A3200_getPosition


class User_FlexPrinter_Alignments_Update(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Update'
        self.requirements['alignmentname'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.getPos = Procedures.Aerotech_A3200_getPosition(self.apparatus, self.executor)

    def Plan(self):
        alignmentname = self.requirements['alignmentname']['value']
        alignment = self.apparatus.getValue(['information', 'alignments', alignmentname])

        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        #Doing stuff
        input('Move to ' + alignmentname + ',and press ENTER when there.')
        dimlist = list(alignment)
        if self.apparatus.simulation:
            tempposition = input('What is the simulated value of the form ' + str(dimlist) + '?')
            tempposition = tempposition.replace('[','')
            tempposition = tempposition.replace(']','')
            tempposition = tempposition.split(',')
            tempposition = [float(x) for x in tempposition]   
        else:
            self.getPos.Do({'axisList': dimlist})
            tempposition = self.getPos.response

        n=0
        for dim in dimlist:
            alignment[dim] = tempposition[n]
            n += 1
        
        self.apparatus.setValue(['information', 'alignments', alignmentname], alignment)

        


