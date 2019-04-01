# blank
# Only import 'basic' python packages up here.  All others should be imported
# within the methods.

# Handle the different relative locations for independently running and
#

from Devices import Device


class Pump(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.descriptors.append('pump')
        self.requirements['Set'] = {}
        self.requirements['Set']['pressure'] = {'value': '', 'source': 'apparatus', 'address': '', 'desc': 'Pump pressure in kPa'}
        
    def Set(self, pressure=''):
        self.pressure = pressure
        self.addlog(self.name + ' set to ' + self.pressure)

        return self.returnlog()
