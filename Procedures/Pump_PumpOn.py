from Core import Procedure


class Pump_PumpOn(Procedure):
    def Prepare(self):
        self.name = 'Pump_PumpOn'
        self.requirements['mid_time']={'source':'apparatus', 'address':'', 'value':'', 'desc':'time to allow things to settle'}
        self.requirements['pumpon_time']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['name']={'source':'apparatus', 'address':'','value':'', 'desc':'name of the pump'}
    
    def Plan(self):
        pumpname = self.requirements['name']['value']
        pumpon = self.apparatus.GetEproc(pumpname, 'On')
        systemname = self.apparatus.findDevice({'descriptors':'system'})
        systemdwell = self.apparatus.GetEproc(systemname, 'Dwell')
        
        mid_time = self.requirements['mid_time']['value']
        pumpon_time = self.requirements['pumpon_time']['value']
        
        systemdwell.Do({'dtime':mid_time})
        pumpon.Do()
        systemdwell.Do({'dtime':pumpon_time})
