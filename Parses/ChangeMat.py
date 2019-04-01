from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Pump_PumpOn
import Procedures.Pump_PumpOff
import Parses.StartofMotion
import Parses.EndofMotion


class ChangeMat(Procedure):
    def Prepare(self):
        self.name = 'ChangeMat'
        self.requirements['startmotion']={'source':'apparatus', 'address':'', 'value':'', 'desc':'motion before change'}
        self.requirements['endmotion']={'source':'apparatus', 'address':'', 'value':'', 'desc':'motion afterchange'}
        self.startofmotion = Parses.StartofMotion(self.apparatus, self.executor)
        self.endofmotion = Parses.EndofMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pumpon = Procedures.Pump_PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures.Pump_PumpOff(self.apparatus, self.executor)

    def Plan(self):
        #Renaming useful pieces of informaiton
        startmotion = self.requirements['startmotion']['value']
        endmotion = self.requirements['endmotion']['value']
        
        #Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors':'motion' })
        endnozzle = self.apparatus.findDevice({'descriptors':['nozzle', endmotion['material']] })
        startpump = self.apparatus.findDevice({'descriptors':['pump', startmotion['material']] })
        endpump = self.apparatus.findDevice({'descriptors':['pump', endmotion['material']] })
        
        #Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')
        
        #Assign apparatus addresses to procedures
        self.pumpon.requirements['pumpon_time']['address']=['devices',endpump,'pumpon_time']
        self.pumpon.requirements['mid_time']['address']=['devices',endpump,'mid_time']
        self.pumpoff.requirements['pumpoff_time']['address']=['devices',startpump,'pumpoff_time']
        self.pumpoff.requirements['mid_time']['address']=['devices',startpump,'mid_time']        
        
        # Doing stuff
        # Handling Print-Slide behavior
        if startmotion['material']==endmotion['material'].replace('slide','') or endmotion['material']==startmotion['material'].replace('slide',''):
            if startmotion['material'].endswith('slide'):
                self.motionset.Do({'Type':endnozzle})
                runmove.Do()
                self.pumpon.Do({'name':endpump})
            else:
                runmove.Do()
                self.pumpoff.Do({'name':startpump})
                self.motionset.Do({'Type':endnozzle})
                runmove.Do()
        else:
            self.endofmotion.Do({'motion':startmotion})
            self.startofmotion.Do({'motion':endmotion})
