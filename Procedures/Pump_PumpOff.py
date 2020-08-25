from Core import Procedure


class Pump_PumpOff(Procedure):
    def Prepare(self):
        self.name = 'Pump_PumpOff'
        self.requirements['mid_time'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'time to allow things to settle',
        }
        self.requirements['pumpoff_time'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'Point relative to reference position',
        }
        self.requirements['pump_name'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of the pump',
        }

    def Plan(self):
        systemname = self.apparatus.findDevice(descriptors='system')

        self.DoEproc(systemname, 'Dwell', {'dtime': self.pumpoff_time})
        self.DoEproc(self.pump_name, 'Off', {})
        self.DoEproc(systemname, 'Dwell', {'dtime': self.mid_time})
