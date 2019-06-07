from Core import Procedure
import Procedures.Aerotech_A3200_Set
import Procedures.Pump_PumpOff


class EndofMotion(Procedure):
    def Prepare(self):
        self.name = 'EndofMotion'
        self.requirements['motion']={'source':'apparatus', 'address':'', 'value':'', 'desc':'motion to start'}
        self.pumpoff = Procedures.Pump_PumpOff(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)        
    
    def Plan(self):
        #Renaming useful pieces of informaiton
        materialname = self.requirements['motion']['value']['material']
        
        #Retreiving necessary device names
        pumpname = self.apparatus.findDevice({'descriptors':['pump', materialname] })
        motionname = self.apparatus.findDevice({'descriptors':'motion' })
        nozzlename = self.apparatus.findDevice({'descriptors':['nozzle', materialname] })
        
        #Assign apparatus addresses to procedures
        self.pumpoff.requirements['pumpoff_time']['address']=['devices',pumpname,'pumpoff_time']
        self.pumpoff.requirements['mid_time']['address']=['devices',pumpname,'mid_time']
        ##Assumes that the +Z axis is the safe direction
        axismask = self.apparatus.getValue(['devices', motionname, nozzlename, 'axismask'])
        if 'Z' in axismask:
            point = self.apparatus.getValue(['information','alignments','safe'+axismask['Z']])
        else:
            point = self.apparatus.getValue(['information','alignments','safeZ'])
        speed = self.apparatus.getValue(['devices',motionname, 'default', 'speed'])

        # Doing stuff
        self.DoEproc(motionname, 'Run', {})  # Run the motion up to this point
        if pumpname != 'No devices met requirments':
            self.pumpoff.Do({'name': pumpname})
        self.DoEproc(motionname, 'LogData_Stop', {})
        self.motionset.Do({'Type': 'default'})
        self.DoEproc(motionname, 'Move', {'point': point, 'speed':speed})
        self.DoEproc(motionname, 'Run', {})
