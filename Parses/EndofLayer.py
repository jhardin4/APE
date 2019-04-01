from Core import Procedure
import Procedures.User_InkCal_Calibrate


class EndofLayer(Procedure):
    def Prepare(self): 
        self.name = 'EndofLayer'
        self.requirements['layernumber']={'source':'apparatus', 'address':'', 'value':'', 'desc':'number of the layer'}
        self.calink = Procedures.User_InkCal_Calibrate(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        matList = list(self.apparatus['information']['materials'])
        lnumber = self.requirements['layernumber']['value']
        
        # Doing stuff
        if lnumber != 0 and lnumber % 4 == 0:
            for material in matList:
                if 'PDMS' in material:
                    self.calink.Do({'material':material})
