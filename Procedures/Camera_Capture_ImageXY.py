from Core import Procedure
import Procedures.Camera_Capture_Image
import Procedures.Aerotech_A3200_Set
import Procedures.Motion_RefRelLinearMotion
import Procedures.Motion_RefRelPriorityLineMotion


class Camera_Capture_ImageXY(Procedure):
    def Prepare(self):
        self.name = 'Camera_Capture_ImageXY'
        self.requirements['point'] = {
            'source': 'apparatus',
            'address': '',
            'value': '',
            'desc': 'XY point to measure relative to start',
        }
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
        self.move = Procedures.Motion_RefRelLinearMotion(self.apparatus, self.executor)
        self.motionset = Procedures.Aerotech_A3200_Set(self.apparatus, self.executor)
        self.pmove = Procedures.Motion_RefRelPriorityLineMotion(
            self.apparatus, self.executor
        )
        self.measure = Procedures.Camera_Capture_Image(self.apparatus, self.executor)

    def Plan(self):
        # Retreiving necessary device names
        motionname = self.apparatus.findDevice(descriptors= 'motion')

        # Retrieving information from apparatus
        zaxis = self.apparatus.getValue(['devices', motionname, self.camera_name, 'axismask'])['Z']

        # Assign apparatus addresses to procedures
        self.move.requirements['speed']['address'] = [
            'devices',
            motionname,
            'default',
            'speed',
        ]
        self.move.requirements['axismask']['address'] = [
            'devices',
            motionname,
            self.camera_name,
            'axismask',
        ]
        self.move.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            'safe' + zaxis,
        ]

        self.pmove.requirements['speed']['address'] = [
            'devices',
            motionname,
            'default',
            'speed',
        ]
        self.pmove.requirements['axismask']['address'] = [
            'devices',
            motionname,
            self.camera_name,
            'axismask',
        ]
        self.pmove.requirements['refpoint']['address'] = [
            'information',
            'alignments',
            self.camera_name + '@start',
        ]

        # Doing stuff
        self.motionset.Do({'Type': 'default'})
        self.move.Do()
        self.pmove.Do(
            {
                'relpoint': {'X': self.point['X'], 'Y': self.point['Y']},
                'priority': [['X', 'Y'], ['Z']],
            }
        )
        self.DoEproc(motionname, 'Run', {})

        self.measure.Do({'file': self.file, 'settle_time':self.settle_time, 'camera_name': self.camera_name, 'config_file':self.config_file})
        self.apparatus.AddTicketItem({'image':self.file})