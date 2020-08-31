from Core import Procedure
from Core import Apparatus

class Touch_Probe_A3200_DisableCalibration(Procedure):
    def Prepare(self):
        self.name = 'Touch_Probe_A3200_DisableCalibration'

    def Plan(self):
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors= 'motion')
        systemname = self.apparatus.findDevice(descriptors= 'system')

        self.DoEproc(motionname, 'disableCalTable', {'task':1})
        self.DoEproc(motionname, 'Run', {})