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

    def Plan(self):
        # Renaming useful pieces of informaiton
        file = self.requirements['file']['value']
        stime = self.requirements['settle_time']['value']
        cname = self.requirements['camera_name']['value']

        # Retreiving necessary device names
        systemname = self.apparatus.findDevice({'descriptors': 'system'})

        # Retrieving information from apparatus
        # Support a default location for the settle_time
        if stime == '':
            stime_address = ['devices', cname, 'settle_time']
            try:
                stime = self.apparatus.getValue(stime_address)
            except Apparatus.InvalidApparatusAddressException:
                stime = 0
        # Assign apparatus addresses to procedures

        # Doing stuff
        self.DoEproc(systemname, 'Dwell', {'dtime': stime})
        self.DoEproc(cname, 'Measure', {'file': file})
