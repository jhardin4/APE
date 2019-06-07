from Core import Procedure


class Pump_PumpOff(Procedure):
    def Prepare(self):
        self.name = 'Pump_PumpOff'
        self.requirements['mid_time']={'source':'apparatus', 'address':'', 'value':'', 'desc':'time to allow things to settle'}
        self.requirements['pumpoff_time']={'source':'apparatus', 'address':'','value':'', 'desc':'Point relative to reference position'}
        self.requirements['name']={'source':'apparatus', 'address':'','value':'', 'desc':'name of the pump'}
    
    def Plan(self):
        pumpname = self.requirements['name']['value']
        systemname = self.apparatus.findDevice({'descriptors': 'system'})

        mid_time = self.requirements['mid_time']['value']
        pumpoff_time = self.requirements['pumpoff_time']['value']

        self.DoEproc(systemname, 'Dwell', {'dtime': pumpoff_time})
        self.DoEproc(pumpname, 'Off', {})
        self.DoEproc(systemname, 'Dwell', {'dtime': mid_time})
