from Core import Procedure
from Core import Apparatus


class Camera_Capture_Image(Procedure):
    def Prepare(self):
        self.name = 'Camera_Capture_Image'
        self.requirements['file'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'path to store image',
        }
        self.requirements['settle_time'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'time to wait before taking picture',
        }
        self.requirements['camera_name'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'name of the camera to be used',
        }
        self.requirements['config_file'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'configuration file to load to camera',
        }

    def Plan(self):
        # Retreiving necessary device names
        systemname = self.apparatus.findDevice(descriptors='system')

        # Retrieving information from apparatus
        # Support a default location for the settle_time
        if self.settle_time == '':
            stime_address = ['devices', self.camera_name, 'settle_time']
            try:
                self.settle_time = self.apparatus.getValue(stime_address)
            except Apparatus.InvalidApparatusAddressException:
                self.settle_time = 0
        # Assign apparatus addresses to procedures

        # Doing stuff
        self.DoEproc(systemname, 'Dwell', {'dtime': self.settle_time})
        if self.config_file != '':
            self.DoEproc(self.camera_name, 'LoadConfiguration', {'file': self.config_file})
        self.DoEproc(self.camera_name, 'Measure', {'file': self.file})
        self.apparatus.AddTicketItem({'image':self.file})
