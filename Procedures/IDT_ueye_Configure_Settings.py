from Core import Procedure


class IDT_ueye_Configure_Settings(Procedure):
    def Prepare(self):
        self.name = 'IDT_ueye_Configure_Settings'
        self.requirements['camera_name'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        self.requirements['gain'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'values for master and RGB gains (0-100)'}
        
        
    def Plan(self):
        # Renaming useful pieces of informaiton
        cname = self.requirements['camera_name']['value']
        gain = self.requirements['gain']['value']

        # Getting necessary eprocs
        configure = self.apparatus.GetEproc(cname, 'Configure')
        
        # Doing stuff
        configure.Do({'gain': gain, 'camera_name': cname})
