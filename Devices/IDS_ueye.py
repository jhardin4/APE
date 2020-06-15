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
        self.requirements['Measure'] = {}
        self.requirements['Measure']['file'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'filename to store image at',
        }
        self.requirements['Configure'] = {}
        self.requirements['Configure']['gain'] = {
            'value': '',
            'source': 'direct',
            'address': '',
            'desc': 'values for master and RGB gains (0-100)',
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

    def AutoConfigure(self, brightness_reference=70):
        """ Auto sets the brightness, gain and white balance.
            Brightness reference argument can be used to adjust resulting image brightness.
        """
        if not self.simulation:
            self.handle.auto_configure(auto_reference=brightness_reference)
        self.addlog(self.name + ' auto configured camera')
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