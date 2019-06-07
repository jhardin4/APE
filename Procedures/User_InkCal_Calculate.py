from Core import Procedure
import Procedures.Pump_PumpOn
import Procedures.Pump_PumpOff
import Procedures.Motion_RefRelPriorityLineMotion
import json
import time


class User_InkCal_Calculate(Procedure):
    def Prepare(self):
        self.name = 'User_InkCal_Calculate'
        self.requirements['material'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'parameters used to generate toolpath'}
        self.requirements['filename'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of alignmentfile'}
        self.requirements['filename']['address'] = ['information', 'calibrationfile']
        self.pmotion = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.pumpon = Procedures.Pump_PumpOn(self.apparatus, self.executor)
        self.pumpoff = Procedures.Pump_PumpOff(self.apparatus, self.executor)

    def Plan(self):
        # Reassignments for convienence
        material = self.requirements['material']['value']
        filename = self.requirements['filename']['value']
        cfilename = material + filename

        motion = self.apparatus.findDevice({'descriptors': ['motion']})
        nozzle = self.apparatus.findDevice({'descriptors': ['nozzle', material]})
        pump = self.apparatus.findDevice({'descriptors': ['pump', material]})

        do_pumpcal = self.apparatus.getValue(['information', 'materials', material, 'do_pumpcal'])
        do_speedcal = self.apparatus.getValue(['information', 'materials', material, 'do_speedcal'])
        density = self.apparatus.getValue(['information', 'materials', material, 'density'])
        trace_width = self.apparatus.getValue(['devices', nozzle, 'trace_width'])
        trace_height = self.apparatus.getValue(['devices', nozzle, 'trace_height'])
        pumpres_time = self.apparatus.getValue(['devices', pump, 'pumpres_time'])
        
        if self.apparatus.getValue(['information', 'materials', material, 'calibrated']):
            with open(cfilename, 'r') as caljson:
                file_data = json.load(caljson)
    
            if len(file_data) == 1:
                dweight = float(file_data[0]['delta_weight'])
                exvolume = dweight / density * 1000  # mm^3
                vexrate = exvolume / file_data[0]['test_time']  # mm^3/s
                crossarea = trace_width * trace_height  # mm^2
                targetspeed = vexrate/crossarea  # m/s
            else:
                initial_time = float(file_data[len(file_data) - 2]['time'])
                final_time = float(file_data[len(file_data) - 1]['time'])
                initial_dweight = float(file_data[len(file_data) - 2]['delta_weight'])
                final_dweight = float(file_data[len(file_data) - 1]['delta_weight'])
                cur_time = time.time()
                # Assume linear change in viscosity with time
                proj_dweight = (cur_time - initial_time) / (final_time - initial_time) * (final_dweight - initial_dweight) + initial_dweight
                # Continue with calculations
                exvolume = proj_dweight / density * 1000  # mm^3
                vexrate = exvolume / file_data[0]['test_time']  # mm^3/s
                crossarea = trace_width * trace_height  # mm^2
                targetspeed = vexrate/crossarea  # m/s            
            if do_speedcal:
                self.apparatus.setValue(['devices', motion, nozzle, 'speed'], targetspeed)
            if do_pumpcal:
                self.apparatus.setValue(['devices', pump, 'pumpon_time'], pumpres_time + 1.5*trace_height / targetspeed)
