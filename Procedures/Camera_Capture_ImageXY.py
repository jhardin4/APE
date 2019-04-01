from Core import Procedure
import Procedures.Camera_Capture_Image
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion


class Camera_Capture_ImageXY(Procedure):
    def Prepare(self):
        self.name = 'Camera_Capture_ImageXY'
        self.requirements['point'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'XY point to measure relative to start'}
        self.requirements['file'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'path to store image'}
        self.requirements['camera_name'] = {'source': 'apparatus', 'address': '', 'value': '', 'desc': 'name of the camera to be used'}
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(self.apparatus, self.executor)
        self.measure = Procedures.Camera_Capture_Image(self.apparatus, self.executor)

    def Plan(self):
        # Renaming useful pieces of informaiton
        point = self.requirements['point']['value']
        file = self.requirements['file']['value']
        cname = self.requirements['camera_name']['value']
        
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice({'descriptors': 'motion'})
        
        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, cname, 'axismask'])['Z']

        # Getting necessary eprocs
        runmove = self.apparatus.GetEproc(motionname, 'Run')

        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.move.requirements['axismask']['address'] = ['devices', motionname, cname, 'axismask']
        self.move.requirements['refpoint']['address'] = ['information', 'alignments', 'safe'+zaxis]

        self.measure.requirements['settle_time']['address']=['devices', cname, 'settle_time']

        self.pmove.requirements['speed']['address'] = ['devices',motionname, 'default', 'speed']
        self.pmove.requirements['axismask']['address'] = ['devices', motionname, cname, 'axismask']
        self.pmove.requirements['refpoint']['address'] = ['information', 'alignments', cname + '@start']
        
        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
        self.pmove.Do({'relpoint': {'X': point['X'], 'Y': point['Y']}, 'priority': [['X', 'Y'],['Z']]})
        runmove.Do()
        self.measure.Do({'file': file, 'camera_name': cname})
