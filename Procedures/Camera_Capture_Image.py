from Core import Procedure


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
            'desc': 'time to weight before taking picture',
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

        # Assign apparatus addresses to procedures

        # Doing stuff
        self.DoEproc(systemname, 'Dwell', {'dtime': stime})
        self.DoEproc(cname, 'Measure', {'file': file})
