from Core import Procedure


class Pump_PumpOn(Procedure):
    def Prepare(self):
        self.name = 'Pump_PumpOn'
        self.requirements['mid_time']={'source':'apparatus', 'address':'', 'value':'', 'desc':'time to allow things to settle'}
        self.requirements['pumpon_time']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['name']={'source':'apparatus', 'address':'','value':'', 'desc':'name of the pump'}
    
    def Plan(self):
        pumpname = self.requirements['name']['value']
        systemname = self.apparatus.findDevice({'descriptors': 'system'})

        mid_time = self.requirements['mid_time']['value']
        pumpon_time = self.requirements['pumpon_time']['value']

        self.DoEproc(systemname, 'Dwell', {'dtime': mid_time})
        self.DoEproc(pumpname, 'On', {})
        self.DoEproc(systemname, 'Dwell', {'dtime': pumpon_time})
