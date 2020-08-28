from Core import Procedure
from Core import Apparatus

class Touch_Probe_A3200_EnableCalibration(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_EnableCalibration'
        self.requirements['file'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'path to store image',
        }
        self.requirements['nozzlename'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of the nozzle being cleaned',
        }

    def Plan(self):
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors= 'motion')

        self.target_settings = self.apparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'settings'])
        self.target_results = self.apparatus.getValue(['information', 'ProcedureData', 'Grid_Measurements', 'result'])
        
        # Retrieving information from apparatus
        #outaxis = self.apparatus.getValue(['devices', motionname, self.nozzlename, 'axismask'])['Z']
        outaxis = 'D'
        
        # Doing stuff
        self.apparatus.AddTicketItem({'calTable':self.file})
        self.DoEproc(motionname, 'gen_cal_table', dict({'outaxis':outaxis,'file':self.file,'result':self.target_results},**self.target_settings))
        self.DoEproc(motionname, 'enableCalTable', {'file':self.file, 'task':1})

        