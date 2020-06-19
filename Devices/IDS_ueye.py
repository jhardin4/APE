# blank
# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#

from Devices import Sensor

class IDS_ueye(Sensor):
    def __init__(self, name):
        Sensor.__init__(self, name)
        self.descriptors.append('ueye')
        self.descriptors.append('camera')
        self.handle = ''
        self.requirements['StartFeed'] ={}
        self.requirements['StopFeed'] ={}
        self.requirements['StartRecord'] ={}
        self.requirements['StartRecord']['file'] ={
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'file to store video in',
        }
        self.requirements['StopRecord'] ={}
        self.requirements['AutoConfigure'] ={}
        self.requirements['AutoConfigure']['brightness_reference'] ={
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'Brightness reference for guiding autto contrast',
        }
        self.requirements['Configure'] = {}
        self.requirements['Configure']['parameters'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'manual configuration for camera settings',
        }
        self.requirements['Measure'] = {}
        self.requirements['Measure']['file'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'filename to store image at',
        }
        self.requirements['LoadConfiguration'] ={}
        self.requirements['LoadConfiguration']['file'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'filename to store image at',
        }
        self.requirements['SaveConfiguration'] ={}
        self.requirements['SaveConfiguration']['file'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'filename to store image at',
        }
        
        self.name = name

    def Connect(self,cam_id=0):
        """ Start connection to camera.
        """
        self.fConnect(cam_id)
        self.addlog(self.name + ' is availible.')
        return self.returnlog()

    def fConnect(self,cam_id):
        if not self.simulation:
            from Devices.Drivers import camera
            try:
                self.handle = camera.UEye(cam_id,self.name)
            except Exception:
                temp = input('Do you want to try to connect again?([y],n)')
                if temp in ['', 'y', 'yes']:
                    self.handle = camera.UEye(cam_id)
        self.addlog(self.name + ' is connected.')

    def Disconnect(self):
        """ Stop connection to camera.
        """
        self.fDisconnect()
        return self.returnlog()

    def fDisconnect(self):
        if not self.simulation:
            self.handle.close()
        self.addlog(self.name + ' is disconnected.')
    
    def StartFeed(self):
        """ Starts a live feed of the camera in a window.
        """
        if not self.simulation:
                self.handle.start_feed()
        self.addlog(self.name + ' started a live feed of camera in window.')
    
    def StopFeed(self):
        """ Stops a live feed of the camera in a window.
        """
        if not self.simulation:
                self.handle.stop_feed()
        self.addlog(self.name + ' stopped a live feed of camera in window.')

    def StartRecord(self, file):
        """ Starts a live feed of the camera in a window.
        """
        if not self.simulation:
                self.handle.start_record(file)
        self.addlog(self.name + ' started a recording of video to file.')
    
    def StopRecord(self):
        """ Starts a live feed of the camera in a window.
        """
        if not self.simulation:
                self.handle.stop_record()
        self.addlog(self.name + ' stopped a recording of video to file.')

    def AutoConfigure(self, brightness_reference=100):
        """ Auto sets the brightness, gain and white balance.
            Brightness reference argument can be used to adjust resulting image brightness.
        """
        if not self.simulation:
            self.handle.auto_configure(brightness_reference)
        self.addlog(self.name + ' auto configured camera')
        return self.returnlog()
    
    def Configure(self, parameters):
        """ Manual control over the exposure, gain, black_level and gamma.
            To use provide a dictionary with keys being the name of the parameter to set.
            ex: parameter = {'exposure':40.0,'gain': 50, 'black_level':200, 'gamma':1.0}
            Exposure varies by camera: 0.020ms to 69.847 for UI-3250 model (check uEye cockpit for specifics)
            Gain (master) can be set between 0-100
            Black level can be set between 0-255
            Gamma can be set between 0.01 and 10
        """
        if not self.simulation:
            self.handle.configure(parameters)
        self.addlog(self.name + ' manually configured camera to ' + str(parameters))
        return self.returnlog()

    def Measure(self, file):
        """ Captures and saves an image to path specified by file argument.
        """
        if not self.simulation:
            self.handle.save_image(file)
        self.addlog(self.name + ' took image and saved at ' + str(file))
        return self.returnlog()

    def LoadConfiguration(self,file=None):
        """ Loads parameters from a .ini file and writes them to camera. 
            If no file is supplied, a Windows open file dialog is displayed.
        """
        if not self.simulation:
            self.handle.load_parameters(file)
        self.addlog(self.name + 'Configured camera according to parameters in: ' + str(file))
        return self.returnlog()

    def SaveConfiguration(self,file=None):
        """ Saves current parameters from a camera to an .ini file. 
            If no file is supplied, a Windows save file dialog is displayed.
        """
        if not self.simulation:
            self.handle.save_parameters(file)
        self.addlog(self.name + 'Saved current camera cparameters to: ' + str(file))
        return self.returnlog()