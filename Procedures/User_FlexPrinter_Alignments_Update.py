from Core import Procedure


class User_FlexPrinter_Alignments_Update(Procedure):
    def Prepare(self):
        self.name = 'User_FlexPrinter_Alignments_Update'
        self.requirements['alignmentname'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}

    def Plan(self):
        alignmentname = self.requirements['alignmentname']['value']
        alignment = self.apparatus['information']['alignments'][alignmentname]

        motionname = self.apparatus.findDevice({'descriptors': 'motion'})

        getpostion = self.apparatus.GetEproc(motionname, 'getPosition')
        
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
            datavessel = [0]
            getpostion.Do({'addresstype':'pointer','address':datavessel, 'axislist':dimlist})
            tempposition = datavessel[0]

        n=0
        for dim in dimlist:
            alignment[dim] = tempposition[n]
            n += 1

        


