# This Device represents a general G-Code motion system. 

# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#
from Devices import Device


class Sensor(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.returnformat = ''
        self.result = ''

    def StoreMeasurement(self, address, addresstype, result):
        if addresstype == 'pointer':
            # this assumes that address=[0] exists when this method is used.
            address[0] = result
        elif addresstype == 'zmqNode_AppAddress':
            # assumes that address is of the form
            # {'global':'appa', 'AppAddress': ['information','procedure']}
            kwargs = {'infoAddress': address['AppAddress'], 'value': result}
            message = {'subject': 'target.apparatus.setValue', 'kwargs': kwargs}
            self.executor.node.send(address['global'], message)

    def Measure(self, address='', addresstype=''):
        pass

    def Sensor_Calibrate():
        pass


if __name__ == '__main__':
    mySensor = Sensor('mySensor')
