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

    def Connect(self):
        self.fConnect()
        self.addlog(self.name + ' is availible.')
        return self.returnlog()

    def fConnect(self):
        if not self.simulation:
            from Devices.Drivers import camera

            try:
                self.handle = camera.UEye()
            except Exception:
                temp = input('Do you want to try to connect again?([y],n)')
                if temp in ['', 'y', 'yes']:
                    self.handle = camera.UEye()
        self.addlog(self.name + ' is connected.')

    def Disconnect(self):
        self.fDisconnect()
        return self.returnlog()

    def fDisconnect(self):
        if not self.simulation:
            self.handle.close()
        self.addlog(self.name + ' is disconnected.')

    def Measure(self, file):
        if not self.simulation:
            self.handle.save_image(file)
        self.addlog(self.name + ' took image and saved at ' + str(file))
        return self.returnlog()

    def Configure(self, **kwargs):
        if not self.simulation:
            if 'gain' in kwargs:
                gain = kwargs['gain']
                self.handle.set_gain(
                    master=gain[0], red=gain[1], green=gain[2], blue=gain[3]
                )

        self.addlog(
            self.name
            + ' configured the following settings:\n\t'
            + str([k for k in kwargs.keys()])
        )
        return self.returnlog()
